"""
Topic-Ausschluss für Session-Recorder-Schreibpfad (DR-25).

Reine Funktionen — sicher im MQTT-Callback-Thread nutzbar (kein Streamlit-State).
"""

from __future__ import annotations

# Preset-IDs (persistiert in session_manager_settings.json)
EXCLUSION_PRESET_NONE = "none"
EXCLUSION_PRESET_ANALYSIS = "analysis"
EXCLUSION_PRESET_NO_CAM = "no_cam"

CUSTOM_FILTER_MODE_NONE = "none"
CUSTOM_FILTER_MODE_EXCLUDE = "exclude"
CUSTOM_FILTER_MODE_INCLUDE = "include"

VALID_PRESETS = frozenset({EXCLUSION_PRESET_NONE, EXCLUSION_PRESET_ANALYSIS, EXCLUSION_PRESET_NO_CAM})
VALID_CUSTOM_FILTER_MODES = frozenset({CUSTOM_FILTER_MODE_NONE, CUSTOM_FILTER_MODE_EXCLUDE, CUSTOM_FILTER_MODE_INCLUDE})


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


def topic_excluded_for_no_cam_preset(topic: str) -> bool:
    """True, wenn die Nachricht bei Preset „no_cam“ nicht ins Session-Log soll."""
    if topic == "/j1/txt/1/i/cam" or topic.startswith("/j1/txt/1/i/cam/"):
        return True
    return False


def normalize_custom_filter_mode(mode: str | None) -> str:
    if not mode or mode not in VALID_CUSTOM_FILTER_MODES:
        return CUSTOM_FILTER_MODE_NONE
    return mode


def _topic_matches_rule(topic: str, rule: str) -> bool:
    rule = (rule or "").strip()
    if not rule:
        return False
    if rule.endswith("/#"):
        return topic.startswith(rule[:-2])
    if rule.endswith("*"):
        return topic.startswith(rule[:-1])
    return topic == rule or topic.startswith(rule + "/")


def _custom_filter_allows(topic: str, mode: str | None, rules: list[str] | None) -> bool:
    normalized_mode = normalize_custom_filter_mode(mode)
    normalized_rules = [r.strip() for r in (rules or []) if str(r).strip()]
    if normalized_mode == CUSTOM_FILTER_MODE_NONE or not normalized_rules:
        return True

    matched = any(_topic_matches_rule(topic, rule) for rule in normalized_rules)
    if normalized_mode == CUSTOM_FILTER_MODE_EXCLUDE:
        return not matched
    if normalized_mode == CUSTOM_FILTER_MODE_INCLUDE:
        return matched
    return True


def should_write_message_to_session_log(
    topic: str,
    exclusion_preset: str | None,
    custom_filter_mode: str | None = None,
    custom_filter_topics: list[str] | None = None,
) -> bool:
    """False = Nachricht nicht in Puffer/Log schreiben."""
    preset = normalize_exclusion_preset(exclusion_preset)
    if preset == EXCLUSION_PRESET_NONE:
        preset_allows = True
    elif preset == EXCLUSION_PRESET_ANALYSIS:
        preset_allows = not topic_excluded_for_analysis_preset(topic)
    elif preset == EXCLUSION_PRESET_NO_CAM:
        preset_allows = not topic_excluded_for_no_cam_preset(topic)
    else:
        preset_allows = True

    if not preset_allows:
        return False
    return _custom_filter_allows(topic, custom_filter_mode, custom_filter_topics)
