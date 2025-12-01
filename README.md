# VinSight

VinSight is a car-focused toolkit I'm building for fun and learning.

Right now it's a **CLI maintenance tracker** written in Python.  
Long term, it will evolve into a full web app that can:

- Track maintenance across multiple cars
- Plan and log mods
- Manage wishlists
- Aggregate car listings from multiple sites

## Features (current)

- Add maintenance records (car, mileage, type, cost, notes)
- List all records or filter by car
- Edit records by ID
- Delete one or more records by ID
- Data saved in a JSON file (`maintenance_data.json`)

## Features (planned)'

- Add support for multiple cars with profiles
- Switch JSON with SQLite to enable queries
- Tagging system for quick categorization
- Cost tracking and automatic summaries
- Upcoming-maintenance reminders
- Mileage-based scheduling
- Import from external maintenance logs
- Build a simple backend API for CRUD operations
- Design a lightweight frontend dashboard
- Sync CLI and web versions
- Optional login + cloud sync

## Possible features
- Car-market watchlist
- Mobile app companion
- AI suggestions for maintenance based on patterns


## Usage

From the project folder:

```bash
python maintenance.py add --car "2025 BRZ" --mileage 4500 --type "Oil change" --cost 89.99 --notes "Motul oil + OEM filter"

python maintenance.py list

python maintenance.py edit --id 1 --mileage 5000 --cost 120 --notes "Updated after alignment"

python maintenance.py delete --id 2 3

```

- Uses Python 3.14
- Argprase for CLI
- JSON for storage




