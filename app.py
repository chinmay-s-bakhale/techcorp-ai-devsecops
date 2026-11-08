"""
TechCorp internal AI assistant - vulnerable-by-design REST API.

Endpoints
  GET  /              service info
  GET  /health        liveness check
  POST /chat          ask the LLM (llama3 via Ollama)       {"message": "..."}
  GET  /docs/<name>   read an internal document
  POST /tickets       submit a support ticket               {"owner": "...", "title": "..."}
  GET  /tickets       list tickets                          ?owner=alice
  GET  /calc          calculator                            ?expr=2*(3+4)
  POST /admin/run     administrative command tool           {"cmd": "uptime"}

This application is intentionally insecure (no authentication, no input
validation, no output scanning) so it can be attacked and then hardened.
"""
import os

from flask import Flask, request, jsonify

import db
import llm
import tools

app = Flask(__name__)
DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")

db.init_db()


@app.route("/")
def index():
    return jsonify(service="TechCorp AI Assistant", model=llm.MODEL,
                   endpoints=["/chat", "/docs/<name>", "/tickets", "/calc", "/admin/run"])


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True, silent=True) or {}
    # VULNERABLE: raw user input goes straight to the model, no auth, no validation
    return jsonify(reply=llm.ask(data.get("message", "")))


@app.route("/docs/<path:name>")
def read_doc(name):
    # VULNERABLE: path traversal - `name` is not restricted to DOCS_DIR
    path = os.path.join(DOCS_DIR, name)
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            return jsonify(name=name, content=fh.read())
    except OSError:
        return jsonify(error="document not found"), 404


@app.route("/tickets", methods=["GET", "POST"])
def tickets():
    if request.method == "POST":
        data = request.get_json(force=True, silent=True) or {}
        owner, title = data.get("owner", "anonymous"), data.get("title", "")
        db.create_ticket(owner, title)
        return jsonify(ref=tools.ticket_ref(owner, title), status="created"), 201
    rows = db.list_tickets(request.args.get("owner", ""))
    return jsonify(tickets=[dict(zip(("id", "owner", "title", "status"), r)) for r in rows])


@app.route("/calc")
def calc():
    try:
        return jsonify(result=tools.calculate(request.args.get("expr", "1+1")))
    except Exception:
        return jsonify(error="invalid expression"), 400


@app.route("/admin/run", methods=["POST"])
def admin_run():
    # VULNERABLE: unauthenticated command execution tool
    data = request.get_json(force=True, silent=True) or {}
    return jsonify(output=tools.run_command(data.get("cmd", "")))


if __name__ == "__main__":
    # Bandit B201 (HIGH): Flask debug mode exposes the Werkzeug interactive console
    app.run(host="0.0.0.0", port=5000, debug=True)
