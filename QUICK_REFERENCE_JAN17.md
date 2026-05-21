# Quick Reference - New Features (Jan 17, 2026)

## 🌤️ Weather API

### Get Current Weather
**By Location Name:**
```bash
POST /api/weather/by-place
{
  "city": "London",
  "place": "Oxford Street",
  "postal_code": "SW1A1AA"
}
```

**By Coordinates:**
```bash
POST /api/weather/by-coordinates
{
  "latitude": 51.5074,
  "longitude": -0.1278
}
```

---

## 🛣️ Travel Time & Routes

### Calculate Travel Time
```bash
POST /api/routes/travel-time

# Option 1: By coordinates
{
  "start": {"latitude": 51.5074, "longitude": -0.1278},
  "end": {"latitude": 51.5175, "longitude": -0.1370}
}

# Option 2: By place names
{
  "start_place": "Oxford Street, London",
  "end_place": "Big Ben, London"
}
```

**Returns:**
- Distance (in km and text format)
- Duration (in minutes and text format)
- Number of steps/turns

---

## 🚌 Bus Routes

### Get Bus Categories
```bash
GET /api/transit/categories
```

**Returns:** Available categories (local, national, express, coach)

### Find Buses by Category & Location
```bash
POST /api/transit/routes/by-category
{
  "transit_type": "bus",
  "category": "local",
  "location": "Johannesburg",
  "search_name": "Route 101"
}
```

### Find Buses Near You
```bash
POST /api/transit/routes/near-location
{
  "latitude": -26.2023,
  "longitude": 28.0436,
  "transit_type": "bus",
  "radius_km": 2.0
}
```

**Returns:**
- All nearby bus stops within 2km radius
- All bus routes that pass through these stops
- Distance to each stop

---

## 🚆 Train Routes

Same as bus routes, but with `"transit_type": "train"`

**Train Categories:**
- local
- national
- express
- rapid
- commuter

---

## 📊 Frontend Usage

### Getting Weather in UI
1. Go to Routes section
2. Enter city name
3. Weather info will be displayed automatically

### Finding Travel Time
1. Click "Routes" in navigation
2. Enter start and end locations
3. Travel time and distance will show automatically

### Finding Local Buses/Trains
1. Use the new transit endpoints to search by:
   - Location name
   - Bus/Train category
   - Geographic radius

---

## 🔧 Configuration

Set these environment variables:

```bash
GOOGLE_MAPS_API_KEY=your_key_here
VC_API_KEY=your_visual_crossing_key
OPENWEATHER_API_KEY=your_key_here (optional)
```

---

## ✅ What's New

| Feature | Status | Type |
|---------|--------|------|
| Weather by location | ✅ Fixed | API |
| Travel time calculation | ✅ Added | API |
| Bus categories | ✅ Added | Data |
| Train categories | ✅ Added | Data |
| Location-based route search | ✅ Added | API |
| Weather UI removed | ✅ Cleaned | UI |

---

## ⚙️ System Status

- **Weather Services**: Available (now with location-based lookup)
- **GPRS Services**: Available (transit, routes, travel time)
- **Route Planning**: Enhanced with travel time
- **Bus/Train Management**: Categories now supported

**Last Updated:** January 17, 2026
