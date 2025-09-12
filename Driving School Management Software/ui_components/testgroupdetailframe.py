class TestGroupDetailFrame(tk.Frame):
    EXAMEN_TYPES = ['Code', 'Créneau', 'Conduite']
    RESULT_OPTIONS = ['Passé', 'Échoué', 'Absent']
    def __init__(self, master, group_id, on_back):
        super().__init__(master)
        self.group_id = group_id
        self.on_back = on_back
        tk.Label(self, text='Détail du groupe d\'examen', font=('Arial', 28, 'bold')).pack(pady=20)
        
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
        
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text='Ajouter des candidats', font=('Arial', 16), command=self.add_candidates).pack(side='left', padx=10)
        tk.Button(btn_frame, text='Supprimer le groupe', font=('Arial', 16), command=self.delete_group).pack(side='left', padx=10)
        tk.Button(btn_frame, text='Enregistrer', font=('Arial', 16), command=self.save_changes).pack(side='left', padx=10)
        tk.Button(btn_frame, text='Imprimer la liste', font=('Arial', 16), command=self.print_table).pack(side='left', padx=10)
        tk.Button(btn_frame, text='Retour', font=('Arial', 16), command=on_back).pack(side='left', padx=10)
        self.load_group()
    
    def _center_inner_frame(self, event):
        """Center the inner frame within the canvas"""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        canvas_width = event.width
        self.inner_frame.update_idletasks()
        frame_width = self.inner_frame.winfo_reqwidth()
        x = max((canvas_width - frame_width) // 2, 0)
        self.canvas.coords(self.window_id, x, 0)
    
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
    def load_group(self):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('SELECT examen_date, license_type, centre_examen FROM examen_groups WHERE id=?', (self.group_id,))
            row = c.fetchone()
            examen_date = row[0] if row else ''
            license_type = row[1] if row and len(row) > 1 else ''
            centre_examen = row[2] if row and len(row) > 2 else ''
            tk.Label(self.inner_frame, text=f'Date de l\'examen : {examen_date}', font=('Arial', 20, 'bold')).grid(row=0, column=0, columnspan=7, sticky='w', pady=(0, 12))
            tk.Label(self.inner_frame, text=f'Type de permis : {license_type}', font=('Arial', 16), fg='#444').grid(row=1, column=0, columnspan=7, sticky='w', pady=(0, 12))
            tk.Label(self.inner_frame, text=f'Centre d\'examen : {centre_examen}', font=('Arial', 16), fg='#444').grid(row=2, column=0, columnspan=7, sticky='w', pady=(0, 12))
            # Table headers
            headers = ['N°', 'Nom et prénom', 'Date de naissance', 'Type d\'examen', 'Dernier examen', 'Résultat', 'Action']
            col_widths = [4, 18, 15, 12, 15, 10, 8]
            for j, h in enumerate(headers):
                tk.Label(self.inner_frame, text=h, font=('Arial', 14, 'bold'), bg='#e9e9e9', padx=8, pady=6, width=col_widths[j], borderwidth=1, relief='solid').grid(row=3, column=j, padx=1, pady=1, sticky='nsew')
            # Fetch candidates in group with last exam date
            c.execute('''SELECT tgc.candidate_id, cl.name, cl.date_of_birth, tgc.examen_type, tgc.result,
                         (SELECT MAX(examen_date) FROM examen_group_candidates egc 
                          JOIN examen_groups eg ON egc.group_id = eg.id 
                          WHERE egc.candidate_id = cl.id AND egc.result IS NOT NULL AND egc.result != '')
                         FROM examen_group_candidates tgc
                         JOIN clients cl ON tgc.candidate_id = cl.id
                         WHERE tgc.group_id=?''', (self.group_id,))
            self.candidates = []
            for i, row in enumerate(c.fetchall(), 1):
                cand_id, name, dob, examen_type, result, last_exam_date = row
                available_types = self.get_available_examen_types(cand_id, examen_type)
                var_type = tk.StringVar(value=examen_type if examen_type else (available_types[0] if available_types else ''))
                var_result = tk.StringVar(value=result if result else '')
                self.candidates.append({'id': cand_id, 'type_var': var_type, 'result_var': var_result, 'types': available_types})
                
                tk.Label(self.inner_frame, text=str(i), font=('Arial', 14), bg='white', width=col_widths[0], borderwidth=1, relief='solid').grid(row=i+3, column=0, padx=1, pady=1, sticky='nsew')
                tk.Label(self.inner_frame, text=name, font=('Arial', 14), bg='white', width=col_widths[1], borderwidth=1, relief='solid', anchor='w').grid(row=i+3, column=1, padx=1, pady=1, sticky='nsew')
                tk.Label(self.inner_frame, text=dob, font=('Arial', 14), bg='white', width=col_widths[2], borderwidth=1, relief='solid', anchor='w').grid(row=i+3, column=2, padx=1, pady=1, sticky='nsew')
                tk.Label(self.inner_frame, text=last_exam_date if last_exam_date else '', font=('Arial', 14), bg='white', width=col_widths[4], borderwidth=1, relief='solid', anchor='w').grid(row=i+3, column=4, padx=1, pady=1, sticky='nsew')
                
                # Handle test type selection based on available tests
                if available_types:
                    # Show combobox with available test types
                    opt = ttk.Combobox(self.inner_frame, values=available_types, textvariable=var_type, state='readonly', width=col_widths[3])
                    opt.grid(row=i+3, column=3, padx=1, pady=1, sticky='nsew')
                    opt.configure(font=('Arial', 14))
                    # Disable mouse wheel on combobox
                    opt.bind('<MouseWheel>', lambda e: 'break')
                else:
                    # Show label indicating all tests passed
                    label = tk.Label(self.inner_frame, text="Tout réussi", font=('Arial', 12), 
                                   bg='#e8f5e8', fg='#2d5a2d', width=col_widths[3], borderwidth=1, relief='solid')
                    label.grid(row=i+3, column=3, padx=1, pady=1, sticky='nsew')
                    # Disable result combobox since no test is available
                    var_result.set('')
                
                # Result combobox (only enable if test type is available)
                if available_types:
                    opt2 = ttk.Combobox(self.inner_frame, values=self.RESULT_OPTIONS, textvariable=var_result, state='readonly', width=col_widths[5])
                    opt2.grid(row=i+3, column=5, padx=1, pady=1, sticky='nsew')
                    opt2.configure(font=('Arial', 14))
                    # Disable mouse wheel on result combobox
                    opt2.bind('<MouseWheel>', lambda e: 'break')
                else:
                    # Disabled result combobox
                    opt2 = ttk.Combobox(self.inner_frame, values=[], textvariable=var_result, state='disabled', width=col_widths[5])
                    opt2.grid(row=i+3, column=5, padx=1, pady=1, sticky='nsew')
                    opt2.configure(font=('Arial', 14))
                
                # Add delete button
                delete_btn = tk.Button(self.inner_frame, text='Supprimer', font=('Arial', 12), bg='#ff4444', fg='white', 
                                     relief='flat', bd=0, padx=4, pady=2,
                                     command=lambda cid=cand_id: self.delete_candidate(cid))
                delete_btn.grid(row=i+3, column=6, padx=1, pady=1, sticky='nsew')
                # No hover effects - removed for consistency
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    def delete_group(self):
        if not messagebox.askyesno('Supprimer le groupe', 'Êtes-vous sûr de vouloir supprimer ce groupe ? Cette action est irréversible.'):
            return
        safe_db_operation(lambda c: c.execute('DELETE FROM examen_group_candidates WHERE group_id=?', (self.group_id,)))
        safe_db_operation(lambda c: c.execute('DELETE FROM examen_groups WHERE id=?', (self.group_id,)))
        messagebox.showinfo('Supprimé', 'Le groupe a été supprimé.')
        self.on_back()
    def delete_candidate(self, candidate_id):
        """Delete a candidate from the group after confirmation"""
        # Get candidate name for confirmation message
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('SELECT name FROM clients WHERE id=?', (candidate_id,))
            result = c.fetchone()
            candidate_name = result[0] if result else "ce candidat"
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
        
        # Show confirmation dialog
        if messagebox.askyesno('Supprimer le candidat', 
                              f'Êtes-vous sûr de vouloir supprimer {candidate_name} de ce groupe ?\n\nCette action ne supprime que l\'association avec le groupe, pas le candidat lui-même.'):
            safe_db_operation(lambda c: c.execute('DELETE FROM examen_group_candidates WHERE group_id=? AND candidate_id=?', 
                     (self.group_id, candidate_id)))
            messagebox.showinfo('Supprimé', f'{candidate_name} a été supprimé du groupe.\n\nLe candidat reste disponible pour d\'autres groupes.')
            # Refresh the table
            self.load_group()
    
    def add_candidates(self):
        self.master._switch_frame(AddCandidatesToGroupFrame(self.master, self.group_id, self.load_group, self.on_back))
    def save_changes(self):
        # Validate age restrictions before saving
        validation_errors = []
        
        for cand in self.candidates:
            examen_type = cand['type_var'].get()
            db_result = cand['result_var'].get()
            
            # Check age restrictions for driving examens using new three-tier system
            if examen_type in ['Créneau', 'Conduite']:
                conn = None
                try:
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute('SELECT date_of_birth FROM clients WHERE id=?', (cand['id'],))
                    birth_date = c.fetchone()
                    if birth_date and birth_date[0]:
                        eligibility = get_examen_eligibility(birth_date[0])
                        if eligibility == "none":
                            validation_errors.append(f"Le candidat ne peut pas être assigné à l'examen '{examen_type}' car il a moins de 17 ans 6 mois")
                        elif eligibility == "limited" and examen_type == "Conduite":
                            validation_errors.append(f"Le candidat ne peut pas être assigné à l'examen '{examen_type}' car il a moins de 18 ans (Conduite non autorisé)")
                except Exception as e:
                    if conn:
                        conn.rollback()
                    raise e
                finally:
                    if conn:
                        conn.close()
        
        # Show validation errors if any
        if validation_errors:
            error_message = "Erreurs de validation:\n\n" + "\n".join(validation_errors)
            messagebox.showerror('Erreur de validation', error_message)
            return
        
        # All validation passed, proceed with saving
        for cand in self.candidates:
            examen_type = cand['type_var'].get()
            db_result = cand['result_var'].get()
            
            # Only update if there's a valid exam type (not empty and not "Tout réussi")
            if examen_type and examen_type != "Tout réussi":
                safe_db_operation(lambda c: c.execute(
                    '''UPDATE examen_group_candidates SET examen_type=?, result=? WHERE group_id=? AND candidate_id=?''',
                    (examen_type, db_result, self.group_id, cand['id'])
                ))
            else:
                # If no valid exam type, clear the result as well
                safe_db_operation(lambda c: c.execute(
                    '''UPDATE examen_group_candidates SET examen_type=?, result=? WHERE group_id=? AND candidate_id=?''',
                    ('', '', self.group_id, cand['id'])
                ))
        
        messagebox.showinfo('Succès', 'Modifications enregistrées!')
        self.load_group()
    def print_table(self):
        import os
        from fpdf import FPDF
        
        # Database operations with error handling
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('SELECT examen_date, license_type, centre_examen FROM examen_groups WHERE id=?', (self.group_id,))
            row = c.fetchone()
            examen_date = row[0] if row else ''
            license_type = row[1] if row and len(row) > 1 else ''
            centre_examen = row[2] if row and len(row) > 2 else ''
            c.execute('''SELECT cl.name, cl.date_of_birth, tgc.examen_type, tgc.result,
                         (SELECT MAX(examen_date) FROM examen_group_candidates egc 
                          JOIN examen_groups eg ON egc.group_id = eg.id 
                          WHERE egc.candidate_id = cl.id AND egc.result IS NOT NULL AND egc.result != '')
                         FROM examen_group_candidates tgc
                         JOIN clients cl ON tgc.candidate_id = cl.id
                         WHERE tgc.group_id=?''', (self.group_id,))
            candidates = c.fetchall()
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ERROR] Database error in print_table: {e}")
            messagebox.showerror('Erreur de base de données', f'Impossible de récupérer les données: {str(e)}')
            return
        finally:
            if conn:
                conn.close()
        
        # PDF creation with error handling
        try:
            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.set_margins(8, 8, 8)  # Minimize margins: left, top, right
            pdf.add_page()

            # Set text color to black
            pdf.set_text_color(0, 0, 0)  # black: RGB(0, 0, 0)

            # School name header
            school_name = 'Auto-école Iskander'
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 8, school_name, ln=1, align='C')
            pdf.ln(2)
            
            # Main title
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 8, 'Liste des candidats du groupe d\'examen', ln=1, align='C')
            pdf.ln(3)
            
            # Form fields section
            pdf.set_font('Arial', '', 12)
            
            # First row: Centre d'examen, Date de l'examen, Type de permis
            pdf.cell(35, 8, 'Centre d\'examen :', 0, 0)
            pdf.cell(40, 8, centre_examen, 0, 0)  # Display the stored centre
            pdf.cell(35, 8, 'Date de l\'examen :', 0, 0)
            pdf.cell(40, 8, examen_date, 0, 0)
            pdf.cell(35, 8, 'Type de permis :', 0, 0)
            pdf.cell(0, 8, license_type, ln=1)
            
            # Second row: Nom et prénom de l'inspecteur
            pdf.cell(35, 8, 'Nom et prénom de l\'inspecteur :', 0, 0)
            pdf.cell(0, 8, '', ln=1)  # Space for writing
            
            pdf.ln(3)
            pdf.set_font('Arial', 'B', 12)
            headers = ['N°', 'Nom et prénom', 'Date de naissance', 'Type d\'examen', 'Dernier examen', 'Résultat']
            
            # Calculate dynamic column widths based on content
            col_widths = []
            pdf.set_font('Arial', 'B', 12)  # Bold for headers
            
            # First, calculate widths based on headers
            for header in headers:
                col_widths.append(pdf.get_string_width(header) + 4)  # Add padding
            
            # Then, check all data rows and adjust widths if needed
            pdf.set_font('Arial', '', 12)  # Regular font for data
            for idx, cand in enumerate(candidates, 1):
                name, dob, examen_type, result, last_exam_date = cand
                row_data = [str(idx), name, dob, last_exam_date if last_exam_date else '', examen_type, result]
                
                for i, val in enumerate(row_data):
                    text_width = pdf.get_string_width(str(val)) + 4  # Add padding
                    if text_width > col_widths[i]:
                        col_widths[i] = text_width
            
            # Check if total width exceeds page width and scale down if necessary
            row_height = 7
            table_width = sum(col_widths)
            page_width = pdf.w - 2 * pdf.l_margin
            
            if table_width > page_width:
                # Scale down all columns proportionally
                scale_factor = page_width / table_width
                col_widths = [int(width * scale_factor) for width in col_widths]
                table_width = sum(col_widths)
            
            left_margin = (page_width - table_width) / 2 + pdf.l_margin
            
            # Set border color to black
            pdf.set_draw_color(0, 0, 0)  # black: RGB(0, 0, 0)

            # Print headers
            pdf.set_font('Arial', 'B', 12)
            pdf.set_x(left_margin)
            for i, h in enumerate(headers):
                pdf.cell(col_widths[i], row_height, str(h), border=1, align='C')
            pdf.ln(row_height)
            
            # Print data rows
            pdf.set_font('Arial', '', 10)
            for idx, cand in enumerate(candidates, 1):
                name, dob, examen_type, result, last_exam_date = cand
                row_data = [str(idx), name, dob, examen_type, last_exam_date if last_exam_date else '', result]
                pdf.set_x(left_margin)
                for i, val in enumerate(row_data):
                    pdf.cell(col_widths[i], row_height, str(val), border=1, align='C')
                pdf.ln(row_height)
        except ImportError as e:
            error_msg = f"Erreur d'importation de la bibliothèque PDF: {str(e)}"
            print(f"[ERROR] {error_msg}")
            messagebox.showerror('Erreur de bibliothèque', error_msg)
            return
        except Exception as e:
            error_msg = f"Erreur lors de la création du PDF: {str(e)}"
            print(f"[ERROR] {error_msg}")
            messagebox.showerror('Erreur de création PDF', error_msg)
            return
        
        # Directory creation with comprehensive error handling
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
            messagebox.showerror('Erreur de permissions', error_msg)
            return
        
        # File path creation with validation
        safe_date = examen_date.replace('/', '-')
        filename = os.path.join(receipts_dir, f'groupe_{safe_date}.pdf')
        filename = os.path.abspath(filename)
        
        # Check if filename is too long
        if len(filename) > 250:
            error_msg = "Nom de fichier trop long - impossible de sauvegarder"
            print(f"[ERROR] {error_msg}: {len(filename)} characters")
            messagebox.showerror('Erreur de nom de fichier', error_msg)
            return
        
        # PDF output with comprehensive error handling
        try:
            pdf.output(filename)
            print(f'[DEBUG] PDF saved at: {filename}')
            messagebox.showinfo('PDF généré', f'PDF sauvegardé sous :\n{filename}')
        except PermissionError:
            error_msg = "Impossible de sauvegarder le PDF - permissions insuffisantes"
            print(f"[ERROR] {error_msg}")
            messagebox.showerror('Erreur de permissions', error_msg)
            return
        except OSError as e:
            if "No space left on device" in str(e):
                error_msg = "Espace disque insuffisant pour sauvegarder le PDF"
                print(f"[ERROR] {error_msg}: {e}")
                messagebox.showerror('Espace disque insuffisant', error_msg)
            else:
                error_msg = f"Erreur système lors de la sauvegarde: {str(e)}"
                print(f"[ERROR] {error_msg}")
                messagebox.showerror('Erreur système', error_msg)
            return
        except Exception as e:
            error_msg = f"Erreur inattendue lors de la sauvegarde: {str(e)}"
            print(f"[ERROR] {error_msg}")
            messagebox.showerror('Erreur de sauvegarde', error_msg)
            return
        
        # Open PDF with comprehensive error handling
        try:
            os.startfile(filename)
        except PermissionError:
            error_msg = "Impossible d'ouvrir le PDF - permissions insuffisantes"
            print(f"[ERROR] {error_msg}")
            try:
                os.startfile(receipts_dir)
                messagebox.showwarning('Permissions insuffisantes', 
                                    f"{error_msg}\nLe dossier des reçus a été ouvert à la place.")
            except Exception:
                messagebox.showerror('Erreur de permissions', 
                                   f"{error_msg}\nImpossible d'ouvrir le dossier des reçus.")
        except FileNotFoundError:
            error_msg = "Fichier PDF introuvable après sauvegarde"
            print(f"[ERROR] {error_msg}")
            try:
                os.startfile(receipts_dir)
                messagebox.showwarning('Fichier introuvable', 
                                    f"{error_msg}\nLe dossier des reçus a été ouvert à la place.")
            except Exception:
                messagebox.showerror('Erreur de fichier', 
                                   f"{error_msg}\nImpossible d'ouvrir le dossier des reçus.")
        except Exception as e:
            error_msg = f"Impossible d'ouvrir le PDF: {str(e)}"
            print(f"[ERROR] {error_msg}")
            try:
                os.startfile(receipts_dir)
                messagebox.showwarning('Erreur d\'ouverture', 
                                    f"{error_msg}\nLe dossier des reçus a été ouvert à la place.")
            except Exception:
                messagebox.showerror('Erreur d\'ouverture', 
                                   f"{error_msg}\nImpossible d'ouvrir le dossier des reçus.")
    def get_available_examen_types(self, candidate_id, current_type=None):
        """Get available test types for a candidate based on their exam history and age.
        Only returns test types that the candidate hasn't passed yet and is eligible for based on age."""
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            # Get candidate's birth date and test history
            c.execute('''SELECT cl.date_of_birth, tgc.examen_type, tgc.result 
                         FROM clients cl
                         LEFT JOIN examen_group_candidates tgc ON cl.id = tgc.candidate_id 
                         LEFT JOIN examen_groups tg ON tgc.group_id = tg.id 
                         WHERE cl.id = ? 
                         ORDER BY tg.examen_date DESC, tg.id DESC''', (candidate_id,))
            
            rows = c.fetchall()
            if not rows:
                return []
            
            birth_date = rows[0][0]  # First row contains birth date
            test_history = [(row[1], row[2]) for row in rows if row[1]]  # Filter out None test types
            
            # Find which exam types the candidate has passed
            passed_examens = set()
            for examen_type, result in test_history:
                if result == 'Passé':
                    passed_examens.add(examen_type)
            
            # Get age-based available exam types
            age_available_types = get_available_examen_types_for_age(birth_date)
            
            # Filter by both age eligibility and not yet passed
            available_types = [examen_type for examen_type in age_available_types if examen_type not in passed_examens]
            
            # If current_type is set and not in available_types, add it back (for editing existing assignments)
            if current_type and current_type not in available_types and current_type in age_available_types:
                available_types.append(current_type)
            
            return available_types
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

