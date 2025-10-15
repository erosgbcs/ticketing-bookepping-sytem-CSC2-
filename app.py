import csv
from datetime import datetime

import csv

file=open("bookkeeping.csv","r")
content=file.read()
file.close()

print(content)
22
file_path = 'bookkeeping.csv'

import csv
from datetime import datetime

file_path = 'bookkeeping.csv'
transactions = []

# --- Load CSV file data ---
try:
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['Amount'] = float(row['Amount'])  # Convert amount string to float
            transactions.append(row)
    print(f"Loaded {len(transactions)} transactions from {file_path}")
except FileNotFoundError:
    print(f"No existing file found at {file_path}. Starting with empty records.")

while True:
    print("\n--- Bookkeeping System ---")
    print("1. Add transaction")
    print("2. View transactions")
    print("3. Show balance")
    print("4. Save and Exit")

    choice = input("Choose an option: ")

    if choice == '1':
        date_str = input("Enter date (YYYY-MM-DD) or leave blank for today: ")
        if not date_str:
            date_str = datetime.today().strftime('%Y-%m-%d')

        description = input("Enter description: ")

        trans_type = ''
        while trans_type.lower() not in ['income', 'expense']:
            trans_type = input("Enter type (Income/Expense): ")

        amount = None
        while amount is None:
            try:
                amount = float(input("Enter amount: "))
            except ValueError:
                print("Invalid amount, try again.")

        transactions.append({
            'Date': date_str,
            'Description': description,
            'Type': trans_type.capitalize(),
            'Amount': amount
        })

        print("Transaction added.")

    elif choice == '2':
        if not transactions:
            print("No transactions found.")
        else:
            print(f"{'Date':<12} {'Description':<20} {'Type':<10} {'Amount':>10}")
            print('-' * 56)
            for t in transactions:
                print(f"{t['Date']:<12} {t['Description']:<20} {t['Type']:<10} {t['Amount']:>10.2f}")

    elif choice == '3':
        balance = 0
        for t in transactions:
            if t['Type'].lower() == 'income':
                balance += t['Amount']
            else:
                balance -= t['Amount']
        print(f"Current Balance: ${balance:.2f}")

    elif choice == '4':
        # --- Save data back to CSV file ---
        with open(file_path, 'w', newline='') as csvfile:
            fieldnames = ['Date', 'Description', 'Type', 'Amount']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for t in transactions:
                writer.writerow(t)

        print(f"Data saved to {file_path}. Goodbye!")
        break

    else:
        print("Invalid choice, please try again.")
