# Face Recognition Attendance System

A Django-based attendance management system leveraging facial recognition technology to streamline attendance tracking in educational institutions.

## Features

- **Facial Recognition**: Automates attendance marking using face detection and recognition.
- **Multi-Role Access**: Provides distinct interfaces for students, faculty, and administrators.
- **Timetable Management**: Facilitates weekly and daily timetable creation and viewing.
- **Attendance Analytics**: Generates attendance reports with visual insights.
- **Secure Data Storage**: Stores facial data securely with custom folder structures.

## Technology Stack

- **Backend**: Python 3.x, Django 4.1
- **Frontend**: HTML, CSS (Tailwind), JavaScript
- **Database**: PostgreSQL
- **Facial Recognition**: OpenCV, dlib, face-recognition library

## Installation Guide

### Prerequisites

- Python 3.8 or above
- PostgreSQL database
- Virtual environment tool (optional)

### Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/attendance-system.git
   cd attendance-system
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Database**:
   - Update `settings.py` with your PostgreSQL credentials.
   - Run migrations:
     ```bash
     python manage.py migrate
     ```

5. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Start Development Server**:
   ```bash
   python manage.py runserver
   ```

7. **Access Application**:
   - Admin: `http://127.0.0.1:8000/admin`
   - Application: `http://127.0.0.1:8000`

## Project Structure

```
attendance_system/
├── core/                # Main application logic
├── media/               # Facial data and uploads
├── static/              # Static files
├── templates/           # HTML templates
├── requirements.txt     # Dependency list
└── manage.py            # Django project entry point
```

## Usage Guide

1. **Admin Panel**:
   - Configure timetables, faculty accounts, and other settings.

2. **Student Registration**:
   - Students sign up and upload face images for recognition.

3. **Attendance**:
   - Faculty uploads images or uses live video for attendance marking.

4. **Reports**:
   - Generate analytics for attendance trends and individual performance.

## Key Modules

- **Face Recognition**: Captures and processes facial data for training and recognition.
- **Analytics**: Uses Pandas for generating detailed attendance summaries.
- **Timetable Management**: Allows dynamic creation and viewing of schedules.

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit changes (`git commit -m "Feature description"`).
4. Push to your fork (`git push origin feature-name`).
5. Open a pull request.


---