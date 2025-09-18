"""
HTML Templates für OMF Dashboard
Wiederverwendbare HTML/CSS-Templates für konsistente UI-Elemente
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
        position: Lagerposition (A1, A2, A3, B1, B2, B3, C1, C2, C3)
        workpiece_type: RED, BLUE, WHITE oder None für leer

    Returns:
        HTML-String für den Bucket
    """
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

def get_status_badge_template(status: str, status_type: str = "info") -> str:
    """
    Template für Status-Badges

    Args:
        status: Status-Text
        status_type: info, success, warning, error

    Returns:
        HTML-String für das Status-Badge
    """
    colors = {
        "info": {"bg": "#e3f2fd", "text": "#1976d2", "border": "#bbdefb"},
        "success": {"bg": "#e8f5e8", "text": "#2e7d32", "border": "#c8e6c9"},
        "warning": {"bg": "#fff3e0", "text": "#f57c00", "border": "#ffcc02"},
        "error": {"bg": "#ffebee", "text": "#c62828", "border": "#ffcdd2"},
    }

    color_config = colors.get(status_type, colors["info"])

    return f"""
    <span style="display: inline-block; padding: 4px 8px; background-color: {color_config['bg']}; color: {color_config['text']}; border: 1px solid {color_config['border']}; border-radius: 12px; font-size: 12px; font-weight: bold; margin: 2px;">
        {status}
    </span>
    """

def get_module_card_template(module_name: str, status: str, ip_address: str = None) -> str:
    """
    Template für Modul-Karten

    Args:
        module_name: Name des Moduls
        status: Verfügbarkeits-Status
        ip_address: IP-Adresse (optional)

    Returns:
        HTML-String für die Modul-Karte
    """
    status_colors = {"READY": "success", "BUSY": "warning", "BLOCKED": "error", "OFFLINE": "error"}

    status_type = status_colors.get(status, "info")
    status_badge = get_status_badge_template(status, status_type)

    ip_info = (
        f"<div style='font-size: 11px; color: #666; margin-top: 4px;'>IP: {ip_address}</div>" if ip_address else ""
    )

    return f"""
    <div style="border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin: 8px; background-color: #fafafa; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="font-weight: bold; font-size: 16px; margin-bottom: 8px;">{module_name}</div>
        <div style="margin-bottom: 8px;">{status_badge}</div>
        {ip_info}
    </div>
    """
