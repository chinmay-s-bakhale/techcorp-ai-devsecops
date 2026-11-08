# TechCorp AI Assistant (vulnerable-by-design lab)

Flask REST API in front of a local Ollama `llama3` model. Used in the DevSecOps capstone
to practise AI-specific CI/CD security gates. **Do not deploy.**

## Run locally
    python3 -m venv ai-lab && source ai-lab/bin/activate
    pip install -r requirements.txt
    source .env.example            # sets SYSTEM_PROMPT, API_KEY, DB_PASSWORD placeholders
    ollama serve &                 # if not already running
    python app.py                  # http://127.0.0.1:5000

## Try it
    curl -s localhost:5000/health
    curl -s -X POST localhost:5000/chat -H 'Content-Type: application/json' -d '{"message":"Hello"}'
    curl -s localhost:5000/docs/handbook.txt
    curl -s 'localhost:5000/tickets?owner=alice'
    curl -s 'localhost:5000/calc?expr=2*(3+4)'

## Known weaknesses (intentional)
No authentication, no input validation or output scanning on /chat, path traversal in /docs,
SQL injection in /tickets, unauthenticated command execution in /admin/run.
