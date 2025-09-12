import tkinter as tk
import tkinter.font as tkfont
import sqlite3
from datetime import datetime
from tkinter import messagebox

from database.config import DB_FILE
from database.operations import safe_db_operation, init_db
from ui_components.home_frame import HomeFrame
from ui_components.add_client_frame import AddClientFrame
from ui_components.clients_list_frame import ClientsListFrame
from ui_components.client_profile_frame import ClientProfileFrame
from ui_components.checked_out_clients_list_frame import CheckedOutClientsListFrame
from ui_components.test_groups_list_frame import TestGroupsListFrame
from ui_components.test_group_detail_frame import TestGroupDetailFrame
from ui_components.add_test_group_frame import AddTestGroupFrame
from ui_components.incomplete_payment_frame import IncompletePaymentFrame

class IskanderDrivingSchool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Auto-école Iskander')
        self.state('zoomed')  # Start maximized
        default_font = tkfont.nametofont('TkDefaultFont')
        default_font.configure(size=24, family='Arial')
        self.option_add('*Font', default_font)
        self.current_frame = None
        
        # Add watermark to main window
        add_watermark(self)
        
        self.show_home()
    def show_home(self):
        self._switch_frame(HomeFrame(self, self.show_add_client, self.show_clients_list))
        if hasattr(self.current_frame, 'stats_section'):
            self.current_frame.stats_section.refresh_stats()
    def show_add_client(self):
        self._switch_frame(AddClientFrame(self, self.save_client, self.show_home))
    def show_clients_list(self):
        self._switch_frame(ClientsListFrame(self, self.show_client_profile, self.show_home))
    def show_client_profile(self, client_id, checked_out=False, return_to=None):
        if checked_out:
            # Create a custom return callback based on return_to parameter
            if return_to == "incomplete_payments":
                def on_back_from_archived():
                    # Return to incomplete payments list
                    self.show_incomplete_payments()
            else:
                def on_back_from_archived():
                    # Default: refresh the archived clients list
                    self.show_checked_out_clients()
            
            self._switch_frame(ClientProfileFrame(self, client_id, on_back_from_archived, checked_out=True))
        else:
            # Determine the correct return destination based on context
            if return_to == "incomplete_payments":
                on_back = self.show_incomplete_payments
            else:
                on_back = self.show_clients_list
            self._switch_frame(ClientProfileFrame(self, client_id, on_back, checked_out=False))
    def save_client(self, name, fathers_name, gender, blood_type, phone, address, date_of_birth, place_of_birth, license_type, total_amount_required):
        date_joined = datetime.now().strftime('%d/%m/%Y')
        safe_db_operation(lambda c: c.execute('''INSERT INTO clients (name, phone, address, date_of_birth, place_of_birth, date_joined, sessions_done, total_paid, total_amount_required, license_type, fathers_name, gender, blood_type) VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?, ?, ?)''',
                  (name, phone, address, date_of_birth, place_of_birth, date_joined, total_amount_required, license_type, fathers_name, gender, blood_type)))
        messagebox.showinfo('Succès', 'Candidat ajouté avec succès!')
        self.show_home()
    def save_edited_client(self, client_id, name, fathers_name, gender, blood_type, phone, address, date_of_birth, place_of_birth, license_type, total_amount_required):
        print(f"[DEBUG] IskanderDrivingSchool.save_edited_client: id={client_id}, name={name}")
        safe_db_operation(lambda c: c.execute('''UPDATE clients SET name=?, phone=?, address=?, date_of_birth=?, place_of_birth=?, license_type=?, total_amount_required=?, fathers_name=?, gender=?, blood_type=? WHERE id=?''',
                  (name, phone, address, date_of_birth, place_of_birth, license_type, total_amount_required, fathers_name, gender, blood_type, client_id)))
        messagebox.showinfo('Succès', 'Informations du candidat mises à jour!')
        self.show_client_profile(client_id)
        print(f"[DEBUG] IskanderDrivingSchool: switched to profile for id={client_id}")
    def _switch_frame(self, frame):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame
        self.current_frame.pack(fill='both', expand=True)
        self.update_idletasks()
        
        # Add watermark to the new frame
        add_watermark(frame)
    def show_checked_out_clients(self):
        self._switch_frame(CheckedOutClientsListFrame(self, self.show_client_profile, self.show_home))
    def show_examen_groups(self):
        self._switch_frame(TestGroupsListFrame(self, self.show_group_detail, self.add_examen_group, self.show_home))
    def show_group_detail(self, group_id):
        self._switch_frame(TestGroupDetailFrame(self, group_id, self.show_examen_groups))
    def add_examen_group(self):
        self._switch_frame(AddTestGroupFrame(self, self.save_new_examen_group, self.show_examen_groups))
    def save_new_examen_group(self, date, license_type, centre_examen):
        safe_db_operation(lambda c: c.execute('INSERT INTO examen_groups (examen_date, license_type, centre_examen) VALUES (?, ?, ?)', (date, license_type, centre_examen)))
        group_id = safe_db_operation(lambda c: c.lastrowid)
        messagebox.showinfo('Succès', 'Groupe créé avec succès!')
        self.show_examen_groups()
    def show_incomplete_payments(self):
        self._switch_frame(IncompletePaymentFrame(self, self.show_client_profile, self.show_home))
    def show_candidates_for_examen_date(self, examen_date):
        import sqlite3
        win = tk.Toplevel(self)
        win.title(f'Candidats pour l\'examen du {examen_date}')
        win.geometry('600x400')
        
        # Add watermark to popup
        add_watermark(win)
        
        tk.Label(win, text=f'Candidats pour l\'examen du {examen_date}', font=('Arial', 18, 'bold')).pack(pady=10)
        frame = tk.Frame(win)
        frame.pack(fill='both', expand=True, padx=20, pady=10)
        headers = ['Nom et prénom', 'Téléphone', 'Type d\'examen']
        for j, h in enumerate(headers):
            tk.Label(frame, text=h, font=('Arial', 14, 'bold'), borderwidth=1, relief='solid', padx=8, pady=4).grid(row=0, column=j, sticky='nsew')
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('''SELECT cl.name, cl.phone, tgc.examen_type
                         FROM examen_group_candidates tgc
                         JOIN clients cl ON tgc.candidate_id = cl.id
                         JOIN examen_groups tg ON tgc.group_id = tg.id
                         WHERE tg.examen_date = ?''', (examen_date,))
            for i, row in enumerate(c.fetchall(), 1):
                for j, val in enumerate(row):
                    tk.Label(frame, text=val, font=('Arial', 13), borderwidth=1, relief='solid', padx=8, pady=4).grid(row=i, column=j, sticky='nsew')
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
        tk.Button(win, text='Fermer', font=('Arial', 13), command=win.destroy).pack(pady=10)

# Simple watermark function
def add_watermark(widget):
    """Add simple watermark to any widget"""
    watermark = tk.Label(
        widget,
        text="All rights reserved – Iskander Soltani © 2025",
        fg="gray",
        bg=widget.cget('bg'),  # Use parent's background color for transparency
        font=("Arial", 8)
    )
    watermark.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)
    return watermark


if __name__ == '__main__':
    init_db()
    app = IskanderDrivingSchool()
    app.mainloop()
