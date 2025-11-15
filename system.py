#!/usr/bin/env python3

import os
import csv
import re
import hashlib
from datetime import datetime, timedelta

PRICING = {
    "C": { # Cinema
        "Regular": 150,
        "VIP": 300,
        "Senior": 0.20, # 20% discount
        "Student": 0.10, # 10% discount
        "PWD": 0.20, # 20% discount
        "Child": 0.50 # 50% discount
    },
    "B": { # Bus
        "Regular": 100,
        "VIP": 150,
        "Senior": 0.20,
        "Student": 0.10,
        "PWD": 0.20,
        "Child": 0.50
    },
    "A": { # Airplane
        "Regular": 1200,
        "VIP": 2000,
        "Senior": 0.20,
        "Student": 0.10,
        "PWD": 0.20,
        "Child": 0.50
    }
}

DATA_FILES = {
    "C": "cinema.csv",
    "B": "bus.csv", 
    "A": "airplane.csv",
}
FIELDNAMES = ["Seat", "Status", "Name", "Timestamp", "TicketType", "BasePrice", "FinalPrice", "Contact", "Address", "IDType", "IDNumber", "VerifiedAt"]

# ------------------------
# Color Class for Console Output
# ------------------------

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.CYAN}ℹ️ {message}{Colors.END}")

def print_header(message):
    print(f"{Colors.BOLD}{Colors.PURPLE}{message}{Colors.END}")

# ------------------------
# Helpers
# ------------------------

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

def normalize_seat_id_input(raw):
    if not raw:
        return raw
    s = raw.strip().upper()
    letters = ''.join(filter(str.isalpha, s))
    digits = ''.join(filter(str.isdigit, s))
    if digits and letters:
        return digits + letters
    return s

def ensure_csv(service_key):
    path = DATA_FILES[service_key]
    if not os.path.exists(path):
        seats = LAYOUT_FUNCTIONS[service_key]()
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for s in seats:
                writer.writerow({
                    "Seat": s,
                    "Status": "Available",
                    "Name": "",
                    "Timestamp": "",
                    "TicketType": "",
                    "BasePrice": "",
                    "FinalPrice": "",
                    "Contact": "",
                    "Address": "",
                    "IDType": "",
                    "IDNumber": "",
                    "VerifiedAt": ""
                })

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
                "Timestamp": row.get("Timestamp", ""),
                "TicketType": row.get("TicketType", ""),
                "BasePrice": row.get("BasePrice", ""),
                "FinalPrice": row.get("FinalPrice", ""),
                "Contact": row.get("Contact", ""),
                "Address": row.get("Address", ""),
                "IDType": row.get("IDType", ""),
                "IDNumber": row.get("IDNumber", ""),
                "VerifiedAt": row.get("VerifiedAt", "")
            }
    return seats

def save_seats(service_key, seats):
    path = DATA_FILES[service_key]
    layout = LAYOUT_FUNCTIONS[service_key]()
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for s in layout:
            info = seats.get(s, {
                "Status": "Unavailable", "Name": "", "Timestamp": "", 
                "TicketType": "", "BasePrice": "", "FinalPrice": "", 
                "Contact": "", "Address": "", "IDType": "", "IDNumber": "", 
                "VerifiedAt": ""
            })
            writer.writerow({
                "Seat": s,
                "Status": info.get("Status", "Unavailable"),
                "Name": info.get("Name", ""),
                "Timestamp": info.get("Timestamp", ""),
                "TicketType": info.get("TicketType", ""),
                "BasePrice": info.get("BasePrice", ""),
                "FinalPrice": info.get("FinalPrice", ""),
                "Contact": info.get("Contact", ""),
                "Address": info.get("Address", ""),
                "IDType": info.get("IDType", ""),
                "IDNumber": info.get("IDNumber", ""),
                "VerifiedAt": info.get("VerifiedAt", "")
            })

def pretty_price(p):
    try:
        return f"₱{float(p):,.2f}"
    except:
        return str(p)

def list_ticket_types(service_key):
    types = list(PRICING[service_key].keys())
    return types

def compute_price(service_key, ticket_type):
    mapping = PRICING[service_key]
    val = mapping.get(ticket_type)
    if val is None:
        base = mapping.get("Regular", 0)
        return base, base
    # If val is < 1 -> discount fraction
    if isinstance(val, float) and 0 < val < 1:
        # base should be Regular price
        base = mapping.get("Regular", 0)
        final = base * (1 - val)
        return float(base), float(final)
    else:
        # fixed price for this type
        base = mapping.get("Regular", 0)
        # If type has its own fixed price (e.g., VIP), treat base as Regular, final as val
        if isinstance(val, (int, float)) and val >= 1:
            final = float(val)
            return float(base), final
        # fallback
        return float(val), float(val)

def choose_ticket_type_interactive(service_key):
    types = list_ticket_types(service_key)
    print("\nSelect ticket type:")
    for i, t in enumerate(types, start=1):
        b, f = compute_price(service_key, t)
        # Show base and final so user understands
        print(f"{i}) {t} (Base: {pretty_price(b)} / Final: {pretty_price(f)})")
    print("B) Back to previous menu")
    
    while True:
        sel = input("Choice (number or name): ").strip()
        if not sel:
            print_warning("Selection required.")
            continue
        # Check for back command
        if sel.upper() == "B":
            return "BACK"
        # try by number
        if sel.isdigit():
            idx = int(sel) - 1
            if 0 <= idx < len(types):
                return types[idx]
            else:
                print_warning("Invalid number.")
                continue
        # try by name
        candidate = sel.title()
        if candidate in types:
            return candidate
        print_warning("Invalid choice. Try again.")

# ------------------------
# Identity Validation System
# ------------------------

def get_full_name_separate():
    """Get first name, middle initial, and surname separately"""
    print_header("\n📝 ADMIN: Legal Name Verification")
    print("Enter client's complete legal name as it appears on government ID:")
    
    # First Name
    while True:
        first_name = input("First Name (or 'B' to go back): ").strip()
        if first_name.upper() == "B":
            return "BACK"
        
        if not first_name:
            print_warning("First name is required")
            continue
        
        if len(first_name) < 2:
            print_warning("First name must be at least 2 characters")
            continue
        
        if not re.match(r'^[a-zA-Z\s\-]+$', first_name):
            print_warning("First name can only contain letters, spaces, and hyphens")
            continue
        
        first_name = first_name.title()
        break
    
    # Middle Initial
    while True:
        middle_initial = input("Middle Initial (or press Enter if none): ").strip()
        if middle_initial.upper() == "B":
            return "BACK"
        
        if middle_initial:
            if len(middle_initial) != 1 or not middle_initial.isalpha():
                print_warning("Middle initial must be a single letter")
                continue
            middle_initial = middle_initial.upper()
        else:
            middle_initial = ""
        break
    
    # Surname
    while True:
        surname = input("Surname (or 'B' to go back): ").strip()
        if surname.upper() == "B":
            return "BACK"
        
        if not surname:
            print_warning("Surname is required")
            continue
        
        if len(surname) < 2:
            print_warning("Surname must be at least 2 characters")
            continue
        
        if not re.match(r'^[a-zA-Z\s\-]+$', surname):
            print_warning("Surname can only contain letters, spaces, and hyphens")
            continue
        
        surname = surname.title()
        break
    
    # Combine into full name
    if middle_initial:
        full_name = f"{first_name} {middle_initial}. {surname}"
    else:
        full_name = f"{first_name} {surname}"
    
    # Confirm the full name
    print(f"\nFull Name: {full_name}")
    confirm = input(f"{Colors.YELLOW}Is this correct? (Y to confirm, N to re-enter, B to go back): {Colors.END}").strip().upper()
    
    if confirm == "B":
        return "BACK"
    elif confirm != "Y":
        return get_full_name_separate()
    
    return full_name

def validate_government_id():
    """Validate government-issued ID with proper format checking"""
    print_header("\n🆔 ADMIN: Government ID Verification (Required by Law)")
    print("Valid ID types for verification:")
    
    id_types = {
        "1": {"name": "Driver's License", "format": r'^[A-Z]{1}\d{2}-\d{2}-\d{2}-\d{6}$', "example": "L12-34-56-789012"},
        "2": {"name": "Passport", "format": r'^[A-Z]{1,2}\d{6,8}$', "example": "AB123456"},
        "3": {"name": "National ID (PhilSys)", "format": r'^\d{12}$', "example": "123456789012"},
        "4": {"name": "SSS ID", "format": r'^\d{10}$', "example": "1234567890"},
        "5": {"name": "GSIS ID", "format": r'^\d{10}$', "example": "1234567890"},
        "6": {"name": "UMID", "format": r'^\d{12}$', "example": "123456789012"},
        "7": {"name": "Postal ID", "format": r'^[A-Z]{2}\d{7}$', "example": "AB1234567"},
        "8": {"name": "PRC ID", "format": r'^\d{6,8}$', "example": "123456"},
        "9": {"name": "Voter's ID", "format": r'^\d{12}$', "example": "123456789012"}
    }
    
    # Display ID options
    for key, info in id_types.items():
        print(f"{key}) {info['name']} (e.g., {info['example']})")
    print("B) Back to previous menu")
    
    while True:
        id_choice = input("\nSelect ID type (1-9 or B): ").strip()
        if id_choice.upper() == "B":
            return "BACK", "BACK"
        
        if id_choice in id_types:
            selected_type = id_types[id_choice]
            break
        print_warning("Invalid selection. Please choose 1-9 or B.")
    
    # Get ID number with format validation
    while True:
        print(f"\nEnter client's {selected_type['name']} number")
        print(f"Format: {selected_type['example']}")
        id_number = input("ID number (or 'B' to go back): ").strip().upper()
        
        if id_number.upper() == "B":
            return "BACK", "BACK"
        
        if not id_number:
            print_warning("ID number is required.")
            continue
        
        # Validate format
        is_valid, message = validate_id_format(selected_type, id_number)
        if not is_valid:
            print_warning(message)
            continue
        
        # Additional validation based on ID type
        if selected_type['name'] == "Driver's License":
            if not validate_drivers_license(id_number):
                print_warning("Invalid Driver's License number")
                continue
        
        print_success(f"✓ {selected_type['name']} format validated")
        break
    
    return selected_type['name'], id_number

def validate_id_format(id_type, id_number):
    """Validate ID number format"""
    if not re.match(id_type['format'], id_number):
        return False, f"Invalid format. Example: {id_type['example']}"
    
    # Additional specific validations
    if id_type['name'] == "Driver's License":
        # Validate LTO format more strictly
        if not id_number[0].isalpha():
            return False, "First character must be a letter"
        if not id_number[1:3].isdigit():
            return False, "Characters 2-3 must be digits"
    
    elif id_type['name'] == "Passport":
        # Passport should start with letter
        if not id_number[0].isalpha():
            return False, "Passport must start with a letter"
    
    return True, "Valid format"

def validate_drivers_license(license_number):
    """Additional validation for Driver's License"""
    try:
        # LTO format: LNN-NN-NN-NNNNNN
        parts = license_number.split('-')
        if len(parts) != 4:
            return False
        
        # Check each part
        if len(parts[0]) != 3 or not parts[0][0].isalpha() or not parts[0][1:].isdigit():
            return False
        if len(parts[1]) != 2 or not parts[1].isdigit():
            return False
        if len(parts[2]) != 2 or not parts[2].isdigit():
            return False
        if len(parts[3]) != 6 or not parts[3].isdigit():
            return False
        
        return True
    except:
        return False

def validate_zip_code(zip_code):
    """Validate Philippine ZIP code format"""
    if not zip_code:
        return False, "ZIP code is required"
    
    if not zip_code.isdigit():
        return False, "ZIP code must contain only digits"
    
    if len(zip_code) != 4:
        return False, "ZIP code must be 4 digits"
    
    # Check if it's a valid Philippine ZIP code range
    zip_num = int(zip_code)
    if zip_num < 800 or zip_num > 9820:
        return False, "Invalid Philippine ZIP code"
    
    return True, "Valid ZIP code"

def get_verified_address():
    """Get and validate complete Philippine address"""
    print_header("\n🏠 ADMIN: Complete Address Verification")
    print("Enter client's complete address as it appears on their ID:")
    
    address_parts = {}
    
    # Street Address
    while True:
        street = input("Street address (including house/building number, or 'B' to go back): ").strip()
        if street.upper() == "B":
            return "BACK"
        
        if not street:
            print_warning("Street address is required")
            continue
        
        if len(street) < 5:
            print_warning("Please enter complete street address")
            continue
        
        # Basic street validation
        if not re.match(r'^[a-zA-Z0-9\s\-\#\.\,]+$', street):
            print_warning("Street address contains invalid characters")
            continue
        
        address_parts['street'] = street
        break
    
    # Barangay
    while True:
        barangay = input("Barangay (or 'B' to go back): ").strip()
        if barangay.upper() == "B":
            return "BACK"
        
        if not barangay:
            print_warning("Barangay is required")
            continue
        
        if len(barangay) < 2:
            print_warning("Please enter valid barangay name")
            continue
        
        address_parts['barangay'] = barangay
        break
    
    # City/Municipality
    while True:
        city = input("City/Municipality (or 'B' to go back): ").strip()
        if city.upper() == "B":
            return "BACK"
        
        if not city:
            print_warning("City/Municipality is required")
            continue
        
        if len(city) < 2:
            print_warning("Please enter valid city/municipality name")
            continue
        
        address_parts['city'] = city.title()
        break
    
    # Province
    while True:
        province = input("Province (or 'B' to go back): ").strip()
        if province.upper() == "B":
            return "BACK"
        
        if not province:
            print_warning("Province is required")
            continue
        
        if len(province) < 2:
            print_warning("Please enter valid province name")
            continue
        
        address_parts['province'] = province.title()
        break
    
    # ZIP Code
    while True:
        zip_code = input("ZIP Code (or 'B' to go back): ").strip()
        if zip_code.upper() == "B":
            return "BACK"
        
        is_valid, message = validate_zip_code(zip_code)
        if not is_valid:
            print_warning(message)
            continue
        
        address_parts['zip_code'] = zip_code
        break
    
    # Compile full address
    full_address = f"{address_parts['street']}, {address_parts['barangay']}, {address_parts['city']}, {address_parts['province']} {address_parts['zip_code']}"
    
    # Address confirmation
    print_header("\n📬 ADMIN: Address Confirmation")
    print(f"Full Address: {full_address}")
    print("\nVerify this matches client's government ID:")
    print(f"• Street: {address_parts['street']}")
    print(f"• Barangay: {address_parts['barangay']}")
    print(f"• City/Municipality: {address_parts['city']}")
    print(f"• Province: {address_parts['province']}")
    print(f"• ZIP Code: {address_parts['zip_code']}")
    
    confirm = input(f"\n{Colors.YELLOW}Is this address correct? (Y to confirm, N to re-enter, B to go back): {Colors.END}").strip().upper()
    if confirm == "B":
        return "BACK"
    elif confirm != "Y":
        print_info("Let's try again...")
        return get_verified_address()
    
    return full_address

def get_verified_personal_details():
    """Comprehensive personal details with government ID validation - ADMIN VERSION"""
    print_header("\n🔐 ADMIN: Identity Verification Required")
    print_warning("Government ID verification is required by law for all bookings.")
    print("This helps prevent fraud and ensures ticket authenticity.\n")
    
    # 1. Legal Name Validation (separate fields)
    full_name = get_full_name_separate()
    if full_name == "BACK":
        return "BACK"
    
    # 2. Government ID Validation
    id_type, id_number = validate_government_id()
    if id_type == "BACK":
        return "BACK"
    
    # 3. Contact Information
    print_header("\n📞 ADMIN: Contact Information")
    while True:
        contact = input("Client's mobile number (or 'B' to go back): ").strip()
        if contact.upper() == "B":
            return "BACK"
        
        is_valid, validated_contact = validate_phone_number(contact)
        if not is_valid:
            print_warning(validated_contact)
            continue
        break
    
    # 4. Address Verification
    address = get_verified_address()
    if address == "BACK":
        return "BACK"
    
    # Summary and final confirmation
    print_header("\n✅ ADMIN: Identity Verification Summary")
    print(f"Legal Name: {full_name}")
    print(f"Government ID Type: {id_type}")
    print(f"Contact: {validated_contact}")
    print(f"Address: {address}")
    
    confirm = input(f"\n{Colors.YELLOW}Confirm all client information is correct? (Y to proceed, N to restart, B to go back): {Colors.END}").strip().upper()
    if confirm == "B":
        return "BACK"
    elif confirm != "Y":
        print_info("Restarting verification process...")
        return get_verified_personal_details()
    
    return {
        'full_name': full_name,
        'id_type': id_type,
        'id_number': id_number,  # Still stored but not displayed
        'contact': validated_contact,
        'address': address,
        'verified_at': now_str()
    }

# ------------------------
# Validation Functions
# ------------------------

def validate_phone_number(phone):
    """Enhanced phone validation"""
    if not phone:
        return False, "Phone number cannot be empty"
    # Remove spaces, dashes, etc.
    clean_phone = ''.join(filter(str.isdigit, phone))
    if len(clean_phone) < 10:
        return False, "Phone number too short (minimum 10 digits)"
    if len(clean_phone) > 11:
        return False, "Phone number too long (maximum 11 digits)"
    return True, clean_phone

def validate_email(email):
    """Basic email validation"""
    if not email:
        return False, "Email cannot be empty"
    if '@' not in email or '.' not in email:
        return False, "Invalid email format (must contain @ and .)"
    if len(email) < 5:
        return False, "Email too short"
    return True, email.strip().lower()

# ------------------------
# Digital Ticket System (CSV Only)
# ------------------------

def generate_verification_hash(ticket_data):
    """Generate secure verification hash for ticket authenticity"""
    data_string = f"{ticket_data['service']}{ticket_data['seat']}{ticket_data['passenger']}{ticket_data['timestamp']}{ticket_data['id_type']}"
    return hashlib.sha256(data_string.encode()).hexdigest()[:16]

def generate_digital_ticket(service_key, seat_id, customer_data, ticket_type, base_price, final_price):
    """Create enhanced ticket files using CSV only"""
    service_name = {"C": "Cinema", "B": "Bus", "A": "Airplane"}.get(service_key, "Unknown")
    timestamp = now_str()
    
    # Create enhanced CSV ticket file
    ticket_dir = "digital_tickets"
    os.makedirs(ticket_dir, exist_ok=True)
    safe_name = safe_filename(customer_data['full_name'])
    ticket_filename = f"ticket_{service_name.lower()}_{seat_id}_{safe_name}_enhanced.csv"
    ticket_filepath = os.path.join(ticket_dir, ticket_filename)
    
    # Write enhanced CSV ticket with verification data
    with open(ticket_filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ENHANCED DIGITAL TICKET - VERIFIED IDENTITY"])
        writer.writerow(["Service", service_name])
        writer.writerow(["Seat", seat_id])
        writer.writerow(["Passenger", customer_data['full_name']])
        writer.writerow(["Ticket Type", ticket_type])
        writer.writerow(["Final Price", f"{final_price:.2f}"])
        writer.writerow(["Timestamp", timestamp])
        writer.writerow(["Contact", customer_data['contact']])
        writer.writerow(["Government ID Type", customer_data['id_type']])
        writer.writerow(["Verified At", customer_data['verified_at']])
        writer.writerow(["Address", customer_data['address']])
        writer.writerow(["Verification Hash", generate_verification_hash({
            "service": service_name,
            "seat": seat_id,
            "passenger": customer_data['full_name'],
            "timestamp": timestamp,
            "id_type": customer_data['id_type']
        })])
        writer.writerow([])
        writer.writerow(["THIS IS A VERIFIED TICKET WITH GOVERNMENT ID VALIDATION"])
    
    print_success(f"🎫 Digital ticket generated!")
    print_success(f"📄 Enhanced Ticket: {ticket_filepath}")
    
    return ticket_filepath

# ------------------------
# Enhanced Bulk Reservation System
# ------------------------

def get_verified_personal_details_individual(seat_number, service_key):
    """Individual passenger verification for bulk bookings"""
    print_header(f"\n👤 PASSENGER {seat_number} - IDENTITY VERIFICATION")
    
    full_name = get_full_name_separate()
    if full_name == "BACK":
        return "BACK"
    
    id_type, id_number = validate_government_id()
    if id_type == "BACK":
        return "BACK"
    
    # Contact Information
    while True:
        contact = input(f"Passenger {seat_number} mobile number (or 'B' to go back): ").strip()
        if contact.upper() == "B":
            return "BACK"
        
        is_valid, validated_contact = validate_phone_number(contact)
        if not is_valid:
            print_warning(validated_contact)
            continue
        break
    
    # Address
    address = get_verified_address()
    if address == "BACK":
        return "BACK"
    
    # Individual ticket type selection
    print_header(f"\n🎫 PASSENGER {seat_number} - TICKET TYPE SELECTION")
    ticket_type = choose_ticket_type_interactive(service_key)
    if ticket_type == "BACK":
        return "BACK"
    
    # Summary confirmation for individual passenger
    print_header(f"\n✅ PASSENGER {seat_number} VERIFICATION SUMMARY")
    print(f"Legal Name: {full_name}")
    print(f"Government ID Type: {id_type}")
    print(f"Contact: {validated_contact}")
    print(f"Ticket Type: {ticket_type}")
    
    confirm = input(f"\n{Colors.YELLOW}Confirm passenger {seat_number} information? (Y to proceed, N to restart, B to go back): {Colors.END}").strip().upper()
    if confirm == "B":
        return "BACK"
    elif confirm != "Y":
        print_info("Restarting passenger verification...")
        return get_verified_personal_details_individual(seat_number, service_key)
    
    base, final = compute_price(service_key, ticket_type)
    
    return {
        'full_name': full_name,
        'id_type': id_type,
        'id_number': id_number,
        'contact': validated_contact,
        'address': address,
        'ticket_type': ticket_type,
        'base_price': base,
        'final_price': final,
        'verified_at': now_str()
    }

def bulk_reserve_enhanced(service_key):
    """Enhanced bulk reservation with individual passenger details"""
    print_header("\n🔐 ENHANCED BULK RESERVATION")
    print("Each seat can have different passengers and ticket types!")
    
    seats = load_seats(service_key)
    available_seats = show_available_seats(service_key, seats)
    
    if not available_seats:
        return
    
    while True:
        raw_seats = input("Enter seat IDs to reserve (comma-separated, e.g. 1A,1B,1C, or 'B' to go back): ").strip()
        if raw_seats.upper() == "B":
            return
        
        if not raw_seats:
            print_warning("No seats entered.")
            continue
        
        seat_ids = [normalize_seat_id_input(x.strip()) for x in raw_seats.split(",")]
        invalid_seats = [s for s in seat_ids if s not in available_seats]
        
        if invalid_seats:
            print_error(f"These seats are invalid or unavailable: {', '.join(invalid_seats)}")
            continue
        
        # Collect individual passenger data for each seat
        passenger_data = {}
        all_ticket_types = set()
        total_amount = 0
        
        for seat_id in seat_ids:
            print_header(f"\n🎟️ SEAT {seat_id} - PASSENGER DETAILS")
            
            passenger_info = get_verified_personal_details_individual(seat_id, service_key)
            if passenger_info == "BACK":
                print_info("Bulk reservation cancelled.")
                return
            
            passenger_data[seat_id] = passenger_info
            all_ticket_types.add(passenger_info['ticket_type'])
            total_amount += passenger_info['final_price']
        
        # Show bulk booking summary
        print_header(f"\n📋 ENHANCED BULK BOOKING SUMMARY - {len(seat_ids)} SEATS")
        for seat_id in seat_ids:
            info = passenger_data[seat_id]
            print(f"Seat {seat_id}: {info['full_name']} - {info['ticket_type']} - {pretty_price(info['final_price'])}")
        
        print(f"\n{Colors.BOLD}Total Amount: {pretty_price(total_amount)}{Colors.END}")
        print(f"Ticket Types Used: {', '.join(all_ticket_types)}")
        
        confirm = input(f"\n{Colors.YELLOW}Confirm enhanced bulk booking? (Y to confirm, B to go back): {Colors.END}").strip().upper()
        if confirm == "B":
            continue
        if confirm != "Y":
            continue
        
        # Process each seat with individual data
        timestamp = now_str()
        successful_reservations = 0
        
        for seat_id in seat_ids:
            if seat_id in available_seats:
                info = passenger_data[seat_id]
                
                seats[seat_id] = {
                    "Status": "Taken",
                    "Name": info['full_name'],
                    "Timestamp": timestamp,
                    "TicketType": info['ticket_type'],
                    "BasePrice": f"{info['base_price']:.2f}",
                    "FinalPrice": f"{info['final_price']:.2f}",
                    "Contact": info['contact'],
                    "Address": info['address'],
                    "IDType": info['id_type'],
                    "IDNumber": info['id_number'],
                    "VerifiedAt": info['verified_at']
                }
                successful_reservations += 1
                
                # Generate individual digital ticket
                generate_digital_ticket(service_key, seat_id, info, info['ticket_type'], 
                                      info['base_price'], info['final_price'])
                
                save_booking_history(service_key, seat_id, "ENHANCED_BULK_RESERVATION", 
                                   f"{info['full_name']} - {info['ticket_type']} - {pretty_price(info['final_price'])}")
        
        save_seats(service_key, seats)
        print_success(f"✅ Enhanced bulk reservation completed! {successful_reservations} seats reserved")
        print_success(f"💰 Total Revenue: {pretty_price(total_amount)}")
        break

# ------------------------
# Consistent Back Button System
# ------------------------

def get_user_choice(prompt, valid_choices=None, allow_back=True):
    """Universal function for consistent user input with back options"""
    if allow_back:
        prompt += " (or 'BACK' to go back)"
    
    while True:
        choice = input(f"{Colors.YELLOW}{prompt}: {Colors.END}").strip().upper()
        
        if allow_back and choice == "BACK":
            return "BACK"
        
        if valid_choices:
            if choice in valid_choices:
                return choice
            else:
                print_error(f"Invalid choice. Please choose from: {', '.join(valid_choices)}")
        else:
            return choice

def confirm_action(prompt):
    """Consistent confirmation with back option"""
    while True:
        response = input(f"{Colors.YELLOW}{prompt} (Y/N/B): {Colors.END}").strip().upper()
        
        if response == "B":
            return "BACK"
        elif response == "Y":
            return True
        elif response == "N":
            return False
        else:
            print_warning("Please enter Y, N, or B")

# ------------------------
# Enhanced Core Functions
# ------------------------

def confirm_booking_summary(service_key, seat_id, customer_data, ticket_type, final_price):
    """Show booking summary with verified identity (ID number hidden)"""
    service_name = {"C": "Cinema", "B": "Bus", "A": "Airplane"}.get(service_key)
    
    print_header("\n" + "="*60)
    print_header("📋 ADMIN: BOOKING SUMMARY WITH IDENTITY VERIFICATION")
    print_header("="*60)
    print(f"{Colors.BOLD}Service:{Colors.END} {service_name}")
    print(f"{Colors.BOLD}Seat:{Colors.END} {seat_id}")
    print(f"{Colors.BOLD}Ticket Type:{Colors.END} {ticket_type}")
    print(f"{Colors.BOLD}Total Amount:{Colors.END} {pretty_price(final_price)}")
    print_header("-" * 60)
    print(f"{Colors.BOLD}Verified Identity:{Colors.END}")
    print(f"Legal Name: {customer_data['full_name']}")
    print(f"Government ID Type: {customer_data['id_type']}")
    print(f"Contact: {customer_data['contact']}")
    print(f"Address: {customer_data['address']}")
    print_header("="*60)
    
    confirm = input(f"{Colors.YELLOW}Confirm booking with verified identity? (Y to confirm, B to go back): {Colors.END}").strip().upper()
    if confirm == "B":
        return "BACK"
    return confirm == "Y"

def reserve_seat(service_key):
    while True:
        seats = load_seats(service_key)
        print_seat_map(service_key, seats)
        
        raw = input("Enter seat ID to reserve (e.g. 1A or A1, or 'B' to go back): ").strip()
        if raw.upper() == "B":
            return
        
        seat_id = normalize_seat_id_input(raw)
        if seat_id not in seats:
            print_error("Invalid seat ID. Please try again.")
            continue
            
        info = seats[seat_id]
        if info["Status"] == "Taken":
            print_error(f"Seat {seat_id} is already taken by '{info['Name']}'.")
            continue
        if info["Status"] == "Unavailable":
            print_error(f"Seat {seat_id} is unavailable.")
            continue

        # Identity Verification REQUIRED
        print_header("\n🔐 IDENTITY VERIFICATION REQUIRED")
        print_warning("Government ID verification is mandatory for all bookings.")
        customer_data = get_verified_personal_details()
        if customer_data == "BACK":
            continue

        # Ticket type selection
        ticket_type = choose_ticket_type_interactive(service_key)
        if ticket_type == "BACK":
            continue
            
        base, final = compute_price(service_key, ticket_type)

        # Final confirmation with verified identity
        confirmation = confirm_booking_summary(service_key, seat_id, customer_data, ticket_type, final)
        if confirmation == "BACK" or not confirmation:
            continue

        timestamp = now_str()

        # Save seat info with verified identity
        seats[seat_id] = {
            "Status": "Taken",
            "Name": customer_data['full_name'],
            "Timestamp": timestamp,
            "TicketType": ticket_type,
            "BasePrice": f"{base:.2f}",
            "FinalPrice": f"{final:.2f}",
            "Contact": customer_data['contact'],
            "Address": customer_data['address'],
            "IDType": customer_data['id_type'],
            "IDNumber": customer_data['id_number'],
            "VerifiedAt": customer_data['verified_at']
        }
        save_seats(service_key, seats)
        
        # Save to booking history
        save_booking_history(service_key, seat_id, "VERIFIED_RESERVATION", 
                           f"{customer_data['full_name']} - {ticket_type} - {pretty_price(final)} - ID: {customer_data['id_type']}")
        
        # Generate digital ticket
        generate_digital_ticket(service_key, seat_id, customer_data, ticket_type, base, final)
        
        print_success(f"✅ Verified reservation completed!")
        print_success(f"Seat {seat_id} reserved for {customer_data['full_name']}")
        print_success(f"Ticket Type: {ticket_type} | Final Price: {pretty_price(final)}")
        print_success(f"Government ID: {customer_data['id_type']} verified")
        break

# ------------------------
# Enhanced Display Functions
# ------------------------

def print_seat_map(service_key, seats):
    layout = LAYOUT_FUNCTIONS[service_key]()
    print_header("\n--- SEAT LAYOUT (🟩 =Available, 🟥 =Taken, ⬛ =Unavailable) ---")
    # Sort by numeric row, then letter
    layout_sorted = sorted(layout, key=lambda x: (int(''.join(filter(str.isdigit, x))), x))
    current_row = None
    for s in layout_sorted:
        row = ''.join(filter(str.isdigit, s))
        seat_letter = s[len(row):]
        if row != current_row:
            if current_row is not None:
                print()
            print(f"{Colors.CYAN}{row:>2}{Colors.END} ", end="")
            current_row = row
        st = seats.get(s, {"Status": "Unavailable"})["Status"]
        if st == "Available":
            symbol = f"{Colors.GREEN}🟩{Colors.END}"
        elif st == "Taken":
            symbol = f"{Colors.RED}🟥{Colors.END}"
        else:
            symbol = "⬛"
        print(f"{seat_letter}{symbol} ", end="")
        # visualize aisle for some layouts
        if service_key == "B" and seat_letter == "B":
            print(" ", end="")
        if service_key == "A" and seat_letter == "C":
            print(" ", end="")
    print("\n")

def show_available_seats(service_key, seats):
    """Enhanced seat selection with filtering"""
    available_seats = [seat for seat, info in seats.items() if info["Status"] == "Available"]
    
    if not available_seats:
        print_warning("No available seats found.")
        return []
    
    print_success(f"Available Seats ({len(available_seats)}):")
    # Group by row for better display
    rows = {}
    for seat in available_seats:
        row = ''.join(filter(str.isdigit, seat))
        if row not in rows:
            rows[row] = []
        rows[row].append(seat)
    
    for row in sorted(rows.keys(), key=int):
        print(f"{Colors.BLUE}Row {row}:{Colors.END} {', '.join(sorted(rows[row]))}")
    
    return available_seats

def get_contact_details():
    """Get contact number and address from user with back option"""
    while True:
        contact = input("Enter contact number (or 'B' to go back): ").strip()
        if contact.upper() == "B":
            return "BACK", "BACK"
        if not contact:
            print_warning("Contact number required.")
            continue
        
        # Enhanced phone validation
        is_valid, validated_contact = validate_phone_number(contact)
        if not is_valid:
            print_warning(validated_contact)
            continue
        break
    
    while True:
        address = input("Enter address (or 'B' to go back): ").strip()
        if address.upper() == "B":
            return "BACK", "BACK"
        if not address:
            address = "-"
        break
    
    return validated_contact, address

# ------------------------
# Utility Functions
# ------------------------

def safe_filename(s):
    """Create safe filenames"""
    return "".join(c for c in s if c.isalnum() or c in (' ', '', '-', '.')).strip().replace(" ", "_")

def generate_ticket_csv(service_key, seat_id, name, timestamp, ticket_type, base_price, final_price, contact="", address=""):
    service_name = {"C": "Cinema", "B": "Bus", "A": "Airplane"}.get(service_key, "Unknown")
    ticket_dir = "tickets"
    os.makedirs(ticket_dir, exist_ok=True)
    safe_name = safe_filename(name)
    filename = f"ticket_{service_name.lower()}_{seat_id}_{safe_name}.csv"
    filepath = os.path.join(ticket_dir, filename)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        # REMOVED: IDNumber from headers
        writer.writerow(["Service", "Seat", "Passenger", "TicketType", "BasePrice", "FinalPrice", "Timestamp", "Contact", "Address"])
        writer.writerow([service_name, seat_id, name, ticket_type, f"{base_price:.2f}", f"{final_price:.2f}", timestamp, contact, address])
    return filepath

# ------------------------
# Additional Core Functions
# ------------------------

def show_ticket(service_key):
    while True:
        seats = load_seats(service_key)
        print_header("\n🎫 === View Verified Ticket ===")
        search = input("Enter client fullname or seat ID (e.g John or 1A, or 'B' to go back): ").strip()
        if search.upper() == "B":
            return
        if not search:
            print_warning("Input required.")
            continue
            
        search_norm = normalize_seat_id_input(search)
        found = False
        for seat_id, info in seats.items():
            if info["Status"] == "Taken" and (info["Name"].lower() == search.lower() or seat_id == search_norm):
                found = True
                service_name = {"C": "Cinema", "B": "Bus", "A": "Airplane"}.get(service_key, "Unknown")
                print_header("\n" + "="*60)
                print_header(f"🎟 VERIFIED TICKET DETAILS ({service_name})")
                print_header("="*60)
                print(f"{Colors.BOLD}Seat:{Colors.END} {seat_id}")
                print(f"{Colors.BOLD}Client:{Colors.END} {info['Name']}")
                print(f"{Colors.BOLD}Contact:{Colors.END} {info.get('Contact', 'Not provided')}")
                print(f"{Colors.BOLD}Address:{Colors.END} {info.get('Address', 'Not provided')}")
                print(f"{Colors.BOLD}Government ID Type:{Colors.END} {info.get('IDType', 'Not provided')}")
                # REMOVED: ID Number display
                print(f"{Colors.BOLD}Verified At:{Colors.END} {info.get('VerifiedAt', 'Not provided')}")
                print(f"{Colors.BOLD}Service:{Colors.END} {service_name}")
                print(f"{Colors.BOLD}TicketType:{Colors.END} {info.get('TicketType') or '-'}")
                print(f"{Colors.BOLD}Base Price:{Colors.END} {pretty_price(info.get('BasePrice') or 0)}")
                print(f"{Colors.BOLD}Final Price:{Colors.END} {pretty_price(info.get('FinalPrice') or 0)}")
                print(f"{Colors.BOLD}Booked At:{Colors.END} {info.get('Timestamp')}")
                print_header("="*60)
                # check for ticket file
                ticket_dir = "tickets"
                safe_name = safe_filename(info['Name'])
                filename = f"ticket_{service_name.lower()}_{seat_id}_{safe_name}.csv"
                filepath = os.path.join(ticket_dir, filename)
                if os.path.exists(filepath):
                    print_info(f"📄 Verified ticket file: {filepath}")
                else:
                    print_warning("⚠️ Ticket CSV file not found (may have been deleted).")
                break
        if not found:
            print_error("❌ No verified ticket found for that client or seat.")
        
        # Ask if user wants to search again
        again = input(f"\n{Colors.YELLOW}Search again? (Y to search again, any other key to go back): {Colors.END}").strip().upper()
        if again != "Y":
            break

def cancel_reservation(service_key):
    while True:
        seats = load_seats(service_key)
        print_seat_map(service_key, seats)
        raw = input("Enter seat ID to cancel (or 'B' to go back): ").strip()
        if raw.upper() == "B":
            return
        seat_id = normalize_seat_id_input(raw)
        if seat_id not in seats or seats[seat_id]["Status"] != "Taken":
            print_error("Invalid or not reserved. Please try again.")
            continue
            
        info = seats[seat_id]
        print_warning(f"Cancel booking for {info['Name']} on {seat_id}?")
        print(f"Contact: {info.get('Contact', 'Not provided')}")
        print(f"Address: {info.get('Address', 'Not provided')}")
        print(f"Government ID Type: {info.get('IDType', 'Not provided')}")
        confirm = input(f"{Colors.YELLOW}Type Y to confirm, N to cancel, or B to go back: {Colors.END}").strip().upper()
        if confirm == "B":
            continue
        if confirm != "Y":
            print_info("Reservation preserved.")
            continue
            
        service_name = {"C": "Cinema", "B": "Bus", "A": "Airplane"}.get(service_key, "Unknown")
        safe_name = safe_filename(info['Name'])
        old_ticket = os.path.join("tickets", f"ticket_{service_name.lower()}_{seat_id}_{safe_name}.csv")
        if os.path.exists(old_ticket):
            try:
                os.remove(old_ticket)
            except Exception:
                pass
        seats[seat_id] = {
            "Status": "Available", "Name": "", "Timestamp": now_str(), "TicketType": "", 
            "BasePrice": "", "FinalPrice": "", "Contact": "", "Address": "", 
            "IDType": "", "IDNumber": "", "VerifiedAt": ""
        }
        save_seats(service_key, seats)
        save_booking_history(service_key, seat_id, "CANCELLATION", f"{info['Name']} - ID: {info.get('IDType', 'Unknown')}")
        print_success(f"Cancelled booking on {seat_id} and removed ticket file if it existed.")
        
        # Ask if user wants to cancel another reservation
        again = input(f"\n{Colors.YELLOW}Cancel another reservation? (Y to continue, any other key to go back): {Colors.END}").strip().upper()
        if again != "Y":
            break

def update_reservation(service_key):
    while True:
        seats = load_seats(service_key)
        print_seat_map(service_key, seats)
        raw = input("Enter seat ID to update (or 'B' to go back): ").strip()
        if raw.upper() == "B":
            return
        seat_id = normalize_seat_id_input(raw)
        if seat_id not in seats or seats[seat_id]["Status"] != "Taken":
            print_error("Seat not taken or invalid. Please try again.")
            continue
            
        info = seats[seat_id]
        print_info(f"\nSeat {seat_id} currently booked by {info['Name']}.")
        print(f"Contact: {info.get('Contact', 'Not provided')}")
        print(f"Address: {info.get('Address', 'Not provided')}")
        print(f"Government ID Type: {info.get('IDType', 'Not provided')}")
        print("\n1) Change client name")
        print("2) Move to another seat")
        print("3) Change ticket type")
        print("4) Update contact details")
        print("B) Back")
        choice = input("Select option (or 'B' to go back): ").strip().upper()
        
        if choice == "B":
            continue
            
        service_name = {"C": "Cinema", "B": "Bus", "A": "Airplane"}.get(service_key, "Unknown")
        ticket_dir = "tickets"
        os.makedirs(ticket_dir, exist_ok=True)
        
        if choice == "1":
            while True:
                new_name = input("Enter new client name (or 'B' to go back): ").strip()
                if new_name.upper() == "B":
                    break
                if not new_name:
                    print_warning("Name required.")
                    continue
                if not all(c.isalpha() or c == " " for c in new_name):
                    print_warning("Name can only contain letters and single spaces. Try again.")
                    continue
                new_name = " ".join(new_name.split())
                break
            
            if new_name.upper() == "B":
                continue
                
            old_safe = safe_filename(info['Name'])
            old_ticket = os.path.join(ticket_dir, f"ticket_{service_name.lower()}_{seat_id}_{old_safe}.csv")
            if os.path.exists(old_ticket):
                try:
                    os.remove(old_ticket)
                except Exception:
                    pass
            seats[seat_id]["Name"] = new_name
            seats[seat_id]["Timestamp"] = now_str()
            save_seats(service_key, seats)
            generate_ticket_csv(service_key, seat_id, new_name, seats[seat_id]["Timestamp"], seats[seat_id].get("TicketType",""), float(seats[seat_id].get("BasePrice") or 0), float(seats[seat_id].get("FinalPrice") or 0), seats[seat_id].get("Contact", ""), seats[seat_id].get("Address", ""))
            save_booking_history(service_key, seat_id, "NAME_UPDATE", f"{info['Name']} -> {new_name}")
            print_success(f"Updated client name for seat {seat_id} to {new_name}.")
            break
            
        elif choice == "2":
            target_raw = input("Enter target seat ID (or 'B' to go back): ").strip()
            if target_raw.upper() == "B":
                continue
            target = normalize_seat_id_input(target_raw)
            if target not in seats or seats[target]["Status"] != "Available":
                print_error("Target seat invalid or not available. Please try again.")
                continue
                
            confirm = input(f"{Colors.YELLOW}Move {info['Name']} from {seat_id} to {target}? (Y/N/B): {Colors.END}").strip().upper()
            if confirm == "B":
                continue
            if confirm != "Y":
                print_info("Action cancelled.")
                continue
                
            old_safe = safe_filename(info['Name'])
            old_ticket = os.path.join(ticket_dir, f"ticket_{service_name.lower()}_{seat_id}_{old_safe}.csv")
            if os.path.exists(old_ticket):
                try:
                    os.remove(old_ticket)
                except Exception:
                    pass
            seats[target] = {
                "Status": "Taken",
                "Name": info["Name"],
                "Timestamp": now_str(),
                "TicketType": info.get("TicketType",""),
                "BasePrice": info.get("BasePrice",""),
                "FinalPrice": info.get("FinalPrice",""),
                "Contact": info.get("Contact",""),
                "Address": info.get("Address",""),
                "IDType": info.get("IDType",""),
                "IDNumber": info.get("IDNumber",""),
                "VerifiedAt": info.get("VerifiedAt","")
            }
            seats[seat_id] = {
                "Status": "Available", "Name": "", "Timestamp": now_str(), "TicketType": "", 
                "BasePrice": "", "FinalPrice": "", "Contact": "", "Address": "", 
                "IDType": "", "IDNumber": "", "VerifiedAt": ""
            }
            save_seats(service_key, seats)
            generate_ticket_csv(service_key, target, seats[target]["Name"], seats[target]["Timestamp"], seats[target].get("TicketType",""), float(seats[target].get("BasePrice") or 0), float(seats[target].get("FinalPrice") or 0), seats[target].get("Contact", ""), seats[target].get("Address", ""))
            save_booking_history(service_key, seat_id, "SEAT_MOVE", f"{info['Name']} from {seat_id} to {target}")
            print_success(f"Moved {info['Name']} from {seat_id} to {target}.")
            break
            
        elif choice == "3":
            # change ticket type (recompute price)
            new_type = choose_ticket_types_with_current(service_key, info.get("TicketType", ""))
            if new_type == "BACK":
                continue
            base, final = compute_price(service_key, new_type)
            seats[seat_id]["TicketType"] = new_type
            seats[seat_id]["BasePrice"] = f"{base:.2f}"
            seats[seat_id]["FinalPrice"] = f"{final:.2f}"
            seats[seat_id]["Timestamp"] = now_str()
            save_seats(service_key, seats)
            # regenerate ticket file
            old_safe = safe_filename(info['Name'])
            old_ticket = os.path.join(ticket_dir, f"ticket_{service_name.lower()}_{seat_id}_{old_safe}.csv")
            if os.path.exists(old_ticket):
                try:
                    os.remove(old_ticket)
                except Exception:
                    pass
            generate_ticket_csv(service_key, seat_id, seats[seat_id]["Name"], seats[seat_id]["Timestamp"], new_type, base, final, seats[seat_id].get("Contact", ""), seats[seat_id].get("Address", ""))
            save_booking_history(service_key, seat_id, "TICKET_TYPE_UPDATE", f"{info.get('TicketType', 'None')} -> {new_type}")
            print_success(f"Ticket type updated to {new_type} for {seat_id}. Final price: {pretty_price(final)}")
            break
            
        elif choice == "4":
            # Update contact details
            print_info("\n--- Update Contact Information ---")
            print(f"Current Contact: {info.get('Contact', 'Not provided')}")
            print(f"Current Address: {info.get('Address', 'Not provided')}")
            
            contact, address = get_contact_details()
            if contact == "BACK":
                continue
                
            seats[seat_id]["Contact"] = contact
            seats[seat_id]["Address"] = address
            seats[seat_id]["Timestamp"] = now_str()
            save_seats(service_key, seats)
            
            # regenerate ticket file
            old_safe = safe_filename(info['Name'])
            old_ticket = os.path.join(ticket_dir, f"ticket_{service_name.lower()}_{seat_id}_{old_safe}.csv")
            if os.path.exists(old_ticket):
                try:
                    os.remove(old_ticket)
                except Exception:
                    pass
            generate_ticket_csv(service_key, seat_id, seats[seat_id]["Name"], seats[seat_id]["Timestamp"], seats[seat_id].get("TicketType",""), float(seats[seat_id].get("BasePrice") or 0), float(seats[seat_id].get("FinalPrice") or 0), contact, address)
            save_booking_history(service_key, seat_id, "CONTACT_UPDATE", f"Contact details updated")
            print_success(f"Updated contact details for {info['Name']} on seat {seat_id}.")
            break
            
        else:
            print_error("Invalid option.")
        
        # Ask if user wants to update another reservation
        again = input(f"\n{Colors.YELLOW}Update another reservation? (Y to continue, any other key to go back): {Colors.END}").strip().upper()
        if again != "Y":
            break

def choose_ticket_types_with_current(service_key, current_type):
    types = list_ticket_types(service_key)
    print("\nSelect new ticket type:")
    for i, t in enumerate(types, start=1):
        b, f = compute_price(service_key, t)
        marker = f" {Colors.GREEN}(current){Colors.END}" if t == current_type else ""
        print(f"{i}) {t} (Base: {pretty_price(b)} / Final: {pretty_price(f)}){marker}")
    print("B) Back to previous menu")
    
    while True:
        sel = input("Choice (number or name, or 'B' to go back): ").strip()
        if not sel:
            print_warning("Selection required.")
            continue
        if sel.upper() == "B":
            return "BACK"
        if sel.isdigit():
            idx = int(sel) - 1
            if 0 <= idx < len(types):
                return types[idx]
            else:
                print_warning("Invalid number.")
                continue
        candidate = sel.title()
        if candidate in types:
            return candidate
        print_warning("Invalid choice. Try again.")

# ------------------------
# Enhanced Report System
# ------------------------

def view_report(service_key):
    while True:
        print_header("\n📊 Enhanced Report Options:")
        print("1) View all bookings")
        print("2) Search client name")
        print("3) Filter by ticket type") 
        print("4) Show revenue summary")
        print("B) Back")
        
        choice = input("Select report type (or 'B' to go back): ").strip()
        
        if choice.upper() == "B":
            return
            
        if choice == "1":
            basic_view_report(service_key)
        elif choice == "2":
            search_passenger_report(service_key)
        elif choice == "3":
            filter_by_ticket_type(service_key)
        elif choice == "4":
            show_revenue_summary(service_key)
        else:
            print_error("Invalid option.")
        
        # Ask if user wants to view another report
        again = input(f"\n{Colors.YELLOW}View another report? (Y to continue, any other key to go back): {Colors.END}").strip().upper()
        if again != "Y":
            break

def basic_view_report(service_key):
    path = DATA_FILES[service_key]
    ensure_csv(service_key)
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    taken = sum(1 for r in rows if r["Status"] == "Taken")
    avail = sum(1 for r in rows if r["Status"] == "Available")
    print_header(f"\n{path}: Taken={taken}, Available={avail}, Total={len(rows)}")
    print("-" * 100)  # Reduced width since we removed ID number
    # REMOVED: ID Number from header
    print(f"{Colors.BOLD}{'Seat':<6} | {'Status':<10} | {'Name':<20} | {'ID Type':<12} | {'Contact':<12} | {'TicketType':<10} | {'FinalPrice':<10} | Timestamp{Colors.END}")
    print("-" * 100)
    for r in rows:
        name = r['Name'] or '-'
        contact = r.get('Contact', '') or '-'
        id_type = r.get('IDType', '') or '-'
        status_color = Colors.GREEN if r['Status'] == 'Available' else Colors.RED if r['Status'] == 'Taken' else Colors.YELLOW
        # REMOVED: ID Number from data row
        print(f"{r['Seat']:<6} | {status_color}{r['Status']:<10}{Colors.END} | {name:<20} | {id_type:<12} | {contact:<12} | {r.get('TicketType',''):<10} | {pretty_price(r.get('FinalPrice') or 0):<10} | {r.get('Timestamp','')}")
    print("-" * 100)
    input("Press Enter to continue...")
    return

def search_passenger_report(service_key):
    seats = load_seats(service_key)
    while True:
        search_term = input("Enter client name to search (or 'B' to go back): ").strip().lower()
        
        if search_term.upper() == "B":
            return
        
        if not search_term:
            print_warning("Search term required.")
            continue
        
        matches = []
        for seat_id, info in seats.items():
            if info["Status"] == "Taken" and search_term in info["Name"].lower():
                matches.append((seat_id, info))
        
        if not matches:
            print_warning(f"No bookings found for client containing '{search_term}'")
            continue
        
        print_header(f"\n📋 Bookings for client containing '{search_term}':")
        print("-" * 100)
        print(f"{Colors.BOLD}{'Seat':<6} | {'Name':<20} | {'ID Type':<12} | {'Contact':<12} | {'TicketType':<10} | {'FinalPrice':<10} | Timestamp{Colors.END}")
        print("-" * 100)
        for seat_id, info in matches:
            print(f"{seat_id:<6} | {info['Name']:<20} | {info.get('IDType','-'):<12} | {info.get('Contact','-'):<12} | {info.get('TicketType','-'):<10} | {pretty_price(info.get('FinalPrice') or 0):<10} | {info.get('Timestamp','')}")
        print("-" * 100)
        input("Press Enter to continue...")
        break

def filter_by_ticket_type(service_key):
    seats = load_seats(service_key)
    ticket_types = list_ticket_types(service_key)
    
    while True:
        print_header("\nAvailable Ticket Types:")
        for i, ttype in enumerate(ticket_types, 1):
            print(f"{i}) {ttype}")
        print("B) Back")
        
        choice = input("Select ticket type to filter by (or 'B' to go back): ").strip()
        
        if choice.upper() == "B":
            return
        
        if not choice.isdigit() or not (1 <= int(choice) <= len(ticket_types)):
            print_error("Invalid selection.")
            continue
        
        selected_type = ticket_types[int(choice) - 1]
        matches = []
        
        for seat_id, info in seats.items():
            if info["Status"] == "Taken" and info.get("TicketType") == selected_type:
                matches.append((seat_id, info))
        
        if not matches:
            print_warning(f"No bookings found for ticket type '{selected_type}'")
            continue
        
        print_header(f"\n📋 Bookings with ticket type '{selected_type}':")
        print("-" * 90)
        print(f"{Colors.BOLD}{'Seat':<6} | {'Name':<20} | {'Contact':<12} | {'FinalPrice':<10} | Timestamp{Colors.END}")
        print("-" * 90)
        for seat_id, info in matches:
            print(f"{seat_id:<6} | {info['Name']:<20} | {info.get('Contact','-'):<12} | {pretty_price(info.get('FinalPrice') or 0):<10} | {info.get('Timestamp','')}")
        print("-" * 90)
        input("Press Enter to continue...")
        break

def show_revenue_summary(service_key):
    seats = load_seats(service_key)
    revenue_by_type = {}
    total_revenue = 0
    total_bookings = 0
    
    for seat_id, info in seats.items():
        if info["Status"] == "Taken" and info.get("FinalPrice"):
            try:
                price = float(info["FinalPrice"])
                ticket_type = info.get("TicketType", "Unknown")
                revenue_by_type[ticket_type] = revenue_by_type.get(ticket_type, 0) + price
                total_revenue += price
                total_bookings += 1
            except ValueError:
                continue
    
    print_header(f"\n💰 Revenue Summary for {service_key}:")
    print("-" * 50)
    print(f"{Colors.BOLD}Total Bookings:{Colors.END} {total_bookings}")
    print(f"{Colors.BOLD}Total Revenue:{Colors.END} {pretty_price(total_revenue)}")
    print_header("\nRevenue by Ticket Type:")
    print("-" * 30)
    for ticket_type, revenue in revenue_by_type.items():
        print(f"{ticket_type:<12}: {pretty_price(revenue)}")
    print("-" * 30)
    input("Press Enter to continue...")

# ------------------------
# Time-based Features
# ------------------------

def check_booking_timeout(service_key):
    """Cancel bookings older than 24 hours if not confirmed"""
    seats = load_seats(service_key)
    current_time = datetime.now()
    expired_count = 0
    
    for seat_id, info in seats.items():
        if info["Status"] == "Taken" and info["Timestamp"]:
            try:
                booking_time = datetime.strptime(info["Timestamp"], "%Y-%m-%d %H:%M:%S")
                if current_time - booking_time > timedelta(hours=24):
                    # Auto-cancel expired booking
                    old_name = info["Name"]
                    seats[seat_id] = {
                        "Status": "Available", "Name": "", "Timestamp": "", 
                        "TicketType": "", "BasePrice": "", "FinalPrice": "", 
                        "Contact": "", "Address": "", "IDType": "", "IDNumber": "", 
                        "VerifiedAt": ""
                    }
                    expired_count += 1
                    save_booking_history(service_key, seat_id, "AUTO_CANCELLATION", f"{old_name} - Booking expired")
            except ValueError:
                continue
    
    if expired_count > 0:
        save_seats(service_key, seats)
        print_warning(f"Auto-cancelled {expired_count} expired bookings.")
    
    return expired_count

# ------------------------
# Notification System
# ------------------------

def send_booking_confirmation(name, contact, service_name, seat_id, ticket_type, final_price):
    """Simulate sending confirmation"""
    print_info(f"\n📧 Sending confirmation to {name}...")
    print(f"Message: Your {service_name} booking for seat {seat_id} is confirmed!")
    print(f"Ticket Type: {ticket_type}")
    print(f"Amount: {pretty_price(final_price)}")
    print_success("Confirmation sent successfully!")

# ------------------------
# Booking History System
# ------------------------

def save_booking_history(service_key, seat_id, action, details):
    """Save all booking activities for audit trail"""
    history_file = "booking_history.csv"
    file_exists = os.path.isfile(history_file)
    
    with open(history_file, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Service", "Seat", "Action", "Details"])
        writer.writerow([now_str(), service_key, seat_id, action, details])

def view_booking_history():
    """View the booking history"""
    history_file = "booking_history.csv"
    if not os.path.exists(history_file):
        print_warning("No booking history found.")
        return
    
    with open(history_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    if not rows:
        print_warning("No booking history records.")
        return
    
    print_header("\n📜 Booking History")
    print("-" * 120)
    print(f"{Colors.BOLD}{'Timestamp':<20} | {'Service':<8} | {'Seat':<6} | {'Action':<15} | {'Details'}{Colors.END}")
    print("-" * 120)
    for row in rows[-20:]:  # Show last 20 records
        print(f"{row['Timestamp']:<20} | {row['Service']:<8} | {row['Seat']:<6} | {row['Action']:<15} | {row['Details']}")
    print("-" * 120)
    input("Press Enter to continue...")

# ------------------------
# System Settings
# ------------------------

def system_settings():
    while True:
        print_header("\n⚙️ System Settings")
        print("1) Check for expired bookings")
        print("2) View booking history")
        print("3) System statistics")
        print("B) Back to main menu")
        
        choice = input("Select option (or 'B' to go back): ").strip().upper()
        
        if choice == "B":
            break
            
        if choice == "1":
            expired_total = 0
            for service_key in DATA_FILES:
                expired = check_booking_timeout(service_key)
                expired_total += expired
            if expired_total == 0:
                print_success("No expired bookings found.")
            input("Press Enter to continue...")
        elif choice == "2":
            view_booking_history()
        elif choice == "3":
            show_system_statistics()
        else:
            print_error("Invalid option.")

def show_system_statistics():
    total_bookings = 0
    total_revenue = 0
    service_stats = {}
    
    for service_key in DATA_FILES:
        seats = load_seats(service_key)
        service_name = {"C": "Cinema", "B": "Bus", "A": "Airplane"}.get(service_key)
        taken_seats = sum(1 for info in seats.values() if info["Status"] == "Taken")
        total_bookings += taken_seats
        
        # Calculate revenue
        service_revenue = 0
        for info in seats.values():
            if info["Status"] == "Taken" and info.get("FinalPrice"):
                try:
                    service_revenue += float(info["FinalPrice"])
                except ValueError:
                    pass
        
        total_revenue += service_revenue
        service_stats[service_name] = {
            'bookings': taken_seats,
            'revenue': service_revenue
        }
    
    print_header("\n📈 System Statistics")
    print("=" * 50)
    print(f"{Colors.BOLD}Total Bookings:{Colors.END} {total_bookings}")
    print(f"{Colors.BOLD}Total Revenue:{Colors.END} {pretty_price(total_revenue)}")
    print_header("\nService-wise Breakdown:")
    print("-" * 40)
    for service_name, stats in service_stats.items():
        print(f"{service_name:<10}: {stats['bookings']:>3} bookings, {pretty_price(stats['revenue'])}")
    print("=" * 50)
    input("Press Enter to continue...")

# ------------------------
# Legacy Bulk Reservation
# ------------------------

def bulk_reserve(service_key):
    """Legacy bulk reservation function"""
    print_header("\n🔐 BULK RESERVATION WITH ID VERIFICATION")
    print_warning("Each seat requires individual identity verification.")
    
    seats = load_seats(service_key)
    available_seats = show_available_seats(service_key, seats)
    
    if not available_seats:
        return
    
    while True:
        raw_seats = input("Enter seat IDs to reserve (comma-separated, e.g. 1A,1B,1C, or 'B' to go back): ").strip()
        if raw_seats.upper() == "B":
            return
        
        if not raw_seats:
            print_warning("No seats entered.")
            continue
        
        seat_ids = [normalize_seat_id_input(x.strip()) for x in raw_seats.split(",")]
        invalid_seats = [s for s in seat_ids if s not in available_seats]
        
        if invalid_seats:
            print_error(f"These seats are invalid or unavailable: {', '.join(invalid_seats)}")
            continue
        
        # Verify identity once for all seats
        customer_data = get_verified_personal_details()
        if customer_data == "BACK":
            continue
        
        # Select ticket type for all seats
        ticket_type = choose_ticket_type_interactive(service_key)
        if ticket_type == "BACK":
            continue
        
        base, final = compute_price(service_key, ticket_type)
        
        # Confirm bulk booking
        print_header(f"\n📋 BULK BOOKING SUMMARY - {len(seat_ids)} SEATS")
        print(f"Client: {customer_data['full_name']}")
        print(f"Seats: {', '.join(seat_ids)}")
        print(f"Ticket Type: {ticket_type}")
        print(f"Total Amount: {pretty_price(final * len(seat_ids))}")
        
        confirm = input(f"{Colors.YELLOW}Confirm bulk booking? (Y to confirm, B to go back): {Colors.END}").strip().upper()
        if confirm == "B" or confirm != "Y":
            continue
        
        # Process each seat
        timestamp = now_str()
        successful_reservations = 0
        
        for seat_id in seat_ids:
            if seat_id in available_seats:  # Double-check availability
                seats[seat_id] = {
                    "Status": "Taken",
                    "Name": customer_data['full_name'],
                    "Timestamp": timestamp,
                    "TicketType": ticket_type,
                    "BasePrice": f"{base:.2f}",
                    "FinalPrice": f"{final:.2f}",
                    "Contact": customer_data['contact'],
                    "Address": customer_data['address'],
                    "IDType": customer_data['id_type'],
                    "IDNumber": customer_data['id_number'],
                    "VerifiedAt": customer_data['verified_at']
                }
                successful_reservations += 1
                
                # Generate individual ticket
                service_name = {"C": "Cinema", "B": "Bus", "A": "Airplane"}.get(service_key, "Unknown")
                ticket_dir = "tickets"
                os.makedirs(ticket_dir, exist_ok=True)
                safe_name = safe_filename(customer_data['full_name'])
                filename = f"ticket_{service_name.lower()}_{seat_id}_{safe_name}.csv"
                filepath = os.path.join(ticket_dir, filename)
                
                with open(filepath, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Service", "Seat", "Passenger", "TicketType", "BasePrice", "FinalPrice", 
                                   "Timestamp", "Contact", "Address", "IDType", "VerifiedAt"])
                    writer.writerow([service_name, seat_id, customer_data['full_name'], ticket_type, 
                                   f"{base:.2f}", f"{final:.2f}", timestamp, customer_data['contact'], 
                                   customer_data['address'], customer_data['id_type'], customer_data['verified_at']])
                
                save_booking_history(service_key, seat_id, "BULK_RESERVATION", 
                                   f"{customer_data['full_name']} - {ticket_type} - {pretty_price(final)}")
        
        save_seats(service_key, seats)
        print_success(f"✅ Bulk reservation completed! {successful_reservations} seats reserved for {customer_data['full_name']}")
        break

# ------------------------
# Seat Management
# ------------------------

def set_unavailable(service_key):
    while True:
        seats = load_seats(service_key)
        print_seat_map(service_key, seats)
        
        print_header("\n🎯 Seat Management Options:")
        print("1) Mark single seat as unavailable")
        print("2) Reset single seat to available")
        print("3) Bulk mark seats as unavailable")
        print("4) Bulk reset seats to available")
        print("5) Reset ALL seats to available")
        print("B) Back to previous menu")
        
        choice = input("Select option (or 'B' to go back): ").strip().upper()
        
        if choice == "B":
            return
            
        elif choice == "1":
            # Mark single seat as unavailable
            raw = input("Enter seat ID to mark unavailable (or 'B' to go back): ").strip().upper()
            if raw == "B":
                continue
                
            seat_id = normalize_seat_id_input(raw)
            if seat_id not in seats:
                print_error("Invalid seat ID.")
                continue
                
            seats[seat_id] = {
                "Status": "Unavailable", "Name": "", "Timestamp": now_str(), "TicketType": "", 
                "BasePrice": "", "FinalPrice": "", "Contact": "", "Address": "", 
                "IDType": "", "IDNumber": "", "VerifiedAt": ""
            }
            save_seats(service_key, seats)
            save_booking_history(service_key, seat_id, "SEAT_UNAVAILABLE", "Marked as unavailable")
            print_success(f"Seat {seat_id} marked Unavailable.")
            
        elif choice == "2":
            # Reset single seat to available
            raw = input("Enter seat ID to reset to available (or 'B' to go back): ").strip().upper()
            if raw == "B":
                continue
                
            seat_id = normalize_seat_id_input(raw)
            if seat_id not in seats:
                print_error("Invalid seat ID.")
                continue
                
            seats[seat_id] = {
                "Status": "Available", "Name": "", "Timestamp": now_str(), "TicketType": "", 
                "BasePrice": "", "FinalPrice": "", "Contact": "", "Address": "", 
                "IDType": "", "IDNumber": "", "VerifiedAt": ""
            }
            save_seats(service_key, seats)
            save_booking_history(service_key, seat_id, "SEAT_RESET", "Reset to available")
            print_success(f"Seat {seat_id} reset to Available.")
            
        elif choice == "3":
            # Bulk mark seats as unavailable
            raw = input("Enter seat IDs to mark unavailable (comma-separated, e.g. 1A,1B,1C, or 'B' to go back): ").strip().upper()
            if raw == "B":
                continue
            if not raw:
                print_warning("No seats entered.")
                continue
                
            seat_ids = [normalize_seat_id_input(x) for x in raw.split(",") if x.strip()]
            invalid_seats = [s for s in seat_ids if s not in seats]
            
            if invalid_seats:
                print_error(f"These seat IDs are invalid: {', '.join(invalid_seats)}")
                continue
                
            # Show confirmation
            print_warning(f"Mark {len(seat_ids)} seats as unavailable: {', '.join(seat_ids)}")
            confirm = input(f"{Colors.YELLOW}Confirm bulk mark as unavailable? (Y to confirm, any other key to cancel): {Colors.END}").strip().upper()
            
            if confirm == "Y":
                marked_count = 0
                for seat_id in seat_ids:
                    seats[seat_id] = {
                        "Status": "Unavailable", "Name": "", "Timestamp": now_str(), "TicketType": "", 
                        "BasePrice": "", "FinalPrice": "", "Contact": "", "Address": "", 
                        "IDType": "", "IDNumber": "", "VerifiedAt": ""
                    }
                    save_booking_history(service_key, seat_id, "BULK_UNAVAILABLE", "Bulk marked as unavailable")
                    marked_count += 1
                    
                save_seats(service_key, seats)
                print_success(f"Bulk operation completed. {marked_count} seats marked as unavailable.")
            else:
                print_info("Bulk operation cancelled.")
                
        elif choice == "4":
            # Bulk reset seats to available
            raw = input("Enter seat IDs to reset to available (comma-separated, e.g. 1A,1B,1C, or 'B' to go back): ").strip().upper()
            if raw == "B":
                continue
            if not raw:
                print_warning("No seats entered.")
                continue
                
            seat_ids = [normalize_seat_id_input(x) for x in raw.split(",") if x.strip()]
            invalid_seats = [s for s in seat_ids if s not in seats]
            
            if invalid_seats:
                print_error(f"These seat IDs are invalid: {', '.join(invalid_seats)}")
                continue
                
            # Show confirmation
            print_warning(f"Reset {len(seat_ids)} seats to available: {', '.join(seat_ids)}")
            confirm = input(f"{Colors.YELLOW}Confirm bulk reset to available? (Y to confirm, any other key to cancel): {Colors.END}").strip().upper()
            
            if confirm == "Y":
                reset_count = 0
                for seat_id in seat_ids:
                    seats[seat_id] = {
                        "Status": "Available", "Name": "", "Timestamp": now_str(), "TicketType": "", 
                        "BasePrice": "", "FinalPrice": "", "Contact": "", "Address": "", 
                        "IDType": "", "IDNumber": "", "VerifiedAt": ""
                    }
                    save_booking_history(service_key, seat_id, "BULK_RESET", "Bulk reset to available")
                    reset_count += 1
                    
                save_seats(service_key, seats)
                print_success(f"Bulk operation completed. {reset_count} seats reset to available.")
            else:
                print_info("Bulk operation cancelled.")
                
        elif choice == "5":
            # Reset ALL seats to available
            print_error("🚨 DANGER ZONE: Reset ALL seats to available")
            print_warning("This will cancel ALL bookings and reset EVERY seat to available status!")
            print_warning("This action cannot be undone!")
            
            total_seats = len(seats)
            taken_seats = sum(1 for info in seats.values() if info["Status"] == "Taken")
            unavailable_seats = sum(1 for info in seats.values() if info["Status"] == "Unavailable")
            
            print(f"\n📊 Current Status:")
            print(f"Total seats: {total_seats}")
            print(f"Taken seats: {taken_seats}")
            print(f"Unavailable seats: {unavailable_seats}")
            print(f"Seats that will be reset: {taken_seats + unavailable_seats}")
            
            # Double confirmation
            confirm1 = input(f"{Colors.RED}Type 'RESET ALL' to confirm this destructive operation: {Colors.END}").strip().upper()
            if confirm1 != "RESET ALL":
                print_info("Reset ALL operation cancelled.")
                continue
                
            confirm2 = input(f"{Colors.RED}Are you ABSOLUTELY sure? This will delete ALL bookings! Type 'YES' to continue: {Colors.END}").strip().upper()
            if confirm2 != "YES":
                print_info("Reset ALL operation cancelled.")
                continue
                
            # Perform reset
            reset_count = 0
            for seat_id in seats:
                if seats[seat_id]["Status"] in ["Taken", "Unavailable"]:
                    seats[seat_id] = {
                        "Status": "Available", "Name": "", "Timestamp": now_str(), "TicketType": "", 
                        "BasePrice": "", "FinalPrice": "", "Contact": "", "Address": "", 
                        "IDType": "", "IDNumber": "", "VerifiedAt": ""
                    }
                    save_booking_history(service_key, seat_id, "FULL_RESET", "All seats reset to available")
                    reset_count += 1
                    
            save_seats(service_key, seats)
            print_success(f"🚀 Full reset completed! {reset_count} seats reset to available status.")
            print_warning("All bookings have been cancelled and all seats are now available.")
            
        else:
            print_error("Invalid option. Please try again.")
        
        # Ask if user wants to manage more seats
        again = input(f"\n{Colors.YELLOW}Manage more seats? (Y to continue, any other key to go back): {Colors.END}").strip().upper()
        if again != "Y":
            break

# ------------------------
# Enhanced Main Menu
# ------------------------

def service_menu(service_key, service_name):
    while True:
        print_header(f"\n== {service_name} Menu ==")
        print("1) View seat layout")
        print("2) Reserve seat")
        print("3) Enhanced Bulk Reserve")  # ENHANCED OPTION
        print("4) Cancel reservation")
        print("5) Update seat booking")
        print("6) View booking report")
        print("7) Mark seat Unavailable / Reset seat")
        print("8) View client ticket")
        print("9) Bulk reserve (Legacy)")
        print("BACK) Back to main menu")
        
        choice = get_user_choice("Choose option", ["1", "2", "3", "4", "5", "6", "7", "8", "9", "BACK"])

        if choice == "BACK":
            break
        if choice == "1":
            seats = load_seats(service_key)
            print_seat_map(service_key, seats)
        elif choice == "2":
            reserve_seat(service_key)
        elif choice == "3":  # ENHANCED BULK RESERVE
            bulk_reserve_enhanced(service_key)
        elif choice == "4":
            cancel_reservation(service_key)
        elif choice == "5":
            update_reservation(service_key)
        elif choice == "6":
            view_report(service_key)
        elif choice == "7":
            set_unavailable(service_key)
        elif choice == "8":
            show_ticket(service_key)
        elif choice == "9":
            bulk_reserve(service_key)  # Legacy bulk reserve
        else:
            print_error("Invalid option.")

def show_system_reports():
    while True:
        print_header("\n📊 System Reports")
        print("1) Cinema Report")
        print("2) Bus Report")
        print("3) Airplane Report")
        print("4) Combined Revenue Report")
        print("B) Back to main menu")
        
        choice = input("Select report (or 'B' to go back): ").strip().upper()
        
        if choice == "B":
            break
            
        if choice == "1":
            view_report("C")
        elif choice == "2":
            view_report("B")
        elif choice == "3":
            view_report("A")
        elif choice == "4":
            show_combined_revenue()
        else:
            print_error("Invalid option.")

def show_combined_revenue():
    total_revenue = 0
    print_header("\n💰 Combined Revenue Report")
    print("=" * 60)
    
    for service_key in DATA_FILES:
        service_name = {"C": "Cinema", "B": "Bus", "A": "Airplane"}.get(service_key)
        seats = load_seats(service_key)
        service_revenue = 0
        service_bookings = 0
        
        for info in seats.values():
            if info["Status"] == "Taken" and info.get("FinalPrice"):
                try:
                    service_revenue += float(info["FinalPrice"])
                    service_bookings += 1
                except ValueError:
                    pass
        
        total_revenue += service_revenue
        print(f"{service_name:<10}: {service_bookings:>3} bookings, {pretty_price(service_revenue)}")
    
    print("-" * 60)
    print(f"{Colors.BOLD}Total Revenue:{Colors.END} {pretty_price(total_revenue)}")
    print("=" * 60)
    input("Press Enter to continue...")

def enhanced_main_menu():
    for k in DATA_FILES:
        ensure_csv(k)
    
    # Auto-check for expired bookings on startup
    print_info("Checking for expired bookings...")
    expired_total = 0
    for service_key in DATA_FILES:
        expired = check_booking_timeout(service_key)
        expired_total += expired
    
    if expired_total > 0:
        print_warning(f"Auto-cancelled {expired_total} expired bookings on startup.")
    
    while True:
        # Show quick stats
        total_bookings = 0
        for service_key in DATA_FILES:
            seats = load_seats(service_key)
            taken_seats = sum(1 for info in seats.values() if info["Status"] == "Taken")
            total_bookings += taken_seats
        
        print_header("\n" + "="*50)
        print_header("🎟️ ENHANCED TICKETING SYSTEM - DASHBOARD")
        print_header("="*50)
        print(f"{Colors.BLUE}📈 Active Bookings: {total_bookings}{Colors.END}")
        print_header("="*50)
        print("1) 🎥 Cinema Booking")
        print("2) 🚌 Bus Booking") 
        print("3) ✈️ Airplane Booking")
        print("4) 📊 System Reports")
        print("5) ⚙️ System Settings")
        print("BACK) Exit System")
        print_header("="*50)
        
        choice = get_user_choice("Select option", ["1", "2", "3", "4", "5", "BACK"])
        
        if choice == "1":
            service_menu("C", "Cinema")
        elif choice == "2":
            service_menu("B", "Bus")
        elif choice == "3":
            service_menu("A", "Airplane")
        elif choice == "4":
            show_system_reports()
        elif choice == "5":
            system_settings()
        elif choice == "BACK":
            print_success("Goodbye!")
            break
        else:
            print_error("Invalid input.")

if __name__ == "__main__":
    enhanced_main_menu()