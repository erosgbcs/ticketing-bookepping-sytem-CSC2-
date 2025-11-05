#!/usr/bin/env python3
"""
Mini Ticketing/Booking System (debugged)
 - Cinema  -> cinema.csv
 - Bus     -> bus.csv
 - Airplane-> airplane.csv

Seat ID format: numeric row first then seat letter (e.g. 1A, 12B, 20F)
Input accepts either A1 or 1A (normalized to 1A).
"""

import csv
import os
from datetime import datetime

DATA_FILES = {
    "C": "cinema.csv",
    "B": "bus.csv",
    "A": "airplane.csv",
}

FIELDNAMES = ["Seat", "Status", "Name", "Timestamp", "Notes"]

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- Seat layout definitions ---
def cinema_layout():
    # Cinema: 10 rows (1–10), seats A–F (6 seats per row)
    rows = range(1, 11)          # rows 1..10
    seat_letters = ["A", "B", "C", "D", "E", "F"]
    seats = [f"{r}{s}" for r in rows for s in seat_letters]
    return seats

def bus_layout():
    # Bus: Rows 1-12, seats A-D (2+2)
    rows = range(1, 13)
    seat_letters = ["A", "B", "C", "D"]
    seats = [f"{r}{s}" for r in rows for s in seat_letters]
    return seats

def airplane_layout():
    # Airplane: Rows 1-20, seats A-F (3+3)
    rows = range(1, 21)
    seat_letters = ["A", "B", "C", "D", "E", "F"]
    seats = [f"{r}{s}" for r in rows for s in seat_letters]
    return seats

LAYOUT_FUNCTIONS = {
    "C": cinema_layout,
    "B": bus_layout,
    "A": airplane_layout,
}

# --- CSV helpers ---
def ensure_csv(service_key):
    path = DATA_FILES[service_key]
    if not os.path.exists(path):
        seats = LAYOUT_FUNCTIONS[service_key]()
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for s in seats:
                writer.writerow({"Seat": s, "Status": "Available", "Name": "", "Timestamp": "", "Notes": ""})

def load_seats(service_key):
    ensure_csv(service_key)
    path = DATA_FILES[service_key]
    seats = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            seats[row["Seat"]] = {
                "Status": row["Status"],
                "Name": row["Name"],
                "Timestamp": row["Timestamp"],
                "Notes": row.get("Notes", "")
            }
    return seats

def save_seats(service_key, seats):
    path = DATA_FILES[service_key]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        # keep ordering consistent with initial layout
        layout = LAYOUT_FUNCTIONS[service_key]()
        for s in layout:
            info = seats.get(s, {"Status": "Unavailable", "Name": "", "Timestamp": "", "Notes": ""})
            writer.writerow({
                "Seat": s,
                "Status": info["Status"],
                "Name": info["Name"],
                "Timestamp": info["Timestamp"],
                "Notes": info.get("Notes", "")
            })

# --- Utilities ---
def normalize_seat_id_input(raw):
    """Accept A1 or 1A (or mixed), return numeric-first like '1A'.
       If normalization impossible, returns original uppercased string."""
    if not raw:
        return raw
    s = raw.strip().upper()
    letters = ''.join(filter(str.isalpha, s))
    digits = ''.join(filter(str.isdigit, s))
    if digits and letters:
        # Return digits+letters (1A)
        return digits + letters
    return s

# --- Display ---
def print_seat_map(service_key, seats):
    layout = LAYOUT_FUNCTIONS[service_key]()
    print("\n--- SEAT LAYOUT (O=Available, X=Taken, -=Unavailable) ---")

    # All services printed with numeric-first format: row then letters
    layout_sorted = sorted(layout, key=lambda x: (int(''.join(filter(str.isdigit, x))), x))
    current_row = None
    for s in layout_sorted:
        row = ''.join(filter(str.isdigit, s))
        seat_letter = s[len(row):]
        if row != current_row:
            if current_row is not None:
                print()  # newline between rows
            # row label
            print(f"{row:>2} ", end="")
            current_row = row

        st = seats.get(s, {"Status": "Unavailable"})["Status"]
        symbol = "O" if st == "Available" else ("X" if st == "Taken" else "-")
        # print seat letter + symbol
        print(f"{seat_letter}{symbol} ", end="")

        # Add aisle spacing where applicable:
        if service_key == "B" and seat_letter == "B":   # bus: after B (2+2)
            print("  ", end="")
        if service_key == "A" and seat_letter == "C":   # airplane: after C (3+3)
            print("  ", end="")
        # cinema has no special aisle by default
    print()  # final newline

# --- Actions ---
def reserve_seat(service_key):
    seats = load_seats(service_key)
    print_seat_map(service_key, seats)

    raw = input("Enter seat ID to reserve (e.g. 1A or A1): ")
    seat_id = normalize_seat_id_input(raw)

    if seat_id not in seats:
        print("⚠️ Invalid seat ID.")
        return

    info = seats[seat_id]
    if info["Status"] == "Taken":
        print(f"⚠️ Seat {seat_id} is already taken by '{info['Name']}' (since {info['Timestamp']}).")
        return
    if info["Status"] == "Unavailable":
        print(f"⚠️ Seat {seat_id} is unavailable.")
        return

    name = input("Enter passenger/name for the booking: ").strip()
    if not name:
        print("⚠️ Name is required to reserve.")
        return
    notes = input("Notes (optional): ").strip()

    seats[seat_id] = {
        "Status": "Taken",
        "Name": name,
        "Timestamp": now_str(),
        "Notes": notes
    }
    save_seats(service_key, seats)
    print(f"✅ Reserved seat {seat_id} for {name}.")

def cancel_reservation(service_key):
    seats = load_seats(service_key)
    print_seat_map(service_key, seats)
    raw = input("Enter seat ID to cancel (e.g. 1A or A1): ")
    seat_id = normalize_seat_id_input(raw)

    if seat_id not in seats:
        print("⚠️ Invalid seat ID.")
        return
    info = seats[seat_id]
    if info["Status"] != "Taken":
        print(f"⚠️ Seat {seat_id} is not currently taken (status: {info['Status']}).")
        return
    print(f"Current booking: {seat_id} -> {info['Name']} (since {info['Timestamp']}).")
    confirm = input("Type 'YES' to confirm cancellation: ").strip().upper()
    if confirm != "YES":
        print("Cancellation aborted.")
        return
    seats[seat_id] = {
        "Status": "Available",
        "Name": "",
        "Timestamp": now_str(),
        "Notes": f"Cancelled booking for {info['Name']} at {now_str()}"
    }
    save_seats(service_key, seats)
    print(f"✅ Reservation for seat {seat_id} cancelled.")

def view_report(service_key):
    path = DATA_FILES[service_key]
    ensure_csv(service_key)
    print(f"\nCSV Report ({path}):")
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        taken = sum(1 for r in rows if r["Status"] == "Taken")
        avail = sum(1 for r in rows if r["Status"] == "Available")
        unavailable = sum(1 for r in rows if r["Status"] == "Unavailable")
        print(f"Total seats: {len(rows)} | Taken: {taken} | Available: {avail} | Unavailable: {unavailable}")
        print("-" * 60)
        for r in rows:
            seat = r["Seat"]
            st = r["Status"]
            name = r["Name"] or "-"
            ts = r["Timestamp"] or "-"
            notes = r.get("Notes", "")
            print(f"{seat:6} | {st:9} | {name:20} | {ts:19} | {notes}")
    print("-" * 60)
    print(f"CSV file path: {os.path.abspath(path)}")

def set_unavailable(service_key):
    seats = load_seats(service_key)
    print_seat_map(service_key, seats)
    raw = input("Enter seat ID to mark Unavailable (or type CLEAR to clear notes on a seat): ").strip()
    if raw.upper() == "CLEAR":
        sid_raw = input("Enter seat ID to clear notes/status reset: ").strip()
        sid = normalize_seat_id_input(sid_raw)
        if sid not in seats:
            print("Invalid seat ID.")
            return
        seats[sid] = {"Status": "Available", "Name": "", "Timestamp": now_str(), "Notes": ""}
        save_seats(service_key, seats)
        print(f"✅ Reset {sid} to Available.")
        return

    seat_id = normalize_seat_id_input(raw)
    if seat_id not in seats:
        print("Invalid seat ID.")
        return
    seats[seat_id]["Status"] = "Unavailable"
    seats[seat_id]["Name"] = ""
    seats[seat_id]["Timestamp"] = now_str()
    seats[seat_id]["Notes"] = seats[seat_id].get("Notes","") + f" Marked unavailable at {now_str()}."
    save_seats(service_key, seats)
    print(f"✅ Seat {seat_id} marked Unavailable.")

# --- Menus ---
def service_menu(service_key, service_name):
    while True:
        print(f"\n== {service_name} Menu ==")
        print("1) View seat layout")
        print("2) Reserve seat")
        print("3) Cancel reservation")
        print("4) View CSV report")
        print("5) Admin: mark seat Unavailable / Reset seat")
        print("B) Back to main menu")
        choice = input("Choose option: ").strip().upper()
        if choice == "1":
            seats = load_seats(service_key)
            print_seat_map(service_key, seats)
        elif choice == "2":
            reserve_seat(service_key)
        elif choice == "3":
            cancel_reservation(service_key)
        elif choice == "4":
            view_report(service_key)
        elif choice == "5":
            set_unavailable(service_key)
        elif choice == "B":
            break
        else:
            print("⚠️ Invalid option. Try again.")

def main_menu():
    # Ensure CSVs exist
    for key in DATA_FILES:
        ensure_csv(key)

    while True:
        print("\n=== Mini Ticketing / Booking System ===")
        print("Choose service type:")
        print("C) Cinema")
        print("B) Bus")
        print("A) Airplane")
        print("X) Exit")
        choice = input("Service: ").strip().upper()
        if choice == "C":
            service_menu("C", "Cinema")
        elif choice == "B":
            service_menu("B", "Bus")
        elif choice == "A":
            service_menu("A", "Airplane")
        elif choice == "X":
            print("Goodbye.")
            break
        else:
            print("⚠️ Invalid choice. Please choose C, B, A or X.")

if __name__ == "__main__":
    main_menu()
