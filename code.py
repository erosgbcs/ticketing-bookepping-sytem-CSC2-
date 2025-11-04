import csv

rows, cols = 5, 5
seats = [["O" for _ in range(cols)] for _ in range(rows)]  # O = Open, X = Taken

def display_seats():
    print("\nSeat Layout (O = Available, X = Booked)")
    print("   " + " ".join([str(c+1) for c in range(cols)]))
    for r in range(rows):
        print(f"R{r+1}  " + " ".join(seats[r]))
    print()

def reserve_seat():
    try:
        display_seats()
        r = int(input("Enter Row (1-10): ")) - 1
        c = int(input("Enter Seat (1-10): ")) - 1
        name = input("Enter Passenger Name: ").strip()

        if seats[r][c] == "X":
            print("❌ Seat already booked. Please choose another one.")
        else:
            seats[r][c] = "X"
            print(f"✅ Seat R{r+1}C{c+1} successfully reserved for {name}.")

            # Save to CSV file
            with open("bookings.csv", mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([name, f"R{r+1}", f"C{c+1}"])
    except (IndexError, ValueError):
        print("⚠ Invalid input. Please try again.")

def cancel_reservation():
    try:
        display_seats()
        r = int(input("Enter Row (1-5) to cancel: ")) - 1
        c = int(input("Enter Seat (1-5) to cancel: ")) - 1

        if seats[r][c] == "O":
            print("⚠ That seat is not currently booked.")
        else:
            seats[r][c] = "O"
            print(f"✅ Seat R{r+1}C{c+1} booking cancelled.")
    except (IndexError, ValueError):
        print("⚠ Invalid input. Please try again.")

def generate_report():
    try:
        with open("bookings.csv", newline="") as file:
            reader = csv.reader(file)
            print("\n📄 Booking Report:")
            print("{:<20} {:<10} {:<10}".format("Name", "Row", "Column"))
            print("-" * 40)
            for row in reader:
                print("{:<20} {:<10} {:<10}".format(row[0], row[1], row[2]))
    except FileNotFoundError:
        print("⚠ No bookings found yet.")

def main():
    # Create header for CSV if not exist
    with open("bookings.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Row", "Column"])

    while True:
        print("\n🎟 MINI TICKETING / BOOKING SYSTEM")
        print("1. View Seats")
        print("2. Reserve Seat")
        print("3. Cancel Reservation")
        print("4. Generate Booking Report")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            display_seats()
        elif choice == "2":
            reserve_seat()
        elif choice == "3":
            cancel_reservation()
        elif choice == "4":
            generate_report()
        elif choice == "5":
            print("👋 Thank you for using the system!")
            break
        else:
            print("⚠ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
