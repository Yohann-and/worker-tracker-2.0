# QR Code Attendance System

## Overview

This is a Flask-based QR code attendance tracking system designed for monitoring worker presence. The application allows administrators to register workers, generate unique QR codes for each worker, and track attendance through QR code scanning. The system provides a simple web interface in French for managing workers and viewing attendance logs.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with Python
- **Database**: Replit DB (key-value store) for data persistence
- **Session Management**: Flask sessions with configurable secret key
- **Logging**: Python's built-in logging module for debugging

### Frontend Architecture
- **Templates**: Jinja2 templating engine with HTML templates
- **Styling**: Bootstrap 5 with dark theme and Font Awesome icons
- **Responsive Design**: Mobile-friendly interface with print styles for QR codes
- **Language**: French UI for all user-facing elements

### Data Storage
- **Primary Storage**: Replit DB with two main collections:
  - `workers`: Stores worker information (matricule, name, creation date)
  - `attendance`: Stores attendance records by worker ID with timestamps
- **Data Structure**: JSON-like key-value pairs with nested objects

## Key Components

### Worker Management
- **Registration**: Add new workers with unique matricule (ID) and full name
- **Validation**: Input validation for matricule format (alphanumeric only)
- **QR Code Generation**: Dynamic QR code creation using the `qrcode` library
- **Worker Listing**: View all registered workers with management options

### Attendance Tracking
- **QR Code Scanning**: Each worker gets a unique QR code linking to their attendance URL
- **Automatic Recording**: Attendance is recorded when the QR code URL is accessed
- **Timestamp Tracking**: Records both date and time of attendance
- **Duplicate Prevention**: Prevents multiple attendance records for the same day

### Reporting and Analytics
- **Daily Reports**: View attendance for specific dates
- **Statistics Dashboard**: Shows total workers and daily attendance counts
- **Attendance Log**: Comprehensive view of all attendance records

## Data Flow

1. **Worker Registration**: Admin adds worker → System generates unique QR code → Worker data stored in DB
2. **Attendance Recording**: Worker scans QR code → System validates worker → Attendance recorded with timestamp
3. **Report Generation**: Admin selects date → System queries attendance records → Displays statistics and worker lists

## External Dependencies

### Python Libraries
- **Flask**: Web framework for routing and request handling
- **qrcode**: QR code generation with PIL/Pillow for image processing
- **replit**: Database integration for persistent storage
- **base64/io**: Image encoding for QR code display

### Frontend Dependencies
- **Bootstrap 5**: CSS framework with dark theme variant
- **Font Awesome 6**: Icon library for UI elements
- **Custom CSS**: Mobile-responsive and print-friendly styles

### Environment Variables
- **SESSION_SECRET**: Flask session security (defaults to development key)

## Deployment Strategy

### Replit Platform
- **Main Entry Point**: `main.py` runs the Flask application
- **Development Mode**: Debug enabled for development environment
- **Port Configuration**: Runs on port 5000 with host binding to 0.0.0.0
- **Static Assets**: Served directly by Flask for CSS and other static files

### Database Initialization
- **Auto-setup**: Database collections are created automatically on first access
- **Data Persistence**: Replit DB provides persistent storage across restarts
- **No Migration Strategy**: Simple key-value structure doesn't require complex migrations

### Security Considerations
- **Session Security**: Configurable secret key for session management
- **Input Validation**: Basic validation on worker matricule format
- **No Authentication**: Currently designed for internal/trusted network use