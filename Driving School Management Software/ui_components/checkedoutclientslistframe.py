class CheckedOutClientsListFrame(tk.Frame):
    def __init__(self, master, show_client_profile, on_back):
        super().__init__(master)
        tk.Label(self, text='Candidats archivés', font=('Arial', 28, 'bold')).pack(pady=20)
        search_frame = tk.Frame(self)
        search_frame.pack(pady=5)
        tk.Label(search_frame, text='Nom et prénom ou Téléphone:', font=('Arial', 18)).pack(side='left')
        self.search_entry = tk.Entry(search_frame, font=('Arial', 18), width=24)
        self.search_entry.pack(side='left', padx=5)
        tk.Button(search_frame, text='Rechercher', font=('Arial', 16), width=14, command=self.update_cards).pack(side='left', padx=5)
        tk.Button(search_frame, text='Vider', font=('Arial', 16), width=10, command=self.clear_search).pack(side='left', padx=5)
        tk.Button(search_frame, text='Retour', font=('Arial', 16), width=14, command=on_back).pack(side='left', padx=5)
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
        self.bind_all('<MouseWheel>', self._on_mousewheel)
        self.show_client_profile = show_client_profile
        self.on_back = on_back
        self.update_cards()

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
        if hasattr(self, 'search_entry'):
            self.search_entry = None
        
        super().destroy()

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

    def update_cards(self):
        # Check if cards_container exists before trying to access it
        if not hasattr(self, 'cards_container') or self.cards_container is None:
            return
        for widget in self.cards_container.winfo_children():
            widget.destroy()
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            query = self.search_entry.get().strip()
            if query:
                # Validate search query length
                if len(query) < 2:
                    show_validation_error('Recherche trop courte', 'La recherche doit contenir au moins 2 caractères.')
                    self.search_entry.focus_set()
                    return
                
                search_pattern = f'%{query}%'
                c.execute("SELECT id, name, phone, license_type, sessions_done, total_paid FROM clients WHERE checked_out=1 AND (name LIKE ? OR phone LIKE ?) ORDER BY name", (search_pattern, search_pattern))
            else:
                c.execute('SELECT id, name, phone, license_type, sessions_done, total_paid FROM clients WHERE checked_out=1 ORDER BY name')
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
                    action_command=lambda cid=row[0]: self.show_client_profile_with_refresh(cid)
                )
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
        self.canvas.update_idletasks()

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.update_cards()
    
    def show_client_profile_with_refresh(self, client_id):
        """Show client profile with a callback to refresh the archived list when returning"""
        def on_profile_return():
            # Refresh the cards to reflect any changes (like unarchiving)
            self.update_cards()
            # Return to this frame
            self.tkraise()
        
        # Show the client profile with the custom return callback
        self.master.show_client_profile(client_id, checked_out=True)
        # Store the return callback for when the profile is closed
        if hasattr(self.master, 'current_frame') and hasattr(self.master.current_frame, 'on_back'):
            self.master.current_frame.on_back = on_profile_return
    
    def refresh_after_unarchive(self, client_id):
        """Refresh the archived list after a candidate has been unarchived"""
        # Check if cards_container exists before trying to access it
        if not hasattr(self, 'cards_container') or self.cards_container is None:
            return
        # Remove the specific candidate card if it exists
        for widget in self.cards_container.winfo_children():
            if hasattr(widget, 'candidate_id') and widget.candidate_id == client_id:
                widget.destroy()
                break
        
        # Update the canvas scroll region
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


