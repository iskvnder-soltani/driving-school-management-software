class IncompletePaymentFrame(tk.Frame):
    def __init__(self, master, show_client_profile, on_back):
        super().__init__(master)
        tk.Label(self, text='Paiement incomplet', font=('Arial', 28, 'bold')).pack(pady=20)
        main_container = tk.Frame(self)
        main_container.pack(expand=True, fill='both')
        self.canvas = tk.Canvas(main_container, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(main_container, orient='vertical', command=self.canvas.yview)
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
        self.cards_container = tk.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.cards_container, anchor='n')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.cards_container.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', self._center_cards)
        self.bind_all('<MouseWheel>', self._on_mousewheel)
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('SELECT id, name, phone, license_type, total_paid, total_amount_required, checked_out FROM clients WHERE total_paid < total_amount_required ORDER BY name')
            for row in c.fetchall():
                candidate_data = {
                    'name': row[1],
                    'phone': row[2],
                    'additional_info': f"Payé: {row[4]:,.2f} DA / {row[5]:,.2f} DA"
                }
                # Check if candidate is archived
                is_archived = bool(row[6])  # checked_out column
                create_original_candidate_card(
                    self.cards_container, 
                    candidate_data, 
                    action_command=lambda cid=row[0], archived=is_archived: show_client_profile(cid, checked_out=archived, return_to="incomplete_payments"),
                    action_text="Voir"
                )
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
        tk.Button(self, text='Retour', font=('Arial', 16), width=20, command=on_back).pack(side='bottom', pady=30, anchor='center')

    def _center_cards(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        canvas_width = event.width
        # Check if cards_container exists before trying to access it
        if not hasattr(self, 'cards_container') or self.cards_container is None:
            return
        self.cards_container.update_idletasks()
        cards_width = self.cards_container.winfo_reqwidth()
        x = max((canvas_width - cards_width) // 2, 0)
        self.canvas.coords(self.window_id, x, 0)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), 'units')

    def destroy(self):
        """Clean up resources to prevent memory leaks"""
        # Unbind global event handlers
        if hasattr(self, 'bind_all'):
            self.unbind_all('<MouseWheel>')
        
        # Clean up canvas and scrollbar
        if hasattr(self, 'canvas'):
            if hasattr(self, 'window_id'):
                self.canvas.delete(self.window_id)
            self.canvas.delete("all")
            self.canvas.destroy()
            self.canvas = None
        
        if hasattr(self, 'scrollbar'):
            self.scrollbar.destroy()
            self.scrollbar = None
        
        # Clean up container frames
        if hasattr(self, 'cards_container'):
            self.cards_container.destroy()
            self.cards_container = None
        
        super().destroy()


