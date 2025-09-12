# 🚗 Driving School Management Software

A comprehensive Python desktop application for managing driving school operations, built with Tkinter and featuring a modular, well-organized codebase.

## ✨ Features

### 🎯 Core Functionality
- **Client Management** - Add, edit, view, and archive client profiles
- **Payment Processing** - Track payments with automatic receipt generation
- **Test Group Management** - Organize and manage examination groups
- **Statistics Dashboard** - View comprehensive application statistics
- **PDF Generation** - Generate receipts, tables, and reports
- **Data Archiving** - Archive completed clients for record keeping

### 🏗️ Technical Features
- **Modular Architecture** - Clean separation of concerns
- **Database Integration** - SQLite database for data persistence
- **Input Validation** - Comprehensive data validation
- **Error Handling** - Robust error handling throughout
- **PDF Export** - Professional PDF generation for receipts and reports
- **Modern UI** - User-friendly interface with Tkinter

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Required Python packages (see requirements below)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/driving-school-management-software.git
   cd driving-school-management-software
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python run_app.py
   ```

## 📁 Project Structure

```
driving-school-management-software/
├── main/
│   └── main_app.py              # Main application class
├── ui_components/               # All UI frames
│   ├── homeframe.py            # Home dashboard
│   ├── addclientframe.py       # Add new client
│   ├── clientprofileframe.py   # Client profile management
│   ├── testgroupdetailframe.py # Test group management
│   └── ... (other UI components)
├── utils/                       # Utility functions
│   ├── formatting.py           # Data formatting utilities
│   ├── candidate_cards.py      # UI card components
│   └── examen_eligibility.py   # Examination eligibility logic
├── database/                    # Database operations
│   ├── config.py               # Database configuration
│   └── operations.py           # Database operations
├── validation/                  # Input validation
│   └── validators.py           # Validation functions
├── imports.py                  # Global imports and constants
├── run_app.py                  # Application entry point
└── README.md                   # This file
```

## 🛠️ Dependencies

### Required Packages
- `tkinter` - GUI framework (included with Python)
- `sqlite3` - Database (included with Python)
- `fpdf` - PDF generation
- `PIL` (Pillow) - Image processing
- `datetime` - Date/time handling (included with Python)
- `functools` - Function utilities (included with Python)
- `re` - Regular expressions (included with Python)

### Install Dependencies
```bash
pip install fpdf pillow
```

## 📖 Usage Guide

### Adding a New Client
1. Click "Ajouter un candidat" from the home screen
2. Fill in client information (name, phone, address, etc.)
3. Click "Enregistrer" to save the client

### Processing Payments
1. Navigate to a client's profile
2. Click "Ajouter un paiement"
3. Enter the payment amount
4. The system will automatically generate a receipt

### Managing Test Groups
1. Click "Groupes d'examens" from the home screen
2. Click "Ajouter un groupe" to create a new test group
3. Add candidates to the group
4. Manage examination results

### Viewing Statistics
- The home screen displays key statistics
- View total clients, payments, and test groups
- Track application performance

## 🔧 Development

### Code Organization
The application follows a modular architecture:
- **UI Components** - All user interface elements
- **Database Layer** - Data persistence and operations
- **Validation Layer** - Input validation and error handling
- **Utilities** - Helper functions and common operations
- **Main Application** - Core application logic

### Adding New Features
1. Create new UI components in `ui_components/`
2. Add database operations in `database/`
3. Implement validation in `validation/`
4. Update the main application to integrate new features

## 📊 Database Schema

The application uses SQLite with the following main tables:
- `clients` - Client information
- `payments` - Payment records
- `test_groups` - Examination groups
- `candidates` - Group candidates
- `sessions` - Training sessions

## 🎨 UI Components

### Main Screens
- **Home Dashboard** - Statistics and navigation
- **Client List** - Browse all clients
- **Client Profile** - Detailed client management
- **Test Groups** - Examination group management
- **Archived Clients** - Completed client records

### Key Features
- **Search Functionality** - Find clients quickly
- **Data Validation** - Ensure data integrity
- **PDF Generation** - Professional document creation
- **Responsive Design** - Clean, modern interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Iskander SOLTANI** - *Driving School Management Software*

## 🙏 Acknowledgments

- Built with Python and Tkinter
- PDF generation with FPDF
- Database management with SQLite
- Modular architecture for maintainability

## 📞 Support

For support or questions, please open an issue in the GitHub repository.
