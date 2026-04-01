import { useState, useRef, useEffect } from 'react';

/**
 * IntakeChat – Animated form-based intake with Web Speech API voice support.
 */
export default function IntakeChat({ onSubmit, loading }) {
  const [form, setForm] = useState({
    name: '', age: '', gender: 'Unknown', symptoms: '', vitals: '', notes: '',
  });
  const [recording, setRecording] = useState(false);
  const [errors, setErrors] = useState({});
  const recognitionRef = useRef(null);

  // Web Speech API setup
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (e) => {
        const transcript = e.results[0][0].transcript;
        setForm((f) => ({ ...f, symptoms: f.symptoms ? `${f.symptoms} ${transcript}` : transcript }));
        setRecording(false);
      };
      recognitionRef.current.onend = () => setRecording(false);
      recognitionRef.current.onerror = () => setRecording(false);
    }
  }, []);

  const toggleVoice = () => {
    if (!recognitionRef.current) {
      alert('Voice input is not supported in this browser. Please use Chrome.');
      return;
    }
    if (recording) {
      recognitionRef.current.stop();
      setRecording(false);
    } else {
      recognitionRef.current.start();
      setRecording(true);
    }
  };

  const validate = () => {
    const e = {};
    if (!form.name.trim()) e.name = 'Required';
    if (!form.age || isNaN(form.age) || +form.age < 0 || +form.age > 150) e.age = 'Invalid age';
    if (!form.symptoms.trim() || form.symptoms.trim().length < 10) e.symptoms = 'Please describe symptoms in more detail';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleChange = (field, value) => {
    setForm((f) => ({ ...f, [field]: value }));
    if (errors[field]) setErrors((e) => ({ ...e, [field]: undefined }));
  };

  const handleSubmit = (ev) => {
    ev.preventDefault();
    if (!validate()) return;
    onSubmit({
      name: form.name.trim(),
      age: parseInt(form.age),
      gender: form.gender,
      symptoms: form.symptoms.trim(),
      vitals: form.vitals.trim() || null,
      notes: form.notes.trim() || null,
    });
  };

  const inputStyle = (field) => ({
    ...(errors[field] ? { borderColor: 'var(--critical)', boxShadow: '0 0 0 3px var(--critical-dim)' } : {}),
  });

  return (
    <form className="intake-form" onSubmit={handleSubmit}>
      {/* Patient Details Row */}
      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Patient Name *</label>
          <input
            id="intake-name"
            className="form-input"
            placeholder="Full name"
            value={form.name}
            onChange={(e) => handleChange('name', e.target.value)}
            style={inputStyle('name')}
          />
          {errors.name && <span style={{ fontSize: '0.72rem', color: 'var(--critical)' }}>{errors.name}</span>}
        </div>
        <div className="form-group">
          <label className="form-label">Age *</label>
          <input
            id="intake-age"
            className="form-input"
            type="number"
            placeholder="Years"
            min={0} max={150}
            value={form.age}
            onChange={(e) => handleChange('age', e.target.value)}
            style={inputStyle('age')}
          />
          {errors.age && <span style={{ fontSize: '0.72rem', color: 'var(--critical)' }}>{errors.age}</span>}
        </div>
        <div className="form-group">
          <label className="form-label">Gender</label>
          <select
            id="intake-gender"
            className="form-input"
            value={form.gender}
            onChange={(e) => handleChange('gender', e.target.value)}
          >
            <option value="Unknown">Prefer not to say</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
            <option value="Other">Other</option>
          </select>
        </div>
      </div>

      {/* Symptoms */}
      <div className="form-group">
        <label className="form-label">Chief Complaint & Symptoms *</label>
        <div className="form-input-voice">
          <textarea
            id="intake-symptoms"
            className="form-input"
            placeholder="Describe symptoms in detail (e.g. 'Severe chest pain radiating to left arm, started 30 minutes ago, shortness of breath...')"
            value={form.symptoms}
            onChange={(e) => handleChange('symptoms', e.target.value)}
            style={{ ...inputStyle('symptoms'), minHeight: 120 }}
          />
          <button
            type="button"
            id="intake-voice-btn"
            className={`voice-btn ${recording ? 'recording' : ''}`}
            onClick={toggleVoice}
            title={recording ? 'Stop recording' : 'Speak symptoms'}
          >
            {recording ? '⏹' : '🎙️'}
          </button>
        </div>
        {recording && (
          <span style={{ fontSize: '0.75rem', color: 'var(--critical)', display: 'flex', alignItems: 'center', gap: 4 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--critical)', display: 'inline-block', animation: 'blink 1s infinite' }} />
            Recording... speak now
          </span>
        )}
        {errors.symptoms && <span style={{ fontSize: '0.72rem', color: 'var(--critical)' }}>{errors.symptoms}</span>}
      </div>

      {/* Vitals (Optional) */}
      <div className="form-group">
        <label className="form-label">Vitals <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(optional)</span></label>
        <input
          id="intake-vitals"
          className="form-input"
          placeholder="e.g. BP: 120/80, HR: 88 bpm, SpO2: 98%, Temp: 37.2°C"
          value={form.vitals}
          onChange={(e) => handleChange('vitals', e.target.value)}
        />
      </div>

      {/* Notes (Optional) */}
      <div className="form-group">
        <label className="form-label">Additional Notes <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(optional)</span></label>
        <input
          id="intake-notes"
          className="form-input"
          placeholder="Allergies, medications, PMH, etc."
          value={form.notes}
          onChange={(e) => handleChange('notes', e.target.value)}
        />
      </div>

      {/* Submit */}
      <button
        id="intake-submit"
        type="submit"
        className="submit-btn"
        disabled={loading}
      >
        {loading ? (
          <>
            <span className="spinner" />
            Assessing with Gemini AI…
          </>
        ) : (
          <>
            🏥 Submit for AI Triage Assessment
          </>
        )}
      </button>
    </form>
  );
}
