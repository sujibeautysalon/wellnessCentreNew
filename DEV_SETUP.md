# Development Setup Guide

## Quick Start (Docker - Recommended)

1. **Clone the repository:**
```bash
git clone https://github.com/sujibeautysalon/wellnessCentreNew.git
cd wellnessCentreNew
```

2. **Install Docker Desktop:**
   - Download from: https://www.docker.com/products/docker-desktop/
   - Start Docker Desktop

3. **Start all services:**
```bash
docker-compose up
```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/v1/
   - Admin Panel: http://localhost:8000/admin/
   - Database: localhost:5432 (postgres/postgres)

## Manual Setup (Without Docker)

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 13+
- Redis (optional, for background tasks)

### Backend Setup

1. **Create virtual environment:**
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up database:**
   - Install PostgreSQL
   - Create database: `wellness_db`
   - Update `backend/.env` with your database credentials

4. **Run migrations:**
```bash
python manage.py migrate
python manage.py createsuperuser
```

5. **Start development server:**
```bash
python manage.py runserver
```

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend/frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm run dev
```

## Environment Variables

All environment variables are included in the repository for development convenience:
- **Root `.env`**: Docker Compose configuration
- **`backend/.env`**: Django backend configuration
- **`frontend/.env`**: React frontend configuration
- **`.env.example`**: Production environment template

## Development Workflow

### Making Changes

1. **Create feature branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**

3. **Test your changes:**
```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend/frontend
npm test
```

4. **Commit and push:**
```bash
git add .
git commit -m "Description of your changes"
git push origin feature/your-feature-name
```

### Docker Development

- **View logs:** `docker-compose logs [service_name]`
- **Restart service:** `docker-compose restart [service_name]`
- **Rebuild:** `docker-compose up --build`
- **Stop all:** `docker-compose down`

## Troubleshooting

### Common Issues

1. **Port conflicts:** Change ports in docker-compose.yml if needed
2. **Database connection:** Ensure PostgreSQL is running
3. **Permission errors:** Check Docker Desktop permissions
4. **Module not found:** Reinstall dependencies

### Development Tools

- **Backend API docs:** http://localhost:8000/swagger/
- **Database admin:** Use pgAdmin or similar tools
- **Redis monitoring:** Use RedisInsight

## Project Structure

```
wellnessCentre/
├── backend/                 # Django REST API
│   ├── apps/               # Django apps
│   ├── config/             # Django settings
│   └── requirements.txt    # Python dependencies
├── frontend/               # React application
│   └── frontend/          # Actual React app
├── infra/                 # Infrastructure configs
├── docker-compose.yml     # Docker services
└── DOCUMENTATION.md       # Full documentation
```
