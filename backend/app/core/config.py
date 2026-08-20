import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://pulsewatch:pulsewatch@localhost:5432/pulsewatch",
)
