class ClientProfileFrame(tk.Frame):
    def __init__(self, master, client_id, on_back, checked_out=False):
        super().__init__(master)
        self.client_id = client_id
        self.master = master
        
        # Title at the top (always visible)
        title_label = tk.Label(self, text='Profil du candidat', font=('Arial', 28, 'bold'))
        title_label.pack(pady=20)
        
        # Create main container with scrollbar
        self.main_container = tk.Frame(self)
        self.main_container.pack(pady=10, fill='both', expand=True)
        
        # Create canvas and scrollbar for scrollable content
        self.canvas = tk.Canvas(self.main_container, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_container, orient='vertical', command=self.canvas.yview)
        
        # Create inner frame for content
        self.inner_frame = tk.Frame(self.canvas)
        
        # Configure canvas
        self.window_id = self.canvas.create_window((0, 0), window=self.inner_frame, anchor='n')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
        
        # Bind events for proper scrolling
        self.inner_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', self._center_inner_frame)
        
        # Bind mouse wheel to canvas for scrolling anywhere in the frame
        self.bind_all('<MouseWheel>', self._on_mousewheel)
        
        # Candidate info in the scrollable frame
        self.info_frame = tk.Frame(self.inner_frame)
        self.info_frame.pack(pady=30, side='top', anchor='n', fill='x')
        
        # Action buttons in the scrollable frame
        btn_grid = tk.Frame(self.inner_frame)
        btn_grid.pack(pady=10, side='top', anchor='n', fill='x')
        
        # Store button references for conditional display
        self.button_refs = {}
        
        buttons = [
            # Row 1: edit candidat - verifie session - add payment - print last receipt
            ("Modifier le candidat", self.edit_client),
            ("Vérifier la session (+1)", self.check_session),
            ("Ajouter un paiement", self.add_payment),
            ("Imprimer le dernier reçu", self.print_last_receipt),
            # Row 2: delete candidat - session history - payment history - print fich candidat
            ("Supprimer le candidat", self.delete_client),
            ("Voir l'historique des sessions", self.view_session_history),
            ("Voir l'historique des paiements", self.view_payment_history),
            ("Imprimer fiche candidat", self.print_candidate_profile),
            # Row 3: archive candidat - unarchive candidat - examens history - retour
            ("Archiver le candidat", self.check_out_client),
            ("Désarchiver le candidat", self.unarchive_client),
            ("Voir l'historique des examens", self.view_test_history),
        ]
        
        # Initialize unarchive button as disabled (only enabled for archived candidates)
        self.unarchive_button_initialized = False
        
        # Configure grid columns with fixed widths for consistent button spacing
        btn_grid.grid_columnconfigure(0, weight=0, minsize=200)
        btn_grid.grid_columnconfigure(1, weight=0, minsize=200)
        btn_grid.grid_columnconfigure(2, weight=0, minsize=200)
        btn_grid.grid_columnconfigure(3, weight=0, minsize=200)
        
        for idx, (label, cmd) in enumerate(buttons):
            row = idx // 4
            col = idx % 4
            btn = tk.Button(btn_grid, text=label, font=('Arial', 16), width=24, command=cmd)
            btn.grid(row=row, column=col, padx=15, pady=15, sticky='ew')
            self.button_refs[label] = btn
        
        # Add 'Retour' button in the 4th position of row 3 (replacing the 12th button)
        # With 12 buttons (0-11), we need 3 rows (0, 1, 2) with 4 buttons each
        retour_btn = tk.Button(btn_grid, text='Retour', font=('Arial', 16), width=24, command=on_back)
        retour_btn.grid(row=2, column=3, padx=15, pady=15, sticky='ew')
        # Store the retour button in button_refs for proper handling in archived logic
        self.button_refs['Retour'] = retour_btn
        
        self.load_client()
        self.on_back = on_back
        self.checked_out = checked_out
        
        # Apply archived candidate logic
        self.apply_archived_candidate_logic()
    
    def _center_inner_frame(self, event):
        """Center the inner frame within the canvas"""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        canvas_width = event.width
        self.inner_frame.update_idletasks()
        frame_width = self.inner_frame.winfo_reqwidth()
        x = max((canvas_width - frame_width) // 2, 0)
        self.canvas.coords(self.window_id, x, 0)
        
        # Ensure the info frame is also centered within the inner frame
        self.info_frame.update_idletasks()
        info_width = self.info_frame.winfo_reqwidth()
        if info_width < frame_width:
            # Center the info frame if it's smaller than the inner frame
            self.info_frame.pack_configure(anchor='center')
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
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
        if hasattr(self, 'inner_frame'):
            self.inner_frame.destroy()
            self.inner_frame = None
        
        if hasattr(self, 'main_container'):
            self.main_container.destroy()
            self.main_container = None
        
        super().destroy()
    
    def apply_archived_candidate_logic(self):
        """Hide or disable buttons for archived candidates"""
        # First, reset all buttons to normal state
        for btn in self.button_refs.values():
            btn.config(state="normal")
        
        if self.checked_out:
            # Buttons to hide/disable for archived candidates
            buttons_to_disable = [
                "Vérifier la session (+1)",
                "Archiver le candidat",  # Already archived
                "Modifier le candidat"
            ]
            
            for button_text in buttons_to_disable:
                if button_text in self.button_refs:
                    btn = self.button_refs[button_text]
                    btn.config(state="disabled")
            
            # Show unarchive button for archived candidates
            if "Désarchiver le candidat" in self.button_refs:
                btn = self.button_refs["Désarchiver le candidat"]
                btn.config(state="normal")
            
            # Ensure retour button remains enabled for archived candidates
            if "Retour" in self.button_refs:
                btn = self.button_refs["Retour"]
                btn.config(state="normal")
            
            # Note: "Voir l'historique des examens" button remains enabled for archived candidates
            # as they can still view their test history
        else:
            # Hide unarchive button for active candidates
            if "Désarchiver le candidat" in self.button_refs:
                btn = self.button_refs["Désarchiver le candidat"]
                btn.config(state="disabled")
            
            # Ensure retour button remains enabled for active candidates
            if "Retour" in self.button_refs:
                btn = self.button_refs["Retour"]
                btn.config(state="normal")
        
        # Mark that the logic has been applied
        self.unarchive_button_initialized = True
    
    def load_client(self):
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('SELECT name, phone, address, date_of_birth, place_of_birth, date_joined, sessions_done, total_paid, total_amount_required, license_type, checked_out, numero_dossier, fathers_name, gender, image_path, blood_type FROM clients WHERE id=?', (self.client_id,))
            row = c.fetchone()
            # Fetch last examen info
            c.execute('''SELECT tg.examen_date, tgc.examen_type, tgc.result FROM examen_group_candidates tgc JOIN examen_groups tg ON tgc.group_id = tg.id WHERE tgc.candidate_id=? AND tgc.examen_type != '' ORDER BY tg.examen_date DESC, tg.id DESC LIMIT 1''', (self.client_id,))
            last_examen = c.fetchone()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
        
        # Update checked_out status from database
        if row:
            self.checked_out = bool(row[10])  # checked_out column
            # Re-apply archived candidate logic after loading client data
            self.apply_archived_candidate_logic()
            
            # Ensure unarchive button is properly initialized
            if not self.unarchive_button_initialized:
                self.apply_archived_candidate_logic()
        
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        if row:
            # Handle dossier number display
            name_display = row[0]  # name column
            # File number is now displayed separately, not in the name field
            
            # Prepare birth date (without eligibility information)
            birth_date_display = row[3] if row[3] else "Non renseigné"
            
            # Get eligibility information separately
            eligibility_display = get_eligibility_display_text(row[3]) if row[3] else "Non renseigné"
            
            # Create single column list with all candidate information
            all_fields = []
            
            # Personal information
            all_fields.extend([
                ("Nom et prénom :", name_display),
                ("Nom du père :", row[12] if row[12] else "Non renseigné"),
                ("Groupe sanguin :", row[15] if row[15] else "Non renseigné"),
                ("Genre :", row[13] if row[13] else "Non renseigné"),
                ("Date de naissance :", birth_date_display),
                ("Lieu de naissance :", row[4]),
                ("Téléphone :", row[1]),
                ("Adresse :", row[2]),
            ])
            
            # Administrative information
            # 1. Status
            status_text = "Archivé" if row[10] else "Actif"
            status_color = "#ff6b6b" if row[10] else "#4CAF50"  # Red for archived, Green for active
            all_fields.append(("Statut :", status_text))
            
            # 2. Numero dossier (only if archived)
            if row[10] and row[11]:  # checked_out and numero_dossier
                all_fields.append(("N° de dossier :", row[11]))
            
            # 3. Inscrit le
            all_fields.append(("Inscrit le :", row[5]))
            
            # 4. Type de permis
            all_fields.append(("Type de permis :", row[9]))
            
            # 5. Éligibilité aux tests
            all_fields.append(("Éligibilité aux examens :", eligibility_display))
            
            # 6. Sessions effectuées
            all_fields.append(("Sessions effectuées :", str(row[6])))
            
            # 7. Dernier examen
            if last_examen:
                examen_date, examen_type, examen_result = last_examen
                result_map = {'✅': 'Réussi', '❌': 'Échoué', 'Absent': 'Absent', '': ''}
                all_fields.append(("Dernier examen :", f"{examen_date} | {examen_type} | {result_map.get(examen_result, examen_result)}"))
            else:
                all_fields.append(("Dernier examen :", "Aucun examen"))
            
            # 8. Montant requis
            all_fields.append(("Montant requis :", f"{row[8]:,.0f} DA"))
            
            # 9. Montant total payé
            all_fields.append(("Montant total payé :", f"{row[7]:,.0f} DA"))
            
            # 10. Montant restant
            remaining_amount = row[8] - row[7]  # total_required - total_paid
            all_fields.append(("Montant restant :", f"{remaining_amount:,.0f} DA"))
            
            # Configure grid for single column layout
            self.info_frame.grid_columnconfigure(0, weight=0)  # Label column
            self.info_frame.grid_columnconfigure(1, weight=1)  # Value column
            
            # Center the entire info frame within its container
            self.info_frame.pack_configure(anchor='center')
            
            # Font configuration
            label_font = ("Arial", 20, "bold")
            value_font = ("Arial", 20)
            
            # Display all fields in a single column list
            for i, (label, value) in enumerate(all_fields):
                # Label (left-aligned)
                tk.Label(
                    self.info_frame, text=label, font=label_font,
                    anchor='w', justify='left', bg='#f0f0f0'
                ).grid(row=i, column=0, sticky='w', pady=8, padx=(30, 5))
                
                # Value (left-aligned)
                value_label = tk.Label(
                    self.info_frame, text=value, font=value_font,
                    anchor='w', justify='left', bg='#f0f0f0'
                )
                value_label.grid(row=i, column=1, sticky='w', pady=8, padx=(5, 30))
                
                # Apply special styling for status field
                if label == "Statut :":
                    if value == "Archivé":
                        value_label.config(fg="#ff6b6b", font=('Arial', 20, 'bold'))
                    else:  # "Actif"
                        value_label.config(fg="#4CAF50", font=('Arial', 20, 'bold'))
        else:
            tk.Label(self.info_frame, text='Candidat non trouvé.', font=('Arial', 28, 'bold')).grid(row=0, column=0, columnspan=2)
        
        # Update canvas scroll region after loading content
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    def check_session(self):
        now = datetime.now()
        date = now.strftime('%d/%m/%Y')
        time = now.strftime('%H:%M')
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('INSERT INTO sessions (client_id, date, time) VALUES (?, ?, ?)', (self.client_id, date, time))
            c.execute('UPDATE clients SET sessions_done = sessions_done + 1 WHERE id=?', (self.client_id,))
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
        messagebox.showinfo('Session vérifiée', 'Session enregistrée!')
        self.load_client()
    def view_session_history(self):
        self.master._switch_frame(SessionHistoryFrame(self.master, self.client_id, self.back_to_profile))
    def back_to_profile(self):
        self.master._switch_frame(ClientProfileFrame(self.master, self.client_id, self.on_back, checked_out=self.checked_out))
    def add_payment(self):
        self.master._switch_frame(AddPaymentFrame(self.master, self.client_id, self.save_payment, self.back_to_profile))
    def save_payment(self, client_id, amount):
        # Prevent overpayment
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('SELECT total_paid, total_amount_required FROM clients WHERE id=?', (client_id,))
            row = c.fetchone()
            if row:
                total_paid, total_required = row
                if amount > (total_required - total_paid):
                    messagebox.showerror('Erreur', f'Le montant dépasse le montant restant à payer ({total_required - total_paid:,.2f} DA).')
                    return
            now = datetime.now()
            date = now.strftime('%d/%m/%Y')
            time = now.strftime('%H:%M')
            c.execute('INSERT INTO payments (client_id, date, time, amount) VALUES (?, ?, ?, ?)', (client_id, date, time, amount))
            c.execute('UPDATE clients SET total_paid = total_paid + ? WHERE id=?', (amount, client_id))
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
        # Show confirmation before generating PDF
        messagebox.showinfo('Paiement ajouté', 'Paiement enregistré! Le reçu va être généré.')
        try:
            self.generate_receipt_pdf(client_id, date, time, amount)
        except Exception as e:
            messagebox.showerror('Erreur', f'Erreur lors de la génération du reçu: {e}')
        self.back_to_profile()
    def view_payment_history(self):
        self.master._switch_frame(PaymentHistoryFrame(self.master, self.client_id, self.back_to_profile))
    
    def view_test_history(self):
        self.master._switch_frame(ExamenHistoryFrame(self.master, self.client_id, self.back_to_profile))
    def print_last_receipt(self):
        # Find last payment for this client with comprehensive error handling
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('SELECT date, time, amount FROM payments WHERE client_id=? ORDER BY id DESC LIMIT 1', (self.client_id,))
            row = c.fetchone()
            if not row:
                messagebox.showwarning('Aucun paiement', 'Aucun paiement trouvé pour ce candidat.')
                return
        except Exception as e:
            print(f"[ERROR] Database error in print_last_receipt: {e}")
            messagebox.showerror('Erreur de base de données', f'Impossible de récupérer le dernier paiement: {str(e)}')
            return
        finally:
            if conn:
                conn.close()
        
        # Generate PDF with comprehensive error handling
        filename = self.generate_receipt_pdf(self.client_id, row[0], row[1], row[2], show_message=True)
        
        # Check if PDF generation was successful
        if not filename:
            print("[ERROR] PDF generation failed in print_last_receipt")
            return
        
        # Open PDF with comprehensive error handling
        try:
            import os
            os.startfile(filename)
        except PermissionError:
            error_msg = "Impossible d'ouvrir le PDF - permissions insuffisantes"
            print(f"[ERROR] {error_msg}")
            messagebox.showerror('Erreur de permissions', error_msg)
        except FileNotFoundError:
            error_msg = "Fichier PDF introuvable après génération"
            print(f"[ERROR] {error_msg}")
            messagebox.showerror('Erreur de fichier', error_msg)
        except OSError as e:
            if "No such file or directory" in str(e):
                error_msg = "Fichier PDF introuvable"
                print(f"[ERROR] {error_msg}: {e}")
                messagebox.showerror('Erreur de fichier', error_msg)
            else:
                error_msg = f"Erreur système lors de l'ouverture: {str(e)}"
                print(f"[ERROR] {error_msg}")
                messagebox.showerror('Erreur système', error_msg)
        except Exception as e:
            error_msg = f"Erreur inattendue lors de l'ouverture du PDF: {str(e)}"
            print(f"[ERROR] {error_msg}")
            messagebox.showerror('Erreur inattendue', error_msg)
    
    def print_candidate_profile(self):
        """Generate and print the candidate profile as a PDF"""
        try:
            filename = self.generate_candidate_profile_pdf()
            if filename:
                import os
                os.startfile(filename)
                messagebox.showinfo('Succès', 'Fiche candidat générée avec succès!')
            else:
                messagebox.showerror('Erreur', 'Impossible de générer la fiche candidat.')
        except Exception as e:
            print(f"[ERROR] Error in print_candidate_profile: {e}")
            messagebox.showerror('Erreur', f'Erreur lors de la génération de la fiche candidat: {str(e)}')
    
    def generate_candidate_profile_pdf(self):
        """Generate a PDF profile for the candidate"""
        # Get client info
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('SELECT name, phone, address, date_of_birth, place_of_birth, date_joined, sessions_done, total_paid, total_amount_required, license_type, checked_out, numero_dossier, fathers_name, gender, image_path, blood_type FROM clients WHERE id=?', (self.client_id,))
            row = c.fetchone()
            if not row:
                messagebox.showerror('Erreur', 'Candidat non trouvé.')
                return None
        except Exception as e:
            print(f"[ERROR] Database error in generate_candidate_profile_pdf: {e}")
            messagebox.showerror('Erreur', f'Erreur de base de données: {str(e)}')
            return None
        finally:
            if conn:
                conn.close()
        
        name, phone, address, date_of_birth, place_of_birth, date_joined, sessions_done, total_paid, total_amount_required, license_type, checked_out, numero_dossier, fathers_name, gender, image_path, blood_type = row
        
        # Get eligibility information
        eligibility_display = get_eligibility_display_text(date_of_birth) if date_of_birth else "Non renseigné"
        
        # Get last test information
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('''SELECT tg.examen_date, tgc.examen_type, tgc.result FROM examen_group_candidates tgc JOIN examen_groups tg ON tgc.group_id = tg.id WHERE tgc.candidate_id=? AND tgc.examen_type != '' ORDER BY tg.examen_date DESC, tg.id DESC LIMIT 1''', (self.client_id,))
            last_test = c.fetchone()
            conn.close()
        except Exception as e:
            print(f"[WARNING] Could not fetch last test info: {e}")
            last_test = None
        
        # Calculate remaining amount
        remaining_amount = total_amount_required - total_paid
        
        # School information
        school_name = 'Auto-école Iskander'
        school_address = 'Bvd Houari Boumedienne, Tébessa'
        school_phone = '0657340587'
        
        # Create profiles directory in user's Documents folder for better accessibility
        import os
        from pathlib import Path
        
        # Try multiple locations in order of preference
        possible_locations = [
            os.path.join(os.path.expanduser('~'), 'Documents', 'Auto-école Iskander', 'Profiles'),
            os.path.join(os.path.expanduser('~'), 'Desktop', 'Auto-école Iskander', 'Profiles'),
            os.path.join(os.getcwd(), 'Profiles')
        ]
        
        profiles_dir = None
        for location in possible_locations:
            try:
                profiles_dir = os.path.abspath(location)
                if not os.path.exists(profiles_dir):
                    os.makedirs(profiles_dir, exist_ok=True)
                # Test write permissions
                test_file = os.path.join(profiles_dir, 'test_write.tmp')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print(f"[DEBUG] Using profiles directory: {profiles_dir}")
                break
            except Exception as e:
                print(f"[WARNING] Cannot use location {location}: {e}")
                continue
        
        if profiles_dir is None:
            error_msg = "Impossible de créer le dossier des profils - permissions insuffisantes"
            print(f"[ERROR] {error_msg}")
            messagebox.showerror('Erreur', error_msg)
            return None
        
        # Generate filename
        safe_name = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(profiles_dir, f'Fiche_Candidat_{safe_name}_{timestamp}.pdf')
        
        try:
            from fpdf import FPDF
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            # Set text color to black
            pdf.set_text_color(0, 0, 0)  # black: RGB(0, 0, 0)

            # Set font
            pdf.set_font('Arial', 'B', 16)
            
            # Header
            pdf.cell(0, 10, 'FICHE CANDIDAT', ln=1, align='C')
            pdf.cell(0, 10, school_name, ln=1, align='C')
            
            # School address and phone with smaller font
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 8, school_address, ln=1, align='C')
            pdf.cell(0, 8, school_phone, ln=1, align='C')
            
            # Reset font for rest of document
            pdf.set_font('Arial', 'B', 16)
            pdf.ln(10)
            
            # Add photo frame in upper left corner
            pdf.set_draw_color(0, 0, 0)  # black: RGB(0, 0, 0)
            pdf.rect(x=10, y=5, w=40, h=50)
            pdf.ln(5)
            
            # Candidate information
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'INFORMATIONS PERSONNELLES', ln=1, align='L')
            pdf.set_font('Arial', '', 12)
            
            # Left column information
            pdf.cell(60, 8, 'Nom et prénom:', 0, 0)
            pdf.cell(0, 8, name, ln=1)
            
            pdf.cell(60, 8, 'Nom du père:', 0, 0)
            pdf.cell(0, 8, fathers_name if fathers_name else 'Non renseigné', ln=1)
            
            pdf.cell(60, 8, 'Groupe sanguin:', 0, 0)
            pdf.cell(0, 8, blood_type if blood_type else 'Non renseigné', ln=1)
            
            pdf.cell(60, 8, 'Genre:', 0, 0)
            pdf.cell(0, 8, gender if gender else 'Non renseigné', ln=1)
            
            pdf.cell(60, 8, 'Date de naissance:', 0, 0)
            pdf.cell(0, 8, date_of_birth if date_of_birth else 'Non renseigné', ln=1)
            
            pdf.cell(60, 8, 'Lieu de naissance:', 0, 0)
            pdf.cell(0, 8, place_of_birth if place_of_birth else 'Non renseigné', ln=1)
            
            pdf.cell(60, 8, 'Téléphone:', 0, 0)
            pdf.cell(0, 8, phone if phone else 'Non renseigné', ln=1)
            
            pdf.cell(60, 8, 'Adresse:', 0, 0)
            pdf.cell(0, 8, address if address else 'Non renseigné', ln=1)
            
            pdf.ln(10)
            
            # Right column information
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'INFORMATIONS ACADÉMIQUES', ln=1, align='L')
            pdf.set_font('Arial', '', 12)
            
            pdf.cell(60, 8, 'Inscrit le:', 0, 0)
            pdf.cell(0, 8, date_joined, ln=1)
            
            pdf.cell(60, 8, 'Type de permis:', 0, 0)
            pdf.cell(0, 8, license_type if license_type else 'Non renseigné', ln=1)
            
            pdf.cell(60, 8, 'Sessions effectuées:', 0, 0)
            pdf.cell(0, 8, str(sessions_done), ln=1)
            
            pdf.cell(60, 8, 'Éligibilité aux examens:', 0, 0)
            pdf.cell(0, 8, eligibility_display, ln=1)
            
            # Add last exam info if available
            if last_test:
                examen_date, examen_type, examen_result = last_test
                result_map = {'✅': 'Réussi', '❌': 'Échoué', 'Absent': 'Absent', '': ''}
                pdf.cell(60, 8, 'Dernier examen:', 0, 0)
                pdf.cell(0, 8, f"{examen_date} | {examen_type} | {result_map.get(examen_result, examen_result)}", ln=1)
            else:
                pdf.cell(60, 8, 'Dernier examen:', 0, 0)
                pdf.cell(0, 8, 'Aucun examen', ln=1)
            
            pdf.cell(60, 8, 'Montant requis:', 0, 0)
            pdf.cell(0, 8, f'{total_amount_required:,.0f} DA', ln=1)
            
            pdf.cell(60, 8, 'Montant total payé:', 0, 0)
            pdf.cell(0, 8, f'{total_paid:,.0f} DA', ln=1)
            
            pdf.cell(60, 8, 'Montant restant:', 0, 0)
            pdf.cell(0, 8, f'{remaining_amount:,.0f} DA', ln=1)
            
            if checked_out and numero_dossier:
                pdf.ln(10)
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, 'INFORMATIONS D\'ARCHIVAGE', ln=1, align='L')
                pdf.set_font('Arial', '', 12)
                pdf.cell(60, 8, 'Numéro de dossier:', 0, 0)
                pdf.cell(0, 8, numero_dossier, ln=1)
            

            
            # Save PDF
            pdf.output(filename)
            return filename
            
        except Exception as e:
            print(f"[ERROR] PDF generation error: {e}")
            messagebox.showerror('Erreur', f'Erreur lors de la génération du PDF: {str(e)}')
            return None
    
    def generate_receipt_pdf(self, client_id, date, time, amount, show_message=False):
        # Get client info
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('SELECT name, phone, address, date_joined, total_paid, total_amount_required, license_type, date_of_birth, place_of_birth, fathers_name, gender FROM clients WHERE id=?', (client_id,))
            client = c.fetchone()
            if not client:
                if show_message:
                    messagebox.showerror('Erreur', 'Candidat non trouvé.')
                return
        except Exception as e:
            print(f"[ERROR] Database error in generate_receipt_pdf: {e}")
            if show_message:
                messagebox.showerror('Erreur', f'Erreur de base de données: {str(e)}')
            return
        finally:
            if conn:
                conn.close()
        
        name, phone, address, date_joined, total_paid, total_required, license_type, date_of_birth, place_of_birth, fathers_name, gender = client
        
        # School information
        school_name = 'Auto-école Iskander'
        school_address = 'Bvd Houari Boumedienne, Tébessa'
        school_phone = '0657340587'
        
        # Generate ticket number (using client_id and timestamp)
        import time as time_module
        ticket_number = int(time_module.time()) % 10000  # 4-digit number
        
        # Calculate remaining amount
        remaining_amount = total_required - total_paid
        
        safe_name = name.replace(' ', '_').replace('/', '_')
        # Try multiple locations in order of preference for receipts
        possible_locations = [
            os.path.join(os.path.expanduser('~'), 'Documents', 'Auto-école Iskander', 'Receipts'),
            os.path.join(os.path.expanduser('~'), 'Desktop', 'Auto-école Iskander', 'Receipts'),
            os.path.join(os.getcwd(), 'Receipts')
        ]
        
        receipts_dir = None
        for location in possible_locations:
            try:
                receipts_dir = os.path.abspath(location)
                if not os.path.exists(receipts_dir):
                    os.makedirs(receipts_dir, exist_ok=True)
                # Test write permissions
                test_file = os.path.join(receipts_dir, 'test_write.tmp')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print(f"[DEBUG] Using receipts directory: {receipts_dir}")
                break
            except Exception as e:
                print(f"[WARNING] Cannot use location {location}: {e}")
                continue
        
        if receipts_dir is None:
            error_msg = "Impossible de créer le dossier des reçus - permissions insuffisantes"
            print(f"[ERROR] {error_msg}")
            if show_message:
                messagebox.showerror('Erreur de permissions', error_msg)
            return
        

        
        # Sanitize date for filename
        safe_date = date.replace('/', '-')
        safe_time = time.replace(':', '-')
        filename = os.path.join(receipts_dir, f"{safe_name}_{safe_date}_{safe_time}.pdf")
        
        # Check if filename is too long (Windows limit is 260 characters)
        if len(filename) > 250:
            # Truncate the filename
            max_name_length = 250 - len(receipts_dir) - len("_YYYY-MM-DD_HH-MM.pdf") - 1
            safe_name = safe_name[:max_name_length]
            filename = os.path.join(receipts_dir, f"{safe_name}_{safe_date}_{safe_time}.pdf")
            print(f"[WARNING] Filename truncated to avoid path length issues")
        
        try:
            # Create PDF with comprehensive error handling
            pdf = FPDF()
            pdf.add_page()
            # Set text color to black
            pdf.set_text_color(0, 0, 0)  # black: RGB(0, 0, 0)

            page_height = pdf.h
            page_width = pdf.w
            
            def draw_client_receipt(y_start):
                """Draw client copy (top half)"""
                pdf.set_y(y_start)
                
                # School header
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 8, school_name, ln=1, align='C')
                pdf.set_font('Arial', '', 10)
                pdf.cell(0, 6, school_address, ln=1, align='C')
                pdf.cell(0, 6, school_phone, ln=1, align='C')
                
                # Ticket number and date/time
                pdf.ln(3)
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 6, f'Ticket n°: {ticket_number}', ln=1, align='C')
                pdf.set_font('Arial', '', 10)
                pdf.cell(0, 6, f'le {date} à {time}', ln=1, align='C')
                
                # Candidate name
                pdf.ln(3)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, f'Nom et prénom: {name}', ln=1, align='C')
                
                # Payment table (2x2)
                pdf.ln(3)
                pdf.set_font('Arial', 'B', 10)
                
                # Table header
                col_width = page_width / 2 - 10
                row_height = 6

                # Set border color to black
                pdf.set_draw_color(0, 0, 0)  # black: RGB(0, 0, 0)

                # Row 1
                pdf.cell(col_width, row_height, f'Montant payé aujourd\'hui: {amount:,.2f} DA', border=1, align='C')
                pdf.cell(col_width, row_height, f'Montant restant: {remaining_amount:,.2f} DA', border=1, align='C')
                pdf.ln(row_height)
                
                # Row 2
                pdf.cell(col_width, row_height, f'Montant total payé: {total_paid:,.2f} DA', border=1, align='C')
                pdf.cell(col_width, row_height, f'Montant total dû: {total_required:,.2f} DA', border=1, align='C')
                pdf.ln(row_height)
                
                # Mission statement
                pdf.ln(5)
                pdf.set_font('Arial', 'I', 10)
                pdf.cell(0, 6, 'Auto-école Iskander - Votre réussite, notre mission.', ln=1, align='C')
            
            def draw_school_receipt(y_start):
                """Draw school copy (bottom half)"""
                pdf.set_y(y_start)
                
                # School header
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 8, school_name, ln=1, align='C')
                pdf.set_font('Arial', '', 10)
                pdf.cell(0, 6, school_address, ln=1, align='C')
                pdf.cell(0, 6, school_phone, ln=1, align='C')
                
                # Ticket number and date/time
                pdf.ln(3)
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 6, f'Ticket n°: {ticket_number}', ln=1, align='C')
                pdf.set_font('Arial', '', 10)
                pdf.cell(0, 6, f'le {date} à {time}', ln=1, align='C')
                
                # Candidate details
                pdf.ln(3)
                pdf.set_font('Arial', 'B', 11)
                pdf.cell(0, 7, 'Détails du candidat:', ln=1, align='C')
                pdf.set_font('Arial', '', 10)
                pdf.cell(0, 6, f'Nom et prénom: {name}', ln=1, align='C')
                pdf.cell(0, 6, f'Nom du père: {fathers_name}', ln=1, align='C')
                pdf.cell(0, 6, f'Date de naissance: {date_of_birth}', ln=1, align='C')
                pdf.cell(0, 6, f'Lieu de naissance: {place_of_birth}', ln=1, align='C')
                pdf.cell(0, 6, f'Numéro de téléphone: {phone}', ln=1, align='C')
                pdf.cell(0, 6, f'Adresse: {address}', ln=1, align='C')
                pdf.cell(0, 6, f'Date d\'inscription: {date_joined}', ln=1, align='C')
                pdf.cell(0, 6, f'Type de permis: {license_type}', ln=1, align='C')
                
                # Payment table (2x2)
                pdf.ln(3)
                pdf.set_font('Arial', 'B', 10)
                
                # Table header
                col_width = page_width / 2 - 10
                row_height = 6

                # Set border color to black
                pdf.set_draw_color(0, 0, 0)  # black: RGB(0, 0, 0)

                # Row 1
                pdf.cell(col_width, row_height, f'Montant payé aujourd\'hui: {amount:,.2f} DA', border=1, align='C')
                pdf.cell(col_width, row_height, f'Montant restant: {remaining_amount:,.2f} DA', border=1, align='C')
                pdf.ln(row_height)
                
                # Row 2
                pdf.cell(col_width, row_height, f'Montant total payé: {total_paid:,.2f} DA', border=1, align='C')
                pdf.cell(col_width, row_height, f'Montant total dû: {total_required:,.2f} DA', border=1, align='C')
                pdf.ln(row_height)
                
                # Mission statement
                pdf.ln(5)
                pdf.set_font('Arial', 'I', 10)
                pdf.cell(0, 6, 'Auto-école Iskander - Votre réussite, notre mission.', ln=1, align='C')
            
            # Calculate positions for both receipts to fit on one A4 page
            # Client receipt (top half) - more compact
            client_y = 15
            draw_client_receipt(client_y)
            
            # Add separator line
            pdf.set_y(page_height / 2 - 3)
            pdf.set_draw_color(0, 0, 0)  # black: RGB(0, 0, 0)
            pdf.line(10, page_height / 2, page_width - 10, page_height / 2)
            
            # School receipt (bottom half) - more compact
            school_y = page_height / 2 + 5
            draw_school_receipt(school_y)
            
            # Save PDF with comprehensive error handling
            try:
                pdf.output(filename)
                print(f"[DEBUG] PDF generated at {filename}")
            except PermissionError:
                error_msg = "Impossible de sauvegarder le PDF - permissions insuffisantes"
                print(f"[ERROR] {error_msg}")
                if show_message:
                    messagebox.showerror('Erreur de permissions', error_msg)
                return
            except OSError as e:
                if "No space left on device" in str(e):
                    error_msg = "Espace disque insuffisant pour sauvegarder le PDF"
                    print(f"[ERROR] {error_msg}: {e}")
                    if show_message:
                        messagebox.showerror('Espace disque insuffisant', error_msg)
                else:
                    error_msg = f"Erreur système lors de la sauvegarde: {str(e)}"
                    print(f"[ERROR] {error_msg}")
                    if show_message:
                        messagebox.showerror('Erreur système', error_msg)
                return
            except Exception as e:
                error_msg = f"Erreur inattendue lors de la sauvegarde du PDF: {str(e)}"
                print(f"[ERROR] {error_msg}")
                if show_message:
                    messagebox.showerror('Erreur de sauvegarde', error_msg)
                return
            
            if show_message:
                messagebox.showinfo('Reçu généré', f'Reçu sauvegardé sous {filename}')
            return filename
            
        except ImportError as e:
            error_msg = f"Erreur d'importation de la bibliothèque PDF: {str(e)}"
            print(f"[ERROR] {error_msg}")
            if show_message:
                messagebox.showerror('Erreur de bibliothèque', error_msg)
            return
        except Exception as e:
            error_msg = f"Erreur inattendue lors de la génération du PDF: {str(e)}"
            print(f"[ERROR] {error_msg}")
            if show_message:
                messagebox.showerror('Erreur inattendue', error_msg)
            return
    def edit_client(self):
        print('Bouton Modifier le candidat cliqué')
        self.master._switch_frame(EditClientFrame(self.master, self.client_id, self.master.save_edited_client, self.back_to_profile))
    def delete_client(self):
        if messagebox.askyesno('Supprimer le candidat', 'Êtes-vous sûr de vouloir supprimer ce candidat? Cette action est irréversible.'):
            safe_db_operation(lambda c: c.execute('DELETE FROM clients WHERE id=?', (self.client_id,)))
            safe_db_operation(lambda c: c.execute('DELETE FROM payments WHERE client_id=?', (self.client_id,)))
            safe_db_operation(lambda c: c.execute('DELETE FROM sessions WHERE client_id=?', (self.client_id,)))
            messagebox.showinfo('Supprimé', 'Candidat et toutes les données associées supprimées.')
            self.on_back()
    def check_out_client(self):
        # Show dossier number dialog
        dialog = DossierNumberDialog(self.master)
        dossier_number = dialog.result
        
        if dossier_number:
            safe_db_operation(lambda c: c.execute('UPDATE clients SET checked_out=1, numero_dossier=? WHERE id=?', (dossier_number, self.client_id)))
            messagebox.showinfo('Archivé', 'Le candidat a été archivé.')
            self.on_back()
    
    def unarchive_client(self):
        """Unarchive a candidate by setting checked_out to 0 and clearing dossier number"""
        # Additional validation: ensure the candidate is actually archived
        if not self.checked_out:
            messagebox.showwarning('Statut invalide', 'Ce candidat n\'est pas archivé.')
            return
            
        if messagebox.askyesno('Désarchiver le candidat', 
                              'Êtes-vous sûr de vouloir désarchiver ce candidat?\n\n'
                              'Le candidat redeviendra actif et pourra à nouveau participer aux sessions et examens.'):
            
            # Update the database to unarchive the candidate
            safe_db_operation(lambda c: c.execute('UPDATE clients SET checked_out=0, numero_dossier=NULL WHERE id=?', (self.client_id,)))
            
            # Show success message
            messagebox.showinfo('Désarchivé', 'Le candidat a été désarchivé avec succès!\n\n'
                              'Il est maintenant redevenu actif.')
            
            # Update the local status
            self.checked_out = False
            
            # Re-apply the button logic for active candidates
            self.apply_archived_candidate_logic()
            
            # Reload client data to reflect the changes
            self.load_client()
            
            # Ask user if they want to return to the archived candidates list
            if messagebox.askyesno('Navigation', 
                                  'Le candidat a été désarchivé. Voulez-vous retourner à la liste des candidats archivés?'):
                self.on_back()
            else:
                # If user chooses to stay, refresh the profile to show active status
                self.load_client()
                
                # Update the canvas scroll region after the refresh
                self.canvas.update_idletasks()
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                
                # Show a message that the candidate is now active
                messagebox.showinfo('Statut mis à jour', 'Le profil a été mis à jour pour refléter le nouveau statut actif du candidat.')
                
                # Also refresh the archived list if we're viewing from there
                if hasattr(self.master, 'current_frame') and hasattr(self.master.current_frame, 'on_back'):
                    # Try to refresh the archived list if possible
                    try:
                        # This will refresh the archived list if we're viewing from there
                        self.master.show_checked_out_clients()
                    except:
                        pass  # Ignore errors if we can't refresh

