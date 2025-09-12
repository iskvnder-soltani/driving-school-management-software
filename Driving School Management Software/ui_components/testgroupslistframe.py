class TestGroupsListFrame(tk.Frame):
    def __init__(self, master, show_group_detail, on_add_group, on_back):
        super().__init__(master)
        tk.Label(self, text='Groupes d\'examen', font=('Arial', 28, 'bold')).pack(pady=20)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text='Ajouter un nouveau groupe', font=('Arial', 16), command=on_add_group).pack(side='left', padx=10)
        tk.Button(btn_frame, text='Retour', font=('Arial', 16), command=on_back).pack(side='left', padx=10)
        self.main_container = tk.Frame(self)
        self.main_container.pack(expand=True, fill='both')
        self.canvas = tk.Canvas(self.main_container, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_container, orient='vertical', command=self.canvas.yview)
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
        self.cards_container = tk.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.cards_container, anchor='n')
        def on_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))
            canvas_width = event.width
            self.cards_container.update_idletasks()
            cards_width = self.cards_container.winfo_reqwidth()
            x = max((canvas_width - cards_width) // 2, 0)
            self.canvas.coords(self.window_id, x, 0)
        self.canvas.bind('<Configure>', on_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set, height=500)
        self.show_group_detail = show_group_detail  # Ensure callback is set
        self.update_cards()
    
    def destroy(self):
        """Clean up resources to prevent memory leaks"""
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
        
        super().destroy()
    
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
            c.execute('''CREATE TABLE IF NOT EXISTS examen_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                examen_date TEXT NOT NULL
            )''')
            c.execute('SELECT id, examen_date, license_type FROM examen_groups ORDER BY examen_date DESC')
            for row in c.fetchall():
                card = tk.Frame(self.cards_container, bd=2, relief='groove', padx=20, pady=10, bg='#f7f7f7')
                card.pack(fill='x', pady=10, padx=10)
                tk.Label(card, text=f"Date de l'examen : {row[1]}", font=('Arial', 20, 'bold'), bg='#f7f7f7').grid(row=0, column=0, sticky='w')
                tk.Label(card, text=f"Type de permis : {row[2] if row[2] else ''}", font=('Arial', 16), bg='#f7f7f7').grid(row=1, column=0, sticky='w')
                tk.Button(card, text='Voir', font=('Arial', 16), command=partial(self.show_group_detail, row[0])).grid(row=0, column=1, rowspan=2, padx=20)
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

