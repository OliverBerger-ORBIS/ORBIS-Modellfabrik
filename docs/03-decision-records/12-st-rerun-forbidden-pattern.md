# Decision Record: st.rerun() Forbidden Pattern

## Status
**ACCEPTED** - 2025-09-24

## Context
Every Chat-Agent makes the same mistake: using `st.rerun()` which causes MQTT Connection-Loops and breaks the dashboard. This is a systematic problem that costs significant time and causes frustration.

## Decision
**FORBIDDEN:** `st.rerun()` and `streamlit.rerun()` usage in ALL dashboard components.

**MANDATORY:** Use the UI-Refresh Pattern with `request_refresh()` instead.

## Implementation

### ✅ CORRECT Pattern:
```python
from omf.dashboard.utils.ui_refresh import request_refresh

def render_component():
    if success:
        request_refresh()  # ✅ CORRECT
```

### ❌ FORBIDDEN Pattern:
```python
def render_component():
    if success:
        st.rerun()        # ❌ FORBIDDEN - causes Connection-Loop
        streamlit.rerun() # ❌ FORBIDDEN - causes Connection-Loop
```

## Enforcement

### 1. Pre-commit Hook
- **File:** `omf2/scripts/check_st_rerun.py`
- **Action:** Automatically detects and blocks commits with `st.rerun()`
- **Error Message:** Clear guidance to use `request_refresh()` instead
- **Exceptions:**
  - `omf.py`: `st.rerun()` allowed after `consume_refresh()` call
  - `main_dashboard.py`: Refresh buttons in sidebar and header are allowed

### 2. Cursor Rules
- **Rule:** "NIEMALS st.rerun() verwenden - IMMER request_refresh() verwenden"
- **Enforcement:** Automatic warning in IDE

### 3. Code Review Checklist
```markdown
## 🚨 VERBOTEN:
- [ ] st.rerun() verwendet?
- [ ] streamlit.rerun() verwendet?
- [ ] Direkte Rerun-Aufrufe?

## ✅ ERLAUBT:
- [ ] request_refresh() verwendet?
- [ ] UI-Refresh Pattern befolgt?
```

## 🔗 **Verwandte Patterns:**
- **MQTT Connection-Loop Prevention:** Ähnlicher Pre-commit Hook (`omf/scripts/check_mqtt_connection_loop.py`) verhindert MQTT-Verbindungsprobleme
- **Siehe auch:** [Decision Record 13: MQTT Connection-Loop Prevention](13-mqtt-connection-loop-prevention.md)

## Consequences

### Positive:
- **No more Connection-Loops** in MQTT
- **Stable dashboard** performance
- **Consistent UI-Refresh** behavior
- **Time savings** - no more debugging Connection-Loops

### Negative:
- **Learning curve** for new Chat-Agents
- **Additional pre-commit** validation step

## Monitoring
- **Pre-commit hooks** automatically enforce this rule
- **Code reviews** check for compliance
- **Chat-Agent training** emphasizes this rule

## Related Decisions
- [UI-Refresh Pattern](10-ui-refresh-pattern.md)
- [Singleton Pattern MQTT Client](01-singleton-pattern-mqtt-client.md)

## Notes
This rule prevents the most common mistake made by Chat-Agents and saves significant debugging time.
