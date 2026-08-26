from datetime import datetime, timezone

from flask import Flask, jsonify

app = Flask(__name__)

# Mock data until Stats Service is wired to PostgreSQL (see docs/architecture/c4-container.md)
_MOCK_STATS = {
    "total_downloads": 0,
    "total_notes": 0,
    "top_contributors": [],
}


@app.get("/health")
def health():
    return jsonify(status="ok", service="stats-service", time=datetime.now(timezone.utc).isoformat())


@app.get("/stats")
def stats():
    return jsonify(_MOCK_STATS)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
