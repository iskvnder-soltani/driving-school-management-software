class AddTestGroupFrame(tk.Frame):
    def __init__(self, master, on_save, on_cancel):
        super().__init__(master)
        container = tk.Frame(self)
        container.pack(expand=True)
        tk.Label(container, text='Ajouter un nouveau groupe', font=('Arial', 28, 'bold')).pack(pady=20)
        card = tk.Frame(container, bg='white', bd=3, relief='groove')
        card.pack(padx=40, pady=20)
        form = tk.Frame(card, bg='white')
        form.pack(pady=10, padx=30)
        tk.Label(form, text='Date de l\'examen :', font=('Arial', 18), bg='white').grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.date_entry = tk.Entry(form, font=('Arial', 18), width=12)
        self.date_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))
        
        # Add date formatting to the date entry
        format_date_input(self.date_entry)
        tk.Label(form, text='Type de permis :', font=('Arial', 18), bg='white').grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.license_entry = tk.Entry(form, font=('Arial', 18), width=16)
        self.license_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        tk.Label(form, text='Centre d\'examen :', font=('Arial', 18), bg='white').grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.centre_entry = tk.Entry(form, font=('Arial', 18), width=20)
        self.centre_entry.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        # Buttons
        btn_frame = tk.Frame(card, bg='white')
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text='Créer le groupe', font=('Arial', 16), command=self.save_group).pack(side='left', padx=10)
        tk.Button(btn_frame, text='Annuler', font=('Arial', 16), command=on_cancel).pack(side='left', padx=10)
        self.on_save = on_save
        self.on_cancel = on_cancel
    def save_group(self):
        # Get and validate input fields
        date = self.date_entry.get().strip()
        license_type = self.license_entry.get().strip()
        centre_examen = self.centre_entry.get().strip()
        
        # Validate all required fields are present
        if not date or not license_type or not centre_examen:
            show_validation_error('Champs requis', 'Veuillez saisir la date du test, le type de permis et le centre d\'examen.')
            return
        
        # Validate date format (test dates can be in the future)
        if not validate_examen_date(date):
            show_validation_error('Date invalide', 
                'La date doit être au format DD/MM/YYYY et ne peut pas être plus d\'un an dans le passé.')
            self.date_entry.focus_set()
            return
        
        # Validate license type
        if not validate_license_type(license_type):
            show_validation_error('Type de permis invalide', 
                'Le type de permis doit être une lettre valide (A-Z).')
            self.license_entry.focus_set()
            return
        
        # All validation passed, proceed with saving
        self.on_save(date, license_type, centre_examen)

