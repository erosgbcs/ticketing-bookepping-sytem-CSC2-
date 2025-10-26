import csv
from datetime import datetime
import os

FILE_PATH = "bookkeeping.csv"
FIELDNAMES = ['Date', 'Description', 'Type', 'Category', 'Amount']


# ---------- CSV FILE HANDLING ----------
def ensure_csv_file():
    """Ensure the bookkeeping.csv file exists with proper headers."""
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writeheader()
        print(f"📁 Created new file: {FILE_PATH}")
    else:
        # Check header validity
        with open(FILE_PATH, 'r', newline='') as csvfile:
            first_line = csvfile.readline().strip()
        if first_line != ','.join(FIELDNAMES):
            print
            ("⚠️ CSV file missing or incorrect headers. Rewriting headers...")
            data = []
            try:
                with open(FILE_PATH, newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        data.append(row)
            except Exception:
                pass
            with open(FILE_PATH, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
                writer.writeheader()
                writer.writerows(data)
            print(f"✅ Headers fixed for {FILE_PATH}.")


# ---------- Utility Functions ----------
def load_transactions():
    """Load transactions from CSV file."""
    ensure_csv_file()
    transactions = []
    try:
        with open(FILE_PATH, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    row['Amount'] = float(row.get('Amount', 0))
                except ValueError:
                    print(f"Skipping invalid row (bad amount): {row}")
                    continue
                for key in FIELDNAMES:
                    row.setdefault(key, 'N/A')
                transactions.append(row)
        print(f"✅ Loaded {len(transactions)} transactions.")
    except Exception as e:
        print(f"⚠️ Error loading transactions: {e}")
    return transactions


def save_transactions(transactions):
    """Save transactions back to CSV."""
    ensure_csv_file()
    with open(FILE_PATH, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(transactions)
    print(f"💾 Data saved to {FILE_PATH}.")


def show_transactions(transactions, filter_type=None):
    """Display transactions (optionally filtered by type)."""
    if not transactions:
        print("No transactions found.")
        return

    if filter_type:
        transactions = [t for t in transactions if t['Type'].lower() == filter_type.lower()]
        if not transactions:
            print(f"No {filter_type.lower()} records found.")
            return
        print(f"\n--- Showing {filter_type.capitalize()} Transactions ---")

    print(f"\n{'#':<3} {'Date':<12} {'Description':<20} {'Type':<10} "
          f"{'Category':<15} {'Amount':>10}")
    print('-' * 75)

    for i, t in enumerate(transactions, start=1):
        print(f"{i:<3} {t['Date']:<12} {t['Description']:<20} {t['Type']:<10} "
              f"{t['Category']:<15} {t['Amount']:>10.2f}")


def calculate_balance(transactions):
    """Compute current total balance."""
    balance = sum(
        t['Amount'] if t['Type'].lower() == 'income' else -t['Amount']
        for t in transactions
    )
    print(f"💰 Current Balance: ₱{balance:,.2f}")


def calculate_monthly_expenses(transactions):
    """Show total monthly expenses by category."""
    monthly = {}
    for t in transactions:
        if t['Type'].lower() == 'expense':
            category = t['Category']
            month = t['Date'][:7]  # YYYY-MM
            key = f"{month} - {category}"
            monthly[key] = monthly.get(key, 0) + t['Amount']

    if not monthly:
        print("No expense records found.")
        return

    print("\n--- Monthly Expense Summary ---")
    for key, total in monthly.items():
        print(f"{key:<25} ₱{total:,.2f}")


# ---------- ADD TRANSACTION (SEPARATED OPTIONS) ----------
def add_income(transactions):
    """Add a new income transaction."""
    print("\n--- Add Income ---")
    date_str = input("Enter date (YYYY-MM-DD) or leave blank for today: ") or datetime.today().strftime('%Y-%m-%d')
    description = input("Enter selled item name: ")
    
    try:
        amount = float(input("Enter income amount: "))
    except ValueError:
        print("Invalid amount.")
        return

    transactions.append({
        'Date': date_str,
        'Description': description,
        'Type': 'Income',
        'Amount': amount
    })
    print("✅ Income added successfully.")


def add_expense(transactions):
    """Add a new expense transaction."""
    print("\n--- Add Expense ---")
    date_str = input("Enter date (YYYY-MM-DD) or leave blank for today: ") or datetime.today().strftime('%Y-%m-%d')
    description = input("Enter expense description: ")
    category = input("Enter expense category (e.g. Rent, Utilities, Supplies): ") or "Expense"
    try:
        amount = float(input("Enter expense amount: "))
    except ValueError:
        print("Invalid amount.")
        return

    transactions.append({
        'Date': date_str,
        'Description': description,
        'Type': 'Expense',
        'Category': category,
        'Amount': amount
    })
    print("✅ Expense added successfully.")


def update_transaction(transactions):
    """Update existing transaction."""
    if not transactions:
        print("No transactions to update.")
        return

    show_transactions(transactions)
    try:
        index = int(input("\nEnter transaction number to update (starting from 1): ")) - 1
        if 0 <= index < len(transactions):
            t = transactions[index]
            print(f"Editing transaction: {t}")

            t['Description'] = input(f"New description ({t['Description']}): ") or t['Description']
            t['Type'] = input(f"New type ({t['Type']}): ") or t['Type']
            t['Category'] = input(f"New category ({t['Category']}): ") or t['Category']
            try:
                new_amount = input(f"New amount ({t['Amount']}): ")
                if new_amount:
                    t['Amount'] = float(new_amount)
            except ValueError:
                print("Invalid amount, keeping old value.")
            print("✅ Transaction updated successfully.")
        else:
            print("Invalid transaction number.")
    except ValueError:
        print("Invalid input.")


def add_payroll(transactions):
    """Add payroll as expense."""
    print("\n--- Payroll Entry ---")
    employee = input("Employee name: ")
    try:
        salary = float(input("Salary amount: "))
    except ValueError:
        print("Invalid salary input.")
        return
    date_str = datetime.today().strftime('%Y-%m-%d')
    transactions.append({
        'Date': date_str,
        'Description': f"Payroll - {employee}",
        'Type': 'Expense',
        'Category': 'Payroll',
        'Amount': salary
    })
    print(f"✅ Payroll added for {employee}.")


# ---------- MAIN PROGRAM ----------
def main():
    transactions = load_transactions()

    while True:
        print("\n---------- BSCS 1A BOOKKEEPING SYSTEM -----------")
        print("1. Add selled (income)")
        print("2. Add Expense")
        print("3. View All Transactions")
        print("4. View Only Income")
        print("5. View Only Expenses")
        print("6. Update Transaction")
        print("7. Show Balance")
        print("8. View Monthly Expenses")
        print("9. Add Payroll")
        print("10. Save")
        print("11. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            add_income(transactions)
        elif choice == '2':
            add_expense(transactions)
        elif choice == '3':
            show_transactions(transactions)
        elif choice == '4':
            show_transactions(transactions, filter_type='Income')
        elif choice == '5':
            show_transactions(transactions, filter_type='Expense')
        elif choice == '6':
            update_transaction(transactions)
        elif choice == '7':
            calculate_balance(transactions)
        elif choice == '8':
            calculate_monthly_expenses(transactions)
        elif choice == '9':
            add_payroll(transactions)
        elif choice == '10':
            save_transactions(transactions)
        elif choice == '11':
            save_now = input("Save before exiting? (y/n): ").lower()
            if save_now == 'y':
                save_transactions(transactions)
            print("👋 Goodbye! Data safely handled.")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
