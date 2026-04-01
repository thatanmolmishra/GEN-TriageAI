"""
Diagnosis Agent – Calls Gemini 1.5 Flash to assess symptom severity.
Returns: severity (Critical/Urgent/Minor), confidence, reasoning, recommended_actions.
"""
from __future__ import annotations
import json
import re
import asyncio
from datetime import datetime
from typing import Optional

import google.generativeai as genai

from config import GOOGLE_API_KEY, GEMINI_MODEL
from models.patient import SeverityResult, SeverityLevel

# Configure Gemini SDK
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

SYSTEM_PROMPT = """You are an expert Emergency Room triage physician with 20+ years of experience.
Your role is to rapidly assess patient symptoms and assign an accurate triage severity level.

You MUST respond ONLY with a valid JSON object — no markdown, no explanation outside the JSON.

Severity levels:
- "Critical": Immediate life-threatening emergency. Requires immediate intervention (e.g. cardiac arrest, stroke, severe respiratory distress, major trauma, anaphylaxis).
- "Urgent": Serious condition requiring treatment within 15-30 minutes (e.g. high fever, severe pain, fractures, significant bleeding).
- "Minor": Non-urgent, can safely wait 1-2 hours (e.g. minor cuts, mild fever, sore throat, cold symptoms).

JSON format:
{
  "severity": "Critical" | "Urgent" | "Minor",
  "confidence": <float 0.0–1.0>,
  "reasoning": "<2-3 sentence clinical reasoning>",
  "recommended_actions": ["<action 1>", "<action 2>", "<action 3>"],
  "estimated_wait_minutes": <integer, 0 for Critical, 1-30 for Urgent, 30-120 for Minor>
}"""


class DiagnosisAgent:
    def __init__(self):
        self.model = genai.GenerativeModel(GEMINI_MODEL) if GOOGLE_API_KEY else None
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.1,         # Low temp for consistent clinical outputs
            max_output_tokens=512,
            response_mime_type="application/json",
        ) if GOOGLE_API_KEY else None

    async def run(
        self,
        name: str,
        age: int,
        gender: str,
        symptoms: str,
        vitals: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> SeverityResult:
        """Call Gemini to assess severity. Falls back to mock if no API key."""
        if not self.model:
            return self._mock_assessment(symptoms)

        prompt = self._build_prompt(name, age, gender, symptoms, vitals, notes)

        try:
            # Run in thread pool to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    [SYSTEM_PROMPT, prompt],
                    generation_config=self.generation_config,
                ),
            )
            return self._parse_response(response.text)
        except Exception as e:
            print(f"[DiagnosisAgent] Gemini call failed: {e}. Using fallback.")
            return self._fallback_assessment(symptoms)

    def _build_prompt(
        self,
        name: str,
        age: int,
        gender: str,
        symptoms: str,
        vitals: Optional[str],
        notes: Optional[str],
    ) -> str:
        parts = [
            f"Patient: {name}, {age} years old, {gender}",
            f"Chief Complaint: {symptoms}",
        ]
        if vitals:
            parts.append(f"Vitals: {vitals}")
        if notes:
            parts.append(f"Additional Notes: {notes}")
        return "\n".join(parts)

    def _parse_response(self, text: str) -> SeverityResult:
        try:
            data = json.loads(text)
            return SeverityResult(
                severity=SeverityLevel(data["severity"]),
                confidence=float(data.get("confidence", 0.8)),
                reasoning=data.get("reasoning", "No reasoning provided."),
                recommended_actions=data.get("recommended_actions", []),
                estimated_wait_minutes=int(data.get("estimated_wait_minutes", 30)),
            )
        except Exception as e:
            print(f"[DiagnosisAgent] Parse error: {e} | Raw: {text[:200]}")
            return self._fallback_assessment("")

    def _mock_assessment(self, symptoms: str) -> SeverityResult:
        """Demo mode when no API key is set — keyword-based mock."""
        text = symptoms.lower()
        if any(k in text for k in ["chest pain", "heart", "stroke", "breathing", "unconscious", "bleeding"]):
            return SeverityResult(
                severity=SeverityLevel.CRITICAL,
                confidence=0.92,
                reasoning="[DEMO] Symptoms suggest a potentially life-threatening emergency requiring immediate intervention.",
                recommended_actions=["Immediate physician assessment", "ECG monitoring", "IV access & oxygen"],
                estimated_wait_minutes=0,
            )
        elif any(k in text for k in ["fever", "pain", "fracture", "vomit", "dizzy", "injury"]):
            return SeverityResult(
                severity=SeverityLevel.URGENT,
                confidence=0.85,
                reasoning="[DEMO] Symptoms indicate a serious condition requiring prompt medical attention.",
                recommended_actions=["Physician assessment within 30 minutes", "Pain management", "Vital signs monitoring"],
                estimated_wait_minutes=20,
            )
        else:
            return SeverityResult(
                severity=SeverityLevel.MINOR,
                confidence=0.78,
                reasoning="[DEMO] Symptoms appear non-urgent and can safely be addressed in standard care queue.",
                recommended_actions=["Standard triage queue", "Symptom monitoring", "Follow-up assessment if worsens"],
                estimated_wait_minutes=60,
            )

    def _fallback_assessment(self, symptoms: str) -> SeverityResult:
        """Fallback when Gemini call fails — defaults to Urgent to be safe."""
        return SeverityResult(
            severity=SeverityLevel.URGENT,
            confidence=0.5,
            reasoning="Automated assessment unavailable. Defaulting to Urgent for patient safety.",
            recommended_actions=["Manual physician assessment required immediately"],
            estimated_wait_minutes=15,
        )


diagnosis_agent = DiagnosisAgent()
