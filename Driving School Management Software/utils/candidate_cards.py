import tkinter as tk

def create_candidate_card(parent, candidate_data, action_button=None, action_command=None, action_text="Voir le profil"):
    """
    Create a consistent candidate card with standardized styling and layout.

    Args:
        parent: Parent widget to place the card in
        candidate_data: Dictionary containing candidate information
        action_button: Optional custom button widget
        action_command: Command to execute when action button is clicked
        action_text: Text for the action button (default: "Voir le profil")

    Returns:
        tk.Frame: The created card widget
    """
    # Create card with consistent styling matching main candidates list
    card = tk.Frame(parent, bd=2, relief='groove', padx=15, pady=10, bg='#f7f7f7')
    card.pack(fill='x', pady=10, padx=20)
    
    # No hover effects - removed for consistency
    
    # Create action button (either custom or default)
    if action_button:
        btn = action_button
        # Set the parent for the custom button
        btn.configure(master=card)
    else:
        btn = tk.Button(card, text=action_text, font=('Arial', 16), width=16, command=action_command)
    
    # Position button on the left, spanning multiple rows
    btn.grid(row=0, column=0, rowspan=4, padx=(0, 20), sticky='w')
    
    # Add candidate information in a 4-row grid layout
    # Row 0: Name (bold, large font)
    name_label = tk.Label(card, text=candidate_data.get('name', ''), font=('Arial', 20, 'bold'), bg='#f7f7f7')
    name_label.grid(row=0, column=1, sticky='w')
    
    # Row 1: License Type
    license_type = candidate_data.get('license_type', '')
    if license_type:
        license_label = tk.Label(card, text=f"Type de permis: {license_type}", font=('Arial', 16), bg='#f7f7f7')
        license_label.grid(row=1, column=1, sticky='w')
    
    # Row 2: Date of birth
    additional_info = candidate_data.get('additional_info', '')
    if additional_info:
        additional_label = tk.Label(card, text=additional_info, font=('Arial', 16), bg='#f7f7f7')
        additional_label.grid(row=2, column=1, sticky='w')
    
    # Row 3: Available exam types
    second_info = candidate_data.get('second_info', '')
    if second_info:
        second_label = tk.Label(card, text=second_info, font=('Arial', 16), bg='#f7f7f7')
        second_label.grid(row=3, column=1, sticky='w')
    
    # No hover effects on labels - removed for consistency
    
    return card

def create_original_candidate_card(parent, candidate_data, action_button=None, action_command=None, action_text="Voir le profil"):
    """
    Create the original candidate card format with phone number and side-by-side layout.
    
    Args:
        parent: Parent widget to place the card in
        candidate_data: Dictionary containing candidate information
        action_button: Optional custom button widget
        action_command: Command to execute when action button is clicked
        action_text: Text for the action button (default: "Voir le profil")
    
    Returns:
        tk.Frame: The created card widget
    """
    # Create card with consistent styling matching main candidates list
    card = tk.Frame(parent, bd=2, relief='groove', padx=20, pady=10, bg='#f7f7f7')
    card.pack(fill='x', pady=10, padx=10)
    
    # Create action button (either custom or default)
    if action_button:
        btn = action_button
        # Set the parent for the custom button
        btn.configure(master=card)
    else:
        btn = tk.Button(card, text=action_text, font=('Arial', 16), width=16, command=action_command)
    
    # Position button on the left, spanning multiple rows
    btn.grid(row=0, column=0, rowspan=4, padx=(0, 20), sticky='w')
    
    # Add candidate information in a 3-row grid layout (original format)
    # Row 0: Name (bold, large font)
    name_label = tk.Label(card, text=candidate_data.get('name', ''), font=('Arial', 20, 'bold'), bg='#f7f7f7')
    name_label.grid(row=0, column=1, sticky='w')
    
    # Row 1: Phone and License Type
    phone_label = tk.Label(card, text=f"Téléphone: {candidate_data.get('phone', '')}", font=('Arial', 16), bg='#f7f7f7')
    phone_label.grid(row=1, column=1, sticky='w')
    
    # Add license type if available
    license_type = candidate_data.get('license_type', '')
    if license_type:
        license_label = tk.Label(card, text=f"Type de permis: {license_type}", font=('Arial', 16), bg='#f7f7f7')
        license_label.grid(row=1, column=2, sticky='w', padx=20)
    
    # Row 2: Additional info (sessions, payments, or other relevant data)
    additional_info = candidate_data.get('additional_info', '')
    if additional_info:
        additional_label = tk.Label(card, text=additional_info, font=('Arial', 16), bg='#f7f7f7')
        additional_label.grid(row=2, column=1, sticky='w')
    
    # Add second additional info if available
    second_info = candidate_data.get('second_info', '')
    if second_info:
        second_label = tk.Label(card, text=second_info, font=('Arial', 16), bg='#f7f7f7')
        second_label.grid(row=2, column=2, sticky='w', padx=20)
    
    return card
