class AddClientFrame(tk.Frame):
    def __init__(self, master, on_save, on_cancel):
        super().__init__(master)
        self.update_idletasks()
        container = tk.Frame(self)
        container.pack(expand=True, fill='both')
        # Center the form in the container using grid
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(2, weight=1)
        form = tk.Frame(container)
        form.grid(row=1, column=1, sticky='nsew')
        tk.Label(form, text='Ajouter un nouveau candidat', font=('Arial', 28, 'bold')).grid(row=0, column=0, columnspan=2, pady=(40, 20), sticky='n')
        labels = ['Nom et prénom:', 'Nom du père:', 'Genre:', 'Groupe sanguin:', 'Date de naissance:', 'Lieu de naissance:', 'Téléphone:', 'Adresse:', 'Type de permis:', 'Montant total requis:']
        placeholders = ['Nom et prénom', 'Nom du père', 'Homme/Femme', 'A+, A-, B+, B-, AB+, AB-, O+, O-', 'DD/MM/YYYY', 'Ville, Pays', 'Numéro de téléphone', 'Adresse complète', 'A, B, C...', 'Montant en DA']
        self.entries = []
        for i, label in enumerate(labels):
            tk.Label(form, text=label, font=('Arial', 22, 'bold'), anchor='w').grid(row=i+1, column=0, sticky='w', pady=10, padx=(0, 10))
            entry = tk.Entry(form, font=('Arial', 22), width=24)
            entry.grid(row=i+1, column=1, sticky='w', pady=10)
            
            # Add placeholder text
            entry.insert(0, placeholders[i])
            entry.config(fg='gray')
            
            # Bind focus events for placeholder behavior
            entry.bind('<FocusIn>', lambda e, entry=entry, placeholder=placeholders[i]: self.on_entry_focus_in(entry, placeholder))
            entry.bind('<FocusOut>', lambda e, entry=entry, placeholder=placeholders[i]: self.on_entry_focus_out(entry, placeholder))
            
            # Add date formatting for date fields
            if i == 4:  # Date of birth field (index 4 after adding father's name, gender, and blood type)
                format_date_input(entry)
            
            # Add autocomplete for gender field
            if i == 2:  # Gender field (index 2)
                self.add_gender_autocomplete(entry)
            
            self.entries.append(entry)
        btn_frame = tk.Frame(form)
        btn_frame.grid(row=len(labels)+1, column=0, columnspan=2, pady=40)
        tk.Button(btn_frame, text='Enregistrer le candidat', font=('Arial', 16), width=24, command=self.save_client).pack(side='left', padx=10, pady=10)
        tk.Button(btn_frame, text='Annuler', font=('Arial', 16), width=14, command=on_cancel).pack(side='left', padx=10, pady=10)
        self.on_save = on_save
        self.update_idletasks()

    def on_entry_focus_in(self, entry, placeholder):
        """Handle focus in event for placeholder text"""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg='black')
    
    def on_entry_focus_out(self, entry, placeholder):
        """Handle focus out event for placeholder text"""
        if not entry.get().strip():
            entry.insert(0, placeholder)
            entry.config(fg='gray')
    
    def add_gender_autocomplete(self, entry):
        """Add autocomplete functionality for gender field"""
        def on_key_release(event):
            current_text = entry.get().lower()
            
            # Clear any existing autocomplete
            if hasattr(entry, '_autocomplete_text'):
                entry._autocomplete_text = ""
            
            # Check for autocomplete suggestions
            if current_text == 'h':
                entry._autocomplete_text = "Homme"
                entry.insert(tk.END, "omme")
                entry.icursor(1)  # Position cursor after 'H'
                entry.selection_range(1, tk.END)  # Select the autocompleted part
            elif current_text == 'f':
                entry._autocomplete_text = "Femme"
                entry.insert(tk.END, "emme")
                entry.icursor(1)  # Position cursor after 'F'
                entry.selection_range(1, tk.END)  # Select the autocompleted part
        
        def on_key_press(event):
            # If user presses Tab or Right arrow, accept the autocomplete
            if event.keysym in ['Tab', 'Right']:
                if hasattr(entry, '_autocomplete_text') and entry._autocomplete_text:
                    # Clear selection and move cursor to end
                    entry.selection_clear()
                    entry.icursor(tk.END)
                    return 'break'  # Prevent default behavior
            
            # If user presses Escape, clear autocomplete
            elif event.keysym == 'Escape':
                if hasattr(entry, '_autocomplete_text') and entry._autocomplete_text:
                    # Clear the autocompleted part
                    current_text = entry.get()
                    if current_text.lower().startswith('m') and len(current_text) > 1:
                        entry.delete(1, tk.END)
                    elif current_text.lower().startswith('f') and len(current_text) > 1:
                        entry.delete(1, tk.END)
                    entry._autocomplete_text = ""
                    return 'break'
            
            # If user types anything else, clear autocomplete
            elif event.keysym not in ['BackSpace', 'Delete', 'Left', 'Right', 'Up', 'Down', 'Home', 'End']:
                if hasattr(entry, '_autocomplete_text'):
                    entry._autocomplete_text = ""
        
        # Bind the events
        entry.bind('<KeyRelease>', on_key_release)
        entry.bind('<KeyPress>', on_key_press)

    def save_client(self):
        # Get and validate all input fields
        name = self.entries[0].get().strip()
        fathers_name = self.entries[1].get().strip()
        gender = self.entries[2].get().strip()
        blood_type = self.entries[3].get().strip()
        date_of_birth = self.entries[4].get().strip()
        place_of_birth = self.entries[5].get().strip()
        phone = self.entries[6].get().strip()
        address = self.entries[7].get().strip()
        license_type = self.entries[8].get().strip()
        total_amount_str = self.entries[9].get().strip()
        
        # Validate all required fields are present
        if not (name and fathers_name and gender and blood_type and phone and address and date_of_birth and place_of_birth and license_type and total_amount_str):
            show_validation_error('Champs requis', 'Tous les champs sont obligatoires.')
            return
        
        # Validate name
        if not validate_name(name):
            show_validation_error('Nom et prénom invalide', 
                'Le nom doit contenir entre 2 et 50 caractères et ne peut contenir que des lettres, espaces, tirets et apostrophes.')
            self.entries[0].focus_set()
            return
        
        # Validate father's name
        if not validate_name(fathers_name):
            show_validation_error('Nom du père invalide', 
                'Le nom du père doit contenir entre 2 et 50 caractères et ne peut contenir que des lettres, espaces, tirets et apostrophes.')
            self.entries[1].focus_set()
            return
        
        # Validate gender
        if not validate_gender(gender):
            show_validation_error('Genre invalide', 
                'Le genre doit être "Homme" ou "Femme".')
            self.entries[2].focus_set()
            return
        
        # Validate date of birth
        if not validate_date(date_of_birth):
            show_validation_error('Date de naissance invalide', 
                'La date doit être au format DD/MM/YYYY et ne peut pas être dans le futur.')
            self.entries[3].focus_set()
            return
        
        # Validate place of birth
        if not validate_place_of_birth(place_of_birth):
            show_validation_error('Lieu de naissance invalide', 
                'Le lieu de naissance doit contenir entre 2 et 100 caractères et ne peut contenir que des lettres, espaces, tirets et apostrophes.')
            self.entries[5].focus_set()
            return
        
        # Validate phone number
        if not validate_phone(phone):
            show_validation_error('Numéro de téléphone invalide', 
                'Le numéro de téléphone doit contenir au moins 10 chiffres.')
            self.entries[6].focus_set()
            return
        
        # Validate address
        if not validate_address(address):
            show_validation_error('Adresse invalide', 
                'L\'adresse doit contenir entre 5 et 200 caractères et ne peut contenir que des caractères valides.')
            self.entries[7].focus_set()
            return
        
        # Validate license type
        if not validate_license_type(license_type):
            show_validation_error('Type de permis invalide', 
                'Le type de permis doit être une lettre valide (A-Z).')
            self.entries[8].focus_set()
            return
        
        # Validate monetary amount
        if not validate_monetary_amount(total_amount_str):
            show_validation_error('Montant invalide', 
                'Le montant total requis doit être un nombre positif.')
            self.entries[9].focus_set()
            return
        
        try:
            total_amount_required = float(total_amount_str)
        except ValueError:
            show_validation_error('Erreur de conversion', 'Le montant total requis doit être un nombre valide.')
            self.entries[9].focus_set()
            return
        
        # All validation passed, proceed with saving
        self.on_save(name, fathers_name, gender, blood_type, phone, address, date_of_birth, place_of_birth, license_type, total_amount_required)
        self.update_idletasks()

