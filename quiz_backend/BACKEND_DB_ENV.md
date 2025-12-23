# Backend Database Environment

The Django backend reads PostgreSQL configuration from environment variables. These must align with the database container which listens on port 5001.

Required variables:
- POSTGRES_DB: Database name (e.g., quizdb)
- POSTGRES_USER: Username (e.g., quizuser)
- POSTGRES_PASSWORD: Password
- POSTGRES_HOST: Hostname or service name of the Postgres container (e.g., quiz_database)
- POSTGRES_PORT: Port (must be 5001 to match the DB container)
- DB_CONN_MAX_AGE: Optional persistent connection age in seconds (default 60)

CORS:
- FRONTEND_URL: React TV app origin (default http://localhost:3000)
- CORS_ALLOW_ALL: If "true", allow any origin (default true)

See quiz_backend/.env.example for a ready-to-copy template.
