class SearchClientFrame(tk.Frame):
    def __init__(self, master, show_client_profile, on_back):
        super().__init__(master)
        tk.Label(self, text='Rechercher un candidat', font=('Arial', 28, 'bold')).pack(pady=20)
        form = tk.Frame(self)
        form.pack(pady=5)
        tk.Label(form, text='Nom et prénom ou Téléphone:', font=('Arial', 18)).grid(row=0, column=0, sticky='e')
        self.query_entry = tk.Entry(form, width=30, font=('Arial', 18))
        self.query_entry.grid(row=0, column=1, padx=5)
        tk.Button(form, text='Rechercher', font=('Arial', 16), width=14, command=self.search).grid(row=0, column=2, padx=5)
        self.main_container = tk.Frame(self)
        self.main_container.pack(expand=True, fill='both')
        self.canvas = tk.Canvas(self.main_container, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_container, orient='vertical', command=self.canvas.yview)
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
        self.cards_container = tk.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.cards_container, anchor='n')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.cards_container.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', self._center_cards)
        tk.Button(self, text='Retour', font=('Arial', 16), width=14, command=on_back).pack(anchor='nw', padx=10, pady=10)
        self.show_client_profile = show_client_profile
        self.bind_all('<MouseWheel>', self._on_mousewheel)

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
        
        if hasattr(self, 'main_container'):
            self.main_container.destroy()
            self.main_container = None
        
        # Clear other references
        if hasattr(self, 'query_entry'):
            self.query_entry = None
        
        super().destroy()

    def search(self):
        query = self.query_entry.get().strip()
        
        # Validate search query
        if not query:
            show_validation_error('Recherche vide', 'Veuillez entrer un nom ou numéro de téléphone pour rechercher.')
            self.query_entry.focus_set()
            return
        
        # Validate minimum search length
        if len(query.strip()) < 2:
            show_validation_error('Recherche trop courte', 'La recherche doit contenir au moins 2 caractères.')
            self.query_entry.focus_set()
            return
        
        # Clear previous results
        for widget in self.cards_container.winfo_children():
            widget.destroy()
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            search_pattern = f'%{query}%'
            c.execute("SELECT id, name, phone, license_type, sessions_done, total_paid FROM clients WHERE name LIKE ? OR phone LIKE ? ORDER BY name", (search_pattern, search_pattern))
            for row in c.fetchall():
                candidate_data = {
                    'name': row[1],
                    'phone': row[2],
                    'license_type': row[3],
                    'additional_info': f"Sessions: {row[4]}",
                    'second_info': f"Total payé: {row[5]:,.2f} DA"
                }
                create_original_candidate_card(
                    self.cards_container, 
                    candidate_data, 
                    action_command=lambda cid=row[0]: self.show_client_profile(cid)
                )
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()


