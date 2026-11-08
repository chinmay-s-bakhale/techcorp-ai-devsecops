"""Application configuration - secrets come from the environment only."""
import os

API_KEY = os.environ.get("API_KEY")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
