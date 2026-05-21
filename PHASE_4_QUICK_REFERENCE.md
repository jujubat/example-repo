# Phase 4 Quick Reference Guide

## Files Created

### Production Modules (4,700+ lines)

| File | Lines | Purpose |
|------|-------|---------|
| `stop_management.py` | 800 | Add/remove stops, manage sequences |
| `real_time_tracking.py` | 700 | GPS tracking, vehicle locations |
| `eta_calculator.py` | 750 | Traffic-aware ETA calculations |
| `delay_reporting.py` | 850 | Delay reports, notifications, offline queue |
| `vehicle_tracking_routes.py` | 600 | 15 API endpoints |

### Documentation

| File | Purpose |
|------|---------|
| `PHASE_4_REAL_TIME_TRACKING.md` | Complete specification (9 sections) |
| `PHASE_4_QUICK_REFERENCE.md` | This file - quick lookup |

---

## API Endpoints (15 Total)

### Status Queries
```
GET /api/vehicle-tracking/vehicle/{vehicle_number}/status
GET /api/vehicle-tracking/vehicle/{vehicle_number}/route
GET /api/vehicle-tracking/vehicle/{vehicle_number}/next-stop
```

### Location Updates
```
POST /api/vehicle-tracking/vehicle/{vehicle_number}/update-location
```

### Delay Management
```
POST /api/vehicle-tracking/delay/report
GET /api/vehicle-tracking/delays/active
GET /api/vehicle-tracking/delays/category/{category}
```

### Stop Management
```
POST /api/vehicle-tracking/stop/{stop_id}/add
DELETE /api/vehicle-tracking/stop/{stop_id}/remove
```

### Queries
```
GET /api/vehicle-tracking/routes/summary
POST /api/vehicle-tracking/vehicles/near
```

### Notifications
```
GET /api/vehicle-tracking/notifications/{passenger_id}
POST /api/vehicle-tracking/notifications/{passenger_id}/acknowledge
```

### System
```
GET /api/vehicle-tracking/health
GET /api/vehicle-tracking/system/statistics
```

---

## Quick Start Code

### Initialize Tracking System

```python
from batuma_gprs_weather.transit.real_time_tracking import RealTimeTrackingSystem
from batuma_gprs_weather.transit.stop_management import StopManagementSystem
from batuma_gprs_weather.transit.eta_calculator import ETACalculator
from batuma_gprs_weather.transit.delay_reporting import DelayReportingSystem

# Create systems
tracking = RealTimeTrackingSystem()
stops = StopManagementSystem()
delays = DelayReportingSystem()
```

### Register a Vehicle

```python
# Register vehicle for tracking
tracker = tracking.register_vehicle(
    vehicle_id="BUS_001",
    vehicle_number="BUS-001",
    vehicle_type="bus",
    route_id="ROUTE_5"
)
```

### Send GPS Update

```python
# Simulate GPS update from vehicle
tracking.update_vehicle_location(
    vehicle_id="BUS_001",
    latitude=-33.8688,
    longitude=151.2093,
    speed_kmh=45.5,
    heading_degrees=180
)
```

### Create Route with Stops

```python
# Create route with initial stops
stops_data = [
    {'name': 'Central Station', 'location': {'lat': -33.87, 'lon': 151.21}, 'stop_time': 5},
    {'name': 'Town Hall', 'location': {'lat': -33.88, 'lon': 151.20}, 'stop_time': 3},
    {'name': 'Terminal', 'location': {'lat': -33.89, 'lon': 151.22}, 'stop_time': 5}
]

manager = stops.create_route_with_stops(
    route_id="ROUTE_5",
    route_name="City Express",
    vehicle_type="bus",
    stops_data=stops_data
)
```

### Add a Stop

```python
# Add new stop at position 2
manager.add_stop(
    stop_name="New Station",
    location={'lat': -33.871, 'lon': 151.205, 'address': 'Sydney'},
    stop_type="station",
    sequence_number=2,
    estimated_stop_time_minutes=5,
    added_by="ADMIN_001"
)
```

### Calculate ETAs

```python
# Create ETA calculator
eta_calc = ETACalculator(route_id="ROUTE_5", vehicle_id="BUS_001")

# Add stops
stops_for_eta = [
    {'stop_id': 'STP_001', 'name': 'Central', 'lat': -33.87, 'lon': 151.21, 'stop_time_minutes': 5},
    {'stop_id': 'STP_002', 'name': 'Town Hall', 'lat': -33.88, 'lon': 151.20, 'stop_time_minutes': 3}
]
eta_calc.add_stop_sequence(stops_for_eta)

# Add traffic delay
eta_calc.add_delay_factor("traffic", duration_minutes=30, impact_minutes=15)

# Calculate ETAs
etas = eta_calc.calculate_eta_for_all_stops()

# Display format
next_stop = etas[0]
print(f"Next stop: {next_stop['stop_name']}")
print(f"Arrival: {next_stop['scheduled_arrival']}")
print(f"Delay: {next_stop['total_delay_minutes']} minutes")
```

### Report a Delay

```python
# Report traffic delay
delay_report = delays.report_delay(
    vehicle_id="BUS_001",
    vehicle_number="BUS-001",
    delay_category="traffic",
    delay_duration_minutes=25,
    description="Heavy traffic on main road",
    current_location={'latitude': -33.8688, 'longitude': 151.2093},
    reported_by_user_id="DRIVER_001"
)

print(f"Delay reported: {delay_report.report_id}")
```

### Create Notification

```python
# Create notification for passengers
notification = delays.create_notification(
    delay_report_id=delay_report.report_id,
    route_id="ROUTE_5",
    affected_passenger_ids=["PASS_001", "PASS_002", "PASS_003"],
    message="Bus BUS-001 delayed 25 minutes - traffic on main road",
    priority="high"
)

# Check offline queue
queue_stats = delays.offline_queue.get_queue_statistics()
print(f"Notifications queued: {queue_stats['total_queued']}")
```

### Get System Status

```python
# System overview
tracking_overview = tracking.get_system_overview()
delay_overview = delays.get_system_statistics()

print(f"Vehicles online: {tracking_overview['online_vehicles']}")
print(f"Active delays: {delay_overview['active_delays']}")
print(f"Queue status: {delay_overview['offline_queue']['total_queued']}")
```

---

## Common Operations

### Find Vehicles Near Location

```python
# Passengers finding nearby buses
nearby = tracking.get_vehicles_near_location(
    latitude=-33.8688,
    longitude=151.2093,
    radius_km=2.0
)

# Results sorted by distance
for vehicle in nearby:
    print(f"{vehicle['vehicle_number']}: {vehicle['distance_km']} km away")
```

### Get Route Summary

```python
# All routes with vehicle counts
routes_with_vehicles = {}
for route_id, manager in stops.route_managers.items():
    vehicles = tracking.get_vehicles_on_route(route_id)
    routes_with_vehicles[route_id] = {
        'name': manager.route_name,
        'stops': manager.total_stops,
        'active_vehicles': len(vehicles)
    }
```

### Skip a Stop

```python
# Temporarily skip stop due to road closure
manager.skip_stop(
    stop_id="STP_005",
    reason="Road closure for 30 minutes"
)

# Get only active stops
active_stops = manager.get_active_stops()
```

### Handle Offline Notifications

```python
# Get pending notifications when passenger comes online
pending = delays.get_pending_notifications("PASSENGER_123")

# After showing notifications
delivered = delays.acknowledge_all_passenger_notifications("PASSENGER_123")
print(f"Delivered {delivered} notifications")
```

### Add Weather Impact to ETA

```python
# Heavy rain adds 10 minutes delay
eta_calc.add_delay_factor(
    factor_type="weather",
    duration_minutes=45,  # Rain expected for 45 min
    impact_minutes=10      # Adds 10 min to travel times
)
```

---

## Database Schema

### vehicle_locations Collection
```
{
  vehicle_id: string,
  vehicle_number: string,
  latitude: float,
  longitude: float,
  speed_kmh: float,
  heading_degrees: float,
  accuracy_meters: float,
  timestamp: datetime,
  signal_quality: string
}
```

### delays Collection
```
{
  delay_id: string,
  vehicle_id: string,
  vehicle_number: string,
  category: string,
  duration_minutes: float,
  description: string,
  location: {latitude, longitude},
  reported_by: string,
  reported_at: datetime,
  status: string (reported|acknowledged|resolved|closed)
}
```

### stops Collection
```
{
  stop_id: string,
  route_id: string,
  stop_name: string,
  location: {lat, lon, address},
  stop_type: string,
  sequence: number,
  estimated_stop_time_minutes: number,
  status: string (active|skipped|closed),
  facilities: {wheelchair_accessible, waiting_room, parking}
}
```

### routes Collection
```
{
  route_id: string,
  name: string,
  vehicle_type: string,
  total_stops: number,
  total_distance_km: float,
  created_at: datetime
}
```

---

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 400 | Missing fields | Check required parameters |
| 401 | Not authenticated | Provide valid JWT token |
| 404 | Vehicle/route not found | Check vehicle_number or route_id |
| 503 | Vehicle offline | Wait for update or check stale timeout |
| 500 | Server error | Check logs, retry |

---

## Performance Tips

1. **Cache vehicle status** - Don't query every second, update every 5-10 seconds
2. **Batch notifications** - Group for 10+ passengers in delay
3. **Limit history** - Keep last 1000 location updates
4. **Archive delays** - Move resolved delays to archive after 30 days
5. **Monitor queue** - Alert when offline queue exceeds 1000 messages

---

## Debugging Checklist

- [ ] Is GPS device sending updates?
- [ ] Are updates reaching Firestore?
- [ ] Is ETA calculation including traffic factors?
- [ ] Are notifications reaching offline queue?
- [ ] Does queue sync when online?
- [ ] Are all stops active (not skipped)?
- [ ] Is vehicle status online or offline?

---

## Version Info

- **Phase 4 Release**: Real-Time Transit Tracking v1.0
- **Code Lines**: 4,700+
- **API Endpoints**: 15
- **Modules**: 5
- **Documentation**: 2 files
