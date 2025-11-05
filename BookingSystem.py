#!/usr/bin/env python3
"""
Mini Ticketing/Booking System (Simplified - No Notes)
 - Cinema  -> cinema.csv
 - Bus     -> bus.csv
 - Airplane-> airplane.csv
"""
# --- Import Required Libraries ---
import csv # For reading and writing CSV files (to store seat data)
import os # For checking if files exist
from datetime import datetime   # For adding timestamps to bookings

# --- File Definitions ---
# Mapping service types to CSV files
DATA_FILES = {
    "C": "cinema.csv",
    "B": "bus.csv",
    "A": "airplane.csv",
}
# CSV header structure
FIELDNAMES = ["Seat", "Status", "Name", "Timestamp"]
# --- Helper Function: Get current date/time as string ---
def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# =========================
#  SEAT LAYOUT DEFINITIONS
# =========================
# Each transport type has its own seat pattern (rows × columns)

def cinema_layout():
    rows = range(1, 11)
    seat_letters = ["A", "B", "C", "D", "E", "F"]
    return [f"{r}{s}" for r in rows for s in seat_letters]
 # Cinema: 10 rows × 6 seats per row (A-F)
def bus_layout():
    rows = range(1, 13)
    seat_letters = ["A", "B", "C", "D"]
    return [f"{r}{s}" for r in rows for s in seat_letters]
# Bus: 12 rows × 4 seats per row (A-D)
def airplane_layout():
    rows = range(1, 21)
    seat_letters = ["A", "B", "C", "D", "E", "F"]
    return [f"{r}{s}" for r in rows for s in seat_letters]
# Shortcut dictionary to choose which layout to use
LAYOUT_FUNCTIONS = {"C": cinema_layout, "B": bus_layout, "A": airplane_layout}

# =========================
#     CSV FILE HANDLING
# =========================

# --- Ensure CSV file exists for each service ---
def ensure_csv(service_key):
    path = DATA_FILES[service_key]
    if not os.path.exists(path):
        seats = LAYOUT_FUNCTIONS[service_key]()
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for s in seats:
                writer.writerow({"Seat": s, "Status": "Available", "Name": "", "Timestamp": ""})
# --- Load all seat info from CSV ---
def load_seats(service_key):
    ensure_csv(service_key)
    path = DATA_FILES[service_key]
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
          # Create a dictionary of seat data
        return {
            row["Seat"]: {
                "Status": row["Status"],
                "Name": row["Name"],
                "Timestamp": row["Timestamp"]
            } for row in reader
        }
# --- Save seat data back to CSV ---
def save_seats(service_key, seats):
    path = DATA_FILES[service_key]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        layout = LAYOUT_FUNCTIONS[service_key]()
        for s in layout:
            info = seats.get(s, {"Status": "Unavailable", "Name": "", "Timestamp": ""})
            writer.writerow({
                "Seat": s,
                "Status": info["Status"],
                "Name": info["Name"],
                "Timestamp": info["Timestamp"]
            })

# =========================
#     INPUT UTILITIES
# =========================

# --- Normalize seat input (e.g., "A1" -> "1A") ---
def normalize_seat_id_input(raw):
    if not raw:
        return raw
    s = raw.strip().upper()
    letters = ''.join(filter(str.isalpha, s))
    digits = ''.join(filter(str.isdigit, s))
    if digits and letters:
        return digits + letters
    return s

# =========================
#     DISPLAY FUNCTIONS
# =========================
# --- Print visual seat map ---
def print_seat_map(service_key, seats):
    layout = LAYOUT_FUNCTIONS[service_key]()
    print("\n--- SEAT LAYOUT (O=Available, X=Taken, -=Unavailable) ---")
    layout_sorted = sorted(layout, key=lambda x: (int(''.join(filter(str.isdigit, x))), x))
    current_row = None
    for s in layout_sorted:
        row = ''.join(filter(str.isdigit, s))
        seat_letter = s[len(row):]
        if row != current_row:
            if current_row is not None:
                print()
            print(f"{row:>2} ", end="")
            current_row = row
        st = seats.get(s, {"Status": "Unavailable"})["Status"]
        symbol = "O" if st == "Available" else ("X" if st == "Taken" else "-")
        print(f"{seat_letter}{symbol} ", end="")
         # Add spacing to represent aisle for bus/plane
        if service_key == "B" and seat_letter == "B":
            print("  ", end="")
        if service_key == "A" and seat_letter == "C":
            print("  ", end="")
    print()

# =========================
#     CORE FUNCTIONS
# =========================

# --- Reserve seat (booking) ---
def reserve_seat(service_key):
    seats = load_seats(service_key)
    print_seat_map(service_key, seats)
    raw = input("Enter seat ID to reserve (e.g. 1A or A1, or 'B' to go back): ").strip()
    if raw.upper() == "B":
        return
    seat_id = normalize_seat_id_input(raw)
    if seat_id not in seats:
        print("⚠️ Invalid seat ID.")
        return
    info = seats[seat_id]
    if info["Status"] == "Taken":
        print(f"⚠️ Seat {seat_id} is already taken by '{info['Name']}'.")
        return
    if info["Status"] == "Unavailable":
        print(f"⚠️ Seat {seat_id} is unavailable.")
        return
    # Reserve seat
    name = input("Enter passenger name: ").strip()
    if not name:
        print("⚠️ Name required.")
        return
    seats[seat_id] = {"Status": "Taken", "Name": name, "Timestamp": now_str()}
    save_seats(service_key, seats)
    print(f"✅ Reserved seat {seat_id} for {name}.")

# --- Cancel reservation ---
def cancel_reservation(service_key):
    seats = load_seats(service_key)
    print_seat_map(service_key, seats)
    raw = input("Enter seat ID to cancel (or 'B' to go back): ").strip()
    if raw.upper() == "B":
        return
    seat_id = normalize_seat_id_input(raw)
        # Validate seat
    if seat_id not in seats or seats[seat_id]["Status"] != "Taken":
        print("⚠️ Invalid or not reserved.")
        return
    info = seats[seat_id]
    print(f"Cancel booking for {info['Name']} on {seat_id}?")
    if input("Type Y to confirm: ").strip().upper() != "Y":
        print("Reservation preserved.")
        return
    seats[seat_id] = {"Status": "Available", "Name": "", "Timestamp": now_str()}
    save_seats(service_key, seats)
    print(f"✅ Cancelled booking on {seat_id}.")

# --- Update reservation (change name or move seat) ---
def update_reservation(service_key):
    seats = load_seats(service_key)
    print_seat_map(service_key, seats)
    raw = input("Enter seat ID to update (or 'B' to go back): ").strip()
    if raw.upper() == "B":
        return
    seat_id = normalize_seat_id_input(raw)
    if seat_id not in seats or seats[seat_id]["Status"] != "Taken":
        print("⚠️ Seat not taken or invalid.")
        return
    info = seats[seat_id]
    print(f"Seat {seat_id} currently booked by {info['Name']}.")
    print("1) Change passenger name\n2) Move to another seat\nB) Back")
    choice = input("Select option: ").strip().upper()
    if choice == "1":
         # Change passenger name
        new_name = input("Enter new passenger name: ").strip()
        if not new_name:
            print("⚠️ Name required.")
            return
        seats[seat_id]["Name"] = new_name
        seats[seat_id]["Timestamp"] = now_str()
        save_seats(service_key, seats)
        print(f"✅ Updated passenger name for seat {seat_id}.")
    elif choice == "2":
           # Move passenger to another seat
        target_raw = input("Enter target seat ID: ").strip()
        target = normalize_seat_id_input(target_raw)
        if target not in seats or seats[target]["Status"] != "Available":
            print("⚠️ Target seat invalid or not available.")
            return
        seats[target] = {"Status": "Taken", "Name": info["Name"], "Timestamp": now_str()}
        seats[seat_id] = {"Status": "Available", "Name": "", "Timestamp": now_str()}
        save_seats(service_key, seats)
        print(f"✅ Moved {info['Name']} from {seat_id} to {target}.")
    else:
        print("Returning...")
# --- Generate booking report ---
def view_report(service_key):
    path = DATA_FILES[service_key]
    ensure_csv(service_key)
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        taken = sum(1 for r in rows if r["Status"] == "Taken")
        avail = sum(1 for r in rows if r["Status"] == "Available")
        print(f"\n{path}: Taken={taken}, Available={avail}, Total={len(rows)}")
        print("-" * 50)
        for r in rows:
            print(f"{r['Seat']:5} | {r['Status']:9} | {r['Name'] or '-':15} | {r['Timestamp']:19}")
        print("-" * 50)

# --- Mark seats unavailable (for maintenance/admin use) ---
def set_unavailable(service_key):
    seats = load_seats(service_key)
    print_seat_map(service_key, seats)
    raw = input("Seat ID to mark unavailable (or CLEAR to reset, B to back): ").strip().upper()
    if raw == "B":
        return
    if raw == "CLEAR":
        sid = normalize_seat_id_input(input("Seat to reset: "))
        if sid in seats:
            seats[sid] = {"Status": "Available", "Name": "", "Timestamp": now_str()}
            save_seats(service_key, seats)
            print(f"✅ Reset {sid} to Available.")
        return
    seat_id = normalize_seat_id_input(raw)
    if seat_id not in seats:
        print("⚠️ Invalid seat ID.")
        return
    seats[seat_id] = {"Status": "Unavailable", "Name": "", "Timestamp": now_str()}
    save_seats(service_key, seats)
    print(f"✅ Seat {seat_id} marked Unavailable.")

# =========================
#        MENUS
# =========================
# --- Menu per service (Cinema/Bus/Airplane) ---
def service_menu(service_key, service_name):
    while True:
        print(f"\n== {service_name} Menu ==")
        print("1) View seat layout")
        print("2) Reserve seat")
        print("3) Cancel reservation")
        print("4) Update seat booking")
        print("5) View bookking report")
        print("6) Admin: mark seat Unavailable / Reset seat")
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
            update_reservation(service_key)
        elif choice == "5":
            view_report(service_key)
        elif choice == "6":
            set_unavailable(service_key)
        elif choice == "B":
            break
        else:
            print("⚠️ Invalid option.")


# --- Main system menu (entry point) ---
def main_menu():
     # Make sure CSVs are initialized before use
    for k in DATA_FILES:
        ensure_csv(k)
    while True:
        print("\n=== Mini Ticketing / Booking System ===")
        print("1) 🎥  Cinema")
        print("2) 🚌  Bus")
        print("3) ✈️   Airplane")
        print("X) Exit")
        print("========================================")
        c = input("Service: ").strip().upper()
        if c == "1":
            service_menu("C", "Cinema")
        elif c == "2":
            service_menu("B", "Bus")
        elif c == "3":
            service_menu("A", "Airplane")
        elif c == "X":
            print("Goodbye!")
            break
        else:
            print("⚠️ Invalid input.")
# --- Run program ---
if __name__ == "__main__":
    main_menu()
