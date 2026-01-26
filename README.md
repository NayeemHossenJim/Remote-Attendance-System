# Remote Attendance System

A production-ready FastAPI-based remote attendance system with GPS location tracking, following a comprehensive workflow for employee check-ins.

## Features

### 🔐 Authentication & User Management
- User registration with Office ID and password
- GPS location capture during registration (saved as home location)
- 50-meter radius validation for check-ins
- Password reset functionality
- JWT-based authentication
- Role-based access (Employee/Team Lead)

### ⏰ Check-In Flow (Following Flowchart)

#### **08:00 - 09:30 Window:**
- System captures GPS location
- Validates location against registered home location (50m radius)
- **If location matches:**
  - ✅ Enable Check-In Button
  - ✅ Mark Present
  - ✅ Notify Employee
  
- **If location doesn't match:**
  - ❌ Disable Check-In Button
  - ❌ Show Location Error
  - ❌ Mark Absent

#### **After 09:30:**
- ❌ Disable Check-In Button
- ❌ Mark Absent (automatically)
- ✅ Enable "Request for Present" option
- 📝 Submit request form with reason
- ⏳ Status: Pending Team Lead Approval

### 👔 Team Lead Features
- View pending late check-in requests
- Approve or reject requests
- Add comments when rejecting

### 📊 Additional Features
- Attendance history tracking
- Distance calculation from home location
- Modern, responsive UI
- Real-time GPS location capture using browser Navigator API

## Project Structure

```
Remote-Attendance-System/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── attendance.py         # Attendance endpoints
│   │   └── dependencies.py       # JWT auth dependencies
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Settings & configuration
│   │   ├── geo.py                # GPS distance calculations
│   │   ├── security.py           # Password hashing & JWT
│   │   └── time.py               # Time window validation
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py               # SQLAlchemy base
│   │   └── session.py            # Database session
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py               # User model
│   │   └── attendance.py          # Attendance model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py               # Auth Pydantic schemas
│   │   └── attendance.py         # Attendance schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py       # Auth business logic
│   │   └── attendance_service.py # Attendance business logic
│   └── main.py                   # FastAPI app
├── frontend/
│   └── index.html                # Complete UI
├── requirements.txt
└── README.md
```

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Remote-Attendance-System
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file:
```env
DATABASE_URL=sqlite:///./attendance.db
SECRET_KEY=your-secret-key-change-in-production
CHECK_IN_START_HOUR=8
CHECK_IN_START_MINUTE=0
CHECK_IN_END_HOUR=9
CHECK_IN_END_MINUTE=30
DEFAULT_RADIUS_METERS=50
```

5. **Run the application**
```bash
uvicorn app.main:app --reload
```

The application will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user with GPS location
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/password-reset-request` - Request password reset
- `POST /api/auth/password-reset` - Reset password with token
- `GET /api/auth/me` - Get current user info (requires auth)

### Attendance
- `POST /api/attendance/check-in` - Check-in with GPS location (requires auth)
- `POST /api/attendance/late-check-in-request` - Submit late check-in request (requires auth)
- `POST /api/attendance/approve-request` - Approve/reject request (Team Lead only)
- `GET /api/attendance/history` - Get attendance history (requires auth)
- `GET /api/attendance/pending-approvals` - Get pending requests (Team Lead only)

## Usage

### 1. Registration
1. Navigate to the application
2. Click "Register"
3. Fill in Office ID, Password, and optional Email
4. Click "Get My Location" to capture GPS coordinates
5. Submit registration

### 2. Check-In (08:00 - 09:30)
1. Login with Office ID and Password
2. Click "Check-In" button
3. System validates GPS location
4. If within 50m radius: Marked as Present
5. If outside radius: Marked as Absent with error message

### 3. Late Check-In Request (After 09:30)
1. After 09:30, check-in button is disabled
2. System automatically marks as Absent
3. "Late Check-In Request" form appears
4. Fill in reason and submit
5. Request status: Pending Team Lead Approval

### 4. Team Lead Approval
1. Team Lead logs in
2. Navigate to "Approvals" section
3. View pending requests
4. Approve or Reject with optional comment

## Technology Stack

- **Backend:** FastAPI
- **Database:** SQLAlchemy (supports SQLite, PostgreSQL, etc.)
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt (passlib)
- **Frontend:** Vanilla JavaScript with modern CSS
- **GPS:** Browser Navigator Geolocation API

## Production Considerations

1. **Security:**
   - Change `SECRET_KEY` in production
   - Use environment variables for sensitive data
   - Enable HTTPS
   - Implement rate limiting
   - Add email service for password reset

2. **Database:**
   - Use PostgreSQL for production
   - Set up database migrations (Alembic)
   - Regular backups

3. **Deployment:**
   - Use Gunicorn or Uvicorn workers
   - Set up reverse proxy (Nginx)
   - Configure CORS properly
   - Use environment-specific settings

4. **Monitoring:**
   - Add logging
   - Set up error tracking (Sentry)
   - Monitor API performance

## License

See LICENSE file for details.
