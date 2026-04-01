"""
TriageAI FastAPI Application Entry Point
"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import DEBUG, SEED_DEMO_PATIENTS
from websocket.manager import ws_manager
from websocket.router import router as ws_router
from routers.intake import router as intake_router
from routers.queue import router as queue_router
from routers.alerts import router as alerts_router
from routers.patients import router as patients_router
from agents.dashboard_agent import dashboard_agent


# ── Demo Patient Seeder ──────────────────────────────────────────────────────────
async def seed_demo_patients():
    """Seeds the store with realistic demo patients for showcase purposes."""
    from datetime import datetime, timedelta
    import uuid
    from models.patient import Patient, SeverityLevel, PatientStatus
    from store.memory_store import store

    demo_patients = [
        {
            "name": "James Mitchell",
            "age": 58, "gender": "Male",
            "symptoms": "Severe chest pain radiating to left arm, shortness of breath, sweating profusely for last 20 minutes",
            "vitals": "BP: 160/95, HR: 110 bpm, SpO2: 91%",
            "severity": SeverityLevel.CRITICAL,
            "confidence": 0.97,
            "reasoning": "Presentation strongly suggests acute myocardial infarction. Chest pain with radiation, diaphoresis, and elevated HR with low SpO2 are classic STEMI signs.",
            "recommended_actions": ["Immediate ECG", "Aspirin 325mg", "Cath lab activation", "IV access & oxygen"],
            "estimated_wait_minutes": 0,
            "wait_offset": 8,
        },
        {
            "name": "Sarah Chen",
            "age": 34, "gender": "Female",
            "symptoms": "Sudden severe headache described as 'worst headache of my life', neck stiffness, photophobia",
            "vitals": "BP: 145/88, HR: 88 bpm, Temp: 38.8°C",
            "severity": SeverityLevel.CRITICAL,
            "confidence": 0.94,
            "reasoning": "Thunderclap headache with meningismus is a red-flag presentation for subarachnoid hemorrhage until proven otherwise. Immediate CT and LP required.",
            "recommended_actions": ["Urgent CT head", "Neurology consult", "Dark quiet room", "IV morphine for pain"],
            "estimated_wait_minutes": 0,
            "wait_offset": 12,
        },
        {
            "name": "Robert Patel",
            "age": 72, "gender": "Male",
            "symptoms": "Right-sided arm weakness, facial droop on right side, slurred speech, onset 45 minutes ago",
            "vitals": "BP: 185/100, HR: 82 bpm, Blood glucose: 8.2 mmol/L",
            "severity": SeverityLevel.CRITICAL,
            "confidence": 0.98,
            "reasoning": "Classic stroke presentation with FAST criteria positive (Face, Arm, Speech, Time). Within thrombolysis window. Immediate stroke protocol activation required.",
            "recommended_actions": ["Immediate stroke protocol", "CT head (no contrast)", "Stroke team activation", "IV tPA assessment"],
            "estimated_wait_minutes": 0,
            "wait_offset": 5,
        },
        {
            "name": "Emma Williams",
            "age": 28, "gender": "Female",
            "symptoms": "High fever 39.8°C, severe lower abdominal pain, vaginal discharge, nausea",
            "vitals": "BP: 110/70, HR: 102 bpm, Temp: 39.8°C",
            "severity": SeverityLevel.URGENT,
            "confidence": 0.88,
            "reasoning": "Presentation consistent with pelvic inflammatory disease or possible ectopic pregnancy. Requires prompt gynaecological assessment and ultrasound.",
            "recommended_actions": ["Gynaecology consult", "Pelvic ultrasound", "Urine & blood cultures", "IV antibiotics"],
            "estimated_wait_minutes": 15,
            "wait_offset": 22,
        },
        {
            "name": "David Okonkwo",
            "age": 45, "gender": "Male",
            "symptoms": "Fall from ladder, right leg pain, unable to weight bear, visible deformity below knee",
            "vitals": "BP: 128/78, HR: 95 bpm",
            "severity": SeverityLevel.URGENT,
            "confidence": 0.92,
            "reasoning": "Suspected closed tibial fracture with associated soft tissue injury. Neurovascular assessment needed. Pain management priority.",
            "recommended_actions": ["X-ray right leg", "Orthopaedics consult", "IV analgesia", "Neurovascular checks"],
            "estimated_wait_minutes": 20,
            "wait_offset": 35,
        },
        {
            "name": "Priya Sharma",
            "age": 9, "gender": "Female",
            "symptoms": "Severe allergic reaction after eating peanuts, face swelling, hives all over body, mild wheeze",
            "vitals": "BP: 115/68, HR: 108 bpm, SpO2: 96%",
            "severity": SeverityLevel.URGENT,
            "confidence": 0.95,
            "reasoning": "Anaphylaxis with urticaria, angioedema, and respiratory symptoms. IM epinephrine indicated. Monitor for biphasic reaction.",
            "recommended_actions": ["IM epinephrine 0.15mg", "IV antihistamine", "Nebulised salbutamol", "90-min observation"],
            "estimated_wait_minutes": 10,
            "wait_offset": 18,
        },
        {
            "name": "Tom Bradley",
            "age": 32, "gender": "Male",
            "symptoms": "Sore throat, mild fever 37.8°C, runny nose, slight cough for 2 days",
            "vitals": None,
            "severity": SeverityLevel.MINOR,
            "confidence": 0.85,
            "reasoning": "Symptoms consistent with upper respiratory tract infection. No red flags for serious illness. Conservative management appropriate.",
            "recommended_actions": ["Throat swab if bacterial suspected", "OTC analgesics", "Rest & hydration", "GP follow-up if worsening"],
            "estimated_wait_minutes": 60,
            "wait_offset": 45,
        },
        {
            "name": "Linda Hassan",
            "age": 65, "gender": "Female",
            "symptoms": "Sudden onset dizziness, room spinning, nausea, vomiting, worse with head movement",
            "vitals": "BP: 138/82, HR: 78 bpm",
            "severity": SeverityLevel.URGENT,
            "confidence": 0.82,
            "reasoning": "Presentation consistent with acute vestibular neuritis vs BPPV. Must exclude central cause (posterior fossa stroke) given age. HINTS exam required urgently.",
            "recommended_actions": ["HINTS exam", "MRI brain if central cause suspected", "Prochlorperazine IV", "Fall risk assessment"],
            "estimated_wait_minutes": 25,
            "wait_offset": 28,
        },
    ]

    for i, demo in enumerate(demo_patients):
        patient = Patient(
            name=demo["name"],
            age=demo["age"],
            gender=demo["gender"],
            symptoms=demo["symptoms"],
            vitals=demo.get("vitals"),
            severity=demo["severity"],
            confidence=demo["confidence"],
            reasoning=demo["reasoning"],
            recommended_actions=demo["recommended_actions"],
            estimated_wait_minutes=demo["estimated_wait_minutes"],
            arrived_at=datetime.utcnow() - timedelta(minutes=demo["wait_offset"]),
            assessed_at=datetime.utcnow() - timedelta(minutes=demo["wait_offset"] - 3),
        )
        store.upsert_patient(patient)

        # Trigger alerts for Critical patients
        from agents.alert_agent import alert_agent as _alert_agent
        _alert_agent.check_and_alert(patient)

    print(f"[Seeder] ✅ Seeded {len(demo_patients)} demo patients.")


# ── Lifespan ─────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🏥 TriageAI starting up...")

    # Wire dashboard agent with WebSocket manager
    dashboard_agent.set_ws_manager(ws_manager)

    # Seed demo patients
    if SEED_DEMO_PATIENTS:
        await seed_demo_patients()

    # Start broadcast loop in background
    task = asyncio.create_task(dashboard_agent.start_broadcast_loop())

    yield

    # Shutdown
    dashboard_agent.stop()
    task.cancel()
    print("🏥 TriageAI shut down.")


# ── App ──────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="TriageAI API",
    description="AI-powered Emergency Room Triage System",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS – allow React dev server and production domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────────
app.include_router(intake_router)
app.include_router(queue_router)
app.include_router(alerts_router)
app.include_router(patients_router)
app.include_router(ws_router)


# ── Health Check ─────────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health():
    from store.memory_store import store
    stats = store.get_stats()
    return {
        "status": "healthy",
        "service": "TriageAI API",
        "version": "1.0.0",
        "queue_stats": stats,
    }


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "🏥 TriageAI API is running",
        "docs": "/docs",
        "websocket": "/ws/dashboard",
    }


# ── Dev Runner ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    from config import HOST, PORT
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
