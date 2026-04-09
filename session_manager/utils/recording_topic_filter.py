"""
Topic-Ausschluss für Session-Recorder-Schreibpfad (DR-25).

Reine Funktionen — sicher im MQTT-Callback-Thread nutzbar (kein Streamlit-State).
"""

from __future__ import annotations

# Preset-IDs (persistiert in session_manager_settings.json)
EXCLUSION_PRESET_NONE = "none"
EXCLUSION_PRESET_ANALYSIS = "analysis"

VALID_PRESETS = frozenset({EXCLUSION_PRESET_NONE, EXCLUSION_PRESET_ANALYSIS})


def normalize_exclusion_preset(preset: str | None) -> str:
    if not preset or preset not in VALID_PRESETS:
        return EXCLUSION_PRESET_NONE
    return preset


def topic_excluded_for_analysis_preset(topic: str) -> bool:
    """
    True, wenn die Nachricht bei Preset „analysis“ nicht ins Session-Log soll.

    Siehe DR-25: Arduino-Multisensor, BME680, Kamera, LDR (TXT).
    """
    if topic.startswith("osf/arduino/"):
        return True
    # DR-25: Kamera (JPEG-Payload dominiert oft das Volumen)
    if topic == "/j1/txt/1/i/cam" or topic.startswith("/j1/txt/1/i/cam/"):
        return True
    # BME680 (TXT) — exakt und kurze Variante wie in Session-Analysis-Vorfilter
    if topic in (
        "/j1/txt/1/i/bme680",
        "/j1/txt/1/i/bme",
        "/j1/txt/1/c/bme680",
    ):
        return True
    # TXT LDR (Lichtsensor — regelmäßige kleine JSON-Payloads)
    if topic in ("/j1/txt/1/i/ldr", "/j1/txt/1/c/ldr"):
        return True
    return False


def should_write_message_to_session_log(topic: str, exclusion_preset: str | None) -> bool:
    """False = Nachricht nicht in Puffer/Log schreiben."""
    preset = normalize_exclusion_preset(exclusion_preset)
    if preset == EXCLUSION_PRESET_NONE:
        return True
    if preset == EXCLUSION_PRESET_ANALYSIS:
        return not topic_excluded_for_analysis_preset(topic)
    return True
