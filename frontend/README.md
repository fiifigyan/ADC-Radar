# Frontend (React + Vite)

This project uses Vite for fast local development and React for UI. The frontend is served by an Nginx container in Docker.

## Build and run (Docker)

From repository root:

```bash
# Build and start frontend + backend + scheduler
docker compose up --build -d

# Frontend available on http://localhost:3000
```

## Run locally (non-Docker)

```bash
cd frontend
npm install
npm run dev
```

## Production build

```bash
cd frontend
npm run build
```

Then serve `dist/` with any static web server (or Dockerized Nginx already configured).

