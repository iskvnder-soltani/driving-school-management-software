class ExamenHistoryFrame(tk.Frame):
    def __init__(self, master, client_id, on_back):
        super().__init__(master)
        tk.Label(self, text='Historique des examens', font=('Arial', 28, 'bold')).pack(pady=20)
        self.listbox = tk.Listbox(self, width=65)
        self.listbox.pack(pady=10)
        tk.Button(self, text='Retour', font=('Arial', 16), width=14, command=on_back).pack(side='bottom', pady=30, anchor='center')
        self.load_examen_history(client_id)
    
    def load_examen_history(self, client_id):
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('''
                SELECT tg.examen_date, tgc.examen_type, tgc.result
                FROM examen_groups tg
                JOIN examen_group_candidates tgc ON tg.id = tgc.group_id
                WHERE tgc.candidate_id = ?
                ORDER BY tg.examen_date DESC, tgc.examen_type
            ''', (client_id,))
            examens = c.fetchall()
            for e in examens:
                result_text = e[2] if e[2] else 'Non défini'
                self.listbox.insert('end', f"{e[0]} - {e[1]} - {result_text}")
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    

    


