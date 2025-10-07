"""
HTML Templates für OMF2 Dashboard
Wiederverwendbare HTML/CSS-Templates für konsistente UI-Elemente
Kopiert und angepasst von omf/dashboard/assets/html_templates.py
"""


def get_workpiece_box_template(workpiece_type: str, count: int, available: bool) -> str:
    """
    Template für Werkstück-Boxen (ROT, BLUE, WHITE) - OHNE HTML-Buttons für Streamlit-Kompatibilität

    Args:
        workpiece_type: RED, BLUE, WHITE
        count: Anzahl verfügbarer Werkstücke
        available: Ob Werkstücke verfügbar sind

    Returns:
        HTML-String für die Werkstück-Box (ohne Buttons)
    """
    # Farben definieren
    colors = {
        "RED": {"bg": "#ff0000", "border": "#cc0000", "text": "white"},
        "BLUE": {"bg": "#0066ff", "border": "#0044cc", "text": "white"},
        "WHITE": {"bg": "#e0e0e0", "border": "#b0b0b0", "text": "black"},
    }

    color_config = colors.get(workpiece_type, colors["WHITE"])

    return f"""
    <div style="display: flex; flex-direction: column; align-items: flex-start; justify-content: flex-start; height: 100%; text-align: left; margin: 10px;">
        <div style="width: 120px; height: 80px; background-color: {color_config['bg']}; border: 2px solid {color_config['border']}; border-radius: 4px; margin: 0 0 10px 0; display: flex; align-items: center; justify-content: center;">
            <div style="color: {color_config['text']}; font-weight: bold; font-size: 14px;">{workpiece_type}</div>
        </div>
        <div style="margin: 5px 0;">
            <strong>Bestand: {count}</strong>
        </div>
        <div style="margin: 5px 0;">
            <strong>Verfügbar: {'✅ Ja' if available else '❌ Nein'}</strong>
        </div>
    </div>
    """


def get_product_catalog_template(workpiece_type: str) -> str:
    """
    Template für Produktkatalog-Boxen (ROT, BLUE, WHITE) - OHNE Bestand/Verfügbar-Info

    Args:
        workpiece_type: RED, BLUE, WHITE

    Returns:
        HTML-String für die Produktkatalog-Box
    """
    # Farben definieren
    colors = {
        "RED": {"bg": "#ff0000", "border": "#cc0000", "text": "white"},
        "BLUE": {"bg": "#0066ff", "border": "#0044cc", "text": "white"},
        "WHITE": {"bg": "#e0e0e0", "border": "#b0b0b0", "text": "black"},
    }

    color_config = colors.get(workpiece_type, colors["WHITE"])

    return f"""
    <div style="display: flex; flex-direction: column; align-items: flex-start; justify-content: flex-start; height: 100%; text-align: left; margin: 10px;">
        <div style="width: 120px; height: 80px; background-color: {color_config['bg']}; border: 2px solid {color_config['border']}; border-radius: 4px; margin: 0 0 10px 0; display: flex; align-items: center; justify-content: center;">
            <div style="color: {color_config['text']}; font-weight: bold; font-size: 14px;">{workpiece_type}</div>
        </div>
    </div>
    """


def get_bucket_template(position: str, workpiece_type: str = None) -> str:
    """
    Template für Lager-Buckets (A1-C3)

    Args:
        position: Bucket-Position (z.B. "A1", "B2", "C3")
        workpiece_type: Optional - RED, BLUE, WHITE für gefüllte Buckets

    Returns:
        HTML-String für den Bucket
    """
    # EXAKT aus omf/dashboard/assets/html_templates.py
    if workpiece_type:
        # Gefüllter Bucket mit Werkstück
        colors = {
            "RED": {"bg": "#ff0000", "border": "#cc0000", "text": "white"},
            "BLUE": {"bg": "#0066ff", "border": "#0044cc", "text": "white"},
            "WHITE": {"bg": "#e0e0e0", "border": "#b0b0b0", "text": "black"},
        }
        color_config = colors.get(workpiece_type, colors["WHITE"])

        return f'<div style="width: 140px; height: 140px; margin: 8px auto; position: relative;"><div style="width: 120px; height: 80px; background-color: {color_config["bg"]}; border: 2px solid {color_config["border"]}; border-radius: 4px; position: absolute; bottom: 8px; left: 8px; display: flex; align-items: center; justify-content: center; z-index: 2;"><div style="color: {color_config["text"]}; font-weight: bold; font-size: 14px;">{workpiece_type}</div></div><div style="width: 140px; height: 60px; border: 4px solid #000000; border-top: none; background-color: #f0f0f0; border-radius: 0 0 12px 12px; position: absolute; bottom: 0; left: 0; z-index: 1;"></div><div style="text-align: center; font-size: 16px; font-weight: bold; color: #333; margin-top: 4px; position: absolute; bottom: -25px; left: 0; right: 0;">{position}</div></div>'
    else:
        # Leerer Bucket
        return f'<div style="width: 140px; height: 140px; margin: 8px auto; position: relative;"><div style="width: 140px; height: 60px; border: 4px solid #000000; border-top: none; background-color: #f9f9f9; border-radius: 0 0 12px 12px; position: absolute; bottom: 0; left: 0;"></div><div style="text-align: center; font-size: 16px; font-weight: bold; color: #999; margin-top: 4px; position: absolute; bottom: -25px; left: 0; right: 0;">{position}</div></div>'
