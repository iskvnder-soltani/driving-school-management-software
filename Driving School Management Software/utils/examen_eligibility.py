from datetime import datetime, timedelta
import re

def get_examen_eligibility(birth_date):
    """
    Return examen eligibility based on age using new three-tier system.
    
    Args:
        birth_date: Birth date string in various formats or datetime.date object
        
    Returns:
        str: "none", "limited", or "all" based on eligibility
    """
    today = datetime.now().date()
    
    # Convert string to date if needed
    if isinstance(birth_date, str):
        # Try multiple date formats
        parsed_date = None
        
        # Format 1: DD/MM/YYYY
        try:
            parsed_date = datetime.strptime(birth_date, '%d/%m/%Y').date()
        except ValueError:
            parsed_date = None
        
        # Format 2: YYYY-MM-DD
        if parsed_date is None:
            try:
                parsed_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
            except ValueError:
                parsed_date = None
        
        # Format 3: DD-MM-YYYY
        if parsed_date is None:
            try:
                parsed_date = datetime.strptime(birth_date, '%d-%m-%Y').date()
            except ValueError:
                parsed_date = None
        
        # If all parsing attempts failed, try regex fallback
        if parsed_date is None:
            year_match = re.search(r'\b(19|20)\d{2}\b', birth_date)
            if year_match:
                birth_year = int(year_match.group())
                # Assume January 1st of birth year as fallback
                parsed_date = datetime(birth_year, 1, 1).date()
            else:
                # If date parsing fails, assume not eligible
                return "none"
        
        birth_date = parsed_date
    
    # Calculate exact ages
    age_17_6_months = birth_date + timedelta(days=365*17 + 183)  # 17.5 years
    age_18_years = birth_date + timedelta(days=365*18)  # 18 years
    
    if today < age_17_6_months:
        return "none"  # No examens allowed
    elif today < age_18_years:
        return "limited"  # Code + Créneau only
    else:
        return "all"  # All examens allowed

def is_eligible_for_driving_examens(birth_date):
    """
    Check if client is 17.5+ years old and eligible for driving examens (Créneau/Conduite).
    DEPRECATED: Use get_examen_eligibility() instead for new three-tier system.
    
    Args:
        birth_date: Birth date string in DD/MM/YYYY format or datetime.date object
        
    Returns:
        bool: True if client is 17.5+ years old, False otherwise
    """
    eligibility = get_examen_eligibility(birth_date)
    return eligibility in ["limited", "all"]

def get_available_examen_types_for_age(birth_date):
    """
    Get available examen types based on client's age using new three-tier system.
    
    Args:
        birth_date: Birth date string in DD/MM/YYYY format or datetime.date object
        
    Returns:
        list: List of available test types for the client
    """
    eligibility = get_examen_eligibility(birth_date)
    
    if eligibility == "none":
        return []  # No examens allowed
    elif eligibility == "limited":
        return ['Code', 'Créneau']  # Code + Créneau only
    else:  # "all"
        return ['Code', 'Créneau', 'Conduite']  # All examens allowed

def get_eligibility_display_text(birth_date):
    """
    Get human-readable eligibility text for display in profiles.
    
    Args:
        birth_date: Birth date string in DD/MM/YYYY format or datetime.date object
        
    Returns:
        str: French text describing eligibility
    """
    eligibility = get_examen_eligibility(birth_date)
    
    if eligibility == "none":
        return "Aucun examen"
    elif eligibility == "limited":
        return "Code, Créneau"
    else:  # "all"
        return "Tous les examens"

def filter_candidates_for_examen(examen_type, all_candidates):
    """
    Filter candidates based on examen type and age eligibility.
    
    Args:
        examen_type: Type of examen ('Code', 'Créneau', 'Conduite')
        all_candidates: List of candidate dictionaries with birth_date
        
    Returns:
        list: Filtered list of eligible candidates
    """
    eligible_candidates = []
    
    for candidate in all_candidates:
        birth_date = candidate.get('birth_date') or candidate.get('date_of_birth')
        if not birth_date:
            continue
            
        eligibility = get_examen_eligibility(birth_date)
        
        if eligibility == "none":
            continue  # Skip completely
        elif eligibility == "limited" and examen_type == "Conduite":
            continue  # Skip conduite for 17.6-18y
        else:
            eligible_candidates.append(candidate)
    
    return eligible_candidates
