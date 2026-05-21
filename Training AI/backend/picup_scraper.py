#!/usr/bin/env python3
"""
Picup Backoffice and Frontend Scraper
Collects driver earnings and trip data from both Picup sites
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, date, timedelta
import re
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PicupScraper:
    """Scraper for collecting driver earnings and trip data from Picup sites"""

    def __init__(self):
        self.backoffice_url = "https://backoffice.picup.co.za"
        self.frontend_url = "https://picup.co.za"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # Load credentials from environment variables
        self.username = os.getenv('PICUP_USERNAME')
        self.password = os.getenv('PICUP_PASSWORD')

    def login_backoffice(self) -> bool:
        """Login to Picup backoffice"""
        return self._login_to_site(self.backoffice_url, "backoffice")

    def login_frontend(self) -> bool:
        """Login to Picup frontend"""
        return self._login_to_site(self.frontend_url, "frontend")

    def _login_to_site(self, base_url: str, site_type: str) -> bool:
        """Generic login method for both sites"""
        try:
            # First, get the login page to extract any CSRF tokens or form data
            login_url = f"{base_url}/login"
            response = self.session.get(login_url)

            if response.status_code != 200:
                logger.error(f"Failed to access {site_type} login page: {response.status_code}")
                return False

            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for login form
            login_form = soup.find('form', {'action': re.compile(r'login|signin|auth')})
            if not login_form:
                # Try alternative login approach
                return self._alternative_login(base_url, site_type)

            # Extract form data
            form_data = {}
            for input_field in login_form.find_all('input'):
                name = input_field.get('name')
                value = input_field.get('value', '')
                if name:
                    form_data[name] = value

            # Update with credentials
            if 'username' in form_data or 'email' in form_data:
                form_data['username'] = self.username or form_data.get('username', '')
                form_data['email'] = self.username or form_data.get('email', '')
            if 'password' in form_data:
                form_data['password'] = self.password or form_data.get('password', '')

            # Submit login form
            action_url = login_form.get('action', '/login')
            if not action_url.startswith('http'):
                action_url = f"{base_url}{action_url}"

            response = self.session.post(action_url, data=form_data)

            # Check if login was successful
            if response.status_code in [200, 302] and ('dashboard' in response.url or 'welcome' in response.url):
                logger.info(f"Successfully logged in to {site_type}")
                return True
            else:
                logger.error(f"{site_type} login failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"{site_type} login error: {e}")
            return False

    def _alternative_login(self, base_url: str, site_type: str) -> bool:
        """Alternative login method for different authentication systems"""
        try:
            # Try direct API login
            api_login_url = f"{base_url}/api/auth/login"
            login_data = {
                'username': self.username,
                'password': self.password,
                'grant_type': 'password'
            }

            response = self.session.post(api_login_url, json=login_data)

            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    self.session.headers.update({
                        'Authorization': f"Bearer {data['access_token']}"
                    })
                    logger.info(f"Successfully logged in to {site_type} via API")
                    return True

            # Try form-based login with common field names
            form_data = {
                'username': self.username,
                'password': self.password,
                'email': self.username,
                'login': self.username,
                'user': self.username
            }

            response = self.session.post(f"{base_url}/login", data=form_data)

            if response.status_code in [200, 302] and ('dashboard' in response.url or 'welcome' in response.url):
                logger.info(f"Successfully logged in to {site_type} via alternative method")
                return True

            return False

        except Exception as e:
            logger.error(f"{site_type} alternative login error: {e}")
            return False

    def get_driver_earnings(self, driver_id: str = None, date_from: date = None, date_to: date = None) -> List[Dict]:
        """Get earnings data from backoffice dashboard"""
        try:
            if not self.login_backoffice():
                logger.error("Failed to login to backoffice, cannot fetch earnings data")
                return []

            # Calculate date range
            if not date_from:
                date_from = date.today() - timedelta(days=30)
            if not date_to:
                date_to = date.today()

            # Try different API endpoints for earnings data
            earnings_data = []

            # Method 1: Try direct API endpoint
            api_endpoints = [
                f"{self.backoffice_url}/api/drivers/earnings",
                f"{self.backoffice_url}/api/earnings/drivers",
                f"{self.backoffice_url}/api/finance/drivers",
                f"{self.backoffice_url}/api/payments/drivers"
            ]

            for endpoint in api_endpoints:
                try:
                    params = {
                        'from': date_from.isoformat(),
                        'to': date_to.isoformat()
                    }
                    if driver_id:
                        params['driver_id'] = driver_id

                    response = self.session.get(endpoint, params=params)

                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list) and len(data) > 0:
                            earnings_data = self._parse_api_response(data)
                            break
                        elif isinstance(data, dict) and 'earnings' in data:
                            earnings_data = self._parse_api_response(data['earnings'])
                            break

                except Exception as e:
                    logger.debug(f"API endpoint {endpoint} failed: {e}")
                    continue

            # Method 2: Scrape dashboard page
            if not earnings_data:
                earnings_data = self._scrape_dashboard_earnings(driver_id, date_from, date_to)

            logger.info(f"Collected earnings data for {len(earnings_data)} drivers")
            return earnings_data

        except Exception as e:
            logger.error(f"Error fetching driver earnings: {e}")
            return []

    def get_trip_information(self, date_from: date = None, date_to: date = None) -> List[Dict]:
        """Get trip information from frontend post-dispatch overview"""
        try:
            if not self.login_frontend():
                logger.error("Failed to login to frontend, cannot fetch trip data")
                return []

            # Calculate date range
            if not date_from:
                date_from = date.today() - timedelta(days=30)
            if not date_to:
                date_to = date.today()

            trip_data = []

            # Try different API endpoints for trip data
            api_endpoints = [
                f"{self.frontend_url}/api/dashboard/post-dispatch/overview",
                f"{self.frontend_url}/api/trips/overview",
                f"{self.frontend_url}/api/dispatch/trips",
                f"{self.frontend_url}/dashboard/post-dispatch/overview"
            ]

            for endpoint in api_endpoints:
                try:
                    params = {
                        'from': date_from.isoformat(),
                        'to': date_to.isoformat()
                    }

                    response = self.session.get(endpoint, params=params)

                    if response.status_code == 200:
                        if endpoint.endswith('.json') or 'api' in endpoint:
                            data = response.json()
                            if isinstance(data, list) and len(data) > 0:
                                trip_data = self._parse_trip_api_response(data)
                                break
                            elif isinstance(data, dict) and 'trips' in data:
                                trip_data = self._parse_trip_api_response(data['trips'])
                                break
                        else:
                            # HTML response - scrape it
                            soup = BeautifulSoup(response.text, 'html.parser')
                            trip_data = self._scrape_trip_overview(soup)
                            if trip_data:
                                break

                except Exception as e:
                    logger.debug(f"Trip endpoint {endpoint} failed: {e}")
                    continue

            logger.info(f"Collected trip data for {len(trip_data)} trips")
            return trip_data

        except Exception as e:
            logger.error(f"Error fetching trip information: {e}")
            return []

    def _parse_api_response(self, data: List[Dict]) -> List[Dict]:
        """Parse API response into standardized earnings format"""
        earnings_data = []

        for item in data:
            try:
                earnings_record = {
                    'driver_id': item.get('driver_id') or item.get('id'),
                    'driver_name': item.get('driver_name') or item.get('name'),
                    'date': item.get('date') or item.get('period'),
                    'total_earnings': float(item.get('total_earnings', 0)),
                    'trips_completed': int(item.get('trips_completed', 0)),
                    'cash_collected': float(item.get('cash_collected', 0)),
                    'tips_received': float(item.get('tips', 0)),
                    'bonuses': float(item.get('bonuses', 0)),
                    'deductions': float(item.get('deductions', 0)),
                    'net_earnings': float(item.get('net_earnings', 0)),
                    'source': 'picup_backoffice'
                }
                earnings_data.append(earnings_record)
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse earnings record: {e}")
                continue

        return earnings_data

    def _parse_trip_api_response(self, data: List[Dict]) -> List[Dict]:
        """Parse trip API response into standardized format"""
        trip_data = []

        for item in data:
            try:
                trip_record = {
                    'trip_id': item.get('trip_id') or item.get('id'),
                    'order_id': item.get('order_id') or item.get('order_number'),
                    'driver_id': item.get('driver_id'),
                    'driver_name': item.get('driver_name'),
                    'client_name': item.get('client_name') or item.get('client'),
                    'store_name': item.get('store_name'),
                    'pickup_address': item.get('pickup_address'),
                    'delivery_address': item.get('delivery_address'),
                    'status': item.get('status'),
                    'amount': float(item.get('amount', 0)),
                    'distance': float(item.get('distance', 0)),
                    'duration': item.get('duration'),
                    'scheduled_time': item.get('scheduled_time'),
                    'pickup_time': item.get('pickup_time'),
                    'delivery_time': item.get('delivery_time'),
                    'created_at': item.get('created_at'),
                    'source': 'picup_frontend'
                }
                trip_data.append(trip_record)
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse trip record: {e}")
                continue

        return trip_data

    def _scrape_dashboard_earnings(self, driver_id: str = None, date_from: date = None, date_to: date = None) -> List[Dict]:
        """Scrape earnings data from backoffice dashboard page"""
        try:
            dashboard_url = f"{self.backoffice_url}/dashboard"
            response = self.session.get(dashboard_url)

            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for earnings tables or data
            earnings_data = []

            # Try to find earnings table
            earnings_table = soup.find('table', {'class': re.compile(r'earnings|finance|payments')})
            if earnings_table:
                earnings_data = self._parse_earnings_table(earnings_table)

            # Look for JSON data in script tags
            scripts = soup.find_all('script', {'type': 'application/json'})
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if 'earnings' in data or 'drivers' in data:
                        earnings_data = self._extract_earnings_from_json(data)
                        break
                except (json.JSONDecodeError, TypeError):
                    continue

            return earnings_data

        except Exception as e:
            logger.error(f"Error scraping backoffice dashboard: {e}")
            return []

    def _scrape_trip_overview(self, soup: BeautifulSoup) -> List[Dict]:
        """Scrape trip data from post-dispatch overview page"""
        try:
            trip_data = []

            # Look for trip tables
            trip_table = soup.find('table', {'class': re.compile(r'trip|dispatch|order')})
            if trip_table:
                trip_data = self._parse_trip_table(trip_table)

            # Look for trip cards or sections
            trip_cards = soup.find_all(['div', 'section'], {'class': re.compile(r'trip|order|dispatch')})
            if not trip_data and trip_cards:
                trip_data = self._extract_trips_from_cards(trip_cards)

            # Look for JSON data in script tags
            if not trip_data:
                scripts = soup.find_all('script', {'type': 'application/json'})
                for script in scripts:
                    try:
                        data = json.loads(script.string)
                        if 'trips' in data or 'orders' in data:
                            trip_data = self._extract_trips_from_json(data)
                            break
                    except (json.JSONDecodeError, TypeError):
                        continue

            return trip_data

        except Exception as e:
            logger.error(f"Error scraping trip overview: {e}")
            return []

    def _parse_earnings_table(self, table) -> List[Dict]:
        """Parse earnings data from HTML table"""
        earnings_data = []

        rows = table.find_all('tr')[1:]  # Skip header row

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 8:  # Assuming standard earnings table format
                try:
                    earnings_record = {
                        'driver_id': cols[0].text.strip(),
                        'driver_name': cols[1].text.strip(),
                        'date': cols[2].text.strip(),
                        'total_earnings': float(re.sub(r'[^\d.]', '', cols[3].text.strip()) or 0),
                        'trips_completed': int(re.sub(r'[^\d]', '', cols[4].text.strip()) or 0),
                        'cash_collected': float(re.sub(r'[^\d.]', '', cols[5].text.strip()) or 0),
                        'tips_received': float(re.sub(r'[^\d.]', '', cols[6].text.strip()) or 0),
                        'net_earnings': float(re.sub(r'[^\d.]', '', cols[7].text.strip()) or 0),
                        'bonuses': 0.0,
                        'deductions': 0.0,
                        'source': 'picup_backoffice_scraped'
                    }
                    earnings_data.append(earnings_record)
                except (ValueError, IndexError) as e:
                    logger.warning(f"Failed to parse earnings table row: {e}")
                    continue

        return earnings_data

    def _parse_trip_table(self, table) -> List[Dict]:
        """Parse trip data from HTML table"""
        trip_data = []

        rows = table.find_all('tr')[1:]  # Skip header row

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 10:  # Assuming standard trip table format
                try:
                    trip_record = {
                        'trip_id': cols[0].text.strip(),
                        'order_id': cols[1].text.strip(),
                        'driver_name': cols[2].text.strip(),
                        'client_name': cols[3].text.strip(),
                        'store_name': cols[4].text.strip(),
                        'status': cols[5].text.strip(),
                        'amount': float(re.sub(r'[^\d.]', '', cols[6].text.strip()) or 0),
                        'scheduled_time': cols[7].text.strip(),
                        'pickup_time': cols[8].text.strip(),
                        'delivery_time': cols[9].text.strip(),
                        'source': 'picup_frontend_scraped'
                    }
                    trip_data.append(trip_record)
                except (ValueError, IndexError) as e:
                    logger.warning(f"Failed to parse trip table row: {e}")
                    continue

        return trip_data

    def _extract_earnings_from_json(self, data: Dict) -> List[Dict]:
        """Extract earnings data from JSON response"""
        earnings_data = []

        # Try different JSON structures
        possible_keys = ['earnings', 'drivers', 'data', 'results']

        for key in possible_keys:
            if key in data and isinstance(data[key], list):
                for item in data[key]:
                    if isinstance(item, dict) and ('earnings' in item or 'total' in item):
                        try:
                            earnings_record = {
                                'driver_id': item.get('driver_id') or item.get('id'),
                                'driver_name': item.get('driver_name') or item.get('name'),
                                'date': item.get('date') or item.get('period'),
                                'total_earnings': float(item.get('total_earnings') or item.get('total', 0)),
                                'trips_completed': int(item.get('trips_completed') or item.get('trips', 0)),
                                'cash_collected': float(item.get('cash_collected', 0)),
                                'tips_received': float(item.get('tips_received') or item.get('tips', 0)),
                                'bonuses': float(item.get('bonuses', 0)),
                                'deductions': float(item.get('deductions', 0)),
                                'net_earnings': float(item.get('net_earnings') or item.get('total', 0)),
                                'source': 'picup_backoffice_json'
                            }
                            earnings_data.append(earnings_record)
                        except (ValueError, TypeError):
                            continue
                break

        return earnings_data

    def _extract_trips_from_json(self, data: Dict) -> List[Dict]:
        """Extract trip data from JSON response"""
        trip_data = []

        # Try different JSON structures
        possible_keys = ['trips', 'orders', 'data', 'results']

        for key in possible_keys:
            if key in data and isinstance(data[key], list):
                for item in data[key]:
                    if isinstance(item, dict) and ('trip_id' in item or 'order_id' in item):
                        try:
                            trip_record = {
                                'trip_id': item.get('trip_id') or item.get('id'),
                                'order_id': item.get('order_id') or item.get('order_number'),
                                'driver_id': item.get('driver_id'),
                                'driver_name': item.get('driver_name'),
                                'client_name': item.get('client_name') or item.get('client'),
                                'store_name': item.get('store_name'),
                                'status': item.get('status'),
                                'amount': float(item.get('amount', 0)),
                                'scheduled_time': item.get('scheduled_time'),
                                'pickup_time': item.get('pickup_time'),
                                'delivery_time': item.get('delivery_time'),
                                'source': 'picup_frontend_json'
                            }
                            trip_data.append(trip_record)
                        except (ValueError, TypeError):
                            continue
                break

        return trip_data

    def _extract_trips_from_cards(self, cards) -> List[Dict]:
        """Extract trip data from HTML cards"""
        trip_data = []

        for card in cards[:20]:  # Limit to first 20 cards
            try:
                # Extract data from card elements
                trip_id = card.find(['span', 'div'], {'class': re.compile(r'trip.*id|order.*id')})
                driver_name = card.find(['span', 'div'], {'class': re.compile(r'driver|agent')})
                status = card.find(['span', 'div'], {'class': re.compile(r'status')})
                amount = card.find(['span', 'div'], {'class': re.compile(r'amount|price')})

                if trip_id and driver_name:
                    trip_record = {
                        'trip_id': trip_id.text.strip(),
                        'driver_name': driver_name.text.strip(),
                        'status': status.text.strip() if status else 'unknown',
                        'amount': float(re.sub(r'[^\d.]', '', amount.text.strip()) or 0) if amount else 0,
                        'source': 'picup_frontend_cards'
                    }
                    trip_data.append(trip_record)

            except Exception as e:
                logger.debug(f"Failed to extract from trip card: {e}")
                continue

        return trip_data


def test_scraper():
    """Test the scraper functionality"""
    scraper = PicupScraper()

    print("Testing Backoffice Login...")
    if scraper.login_backoffice():
        print("✓ Backoffice login successful")

        # Test getting earnings
        earnings = scraper.get_driver_earnings()
        print(f"✓ Found {len(earnings)} earnings records from backoffice")

        if earnings:
            print("Sample earnings record:")
            print(json.dumps(earnings[0], indent=2))
    else:
        print("✗ Backoffice login failed")

    print("\nTesting Frontend Login...")
    if scraper.login_frontend():
        print("✓ Frontend login successful")

        # Test getting trip information
        trips = scraper.get_trip_information()
        print(f"✓ Found {len(trips)} trip records from frontend")

        if trips:
            print("Sample trip record:")
            print(json.dumps(trips[0], indent=2))
    else:
        print("✗ Frontend login failed")


if __name__ == "__main__":
    test_scraper()