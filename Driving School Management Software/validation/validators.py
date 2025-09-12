import re
from datetime import datetime, timedelta
from tkinter import messagebox

def validate_phone(phone):
    """
    Validate phone number format.
    Phone should be 10+ digits, can contain +, spaces, and hyphens.
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove common separators and check if remaining characters are digits
    cleaned = phone.strip().replace('+', '').replace(' ', '').replace('-', '').replace('.', '')
    return len(cleaned) >= 10 and cleaned.isdigit()

def validate_date(date_str):
    """
    Validate date format DD/MM/YYYY.
    Returns True if valid, False otherwise.
    """
    if not date_str or not isinstance(date_str, str):
        return False
    
    try:
        # Check if the date string matches the expected format
        if not re.match(r'^\d{2}/\d{2}/\d{4}$', date_str.strip()):
            return False
        
        # Parse the date to ensure it's actually valid
        parsed_date = datetime.strptime(date_str.strip(), '%d/%m/%Y')
        
        # Check if date is not in the future (for birth dates and join dates)
        if parsed_date.date() > datetime.now().date():
            return False
            
        return True
    except ValueError:
        return False

def validate_examen_date(date_str):
    """
    Validate examen date format DD/MM/YYYY.
    Examen dates can be in the future.
    """
    if not date_str or not isinstance(date_str, str):
        return False
    
    try:
        # Check if the date string matches the expected format
        if not re.match(r'^\d{2}/\d{2}/\d{4}$', date_str.strip()):
            return False
        
        # Parse the date to ensure it's actually valid
        parsed_date = datetime.strptime(date_str.strip(), '%d/%m/%Y')
        
        # Examen dates can be in the future, but not too far in the past
        if parsed_date.date() < datetime.now().date() - timedelta(days=365):
            return False
            
        return True
    except ValueError:
        return False

def validate_monetary_amount(amount_str):
    """
    Validate monetary amount.
    Amount should be a positive number.
    """
    if not amount_str or not isinstance(amount_str, str):
        return False
    
    try:
        amount = float(amount_str.strip())
        return amount > 0
    except ValueError:
        return False

def validate_name(name):
    """
    Validate name format.
    Name should contain only letters, spaces, hyphens, and apostrophes.
    Minimum 2 characters, maximum 50 characters.
    """
    if not name or not isinstance(name, str):
        return False
    
    name = name.strip()
    if len(name) < 2 or len(name) > 50:
        return False
    
    # Allow letters, spaces, hyphens, apostrophes, and common accented characters
    # This regex allows French/Arabic names with proper characters
    pattern = r'^[a-zA-ZÀ-ÿ\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\s\'-]+$'
    return bool(re.match(pattern, name))

def validate_license_type(license_type):
    """
    Validate license type.
    Should be one of the common license types.
    """
    if not license_type or not isinstance(license_type, str):
        return False
    
    # Allow common license types including combinations
    valid_types = [
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
        'A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2', 'E1', 'E2', 'F1', 'F2', 'G1', 'G2', 'H1', 'H2',
        'AM', 'A1M', 'A2M', 'BM', 'CM', 'DM', 'EM', 'FM', 'GM', 'HM'
    ]
    return license_type.strip().upper() in valid_types

def validate_address(address):
    """
    Validate address format.
    Address should be reasonable length and contain valid characters.
    """
    if not address or not isinstance(address, str):
        return False
    
    address = address.strip()
    if len(address) < 5 or len(address) > 200:
        return False
    
    # Allow letters, numbers, spaces, hyphens, commas, periods, and common punctuation
    pattern = r'^[a-zA-ZÀ-ÿ\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF0-9\s\'-.,;:()]+$'
    return bool(re.match(pattern, address))

def validate_place_of_birth(place):
    """
    Validate place of birth.
    Similar to name validation but for places.
    """
    if not place or not isinstance(place, str):
        return False
    
    place = place.strip()
    if len(place) < 2 or len(place) > 100:
        return False
    
    # Allow letters, spaces, hyphens, and apostrophes
    pattern = r'^[a-zA-ZÀ-ÿ\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\s\'-]+$'
    return bool(re.match(pattern, place))

def validate_gender(gender):
    """
    Validate gender field.
    Should be either 'Homme' or 'Femme'.
    """
    if not gender or not isinstance(gender, str):
        return False
    
    gender = gender.strip()
    valid_genders = ['Homme', 'Femme', 'homme', 'femme', 'M', 'F', 'm', 'f']
    return gender in valid_genders

def validate_blood_type(blood_type):
    """
    Validate blood type field.
    Should be one of the standard blood types: A+, A-, B+, B-, AB+, AB-, O+, O-
    """
    if not blood_type or not isinstance(blood_type, str):
        return False
    
    blood_type = blood_type.strip()
    valid_blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 
                        'a+', 'a-', 'b+', 'b-', 'ab+', 'ab-', 'o+', 'o-']
    return blood_type in valid_blood_types

def show_validation_error(title, message):
    """
    Show a standardized validation error message.
    """
    messagebox.showerror(title, message)

def validate_session_date(date_str):
    """
    Validate session date format DD/MM/YYYY.
    Session dates should not be in the future.
    """
    if not date_str or not isinstance(date_str, str):
        return False
    
    try:
        # Check if the date string matches the expected format
        if not re.match(r'^\d{2}/\d{2}/\d{4}$', date_str.strip()):
            return False
        
        # Parse the date to ensure it's actually valid
        parsed_date = datetime.strptime(date_str.strip(), '%d/%m/%Y')
        
        # Session dates should not be in the future
        if parsed_date.date() > datetime.now().date():
            return False
            
        return True
    except ValueError:
        return False

def validate_payment_date(date_str):
    """
    Validate payment date format DD/MM/YYYY.
    Payment dates should not be in the future.
    """
    if not date_str or not isinstance(date_str, str):
        return False
    
    try:
        # Check if the date string matches the expected format
        if not re.match(r'^\d{2}/\d{2}/\d{4}$', date_str.strip()):
            return False
        
        # Parse the date to ensure it's actually valid
        parsed_date = datetime.strptime(date_str.strip(), '%d/%m/%Y')
        
        # Payment dates should not be in the future
        if parsed_date.date() > datetime.now().date():
            return False
            
        return True
    except ValueError:
        return False
