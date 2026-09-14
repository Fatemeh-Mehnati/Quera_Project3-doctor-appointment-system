# 🏥 Doctor Appointment System

A web-based doctor appointment system developed as part of **Quera Bootcamp Project 3**.

The system allows users to register and log in, search for doctors, view available appointment slots, book appointments, manage their wallet, and submit reviews and ratings after visiting a doctor.

---

## ✨ Features

### 👤 Authentication & Accounts

- User registration and login
- Logout
- Custom user management
- Email-based OTP login
- OTP expiration
- OTP session management
- Protected pages for authenticated users

### 👨‍⚕️ Doctors

- Doctor listing
- Doctor detail page
- Doctor search
- Search by doctor name
- Search and filtering by specialty
- Pagination
- Display doctor consultation fee
- Display doctor rating and reviews
- Display available appointment slots

### 📅 Appointments

- Create and manage doctor time slots
- Display available slots
- Book appointments
- View user's appointments
- Cancel appointments
- Refund appointment cost after cancellation
- Email confirmation for successful bookings
- Protection against double booking

### 💰 Wallet & Transactions

- View wallet balance
- Charge wallet
- Withdraw from wallet
- Appointment payment using wallet
- Transaction history
- Prevention of negative wallet balance
- Atomic balance updates

### ⭐ Reviews & Ratings

- Submit reviews for doctors
- Rate doctors from 1 to 5
- Display reviews
- Calculate average doctor rating
- Prevent duplicate reviews
- Allow reviews only from users who have actually visited the doctor

### 🛠 Admin Panel

The project uses Django Admin for managing:

- Users
- Doctors
- Specialties
- Time slots
- Appointments
- Wallets
- Transactions
- Reviews

---

# 🧱 Project Architecture

The project is implemented using Django's **MVT (Model - View - Template)** architecture.

```text
Quera_Project3-doctor-appointment-system/
│
├── accounts/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── appointments/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── doctors/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── templates/
│   ├── accounts/
│   ├── appointments/
│   ├── doctors/
│   └── ...
│
├── documents/
│   ├── ERD.png
│   ├── erd-notes.md
│   ├── api-routes.md
│   └── manual-test-report.md
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── manage.py
└── README.md
```

---

# 🧩 Project Applications

| Application | Responsibility |
|---|---|
| `accounts` | Users, authentication, OTP, wallet and transactions |
| `doctors` | Doctors, specialties, search, reviews and ratings |
| `appointments` | Time slots, booking, cancellation and payments |
| `config` | Main Django settings and project URLs |
| `templates` | User interface and HTML templates |
| `documents` | Project documentation and testing reports |

---

# 🛠 Technologies

- Python 3.13
- Django 6.1
- PostgreSQL 16
- SQLite
- Docker
- Docker Compose
- python-decouple
- HTML / CSS
- Django MVT Architecture

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/Fatemeh-Mehnati/Quera_Project3-doctor-appointment-system.git
cd Quera_Project3-doctor-appointment-system
```

The main branch is:

```bash
git checkout main
git pull origin main
```

---

## 2. Create a virtual environment

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Environment Variables

Create a `.env` file based on `.env.example`.

Example:

```env
SECRET_KEY=your-secret-key
DEBUG=True

ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.postgresql
DB_NAME=appointment_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

OTP_EXPIRY_SECONDS=120
```

For local development, Django's console email backend can be used to display OTP and email messages directly in the terminal.

---

# 🗄 Database

Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create a superuser:

```bash
python manage.py createsuperuser
```

---

# ▶️ Run Without Docker

Start the Django development server:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Django Admin:

```text
http://127.0.0.1:8000/admin/
```

---

# 🐳 Run With Docker

The project includes both `Dockerfile` and `docker-compose.yml`.

Build and start the containers:

```bash
docker compose up --build
```

Or run in detached mode:

```bash
docker compose up --build -d
```

Check running containers:

```bash
docker compose ps
```

View web application logs:

```bash
docker compose logs web
```

The application will be available at:

```text
http://localhost:8000/
```

Stop the containers:

```bash
docker compose down
```

---

# 🧪 Testing

Run all Django tests:

```bash
python manage.py test
```

Run tests for a specific application:

```bash
python manage.py test accounts
```

The project includes tests for important parts of the system, including:

- Models
- Authentication
- OTP
- Forms
- Wallet
- Transactions
- Appointment booking
- Appointment cancellation
- Payments
- Reviews
- Ratings
- Access control
- Database constraints
- Concurrent appointment booking

---

# 📚 Documentation

Additional project documentation is available inside the `documents/` directory.

### ERD

```text
documents/ERD.png
```

Entity Relationship Diagram of the project database.

### ERD Notes

```text
documents/erd-notes.md
```

Explanation of the database design and relationships.

### API Routes

```text
documents/api-routes.md
```

List of project URLs and their responsibilities.

### Manual Test Report

```text
documents/manual-test-report.md
```

Manual testing scenarios and results.

---

# 👥 Team Members & Responsibilities

The project was developed collaboratively and divided into several Work Packages.

---

## 👩‍💻 Fatemeh Mehnati

**GitHub:** `Fatemeh-Mehnati`

### Responsibilities

- Project coordination
- Doctor-related views
- Doctor listing
- Doctor detail page
- Doctor search and filtering
- Pagination
- Templates and UI integration
- Authentication templates
- Error pages
- Project integration
- Documentation and presentation

### Main Work Packages

- WP1 — ERD collaboration
- WP5 — Doctor views and search
- WP10 — Templates
- WP14 — Documentation
- WP15 — Presentation

---

## 👨‍💻 Ali

### Responsibilities

- ERD collaboration
- Django models
- Forms and ModelForms
- Doctor and appointment models
- Appointment booking logic
- Database transactions
- Concurrency handling
- `transaction.atomic()`
- `select_for_update()`
- Docker configuration
- PostgreSQL and Docker Compose

### Main Work Packages

- WP1 — ERD
- WP2 — Models
- WP3 — Forms
- WP6 — Appointment booking logic
- WP13 — Docker and deployment configuration

---

## 👨‍💻 Erfan

### Responsibilities

- Custom User Model
- Authentication
- User registration and login
- OTP authentication
- Email OTP
- OTP expiration
- Session management
- URL integration
- Project integration
- Automated tests

### Main Work Packages

- WP1 — ERD
- WP2 — Accounts models
- WP4 — Authentication and OTP
- WP9 — Integration
- WP11 — Automated Tests

---

## 👨‍💻 Mahyar

### Responsibilities

- Wallet implementation
- Wallet balance management
- Deposit and withdrawal
- Transaction management
- Transaction history
- Appointment cancellation
- Refund logic
- Appointment-related administrative views
- Manual testing

### Main Work Packages

- WP6 — Appointment list, cancellation and related views
- WP7 — Wallet and payment
- WP12 — Manual Testing

---

## 👨‍💻 Sam

### Responsibilities

- Review system
- Rating system
- Doctor reviews
- Rating from 1 to 5
- Average rating
- Review validation
- Doctor and appointment templates
- Wallet templates
- Review templates
- Forms
- Documentation

### Main Work Packages

- WP3 — Forms and ModelForms
- WP8 — Review and Rating
- WP10 — Templates
- WP11 — Automated Tests
- WP14 — Documentation

---

# 📋 Team Work Summary

| Team Member | Main Areas |
|---|---|
| **Fatemeh** | Doctor Views, Search, Templates, Project Management, Presentation |
| **Ali** | Models, Forms, Appointment Logic, Concurrency, Docker |
| **Erfan** | Authentication, Custom User, OTP, Integration, Automated Tests |
| **Mahyar** | Wallet, Payment, Appointment Cancellation, Admin Views, Manual Tests |
| **Sam** | Reviews, Ratings, Templates, Forms, Documentation |

---

# 🔄 Main User Flow

```text
Register
   ↓
Login / OTP
   ↓
Doctor Search
   ↓
Doctor Details
   ↓
View Available Time Slots
   ↓
Book Appointment
   ↓
Pay From Wallet
   ↓
Email Confirmation
   ↓
Visit Doctor
   ↓
Submit Review & Rating
```

---

# 🔐 Security & Technical Considerations

- Django Authentication
- Custom User Model
- Email-based OTP authentication
- OTP expiration
- Session-based OTP management
- CSRF protection
- Environment variables for sensitive configuration
- Database transactions for critical operations
- `transaction.atomic()` for atomic operations
- `select_for_update()` to prevent race conditions during booking
- Prevention of negative wallet balance
- Database constraints for unique records
- Protection against duplicate appointment booking
- Protection against duplicate reviews

---

# 🐘 PostgreSQL & Docker

The Docker environment uses PostgreSQL as the database.

The Docker Compose setup contains:

```text
web
 │
 └── Django Application

db
 │
 └── PostgreSQL
```

Start the project:

```bash
docker compose up --build
```

Check containers:

```bash
docker compose ps
```

Stop containers:

```bash
docker compose down
```

---

# 🌿 Git Workflow

The project is managed using Git and GitHub.

The main branch is:

```text
main
```

To get the latest version:

```bash
git checkout main
git pull origin main
```

For developing a new feature:

```bash
git checkout -b feature/<feature-name>
```

After completing the feature:

```bash
git add .
git commit -m "Add <feature>"
git push -u origin feature/<feature-name>
```

Then create a Pull Request to the `main` branch.

---

# 📌 Project Status

This project was developed as a team project for **Quera Bootcamp** and implements the main functionality of an online doctor appointment platform.

The system includes:

- User Authentication
- OTP Login
- Doctor Management
- Doctor Search
- Appointment Booking
- Appointment Cancellation
- Wallet & Payment
- Transactions
- Reviews & Ratings
- Email Notifications
- Automated Tests
- Manual Tests
- Docker
- PostgreSQL
- Project Documentation

---

# 📄 License

This project was developed for educational purposes as part of the Quera Bootcamp.

See the `LICENSE` file for more information.
