import argparse
import csv
import sqlite3
from datetime import datetime, UTC
from pathlib import Path

DB_FILE = Path("maintenance.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS maintenance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car TEXT NOT NULL,
            date TEXT NOT NULL,          -- store as ISO string, e.g. '2025-12-02'
            mileage INTEGER,             -- odometer reading
            type TEXT NOT NULL,          
            cost REAL DEFAULT 0,         -- numeric cost
            notes TEXT,                  -- optional
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def print_record(r):
    id_str = f"#{r['id']}"
    date_str = r.get("date", "")
    car_str = r.get("car", "")

    mileage = r.get("mileage")
    if mileage is not None:
        mileage_str = f"{mileage:,} mi"
    else:
        mileage_str = "—"

    cost = r.get("cost")
    if cost is not None:
        cost_str = f"${cost:.2f}"
    else:
        cost_str = "—"

    rec_type = r.get("type", "maintenance")
    
    print(f"{id_str:<4} | {date_str} | {car_str} | {mileage_str}")
    print(f"     {rec_type} - {cost_str}")

    notes = r.get("notes")
    if notes:
        print(f"     Notes: {notes}")

    print()


def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format '{date_str}'. Use YYYY-MM-DD") 


def handle_add(args):
    date_str = args.date or datetime.now().strftime("%Y-%m-%d")
    now_iso = datetime.now(UTC).isoformat(timespec="seconds")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO maintenance_records (
            car, date, mileage, type, cost, notes, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            args.car,
            date_str,
            args.mileage,
            args.type,
            args.cost or 0,
            args.notes,
            now_iso,
            now_iso,
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    print("Maintenance record added successfully.")
    print(f"Record ID: {new_id}")
    print(f"Date: {date_str}")
    print(f"Car: {args.car}")
    print(f"Mileage: {args.mileage}")
    print(f"Type: {args.type}")
    print(f"Cost: {args.cost or 0}")
    if args.notes:
        print(f"Notes: {args.notes}")



def handle_list(args):
    conn = get_connection()
    cur = conn.cursor()

    if args.car:
        rows = cur.execute(
            "SELECT * FROM maintenance_records WHERE LOWER(car) = LOWER(?) ORDER BY date ASC",
            (args.car,)
        ).fetchall()
    else:
        rows = cur.execute(
            "SELECT * FROM maintenance_records ORDER BY date ASC"
        ).fetchall()

    conn.close()

    if not rows:
        print("No maintenance records found.")
        return

    print(f"Showing {len(rows)} maintenance records:")
    for r in rows:
        record = dict(r)
        print_record(record)


def handle_export(args):
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM maintenance_records ORDER BY date ASC").fetchall()
    conn.close()

    if not rows:
        print("No records to export.")
        return

    output_path = args.file or "maintenance_export.csv"

    fieldnames = ["id", "date", "car", "mileage", "type", "cost", "notes"]

    try:
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                r = dict(row)
                writer.writerow({
                    "id": r["id"],
                    "date": r["date"],
                    "car": r["car"],
                    "mileage": r["mileage"],
                    "type": r["type"],
                    "cost": r["cost"],
                    "notes": r["notes"],
                })
    except OSError as e:
        print(f"Failed to write export file: {e}")
        return
    
    print(f"Exported {len(rows)} record(s) to {output_path}")


def handle_search(args):
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM maintenance_records").fetchall()
    conn.close()

    records = [dict(r) for r in rows]

    after_date = None
    before_date = None

    if getattr(args, "after", None):
        try:
            after_date = parse_date(args.after)
        except ValueError as e:
            print(e)
            return
        
    if getattr(args, "before", None):
        try:
            before_date = parse_date(args.before)
        except ValueError as e:
            print(e)
            return
        
    results = []

    for r in records:
        match = True

        if args.car:
            if args.car.lower() not in r["car"].lower():
                match = False

        if match and args.type:
            if args.type.lower() not in r["type"].lower():
                match = False

        if match and args.min_mileage is not None:
            if r["mileage"] is None or r["mileage"] < args.min_mileage:
                match = False

        if match and args.max_mileage is not None:
            if r["mileage"] is None or r["mileage"] > args.max_mileage:
                match = False

        if match and (after_date or before_date):
            try:
                record_date = parse_date(r["date"])
            except ValueError:
                match = False
            else:
                if after_date and record_date <= after_date:
                    match = False
                if before_date and record_date >= before_date:
                    match = False

        if match and args.notes_contains:
            notes = r.get("notes", "") or ""
            if args.notes_contains.lower() not in notes.lower():
                match = False

        if match:
            results.append(r)

    if not results:
        print("No records matched your search.")
        return
    
    print(f"Found {len(results)} matching record(s):")
    for r in results:
        print_record(r)



def handle_delete(args):
    rec_id = args.id

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM maintenance_records WHERE id = ?",
        (rec_id,),
    )
    deleted_rows = cur.rowcount
    conn.commit()
    conn.close()

    if deleted_rows == 0:
        print(f"No record found with ID {rec_id}.")
    else:
        print(f"Record ID {rec_id} deleted successfully.")


def handle_edit(args):
    rec_id = args.id

    # Fetch current record
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT * FROM maintenance_records WHERE id = ?",
        (rec_id,),
    ).fetchone()

    if row is None:
        conn.close()
        print(f"No record found with ID {rec_id}")
        return

    # Build UPDATE dynamically
    updates = []
    params = []

    if args.car is not None:
        updates.append("car = ?")
        params.append(args.car)
    if args.mileage is not None:
        updates.append("mileage = ?")
        params.append(args.mileage)
    if args.type is not None:
        updates.append("type = ?")
        params.append(args.type)
    if args.cost is not None:
        updates.append("cost = ?")
        params.append(args.cost)
    if args.date is not None:
        updates.append("date = ?")
        params.append(args.date)
    if args.notes is not None:
        updates.append("notes = ?")
        params.append(args.notes)

    if not updates:
        conn.close()
        print("No changes provided.")
        return

    updates.append("updated_at = ?")
    params.append(datetime.now(UTC).isoformat(timespec="seconds"))

    params.append(rec_id)
    sql = f"UPDATE maintenance_records SET {', '.join(updates)} WHERE id = ?"

    cur.execute(sql, params)
    conn.commit()
    conn.close()

    print(f"Updated record ID {rec_id}")




def build_parser():
    parser = argparse.ArgumentParser(
        description = "VinSight Maintenance Tracker"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    p_add = subparsers.add_parser("add", help="Add a maintenance record")
    p_add.add_argument("--car", required=True)
    p_add.add_argument("--mileage", type=int, required=True)
    p_add.add_argument("--type", required=True)
    p_add.add_argument("--cost", type=float, default=0)
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

    p_search = subparsers.add_parser("search", help="Search/filter maintenance records")
    p_search.add_argument("--car", help="Filter by car substring")
    p_search.add_argument("--type", help="Filter by maintenance type substring")
    p_search.add_argument("--min-mileage", type=int, dest="min_mileage")
    p_search.add_argument("--max-mileage", type=int, dest="max_mileage")
    p_search.add_argument("--after", help="Only show records after this date (YYYY-MM-DD)")
    p_search.add_argument("--before", help="Only show records before this date (YYYY-MM-DD)")
    p_search.add_argument("--notes-contains", dest="notes_contains", help="Filter by text in notes")
    p_search.set_defaults(func=handle_search)

    p_export = subparsers.add_parser("export", help="Export all records to CSV")
    p_export.add_argument("--file", help="Output CSV file name (option)")
    p_export.set_defaults(func=handle_export)



    return parser


def main():
    init_db()

    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

