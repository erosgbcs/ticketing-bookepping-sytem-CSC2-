from flask import Flask, render_template, request, redirect
import csv
import os

app = Flask(__name__)
DATA_FILE = 'data/tickets.csv'

# Ensure CSV file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Issue", "Status"])

def read_tickets():
    with open(DATA_FILE, newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)

def add_ticket(name, issue, status="Open"):
    tickets = read_tickets()
    ticket_id = len(tickets) + 1
    with open(DATA_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([ticket_id, name, issue, status])

@app.route('/')
def index():
    tickets = read_tickets()
    return render_template('index.html', tickets=tickets)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        issue = request.form['issue']
        add_ticket(name, issue)
        return redirect('/')
    return render_template('add_ticket.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)