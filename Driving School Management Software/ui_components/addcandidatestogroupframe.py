class AddCandidatesToGroupFrame(tk.Frame):
    def __init__(self, master, group_id, on_save, on_cancel):
        super().__init__(master)
        self.group_id = group_id
        self.on_save = on_save
        self.on_cancel = on_cancel
        # Store candidate card references for easy removal
        self.candidate_cards = {}  # {candidate_id: card_widget}
        
        tk.Label(self, text='Ajouter des candidats au groupe', font=('Arial', 28, 'bold')).pack(pady=20)
        form = tk.Frame(self)
        form.pack(pady=10)
        tk.Label(form, text='Nom et prénom ou téléphone :', font=('Arial', 18)).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.search_entry = tk.Entry(form, font=('Arial', 18), width=20)
        self.search_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        tk.Button(form, text='Rechercher', font=('Arial', 16), command=self.update_candidates).grid(row=0, column=2, padx=5)
        self.candidates_frame = tk.Frame(self)
        self.candidates_frame.pack(pady=10, fill='both', expand=True)
        self.candidate_vars = []
        # Add a canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(self.candidates_frame, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.candidates_frame, orient='vertical', command=self.canvas.yview)
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
        self.inner_frame = tk.Frame(self.candidates_frame)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner_frame, anchor='n')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.inner_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', self._center_inner_frame)
        # Bind mouse wheel to canvas for scrolling anywhere in the frame
        self.bind_all('<MouseWheel>', self._on_mousewheel)
        self.update_candidates()
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20, fill='x')
        # Center the Annuler button at the bottom
        tk.Button(btn_frame, text='Annuler', font=('Arial', 16), command=self.back_to_group_details).pack(anchor='center', pady=0)

    def _center_inner_frame(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        canvas_width = event.width
        self.inner_frame.update_idletasks()
        frame_width = self.inner_frame.winfo_reqwidth()
        x = max((canvas_width - frame_width) // 2, 0)
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
        if hasattr(self, 'inner_frame'):
            self.inner_frame.destroy()
            self.inner_frame = None
        
        if hasattr(self, 'candidates_frame'):
            self.candidates_frame.destroy()
            self.candidates_frame = None
        
        # Clear other references
        if hasattr(self, 'search_entry'):
            self.search_entry = None
        
        super().destroy()

    def update_candidates(self):
        # Clear previous candidate card references
        self.candidate_cards.clear()
        
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        query = self.search_entry.get().strip()
        
        # Validate search query if provided
        if query and len(query.strip()) < 2:
            show_validation_error('Recherche trop courte', 'La recherche doit contenir au moins 2 caractères.')
            self.search_entry.focus_set()
            return
        
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            # Get the test date for the current group
            c.execute('SELECT examen_date FROM examen_groups WHERE id=?', (self.group_id,))
            current_test_date = c.fetchone()
            if not current_test_date:
                messagebox.showerror('Erreur', 'Groupe de test non trouvé.')
                return
            
            current_test_date = current_test_date[0]
            
            # Only show candidates not already in this group AND not assigned to any other group on the same test date
            # AND who have at least one test type they haven't passed yet AND are eligible for the test type
            if query:
                search_pattern = f'%{query}%'
                c.execute("""SELECT id, name, date_of_birth, place_of_birth, license_type, phone 
                             FROM clients 
                             WHERE checked_out=0 
                             AND (name LIKE ? OR phone LIKE ?) 
                             AND id NOT IN (SELECT candidate_id FROM examen_group_candidates WHERE group_id=?) 
                             AND id NOT IN (
                                 SELECT tgc.candidate_id 
                                 FROM examen_group_candidates tgc 
                                 JOIN examen_groups tg ON tgc.group_id = tg.id 
                                 WHERE tg.examen_date = ?
                             )
                             AND id NOT IN (
                                 -- Candidates who have passed all three test types
                                 SELECT candidate_id FROM (
                                     SELECT tgc.candidate_id, COUNT(*) as passed_count
                                     FROM examen_group_candidates tgc 
                                     JOIN examen_groups tg ON tgc.group_id = tg.id 
                                     WHERE tgc.result = 'Passé'
                                     GROUP BY tgc.candidate_id
                                     HAVING passed_count >= 3
                                 )
                             )
                             ORDER BY name""", (search_pattern, search_pattern, self.group_id, current_test_date))
            else:
                c.execute("""SELECT id, name, date_of_birth, place_of_birth, license_type, phone 
                             FROM clients 
                             WHERE checked_out=0 
                             AND id NOT IN (SELECT candidate_id FROM examen_group_candidates WHERE group_id=?) 
                             AND id NOT IN (
                                 SELECT tgc.candidate_id 
                                 FROM examen_group_candidates tgc 
                                 JOIN examen_groups tg ON tgc.group_id = tg.id 
                                 WHERE tg.examen_date = ?
                             )
                             AND id NOT IN (
                                 -- Candidates who have passed all three test types
                                 SELECT candidate_id FROM (
                                     SELECT tgc.candidate_id, COUNT(*) as passed_count
                                     FROM examen_group_candidates tgc 
                                     JOIN examen_groups tg ON tgc.group_id = tg.id 
                                     WHERE tgc.result = 'Passé'
                                     GROUP BY tgc.candidate_id
                                     HAVING passed_count >= 3
                                 )
                             )
                             ORDER BY name""", (self.group_id, current_test_date))
            
            candidates = c.fetchall()
            for idx, row in enumerate(candidates):
                candidate_id, name, dob, pob, license_type, phone = row
                
                # Get available test types for this candidate based on age
                age_available_types = get_available_examen_types_for_age(dob)
                
                # Get passed exam types for this candidate
                passed_examens = set()
                c.execute("""SELECT examen_type, result FROM examen_group_candidates tgc 
                             JOIN examen_groups tg ON tgc.group_id = tg.id 
                             WHERE tgc.candidate_id=? AND tgc.result = 'Passé'""", (candidate_id,))
                passed_results = c.fetchall()
                for examen_type, result in passed_results:
                    if result == 'Passé':
                        passed_examens.add(examen_type)
                
                # Filter out passed exams from available types
                available_examen_types = [examen_type for examen_type in age_available_types if examen_type not in passed_examens]
                
                # Skip candidates who have no available exam types (all passed or age-restricted)
                if not available_examen_types:
                    continue
                
                # Create candidate data for the shared card function
                # Show available exam types (only those not yet passed)
                exam_types_text = ", ".join(available_examen_types)
                eligibility = get_examen_eligibility(dob)
                if eligibility == "none":
                    exam_types_text = "Aucun examen - <17.5 ans"
                elif eligibility == "limited" and not available_examen_types:
                    exam_types_text = "Tous les examens passés - <18 ans"
                elif not available_examen_types:
                    exam_types_text = "Tous les examens passés"
                
                candidate_data = {
                    'name': name,
                    'phone': phone,
                    'license_type': license_type,
                    'additional_info': f"Date de naissance: {dob}",
                    'second_info': f"Examens disponibles: {exam_types_text}"
                }
                
                # Use shared card creation function for consistent design
                # Pass the command directly instead of a pre-created button
                card = create_candidate_card(
                    self.inner_frame, 
                    candidate_data, 
                    action_command=lambda r=row: self.save_single_candidate(r),
                    action_text="Ajouter au groupe"
                )
                
                # Store reference to the candidate card for easy removal
                self.candidate_cards[candidate_id] = card
            
            # Show message if no candidates found
            if not self.candidate_cards:
                self.show_no_candidates_message(query)
                
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def show_no_candidates_message(self, search_query=None):
        """
        Show a message when no candidates are found during search.
        """
        # Clear the inner frame and show a message
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        
        # Create a centered message
        message_frame = tk.Frame(self.inner_frame)
        message_frame.pack(expand=True, fill='both')
        
        # Center the message
        message_frame.grid_rowconfigure(0, weight=1)
        message_frame.grid_rowconfigure(2, weight=1)
        message_frame.grid_columnconfigure(0, weight=1)
        message_frame.grid_columnconfigure(2, weight=1)
        
        if search_query:
            message_text = f"Aucun candidat trouvé pour la recherche: '{search_query}'"
        else:
            message_text = "Aucun candidat disponible pour ce groupe"
        
        message_label = tk.Label(
            message_frame, 
            text=message_text, 
            font=('Arial', 16),
            fg='#666'
        )
        message_label.grid(row=1, column=1, sticky='nsew')
        
        # Add suggestions
        suggestions_frame = tk.Frame(message_frame)
        suggestions_frame.grid(row=2, column=1, pady=20)
        
        suggestions_text = """Suggestions:
• Vérifiez l'orthographe du nom ou numéro de téléphone
• Essayez une recherche plus courte
• Tous les candidats disponibles ont peut-être déjà été ajoutés
• Vérifiez les restrictions d'âge pour les examens"""
        
        suggestions_label = tk.Label(
            suggestions_frame, 
            text=suggestions_text, 
            font=('Arial', 12),
            fg='#888',
            justify='left'
        )
        suggestions_label.pack()
    def save_single_candidate(self, row):
        # Check if candidate is already assigned to another group on the same test date
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            # Get the test date for the current group
            c.execute('SELECT examen_date FROM examen_groups WHERE id=?', (self.group_id,))
            current_test_date = c.fetchone()
            if not current_test_date:
                messagebox.showerror('Erreur', 'Groupe de test non trouvé.')
                return
            
            current_test_date = current_test_date[0]
            
            # Check if candidate is already assigned to another group on the same test date
            c.execute('''SELECT tg.examen_date, tg.id 
                         FROM examen_group_candidates tgc 
                         JOIN examen_groups tg ON tgc.group_id = tg.id 
                         WHERE tgc.candidate_id = ? AND tg.examen_date = ? AND tgc.group_id != ?''', 
                      (row[0], current_test_date, self.group_id))
            
            existing_assignment = c.fetchone()
            if existing_assignment:
                messagebox.showerror('Erreur', 
                                   f"{row[1]} est déjà assigné à un autre groupe pour le test du {current_test_date}.\n\n"
                                   "Un candidat ne peut pas être assigné à plusieurs groupes le même jour.")
                return
            
            # Check age eligibility for the test group using new three-tier system
            birth_date = row[2]  # date_of_birth from row
            eligibility = get_examen_eligibility(birth_date)
            
            if eligibility == "none":
                messagebox.showerror('Erreur', 
                                   f"{row[1]} n'est pas éligible pour aucun test car il a moins de 17 ans 6 mois.")
                return
            
            # Get available test types for display purposes
            available_examen_types = get_available_examen_types_for_age(birth_date)
            
            # If no conflict, proceed with adding the candidate
            safe_db_operation(lambda c: c.execute('INSERT INTO examen_group_candidates (group_id, candidate_id, examen_type, result) VALUES (?, ?, ?, ?)', 
                      (self.group_id, row[0], '', '')))
            
            # Show success message
            messagebox.showinfo('Succès', f"{row[1]} ajouté au groupe!")
            
            # Remove the candidate card from the display to prevent duplicate additions
            self.remove_candidate_card(row[0])
            
            # Refresh the candidates list to update the display
            self.update_candidates()
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def remove_candidate_card(self, candidate_id):
        """
        Remove a specific candidate card from the display after successful addition.
        This prevents duplicate additions and provides visual feedback.
        """
        if candidate_id in self.candidate_cards:
            # Remove the card widget from the display
            card_widget = self.candidate_cards[candidate_id]
            card_widget.destroy()
            
            # Remove the reference from our dictionary
            del self.candidate_cards[candidate_id]
            
            print(f"[DEBUG] Removed candidate card for ID: {candidate_id}")
            
            # Check if all candidates have been added
            if not self.candidate_cards:
                self.show_all_candidates_added_message()
        else:
            print(f"[WARNING] Candidate card not found for ID: {candidate_id}")
    
    def show_all_candidates_added_message(self):
        """
        Show a message when all candidates have been added to the group.
        This provides clear feedback to the user.
        """
        # Clear the inner frame and show a message
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        
        # Create a centered message
        message_frame = tk.Frame(self.inner_frame)
        message_frame.pack(expand=True, fill='both')
        
        # Center the message
        message_frame.grid_rowconfigure(0, weight=1)
        message_frame.grid_rowconfigure(2, weight=1)
        message_frame.grid_columnconfigure(0, weight=1)
        message_frame.grid_columnconfigure(2, weight=1)
        
        message_label = tk.Label(
            message_frame, 
            text="✅ Tous les candidats disponibles ont été ajoutés au groupe!", 
            font=('Arial', 18, 'bold'),
            fg='green'
        )
        message_label.grid(row=1, column=1, sticky='nsew')
        
        # Add a button to return to group details
        button_frame = tk.Frame(message_frame)
        button_frame.grid(row=2, column=1, pady=20)
        
        tk.Button(
            button_frame, 
            text='Retour aux détails du groupe', 
            font=('Arial', 16), 
            command=self.back_to_group_details
        ).pack()
    def back_to_group_details(self):
        """Return to the group details view"""
        # Switch back to the TestGroupDetailFrame for this group
        self.master._switch_frame(TestGroupDetailFrame(self.master, self.group_id, self.on_cancel))
    
    def save_candidates(self):
        # This function is now unused but kept for compatibility
        pass



