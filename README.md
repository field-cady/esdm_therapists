# Contact Map

Interactive map showing contact locations with clickable markers.

## Features

- 📍 Visual map of all contact locations
- 🖱️ Click markers to see contact details
- 🔍 Search contacts in sidebar
- 📊 Statistics dashboard
- 👥 Multiple people per location support

## Files

- `app.py` - Main Streamlit application
- `contacts.jsonl` - Contact data (JSON Lines format)
- `requirements.txt` - Python dependencies

## Contact Data Format

Each line in `contacts.jsonl` is a JSON object with:

```json
{
  "lat": 37.7749,
  "lon": -122.4194,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "(555) 555-5555",
  "organization": "Company Name",
  "role": "Job Title"
}
```

**Required fields:**
- `lat` - Latitude
- `lon` - Longitude
- `name` - Person's name

**Optional fields:**
- `email` - Email address
- `phone` - Phone number
- `organization` - Company/organization
- `role` - Job title/role

## Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Push this directory to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select your repository and branch
5. Set main file path to `app.py`
6. Deploy!

## Adding Your Data

Replace the contents of `contacts.jsonl` with your actual contact data. 

**Important:** Keep one JSON object per line (JSONL format).

Example:
```
{"lat": 40.7128, "lon": -74.0060, "name": "Alice Smith", "email": "alice@example.com", "phone": "555-1234", "organization": "Acme Corp", "role": "Manager"}
{"lat": 40.7128, "lon": -74.0060, "name": "Bob Jones", "email": "bob@example.com", "phone": "555-5678", "organization": "Acme Corp", "role": "Developer"}
```

## Features Explained

### Map Interaction
- **Red markers** show locations with contacts
- **Hover** over markers to see a tooltip with all people at that location
- **Click** markers for detailed information
- **Zoom/Pan** to explore different areas

### Sidebar
- View all contacts organized by location
- Search by name, email, or organization
- See contact details without clicking map

### Multiple People Per Location
The app automatically groups people at the same coordinates and shows them all when you click the marker.

## Customization

### Marker Size
Change `get_radius=20000` in `app.py` to adjust marker size (in meters)

### Marker Color
Change `get_fill_color=[255, 0, 0, 160]` to use different colors:
- `[R, G, B, Alpha]` where values are 0-255
- Example: `[0, 128, 255, 160]` for blue

### Initial Zoom
Change `zoom=4` in the `ViewState` to adjust initial zoom level (higher = more zoomed in)

## Tips

- Use actual lat/lon coordinates for accurate positioning
- Multiple people at the exact same location will be grouped together
- Search is case-insensitive and searches across all fields
- Map centers automatically on your data

## Example Use Cases

- Sales team territory map
- Customer locations
- Remote team member directory
- Event attendee map
- Field agent locations
- Office/branch locations
