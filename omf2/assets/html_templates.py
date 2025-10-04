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
    # Standard-Bucket-Farbe (leer)
    bg_color = "#f0f0f0"
    border_color = "#cccccc"
    text_color = "#666666"
    
    # Wenn Werkstück vorhanden, verwende entsprechende Farbe
    if workpiece_type:
        colors = {
            "RED": {"bg": "#ffcccc", "border": "#ff6666", "text": "#cc0000"},
            "BLUE": {"bg": "#ccccff", "border": "#6666ff", "text": "#0000cc"},
            "WHITE": {"bg": "#ffffff", "border": "#cccccc", "text": "#666666"},
        }
        color_config = colors.get(workpiece_type, colors["WHITE"])
        bg_color = color_config["bg"]
        border_color = color_config["border"]
        text_color = color_config["text"]

    return f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; margin: 5px;">
        <div style="width: 80px; height: 60px; background-color: {bg_color}; border: 2px solid {border_color}; border-radius: 4px; display: flex; align-items: center; justify-content: center; margin-bottom: 5px;">
            <div style="color: {text_color}; font-weight: bold; font-size: 12px;">{position}</div>
        </div>
        {f'<div style="color: {text_color}; font-size: 10px; font-weight: bold;">{workpiece_type}</div>' if workpiece_type else ''}
    </div>
    """
