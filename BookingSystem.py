#!/usr/bin/env python3
"""
Mini Ticketing/Booking System
 - Cinema  -> cinema.csv
 - Bus     -> bus.csv
 - Airplane-> airplane.csv
"""

# --- Import Required Libraries ---
import csv
import os
from datetime import datetime

# --- File Definitions ---
DATA_FILES = {
    "C": "cinema.csv",
    "B": "bus.csv",
    "A": "airplane.csv",
}
FIELDNAMES = ["Seat", "Status", "Name", "Timestamp"]

# --- Helper Function ---
def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# =========================
#  SEAT LAYOUT DEFINITIONS
# =========================
def cinema_layout():
    rows = range(1, 11)
    seat_letters = ["A", "B", "C", "D", "E", "F"]
    return [f"{r}{s}" for r in rows for s in seat_letters]

def bus_layout():
    rows = range(1, 13)
    seat_letters = ["A", "B", "C", "D"]
    return [f"{r}{s}" for r in rows for s in seat_letters]

def airplane_layout():
    rows = range(1, 17)
    seat_letters = ["A", "B", "C", "D", "E", "F"]
    return [f"{r}{s}" for r in rows for s in seat_letters]

LAYOUT_FUNCTIONS = {"C": cinema_layout, "B": bus_layout, "A": airplane_layout}

# =========================
#     CSV FILE HANDLING
# =========================
def ensure_csv(service_key):
    path = DATA_FILES[service_key]
    if not os.path.exists(path):
        seats = LAYOUT_FUNCTIONS[service_key]()
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for s in seats:
                writer.writerow({"Seat": s, "Status": "Available", "Name": "", "Timestamp": ""})

def load_seats(service_key):
    ensure_csv(service_key)
    path = DATA_FILES[service_key]
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return {
            row["Seat"]: {
                "Status": row["Status"],
                "Name": row["Name"],
                "Timestamp": row["Timestamp"]
            } for row in reader
        }

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
def print_seat_map(service_key, seats):
    layout = LAYOUT_FUNCTIONS[service_key]()
    print("\n--- SEAT LAYOUT (🟩=Available, 🟥=Taken, ⬛=Unavailable) ---")
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
        symbol = "🟩" if st == "Available" else ("🟥" if st == "Taken" else "⬛")
        print(f"{seat_letter}{symbol} ", end="")
        if service_key == "B" and seat_letter == "B":
            print("  ", end="")
        if service_key == "A" and seat_letter == "C":
            print("  ", end="")
    print()

# =========================
#     CORE FUNCTIONS
# =========================
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

    # --- Passenger name validation ---
    while True:
        name = input("Enter passenger name: ").strip()
        if not name:
            print("⚠️ Name required.")
            continue
        if not all(c.isalpha() or c == " " for c in name):
            print("⚠️ Name can only contain letters and single spaces. Try again.")
            continue
        if "  " in name:
            print("⚠️ Please avoid multiple spaces in the name.")
            continue
        name = " ".join(name.split())  # Trim extra spaces
        break

    timestamp = now_str()
    seats[seat_id] = {"Status": "Taken", "Name": name, "Timestamp": timestamp}
    save_seats(service_key, seats)
    print(f"✅ Reserved seat {seat_id} for {name}.")

    generate_ticket_csv(service_key, seat_id, name, timestamp)
    print(f"🎫 Ticket generated for {name} (seat {seat_id}). Check 'tickets/' folder.")

def show_ticket(service_key):
    seats = load_seats(service_key)
    print("\n🎫 === View Ticket ===")
    search = input("Enter passenger name or seat ID (e.g. John or 1A): ").strip()
    if not search:
        print("⚠️ Input required.")
        return

    search_norm = normalize_seat_id_input(search)
    found = False

    for seat_id, info in seats.items():
        if info["Status"] == "Taken" and (
            info["Name"].lower() == search.lower() or seat_id == search_norm
        ):
            found = True
            service_name = {"C": "Cinema", "B": "Bus", "A": "Airplane"}.get(service_key, "Unknown")
            print("\n==============================")
            print(f"🎟  TICKET DETAILS ({service_name})")
            print("==============================")
            print(f"Seat       : {seat_id}")
            print(f"Passenger  : {info['Name']}")
            print(f"Service    : {service_name}")
            print(f"Booked At  : {info['Timestamp']}")
            print("==============================")
            ticket_dir = "tickets"
            safe_name = "".join(c for c in info['Name'] if c.isalnum() or c in (' ', '_')).strip().replace(" ", "_")
            filename = f"ticket_{service_name.lower()}_{seat_id}_{safe_name}.csv"
            filepath = os.path.join(ticket_dir, filename)
            if os.path.exists(filepath):
                print(f"📄 Ticket file found: {filepath}")
            else:
                print("⚠️ Ticket CSV file not found (may have been deleted).")
            break

    if not found:
        print("❌ No ticket found for that passenger or seat.")

def generate_ticket_csv(service_key, seat_id, name, timestamp):
    service_name = {"C": "Cinema", "B": "Bus", "A": "Airplane"}.get(service_key, "Unknown")
    ticket_dir = "tickets"
    os.makedirs(ticket_dir, exist_ok=True)
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_')).strip().replace(" ", "_")
    filename = f"ticket_{service_name.lower()}_{seat_id}_{safe_name}.csv"
    filepath = os.path.join(ticket_dir, filename)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Service", "Seat", "Passenger", "Timestamp"])
        writer.writerow([service_name, seat_id, name, timestamp])

def cancel_reservation(service_key):
    seats = load_seats(service_key)
    print_seat_map(service_key, seats)
    raw = input("Enter seat ID to cancel (or 'B' to go back): ").strip()
    if raw.upper() == "B":
        return
    seat_id = normalize_seat_id_input(raw)
    if seat_id not in seats or seats[seat_id]["Status"] != "Taken":
        print("⚠️ Invalid or not reserved.")
        return
    info = seats[seat_id]
    print(f"Cancel booking for {info['Name']} on {seat_id}?")
    if input("Type Y to confirm: ").strip().upper() != "Y":
        print("Reservation preserved.")
        return
    service_name = {"C": "Cinema", "B": "Bus", "A": "Airplane"}.get(service_key, "Unknown")
    safe_name = "".join(c for c in info['Name'] if c.isalnum() or c in (' ', '_')).strip().replace(" ", "_")
    old_ticket = os.path.join("tickets", f"ticket_{service_name.lower()}_{seat_id}_{safe_name}.csv")
    if os.path.exists(old_ticket):
        os.remove(old_ticket)
    seats[seat_id] = {"Status": "Available", "Name": "", "Timestamp": now_str()}
    save_seats(service_key, seats)
    print(f"✅ Cancelled booking on {seat_id} and removed ticket file.")

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
    print(f"\nSeat {seat_id} currently booked by {info['Name']}.")
    print("1) Change passenger name")
    print("2) Move to another seat")
    print("B) Back")
    choice = input("Select option: ").strip().upper()
    service_name = {"C": "Cinema", "B": "Bus", "A": "Airplane"}.get(service_key, "Unknown")
    ticket_dir = "tickets"
    os.makedirs(ticket_dir, exist_ok=True)
    if choice == "1":
        # Name validation for updates
        while True:
            new_name = input("Enter new passenger name: ").strip()
            if not new_name:
                print("⚠️ Name required.")
                continue
            if not all(c.isalpha() or c == " " for c in new_name):
                print("⚠️ Name can only contain letters and single spaces. Try again.")
                continue
            if "  " in new_name:
                print("⚠️ Please avoid multiple spaces in the name.")
                continue
            new_name = " ".join(new_name.split())
            break
        old_safe_name = "".join(c for c in info['Name'] if c.isalnum() or c in (' ', '_')).strip().replace(" ", "_")
        old_ticket = os.path.join(ticket_dir, f"ticket_{service_name.lower()}_{seat_id}_{old_safe_name}.csv")
        if os.path.exists(old_ticket):
            os.remove(old_ticket)
        seats[seat_id]["Name"] = new_name
        seats[seat_id]["Timestamp"] = now_str()
        save_seats(service_key, seats)
        print(f"✅ Updated passenger name for seat {seat_id} to {new_name}.")
        generate_ticket_csv(service_key, seat_id, new_name, seats[seat_id]["Timestamp"])
        print(f"🎫 Ticket regenerated for {new_name} (seat {seat_id}).")
    elif choice == "2":
        target_raw = input("Enter target seat ID: ").strip()
        target = normalize_seat_id_input(target_raw)
        if target not in seats or seats[target]["Status"] != "Available":
            print("⚠️ Target seat invalid or not available.")
            return
        confirm = input(f"Move {info['Name']} from {seat_id} to {target}? (Y/N): ").strip().upper()
        if confirm != "Y":
            print("Action cancelled.")
            return
        safe_name = "".join(c for c in info['Name'] if c.isalnum() or c in (' ', '_')).strip().replace(" ", "_")
        old_ticket = os.path.join(ticket_dir, f"ticket_{service_name.lower()}_{seat_id}_{safe_name}.csv")
        if os.path.exists(old_ticket):
            os.remove(old_ticket)
        seats[target] = {"Status": "Taken", "Name": info["Name"], "Timestamp": now_str()}
        seats[seat_id] = {"Status": "Available", "Name": "", "Timestamp": now_str()}
        save_seats(service_key, seats)
        print(f"✅ Moved {info['Name']} from {seat_id} to {target}.")
        generate_ticket_csv(service_key, target, info["Name"], seats[target]["Timestamp"])
        print(f"🎫 New ticket generated for {info['Name']} (seat {target}).")
    elif choice == "B":
        print("Returning...")
    else:
        print("⚠️ Invalid option.")

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
            print(f"{r['Seat']:<5} | {r['Status']:<9} | {r['Name'] or '-':<20} | {r['Timestamp']}")
        print("-" * 50)

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
def service_menu(service_key, service_name):
    while True:
        print(f"\n== {service_name} Menu ==")
        print("1) View seat layout")
        print("2) Reserve seat")
        print("3) Cancel reservation")
        print("4) Update seat booking")
        print("5) View booking report")
        print("6) Admin: mark seat Unavailable / Reset seat")
        print("7) View passenger ticket")
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
        elif choice == "7":
            show_ticket(service_key)
        elif choice == "B":
            break
        else:
            print("⚠️ Invalid option.")

def main_menu():
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

if __name__ == "__main__":
    main_menu()
