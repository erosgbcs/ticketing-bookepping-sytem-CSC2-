import csv
import os

FILE_PATH = "bookings.csv"

# ============================================================
# 🗂️ CSV FILE HANDLING
# ============================================================
def ensure_csv_file():
    """Ensure the bookings.csv file exists with correct headers and default seats."""
    if not os.path.exists(FILE_PATH):
        print("⚙️ Creating new bookings.csv file...")
        seats = []
        for row in ["A", "B", "C", "D", "E"]:
            for num in range(1, 5):
                seats.append({
                    'Seat': f'{row}{num}',
                    'Status': 'Available',
                    'Name': ''
                })
        with open(FILE_PATH, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['Seat', 'Status', 'Name'])
            writer.writeheader()
            writer.writerows(seats)

def load_seats():
    """Load seat data, recreate file if empty or corrupted."""
    if not os.path.exists(FILE_PATH):
        ensure_csv_file()
    with open(FILE_PATH, 'r') as file:
        reader = csv.DictReader(file)
        seats = list(reader)
        # If CSV is empty or missing seat data, recreate it
        if not seats:
            ensure_csv_file()
            with open(FILE_PATH, 'r') as f:
                seats = list(csv.DictReader(f))
        return seats

def save_seats(seats):
    """Save updated seat info back to the CSV."""
    with open(FILE_PATH, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Seat', 'Status', 'Name'])
        writer.writeheader()
        writer.writerows(seats)

# ============================================================
# 🎟️ VIEW SEAT LAYOUT
# ============================================================
def view_seat_layout():
    seats = load_seats()
    print("\n--- SEAT LAYOUT ---")
    count = 0
    for seat in seats:
        # Determine symbol for seat status
        status = seat['Status'].strip().capitalize()
        if status == 'Available':
            icon = "O"
        elif status == 'Taken':
            icon = "X"
        elif status == 'Unavailable':
            icon = "-"
        else:
            icon = "?"
        print(f"{seat['Seat']}({icon})", end="\t")
        count += 1
        if count % 4 == 0:
            print()
    print("\nLegend: O = Available, X = Taken, - = Unavailable")
    input("\nPress Enter to continue...")

# ============================================================
# 🪑 RESERVE SEAT
# ============================================================
def reserve_seat():
    seats = load_seats()
    print("\n--- RESERVE SEAT ---")
    seat_no = input("Enter seat number to reserve: ").upper()
    found = False
    for seat in seats:
        if seat['Seat'] == seat_no:
            found = True
            if seat['Status'] == 'Available':
                name = input("Enter passenger name: ")
                seat['Status'] = 'Taken'
                seat['Name'] = name
                save_seats(seats)
                print(f"✅ Seat {seat_no} reserved for {name}.")
            else:
                print("❌ Seat already taken or unavailable.")
            break
    if not found:
        print("⚠️ Seat not found.")
    input("\nPress Enter to continue...")

# ============================================================
# ✏️ UPDATE SEAT INFO
# ============================================================
def update_seat():
    seats = load_seats()
    print("\n--- UPDATE SEAT ---")
    seat_no = input("Enter seat number to update: ").upper()
    for seat in seats:
        if seat['Seat'] == seat_no:
            if seat['Status'] == 'Taken':
                print(f"Current passenger: {seat['Name']}")
                new_name = input("Enter new name: ")
                seat['Name'] = new_name
                save_seats(seats)
                print(f"✅ Seat {seat_no} updated to {new_name}.")
            else:
                print("❌ Seat is not currently reserved.")
            break
    else:
        print("⚠️ Seat not found.")
    input("\nPress Enter to continue...")

# ============================================================
# ❌ CANCEL RESERVATION
# ============================================================
def cancel_seat():
    seats = load_seats()
    print("\n--- CANCEL RESERVATION ---")
    seat_no = input("Enter seat number to cancel: ").upper()
    for seat in seats:
        if seat['Seat'] == seat_no:
            if seat['Status'] == 'Taken':
                seat['Status'] = 'Available'
                seat['Name'] = ''
                save_seats(seats)
                print(f"✅ Seat {seat_no} is now available.")
            else:
                print("❌ Seat is not reserved.")
            break
    else:
        print("⚠️ Seat not found.")
    input("\nPress Enter to continue...")

# ============================================================
# 🗃️ ARCHIVE / STATUS UPDATE
# ============================================================
def archive_or_status_update():
    seats = load_seats()
    print("\n--- ARCHIVE / STATUS UPDATE ---")
    seat_no = input("Enter seat number: ").upper()
    for seat in seats:
        if seat['Seat'] == seat_no:
            print(f"Current status: {seat['Status']}")
            new_status = input("Enter new status (Available/Taken/Archived): ").capitalize()
            if new_status in ['Available', 'Taken', 'Archived']:
                seat['Status'] = new_status
                if new_status != 'Taken':
                    seat['Name'] = ''
                save_seats(seats)
                print(f"✅ Seat {seat_no} updated to {new_status}.")
            else:
                print("⚠️ Invalid status. Please type Available, Taken, or Archived.")
            break
    else:
        print("⚠️ Seat not found.")
    input("\nPress Enter to continue...")

# ============================================================
# 📋 GENERATE REPORT
# ============================================================
def generate_report():
    seats = load_seats()
    print("\n--- BOOKING REPORT ---")
    print(f"{'Seat':<5} {'Status':<10} {'Passenger':<15}")
    print("-" * 35)
    for seat in seats:
        print(f"{seat['Seat']:<5} {seat['Status']:<10} {seat['Name']:<15}")
    print("-" * 35)
    input("\nPress Enter to continue...")

# ============================================================
# 🏠 MAIN MENU
# ============================================================
def main():
    ensure_csv_file()
    while True:
        print("\n===== MINI TICKETING / BOOKING SYSTEM =====")
        print("1. View Seat Layout")
        print("2. Reserve Seat")
        print("3. Update Seat Info")
        print("4. Cancel Reservation")
        print("5. Archive / Status Update")
        print("6. Generate Booking Report")
        print("7. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            view_seat_layout()
        elif choice == '2':
            reserve_seat()
        elif choice == '3':
            update_seat()
        elif choice == '4':
            cancel_seat()
        elif choice == '5':
            archive_or_status_update()
        elif choice == '6':
            generate_report()
        elif choice == '7':
            print("👋 Exiting system. Thank you!")
            break
        else:
            print("⚠️ Invalid option. Try again.")

# ============================================================
# 🚀 RUN PROGRAM
# ============================================================
if __name__ == "__main__":
    main()
