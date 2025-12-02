# VinSight

VinSight is a car-focused toolkit I'm building for fun and learning.

Right now it's a **CLI maintenance tracker** written in Python.  
Long term, it will evolve into a full web app that can:

- Track maintenance across multiple cars  
- Plan and log mods  
- Manage wishlists  
- Aggregate car listings from multiple sites  

---

## Features (current)

- Add maintenance records (car, mileage, type, cost, notes)
- List all records or filter by car
- Edit records by ID
- Delete records by ID
- Fully migrated to **SQLite** for storage (replaces the old JSON system)

---

## Features (planned)

- Support multiple car profiles
- Tagging system for categorizing maintenance
- Cost tracking + automatic summaries
- Upcoming-maintenance reminders
- Mileage-based scheduling
- Import from external maintenance logs
- Build a backend API for CRUD operations
- Lightweight frontend dashboard
- Sync between CLI and web versions
- Optional login + cloud sync

---

## Possible future features

- Car-market watchlist
- Mobile companion app
- AI suggestions based on maintenance patterns

---

## Usage

From the project folder:

```bash
python maintenance.py add --car "2025 BRZ" --mileage 4500 --type "Oil change" --cost 89.99 --notes "Motul oil + OEM filter"

python maintenance.py list

python maintenance.py edit --id 1 --mileage 5000 --cost 120 --notes "Updated after alignment"

python maintenance.py delete --id 3
