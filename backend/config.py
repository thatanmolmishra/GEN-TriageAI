import os
from dotenv import load_dotenv

load_dotenv()

# ── Gemini ──────────────────────────────────────────────────────────────────────
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# ── Server ──────────────────────────────────────────────────────────────────────
PORT: int = int(os.getenv("PORT", 8000))
HOST: str = os.getenv("HOST", "0.0.0.0")
DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

# ── Queue ────────────────────────────────────────────────────────────────────────
WS_BROADCAST_INTERVAL: float = float(os.getenv("WS_BROADCAST_INTERVAL", 3))
SEED_DEMO_PATIENTS: bool = os.getenv("SEED_DEMO_PATIENTS", "true").lower() == "true"

# ── Priority Scoring ─────────────────────────────────────────────────────────────
SEVERITY_BASE_SCORES = {
    "Critical": 10000,
    "Urgent":    5000,
    "Minor":     1000,
}

# Seconds before a Minor patient's score bumps up to Urgent-equivalent
MINOR_ESCALATION_SECONDS = 1800   # 30 minutes
URGENT_ESCALATION_SECONDS = 900   # 15 minutes

if not GOOGLE_API_KEY:
    import warnings
    warnings.warn(
        "⚠️  GOOGLE_API_KEY is not set. Diagnosis Agent will return mock severity. "
        "Set it in your .env file to enable real AI assessment.",
        stacklevel=2,
    )
