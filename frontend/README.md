# Wellness Centre Frontend

This is the frontend application for the Wellness Centre platform.

## Technology Stack

- React 18 with Vite
- Tailwind CSS for styling
- React Router for navigation
- React Query for data fetching
- React Hook Form for form handling

## Development

To start the development server:

```bash
npm run dev
```

## Production Build

To create a production build:

```bash
npm run build
```

## Docker

This application can be run in Docker using the provided Dockerfile:

```bash
docker build -t wellness-centre-frontend .
docker run -p 3000:80 wellness-centre-frontend
```

## Project Structure

- `/frontend` - The main React application
  - `/src` - Source code
    - `/api` - API client and service functions
    - `/components` - Reusable UI components
    - `/context` - React context providers
    - `/hooks` - Custom hooks
    - `/pages` - Route components
    - `/utils` - Helper functions and utilities
