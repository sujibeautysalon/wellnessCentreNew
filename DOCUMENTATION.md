# Wellness Centre Platform Documentation

## Project Overview

The Wellness Centre platform is a comprehensive application for managing wellness clinics, including appointment booking, electronic health records, patient engagement, inventory management, and financial tracking.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Setup Instructions](#setup-instructions)
3. [Project Structure](#project-structure)
4. [Backend API Documentation](#backend-api-documentation)
5. [Frontend Components](#frontend-components)
6. [Database Schema](#database-schema)
7. [Development Workflow](#development-workflow)
8. [Deployment Guidelines](#deployment-guidelines)
9. [Troubleshooting](#troubleshooting)

## System Architecture

The Wellness Centre platform uses a microservices-inspired architecture with the following components:

- **Backend**: Django REST Framework API server
- **Frontend**: React single-page application built with Vite
- **Database**: PostgreSQL
- **Caching & Task Queue**: Redis with Celery
- **Web Server**: Nginx

All components are containerized with Docker for consistent development and deployment environments.

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Git
- Node.js (v18+) for frontend development
- Python 3.10+ for backend development

### Getting Started

1. Clone the repository:
```bash
git clone https://github.com/sujibeautysalon/wellnessCentreNew.git
cd wellnessCentreNew
```

2. Start all services using Docker Compose:
```bash
docker-compose up
```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/v1/
   - Admin interface: http://localhost:8000/admin/

### Local Development Setup (Without Docker)

#### Backend Setup

1. Set up a Python virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure the database:
```bash
python manage.py migrate
python manage.py createsuperuser
```

3. Run the development server:
```bash
python manage.py runserver
```

#### Frontend Setup

1. Install dependencies:
```bash
cd frontend/frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

## Project Structure

### Backend Structure

The backend is organized as a Django project with multiple apps, each representing a domain of functionality:

- **apps/analytics**: Reporting and analytics features
- **apps/booking**: Appointment scheduling and management
- **apps/clinic**: Clinic information and settings
- **apps/core**: Core functionality including user models and authentication
- **apps/ehr**: Electronic Health Records management
- **apps/engagement**: Patient engagement tools (messaging, reminders)
- **apps/finance**: Financial management and billing
- **apps/inventory**: Inventory and supply chain management

Each app follows a standard Django structure with models, views, serializers, and URLs.

### Frontend Structure

The frontend follows a standard React application structure:

- **src/api**: API service interfaces
- **src/assets**: Static assets and images
- **src/components**: Reusable UI components
  - **layouts**: Page layout components
  - **ui**: Atomic UI components
- **src/context**: React context providers
- **src/pages**: Page components organized by user role
- **src/router**: Application routing configuration
- **src/hooks**: Custom React hooks
- **src/utils**: Utility functions

## Backend API Documentation

### Authentication

The API uses JWT (JSON Web Tokens) for authentication. To authenticate:

1. Get a token:
```
POST /api/v1/auth/token/
{
  "username": "user@example.com",
  "password": "password"
}
```

2. Use the token in subsequent requests:
```
Authorization: Bearer <token>
```

### API Endpoints

#### User Management

- `GET /api/v1/users/`: List all users
- `POST /api/v1/users/`: Create a user
- `GET /api/v1/users/{id}/`: Get user details
- `PUT /api/v1/users/{id}/`: Update user
- `DELETE /api/v1/users/{id}/`: Delete user

#### Booking Management

- `GET /api/v1/bookings/`: List all bookings
- `POST /api/v1/bookings/`: Create a booking
- `GET /api/v1/bookings/{id}/`: Get booking details
- `PUT /api/v1/bookings/{id}/`: Update booking
- `DELETE /api/v1/bookings/{id}/`: Delete booking

#### Clinic Management

[Additional endpoints documented for other modules...]

## Frontend Components

### Page Components

- **HomePage**: Public landing page
- **LoginPage**: User authentication
- **Dashboard**: User-specific dashboard
- **BookingPage**: Appointment booking interface
- **ProfilePage**: User profile management

### Layouts

- **RootLayout**: Base layout for public pages
- **AdminLayout**: Layout for admin users
- **TherapistLayout**: Layout for therapist users
- **CustomerLayout**: Layout for customer users

## Database Schema

### Core Models

- **User**: Extended Django user model
  - Fields: email, name, user_type, phone, etc.

- **Clinic**: Clinic information
  - Fields: name, address, contact, operating_hours, etc.

- **Staff**: Staff profiles
  - Fields: user (FK), specialization, bio, etc.

- **Patient**: Patient profiles
  - Fields: user (FK), date_of_birth, emergency_contact, etc.

### Booking Models

- **Service**: Available services
  - Fields: name, description, duration, price, etc.

- **Appointment**: Scheduled appointments
  - Fields: patient (FK), staff (FK), service (FK), date_time, status, etc.

### EHR Models

- **MedicalRecord**: Patient medical records
  - Fields: patient (FK), created_by (FK), notes, date, etc.

[Additional models documented...]

## Development Workflow

### Git Workflow

1. Create a new feature branch:
```bash
git checkout -b feature/feature-name
```

2. Make changes and commit:
```bash
git add .
git commit -m "Description of changes"
```

3. Push changes to remote:
```bash
git push origin feature/feature-name
```

4. Create a pull request on GitHub

### Testing

#### Backend Testing

Run Django tests:
```bash
python manage.py test
```

Or specific apps:
```bash
python manage.py test apps.booking
```

#### Frontend Testing

Run Jest tests:
```bash
cd frontend/frontend
npm test
```

## Deployment Guidelines

### Production Configuration

1. Update environment variables in `.env` files
2. Build Docker images for production
3. Configure Nginx for SSL/TLS
4. Set up a CI/CD pipeline

### Deployment Options

- **Self-hosted**: Use Docker Compose with Nginx and Let's Encrypt
- **Cloud Platforms**: AWS, Google Cloud, or Azure
- **PaaS**: Heroku, DigitalOcean App Platform, etc.

## Troubleshooting

### Common Issues

1. **Database connection errors**:
   - Check PostgreSQL service is running
   - Verify database credentials in .env file
   - Ensure migrations are applied

2. **Missing static files**:
   - Run `python manage.py collectstatic`
   - Check Nginx configuration for static file serving

3. **API errors**:
   - Check Django server logs
   - Verify API endpoints and request format
   - Check authentication tokens

4. **Frontend build issues**:
   - Clear npm cache: `npm cache clean --force`
   - Delete node_modules and reinstall: `rm -rf node_modules && npm install`

### Support

For additional support, contact the development team or create an issue on GitHub.
