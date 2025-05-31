# Wellness Center Platform

A full-stack wellness center management system built with Django 5 + REST Framework for the backend and React 18 + Vite + Tailwind CSS for the frontend.

## Features

- 🧠 **Patient Management** - Manage patient profiles, medical records, and appointments
- 💼 **Staff Management** - Handle staff profiles, schedules, and specializations
- 📅 **Appointment Booking** - Online booking system with availability checking
- 💰 **Finance Management** - Track expenses, revenue, and generate financial reports
- 📊 **Analytics Dashboard** - Monitor business performance and patient statistics
- 📋 **Inventory Management** - Track supplies and equipment
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile devices

## Tech Stack

### Backend
- Django 5.0
- Django REST Framework
- PostgreSQL
- Redis & Celery
- JWT Authentication

### Frontend
- React 18
- Vite
- Tailwind CSS
- React Router
- React Query

### DevOps
- Docker & Docker Compose
- Nginx
- Let's Encrypt SSL

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sujibeautysalon/wellnessCentreNew.git
   cd wellnessCentreNew
   ```

2. Start the development environment:
   ```bash
   docker-compose up
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/v1/
   - Admin interface: http://localhost:8000/admin/

## Project Structure

```
wellness-centre/
├── backend/                 # Django backend
│   ├── apps/                # Django applications
│   │   ├── analytics/       # Analytics module
│   │   ├── booking/         # Appointment booking module
│   │   ├── clinic/          # Clinic management module
│   │   ├── core/            # Core functionality
│   │   ├── ehr/             # Electronic Health Records module
│   │   ├── engagement/      # Customer engagement module
│   │   ├── finance/         # Financial management module
│   │   └── inventory/       # Inventory management module
│   ├── config/              # Django settings
│   └── requirements.txt     # Python dependencies
├── frontend/                # React frontend
│   └── frontend/            # Nested React application directory
│       ├── src/             # React source code
│       │   ├── api/         # API clients
│       │   ├── components/  # Reusable components
│       │   ├── context/     # React context providers
│       │   ├── pages/       # Page components
│       │   └── utils/       # Utility functions
│       └── public/          # Static assets
├── infra/                   # Infrastructure configuration
│   └── nginx/               # Nginx configuration
└── docker-compose.yml       # Docker services definition
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Django](https://www.djangoproject.com/)
- [React](https://reactjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Docker](https://www.docker.com/)
