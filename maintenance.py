import argparse
import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path("maintenance_data.json")


def load_records():
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_records(records):
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def handle_add(args):
    records = load_records()

    record = {
        "id": len(records) + 1,
        "date": args.date or datetime.now().strftime("%Y-%m-%d"),
        "car": args.car,
        "mileage": args.mileage,
        "type": args.type,
        "cost": args.cost,
        "notes": args.notes
    }

    records.append(record)
    save_records(records)

    print("Maintenance record added successfully.")
    print(f"Record ID: {record['id']}")
    print(f"Date: {record['date']}")
    print(f"Car: {record['car']}")
    print(f"Mileage: {record['mileage']}")
    print(f"Type: {record['type']}")
    print(f"Cost: {record['cost']}")
    if record['notes']:
        print(f"Notes: {record['notes']}")

def handle_list(args):
    records = load_records()

    if args.car:
        records = [r for r in records if r["car"].lower() == args.car.lower()]

    if not records:
        print("No maintenance records found.")
        return
    
    print(f"Showing {len(records)} maintenance records:")
    for r in records:
        print(f"#{r['id']} | {r['date']} | {r['car']} | {r['mileage']} mi")
        print(f"   {r['type']} - ${r['cost']}")
        if r['notes']:
            print(f"   Notes: {r['notes']}")
        print()

def handle_delete(args):
    records = load_records()

    record_to_delete = None
    for r in records:
        if r["id"] == args.id:
            record_to_delete = r
            break
    if not record_to_delete:
        print(f"No record found with ID{args.id}")
        return
    
    records.remove(record_to_delete)
    save_records(records)

def handle_edit(args):
    records = load_records()

    record = None
    for r in records:
        if r["id"] == args.id:
            record = r
            break

    if not record:
        print(f"No record found with ID {args.id}")
        return
    
    if args.car is not None:
        record["car"] = args.car
    if args.mileage is not None:
        record["mileage"] = args.mileage
    if args.type is not None:
        record["type"] = args.type
    if args.cost is not None:
        record["cost"] = args.cost
    if args.date is not None:
        record["date"] = args.date
    if args.notes is not None:
        record["notes"] = args.notes

    save_records(records)
    print(f"Updated record ID {args.id}")


def build_parser():
    parser = argparse.ArgumentParser(
        description = "VinSight Maintenance Tracker"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    p_add = subparsers.add_parser("add", help="Add a maintenance record")
    p_add.add_argument("--car", required=True)
    p_add.add_argument("--mileage", type=int, required=True)
    p_add.add_argument("--type", required=True)
    p_add.add_argument("--cost", type=float, required=True)
    p_add.add_argument("--notes", default="")
    p_add.add_argument("--date", help="Date in YYYY-MM-DD (optional)")
    p_add.set_defaults(func=handle_add)
    

    p_list = subparsers.add_parser("list", help="List maintenance records")
    p_list.add_argument("--car", help="Filter records by car")
    p_list.set_defaults(func=handle_list)

    p_delete = subparsers.add_parser("delete", help="Delete a record by ID")
    p_delete.add_argument("--id", type=int, required=True, help="Record ID to delete")
    p_delete.set_defaults(func=handle_delete)

    p_edit = subparsers.add_parser("edit", help="Edit a record by ID")
    p_edit.add_argument("--id", type=int, required=True, help="Record ID to edit")
    p_edit.add_argument("--car", help="New car name")
    p_edit.add_argument("--mileage", type=int, help="New mileage")
    p_edit.add_argument("--type", help="New service type")
    p_edit.add_argument("--cost", type=float, help="New cost")
    p_edit.add_argument("--date", help="New date (YYYY-MM-DD)")
    p_edit.add_argument("--notes", help="New notes")
    p_edit.set_defaults(func=handle_edit)


    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

