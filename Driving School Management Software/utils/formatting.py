import re
import tkinter as tk

def format_phone_number(phone):
    """
    Format phone number for display.
    Adds spaces and formatting for better readability.
    """
    if not phone:
        return phone
    
    # Remove all non-digit characters
    digits = re.sub(r'[^\d]', '', phone)
    
    if len(digits) == 10:
        return f"{digits[:2]} {digits[2:4]} {digits[4:6]} {digits[6:8]} {digits[8:10]}"
    elif len(digits) == 11:
        return f"{digits[:1]} {digits[1:3]} {digits[3:5]} {digits[5:7]} {digits[7:9]} {digits[9:11]}"
    else:
        return phone

def format_date_input(entry_widget):
    """
    Format date input as user types (DD/MM/YYYY).
    """
    def on_key_release(event):
        # Get current content
        content = entry_widget.get()
        
        # Remove any non-digit characters
        digits = re.sub(r'[^\d]', '', content)
        
        # Format as DD/MM/YYYY
        if len(digits) <= 2:
            formatted = digits
        elif len(digits) <= 4:
            formatted = f"{digits[:2]}/{digits[2:]}"
        elif len(digits) <= 8:
            formatted = f"{digits[:2]}/{digits[2:4]}/{digits[4:]}"
        else:
            formatted = f"{digits[:2]}/{digits[2:4]}/{digits[4:8]}"
        
        # Update entry if different
        if formatted != content:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, formatted)
    
    entry_widget.bind('<KeyRelease>', on_key_release)
