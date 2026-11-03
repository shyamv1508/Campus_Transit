# Campus Transit

A beginner-friendly campus bus management and live-tracking project built with Python, SQLite, Tkinter, and a small standard-library HTTP server.

## Features
- Role-based sign-in for administrators, drivers, and students
- SQLite database with demo accounts and sample buses
- Admin dashboard for viewing students, drivers, and buses
- Driver page to publish bus GPS coordinates
- Live map page that refreshes the latest bus location
- No external Python packages required

## Requirements
- Python 3.10 or newer
- A web browser for the live map
- Internet connection for the Leaflet/OpenStreetMap map tiles

## Run on Windows
1. Download or clone this repository.
2. Open a terminal in the project folder.
3. Run `python app.py`.
4. Sign in with one of the demo accounts below.

## Demo accounts
| Role | Username | Password |
|---|---|---|
| Admin | admin | admin123 |
| Driver | driver1 | driver123 |
| Student | student1 | student123 |

These are demonstration credentials. Change them before using this project with real users.

## Live tracking
1. Start the desktop application.
2. Choose **Open live map** to open `http://127.0.0.1:8765/map`.
3. Choose **Start tracking page** to open the driver location sender.
4. Allow browser location access. GPS works on localhost; phones accessing the server over a network generally require HTTPS and firewall/network configuration.
5. The map polls the local server every three seconds.

The sample tracking endpoint accepts JSON in this shape:
```json
{"bus_id": 1, "latitude": 13.0827, "longitude": 80.2707}
```

## Project layout
- `app.py` — Tkinter desktop interface and login
- `database.py` — SQLite setup, demo data, and queries
- `tracking_server.py` — local HTTP API and map pages
- `templates/map.html` — live bus map
- `templates/driver.html` — browser GPS sender
- `tests/test_database.py` — basic database tests

## Notes
This is an educational starter project, not a production transport platform. It does not provide secure password hashing, HTTPS deployment, access tokens, or hardened user permissions. Do not store real student data until those safeguards are implemented.
