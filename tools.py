"""Helper tools used by the API (calculator, admin command runner, ticket refs)."""
import ast
import hashlib
import operator
import shlex
import subprocess

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv}


def _safe_eval(node):
    """Arithmetic-only evaluator built on ast (no eval())."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    raise ValueError("unsupported expression")


def calculate(expr):
    return _safe_eval(ast.parse(expr, mode="eval"))


def run_command(cmd):
    """Run an administrative command. VULNERABLE: no allowlist, no auth."""
    try:
        done = subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=10)
        return done.stdout + done.stderr
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        return "error: " + str(exc)


def ticket_ref(owner, title):
    return hashlib.sha256((owner + title).encode()).hexdigest()[:12]
