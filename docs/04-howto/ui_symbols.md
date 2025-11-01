# UI Symbols - Centralized usage for tabs and headings

Purpose
- Define one source of truth for UI emojis/symbols for all tabs, subtabs, and nested subtabs.
- Ensure consistent labels across the dashboard by resolving icons via `UISymbols`.

Where to define icons
- Add/adjust keys in `omf2/ui/common/symbols.py` under `UISymbols.TAB_ICONS`.
- Keep strict order: TOP-LEVEL → SECOND-LEVEL → THIRD-LEVEL (traverse the UI tree root-to-leaves like in `main_dashboard`).
- Only store emojis in the dict; comments next to entries document level and meaning.

When to use which helper
- Tabs and Subtabs (navigation): `UISymbols.get_tab_icon(key)`
- Headings/Section icons (inside content): prefer inline SVG via `heading_icons.get_svg_inline(...)`; fall back to emojis with `get_icon_html` if needed.

Do
- Prefix all tab labels with `UISymbols.get_tab_icon(...)` and the i18n label.
- Add new tab/subtab keys to `TAB_ICONS` when creating UI wrappers.
- Keep technical keys stable; adjust only the emoji in `TAB_ICONS` to change visuals.

Don't
- Do not hardcode emojis directly in tab lists.
- Do not embed SVGs in `st.tabs(...)` (Streamlit limitation) – use emojis via `UISymbols`.

Examples
```python
# main_dashboard: top-level tabs (already implemented)
icon = UISymbols.get_tab_icon(tab_key)
label = f"{icon} {i18n.t(f'tabs.{tab_key}')}"

# overview subtabs
st.tabs([
    f"{UISymbols.get_tab_icon('product_catalog')} {i18n.t('ccu_overview.tabs.product_catalog')}",
    f"{UISymbols.get_tab_icon('inventory')} {i18n.t('ccu_overview.tabs.inventory')}",
    f"{UISymbols.get_tab_icon('sensor_data')} {i18n.t('ccu_overview.tabs.sensor_data')}",
])

# admin settings subtabs
st.tabs([
    f"{UISymbols.get_tab_icon('admin_dashboard')} {i18n.t('admin.settings.subtabs.dashboard')}",
    f"{UISymbols.get_tab_icon('mqtt_clients')} {i18n.t('admin.settings.subtabs.mqtt_clients')}",
    f"{UISymbols.get_tab_icon('gateway')} {i18n.t('admin.settings.subtabs.gateway')}",
    f"{UISymbols.get_tab_icon('topics')} {i18n.t('admin.settings.subtabs.topics')}",
    f"{UISymbols.get_tab_icon('schemas')} {i18n.t('admin.settings.subtabs.schemas')}",
    f"{UISymbols.get_tab_icon('admin_modules')} {i18n.t('admin.settings.subtabs.modules')}",
    f"{UISymbols.get_tab_icon('stations')} {i18n.t('admin.settings.subtabs.stations')}",
    f"{UISymbols.get_tab_icon('txt_controllers')} {i18n.t('admin.settings.subtabs.txt_controllers')}",
    f"{UISymbols.get_tab_icon('workpieces')} {i18n.t('admin.settings.subtabs.workpieces')}",
])

# message center
st.tabs([
    f"{UISymbols.get_tab_icon('message_monitor')} Message Monitor",
    f"{UISymbols.get_tab_icon('topic_monitor')} Topic Monitor",
    f"{UISymbols.get_tab_icon('send_test_message')} Send Messages",
])
```

Notes
- Any rebranding or icon changes happen centrally by editing `TAB_ICONS` only.
- Keep i18n keys for labels; icons do not translate.
- For camera/placeholder or product/module SVGs, use the asset pipeline (`heading_icons`, `asset_manager`).
