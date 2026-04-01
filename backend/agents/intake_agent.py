"""
Intake Agent – Validates and structures incoming raw symptom text into a clean PatientIntake.
"""
from __future__ import annotations
import re
from models.patient import PatientIntakeRequest


class IntakeAgent:
    """
    Validates patient intake data, normalises text, and flags incomplete submissions.
    Runs synchronously (no AI call needed – structured data validation only).
    """

    REQUIRED_FIELDS = ["name", "age", "symptoms"]

    def run(self, raw: PatientIntakeRequest) -> dict:
        """
        Validate and enrich the intake request.
        Returns a dict with `valid`, `errors`, and the cleaned `patient` data.
        """
        errors: list[str] = []

        # Name validation
        name = raw.name.strip().title()
        if not name:
            errors.append("Patient name is required.")

        # Age validation
        if raw.age < 0 or raw.age > 150:
            errors.append(f"Invalid age: {raw.age}. Must be between 0 and 150.")

        # Symptoms must be descriptive enough
        symptoms = raw.symptoms.strip()
        if len(symptoms) < 10:
            errors.append("Symptoms description is too short. Please provide more detail.")

        # Gender normalisation
        gender = raw.gender.strip().title() if raw.gender else "Unknown"
        valid_genders = {"Male", "Female", "Other", "Unknown"}
        if gender not in valid_genders:
            gender = "Unknown"

        # Vitals – strip and uppercase if present
        vitals = raw.vitals.strip() if raw.vitals else None

        # Urgency keywords for quick pre-flag
        urgency_keywords = [
            "chest pain", "heart attack", "stroke", "cannot breathe", "not breathing",
            "unconscious", "seizure", "severe bleeding", "unresponsive", "overdose",
            "anaphylaxis", "allergic reaction", "trauma", "broken", "fracture",
        ]
        has_urgency_flag = any(kw in symptoms.lower() for kw in urgency_keywords)

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "patient": {
                "name": name,
                "age": raw.age,
                "gender": gender,
                "symptoms": symptoms,
                "vitals": vitals,
                "notes": raw.notes,
                "urgency_flag": has_urgency_flag,
            },
        }


intake_agent = IntakeAgent()
