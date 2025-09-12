class AddPaymentFrame(tk.Frame):
    def __init__(self, master, client_id, on_save, on_cancel):
        super().__init__(master)
        self.update_idletasks()
        self.client_id = client_id
        container = tk.Frame(self)
        container.pack(expand=True, fill='both')
        # Center the form in the container using grid
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(2, weight=1)
        form = tk.Frame(container)
        form.grid(row=1, column=1, sticky='nsew')
        tk.Label(form, text='Ajouter un paiement', font=('Arial', 28, 'bold')).grid(row=0, column=0, columnspan=3, pady=(40, 20), sticky='n')
        tk.Label(form, text='Montant:').grid(row=1, column=0, sticky='e')
        self.amount_entry = tk.Entry(form, width=20)
        self.amount_entry.grid(row=1, column=1, padx=5)
        tk.Label(form, text='DA').grid(row=1, column=2, sticky='w')
        btn_frame = tk.Frame(form)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=10)
        tk.Button(btn_frame, text='Confirmer le paiement', font=('Arial', 16), width=24, command=self.save_payment).pack(side='left', padx=10, pady=10)
        tk.Button(btn_frame, text='Annuler', font=('Arial', 16), width=14, command=on_cancel).pack(side='left', padx=10, pady=10)
        self.on_save = on_save
        self.update_idletasks()
    def save_payment(self):
        # Get and validate amount
        amount_str = self.amount_entry.get().strip()
        
        # Validate amount is present
        if not amount_str:
            show_validation_error('Montant requis', 'Le montant est obligatoire.')
            self.amount_entry.focus_set()
            return
        
        # Validate monetary amount format
        if not validate_monetary_amount(amount_str):
            show_validation_error('Montant invalide', 'Le montant doit être un nombre positif.')
            self.amount_entry.focus_set()
            return
        
        try:
            amount = float(amount_str)
        except ValueError:
            show_validation_error('Erreur de conversion', 'Le montant doit être un nombre valide.')
            self.amount_entry.focus_set()
            return
        
        # Prevent overpayment
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('SELECT total_paid, total_amount_required FROM clients WHERE id=?', (self.client_id,))
            row = c.fetchone()
            if row:
                total_paid, total_required = row
                if amount > (total_required - total_paid):
                    show_validation_error('Montant trop élevé', 
                        f'Le montant dépasse le montant restant à payer ({total_required - total_paid:,.2f} DA).')
                    self.amount_entry.focus_set()
                    return
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
        
        # All validation passed, proceed with saving
        self.on_save(self.client_id, amount)
        self.update_idletasks()

