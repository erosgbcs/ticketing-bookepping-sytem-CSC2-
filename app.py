import csv
from datetime import datetime

FILENAME = 'bookkeeping.csv'

def load_transactions():
    transactions = []
    try:
        with open(FILENAME, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['Amount'] = float(row['Amount'])
                transactions.append(row)
    except FileNotFoundError:
        # No existing file, return empty list
        pass
    return transactions

def save_transactions(transactions):
    with open(FILENAME, 'w', newline='') as csvfile:
        fieldnames = ['Date', 'Description', 'Type', 'Amount']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for trans in transactions:
            writer.writerow(trans)

def add_transaction(transactions):
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

def view_transactions(transactions):
    if not transactions:
        print("No transactions found.")
        return

    print(f"{'Date':<12} {'Description':<20} {'Type':<10} {'Amount':>10}")
    print('-' * 56)
    for t in transactions:
        print(f"{t['Date']:<12} {t['Description']:<20} {t['Type']:<10} {t['Amount']:>10.2f}")

def calculate_balance(transactions):
    balance = 0
    for t in transactions:
        if t['Type'].lower() == 'income':
            balance += t['Amount']
        else:
            balance -= t['Amount']
    return balance

def main():
    transactions = load_transactions()

    while True:
        print("\n--- Bookkeeping System ---")
        print("1. Add transaction")
        print("2. View transactions")
        print("3. Show balance")
        print("4. Save and Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            add_transaction(transactions)
        elif choice == '2':
            view_transactions(transactions)
        elif choice == '3':
            balance = calculate_balance(transactions)
            print(f"Current Balance: ${balance:.2f}")
        elif choice == '4':
            save_transactions(transactions)
            print("Data saved. Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == '__main__':
    main()
