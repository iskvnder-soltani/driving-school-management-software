class HomeFrame(tk.Frame):
    def __init__(self, master, show_add_client, show_clients_list):
        super().__init__(master, bg='#f5f5f5')
        # Statistics section at the top
        self.stats_section = StatisticsSection(self)
        self.stats_section.pack(pady=(20, 5), padx=10, fill='x')
        container = tk.Frame(self, bg='#f5f5f5')
        container.pack(expand=True)
        
        # Title
        tk.Label(container, text='Auto-école Iskander', font=('Arial', 28, 'bold'), bg='#f5f5f5').pack(pady=10)
        
        # Button container using grid layout
        button_container = tk.Frame(container, bg='#f5f5f5')
        button_container.pack(pady=20)
        
        # Row 1: Add new client button (centered)
        tk.Button(button_container, text='Ajouter un nouveau candidat', width=28, command=show_add_client).grid(row=0, column=0, columnspan=2, pady=10, padx=10)
        
        # Row 2: List of clients and Archived clients
        tk.Button(button_container, text='Candidats actifs', width=22, command=show_clients_list).grid(row=1, column=0, pady=10, padx=10)
        tk.Button(button_container, text='Candidats archivés', width=22, command=master.show_checked_out_clients).grid(row=1, column=1, pady=10, padx=10)
        
        # Row 3: Group examen and Payment incomplet
        tk.Button(button_container, text='Groupes d\'examen', width=22, command=master.show_examen_groups).grid(row=2, column=0, pady=10, padx=10)
        tk.Button(button_container, text='Paiement incomplet', width=22, command=master.show_incomplete_payments).grid(row=2, column=1, pady=10, padx=10)
    def tkraise(self, aboveThis=None):
        super().tkraise(aboveThis)
        self.stats_section.refresh_stats()

