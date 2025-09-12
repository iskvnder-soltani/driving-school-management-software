class StatisticsSection(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, bg='#f5f5f5', *args, **kwargs)
        self.font_label = ('Arial', 16, 'bold')
        self.font_value = ('Arial', 22, 'bold')
        self.stats = [
            {'label': 'Total candidats', 'value': '0'},
            {'label': 'Candidats archivés', 'value': '0'},
            {'label': 'Total des séances', 'value': '0'},
            {'label': 'Total d\'examens passés', 'value': '0'},
            {'label': 'Montant total payé', 'value': '0 DA'},
            {'label': 'Montant restant à payer', 'value': '0 DA'},
            {'label': 'Revenus par mois', 'value': '0 DA'},
            {'label': 'Prochain examen', 'value': 'Aucun'},
        ]
        self.value_labels = []
        self._build_ui()
    
    def _build_ui(self):
        grid = tk.Frame(self, bg='#f5f5f5')
        grid.pack(padx=20, pady=10)
        
        # Create a 2-row grid for better organization
        for i, stat in enumerate(self.stats):
            row = i // 4  # 4 columns per row
            col = i % 4
            frame = tk.Frame(grid, bg='#fff', bd=2, relief='groove', padx=18, pady=10)
            frame.grid(row=row, column=col, padx=10, pady=5, sticky='nsew')
            tk.Label(frame, text=stat['label'], font=self.font_label, bg='#fff').pack()
            val = tk.Label(frame, text=stat['value'], font=self.font_value, fg='#222', bg='#fff')
            val.pack()
            self.value_labels.append(val)
    
    def refresh_stats(self):
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            # Total candidats
            c.execute('SELECT COUNT(*) FROM clients')
            total_cand = c.fetchone()[0]
            
            # Candidats archivés
            c.execute('SELECT COUNT(*) FROM clients WHERE checked_out = 1')
            archived_candidates = c.fetchone()[0] or 0
            
            # Total des séances
            c.execute('SELECT COUNT(*) FROM sessions')
            total_sessions = c.fetchone()[0]
            
            # Total d'examens passés
            c.execute('''SELECT COUNT(*) FROM examen_group_candidates
                         WHERE result = 'Passé' AND examen_type != '' ''')
            total_examens_passed = c.fetchone()[0] or 0
            
            # Montant total payé
            c.execute('SELECT SUM(amount) FROM payments')
            total_paid = c.fetchone()[0] or 0
            
            # Montant restant à payer (total required - total paid)
            c.execute('SELECT SUM(total_amount_required) FROM clients')
            total_required = c.fetchone()[0] or 0
            remaining_amount = total_required - total_paid
            
            # Revenus par mois (current month)
            current_month = datetime.now().strftime('%m/%Y')
            # Fix: Extract month and year from DD/MM/YYYY format in database
            c.execute('''SELECT SUM(amount) FROM payments 
                         WHERE SUBSTR(date, 4, 2) || '/' || SUBSTR(date, 7, 4) = ?''', (current_month,))
            monthly_revenue = c.fetchone()[0] or 0
            
            # Prochain examen - Get all examen dates and find the next upcoming one
            c.execute('SELECT examen_date FROM examen_groups ORDER BY examen_date ASC')
            all_examen_dates = c.fetchall()
            
            # Find the next upcoming examen date
            next_examen = self.find_next_upcoming_examen(all_examen_dates)
        except Exception as e:
            if conn:
                conn.rollback()
            total_cand = 0
            total_paid = 0
            total_sessions = 0
            remaining_amount = 0
            monthly_revenue = 0
            archived_candidates = 0
            total_examens_passed = 0
            next_examen = 'Aucun examen à venir'
        finally:
            if conn:
                conn.close()
        
        # Update all value labels in the new order
        self.value_labels[0]['text'] = str(total_cand)
        self.value_labels[1]['text'] = str(archived_candidates)
        self.value_labels[2]['text'] = str(total_sessions)
        self.value_labels[3]['text'] = str(total_examens_passed)
        self.value_labels[4]['text'] = f"{total_paid:,.0f} DA"
        self.value_labels[5]['text'] = f"{remaining_amount:,.0f} DA"
        self.value_labels[6]['text'] = f"{monthly_revenue:,.0f} DA"
        self.value_labels[7]['text'] = next_examen
    
    def find_next_upcoming_examen(self, examen_dates):
        """Find the next upcoming examen date from a list of exam dates"""
        if not examen_dates:
            return 'Aucun examen à venir'
        
        today = datetime.now().date()
        
        for examen_date_tuple in examen_dates:
            examen_date_str = examen_date_tuple[0]
            try:
                # Parse the date string (format: dd/mm/yyyy)
                examen_date = datetime.strptime(examen_date_str, '%d/%m/%Y').date()
                
                # If this exam date is today or in the future, it's the next upcoming exam
                if examen_date >= today:
                    return examen_date_str
            except ValueError:
                # Skip invalid date formats
                continue
        
        # If no upcoming exams found
        return 'Aucun examen à venir'

