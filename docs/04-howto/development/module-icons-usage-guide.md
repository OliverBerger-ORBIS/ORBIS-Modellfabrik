Module Icons Usage Guide (SVG + Emoji)

Scope
- Consistent rendering of module icons across the UI
- SVG for HTML-capable components; emoji for plain-text components
- FTS is treated like a module (serial-based mapping)

Architecture
- Source of truth: `omf2/ccu/module_manager.py`
  - `get_module_icon_html(module_id, size_px=24)` → SVG HTML for `st.markdown(..., unsafe_allow_html=True)`
  - `get_module_icon(module_id)` → Emoji for `st.selectbox()` / `st.dataframe()`
- Helper: `omf2/ui/common/symbols.py` (CSS scoping, cleanup)

Streamlit Limitations
- Plain text only: `st.selectbox()`, `st.dataframe()` → use emoji
- HTML allowed: `st.markdown(..., unsafe_allow_html=True)` → use SVG

Module Table Pattern (HTML table with SVG)
Use this pattern whenever a table displays module-related rows and you need SVG icons.

```python
from omf2.ccu.module_manager import get_ccu_module_manager
import streamlit as st
import html

def render_module_table(modules: dict):
    manager = get_ccu_module_manager()

    table_html = '<table style="width: 100%; border-collapse: collapse;">'
    table_html += '<thead><tr style="background-color: #f0f2f6; border-bottom: 2px solid #ddd;">'
    for header in ["ID", "Name", "Type", "Enabled"]:
        table_html += f'<th style="padding: 8px; text-align: left; font-weight: bold;">{html.escape(header)}</th>'
    table_html += '</tr></thead><tbody>'

    for module_id, module_info in modules.items():
        name = module_info.get("name", module_id)
        enabled = "✅" if module_info.get("enabled", True) else "❌"
        module_type = module_info.get("type", "Unknown")

        icon_html = manager.get_module_icon_html(module_id, size_px=20)
        name_cell = (
            f"<span style=\"display: inline-flex; align-items: center; gap: 6px; white-space: nowrap;\">"
            f"{icon_html}<span>{html.escape(name)}</span></span>"
        )

        table_html += '<tr style="border-bottom: 1px solid #ddd;">'
        table_html += f'<td style=\"padding: 8px; font-family: monospace; white-space: nowrap;\">{html.escape(module_id)}</td>'
        table_html += f'<td style=\"padding: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;\">{name_cell}</td>'
        table_html += f'<td style=\"padding: 8px; white-space: nowrap;\">{html.escape(module_type)}</td>'
        table_html += f'<td style=\"padding: 8px; white-space: nowrap;\">{enabled}</td>'
        table_html += '</tr>'

    table_html += '</tbody></table>'
    st.markdown(table_html, unsafe_allow_html=True)
```

Message Monitor Data Column (Expandable JSON)
Show an inline one-line preview and the full JSON on demand.

```python
import html

def render_data_cell(preview: str, full: str) -> str:
    safe_preview = html.escape(preview)
    safe_full = html.escape(full)
    return (
        f"<details style=\"max-width: 100%;\">"
        f"<summary style=\"cursor: pointer; color: #444; display: inline-block; max-width: 100%; "
        f"white-space: nowrap; overflow: hidden; text-overflow: ellipsis;\">{safe_preview}</summary>"
        f"<pre style=\"white-space: pre-wrap; margin-top: 8px;\">{safe_full}</pre>"
        f"</details>"
    )
```

Emoji-only Patterns
- Use `get_module_icon()` for `st.selectbox()` and `st.dataframe()`
- Build display strings like `"{emoji} {name} ({serial})"`

FTS Handling
- Topics starting with `fts/v1/ff/{serial}/...` are treated like modules
- Use the same API: `get_module_icon_html(serial)` and `get_module_icon(serial)`

References
- Module Manager: `omf2/ccu/module_manager.py`
- Symbols helper: `omf2/ui/common/symbols.py`
- Admin Modules (example HTML table): `omf2/ui/admin/admin_settings/module_subtab.py`
- CCU Message Monitor (expandable data): `omf2/ui/ccu/ccu_message_monitor/ccu_message_monitor_component.py`


