class SessionHistoryFrame(tk.Frame):
    def __init__(self, master, client_id, on_back):
        super().__init__(master)
        tk.Label(self, text='Historique des sessions', font=('Arial', 28, 'bold')).pack(pady=20)
        self.listbox = tk.Listbox(self, width=60)
        self.listbox.pack(pady=10)
        tk.Button(self, text='Retour', font=('Arial', 16), width=14, command=on_back).pack(side='bottom', pady=30, anchor='center')
        self.load_sessions(client_id)
    def load_sessions(self, client_id):
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('SELECT date, time FROM sessions WHERE client_id=? ORDER BY date, time', (client_id,))
            sessions = c.fetchall()
            for s in sessions:
                self.listbox.insert('end', f"{s[0]} - {s[1]}")
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

