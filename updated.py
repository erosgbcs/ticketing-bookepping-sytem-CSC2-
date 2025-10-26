import csv
from datetime import datetime

FILE_PATH = "bookkeeping.csv"


# ---------- Utility Functions ----------
def load_transactions():
    """Load transactions from CSV file."""
    transactions = []
    try:
        with open(FILE_PATH, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['Amount'] = float(row['Amount'])
                transactions.append(row)
        print(f"Loaded {len(transactions)} transactions.")
    except FileNotFoundError:
        print("No existing file found. Starting fresh.")
    return transactions


def save_transactions(transactions):
    """Save transactions back to CSV."""
    with open(FILE_PATH, 'w', newline='') as csvfile:
        fieldnames = ['Date', 'Description', 'Type', 'Category', 'Amount', 'Purchase Type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transactions)
    print(f"Data saved to {FILE_PATH}.")


def show_transactions(transactions):
    """Display all transactions."""
    if not transactions:
        print("No transactions found.")
        return
    print(f"\n{'Date':<12} {'Description':<20} {'Type':<10} {'Category':<15} {'Amount':>10} {'Purchase Type':<15}")
    print('-' * 85)
    for t in transactions:
        print(f"{t['Date']:<12} {t['Description']:<20} {t['Type']:<10} {t['Category']:<15} {t['Amount']:>10.2f} {t['Purchase Type']:<15}")


def calculate_balance(transactions):
    """Compute current total balance."""
    balance = sum(
        t['Amount'] if t['Type'].lower() == 'income' else -t['Amount']
        for t in transactions
    )
    print(f"Current Balance: ${balance:.2f}")


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
        print(f"{key:<20} ₱{total:,.2f}")


def add_transaction(transactions):
    """Add new income or expense."""
    date_str = input("Enter date (YYYY-MM-DD) or leave blank for today: ") or datetime.today().strftime('%Y-%m-%d')
    description = input("Enter description: ")

    trans_type = input("Enter type (Income/Expense): ").capitalize()
    while trans_type not in ['Income', 'Expense']:
        trans_type = input("Invalid. Enter type (Income/Expense): ").capitalize()

    category = input("Enter category (e.g. Salary, Rent, Water, Electricity): ") or "General"
    purchase_type = input("Enter type of purchased (e.g. Food, Supplies, Payroll, etc.): ") or "N/A"

    try:
        amount = float(input("Enter amount: "))
    except ValueError:
        print("Invalid amount.")
        return

    transactions.append({
        'Date': date_str,
        'Description': description,
        'Type': trans_type,
        'Category': category,
        'Amount': amount,
        'Purchase Type': purchase_type
    })
    print("Transaction added successfully.")


def update_transaction(transactions):
    """Update existing transaction."""
    show_transactions(transactions)
    try:
        index = int(input("\nEnter transaction number to update (starting from 1): ")) - 1
        if 0 <= index < len(transactions):
            t = transactions[index]
            print(f"Editing transaction: {t}")

            t['Description'] = input(f"New description ({t['Description']}): ") or t['Description']
            t['Type'] = input(f"New type ({t['Type']}): ") or t['Type']
            t['Category'] = input(f"New category ({t['Category']}): ") or t['Category']
            t['Purchase Type'] = input(f"New purchase type ({t['Purchase Type']}): ") or t['Purchase Type']
            try:
                new_amount = input(f"New amount ({t['Amount']}): ")
                if new_amount:
                    t['Amount'] = float(new_amount)
            except ValueError:
                print("Invalid amount, keeping old value.")
            print("Transaction updated successfully.")
        else:
            print("Invalid index.")
    except ValueError:
        print("Invalid input.")


def add_payroll(transactions):
    """Add payroll as income or expense."""
    print("\n--- Payroll Entry ---")
    employee = input("Employee name: ")
    salary = float(input("Salary amount: "))
    date_str = datetime.today().strftime('%Y-%m-%d')
    transactions.append({
        'Date': date_str,
        'Description': f"Payroll - {employee}",
        'Type': 'Expense',
        'Category': 'Payroll',
        'Amount': salary,
        'Purchase Type': 'Salary'
    })
    print(f"Payroll added for {employee}.")


# ---------- Main Program ----------
def main():
    transactions = load_transactions()

    while True:
        print("\n---------- BSCS 1A BOOKKEEPING SYSTEM -----------")
        print("1. Add Transaction")
        print("2. View Transactions")
        print("3. Update Transaction")
        print("4. Show Balance")
        print("5. View Monthly Expenses")
        print("6. Add Payroll")
        print("7. Save")
        print("8. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            add_transaction(transactions)
        elif choice == '2':
            show_transactions(transactions)
        elif choice == '3':
            update_transaction(transactions)
        elif choice == '4':
            calculate_balance(transactions)
        elif choice == '5':
            calculate_monthly_expenses(transactions)
        elif choice == '6':
            add_payroll(transactions)
        elif choice == '7':
            save_transactions(transactions)
        elif choice == '8':
            print("Goodbye! Remember to save your data before exiting.")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()