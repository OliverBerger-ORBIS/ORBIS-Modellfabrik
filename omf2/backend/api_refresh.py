#!/usr/bin/env python3
"""
Flask API Endpoint for UI Refresh

Provides a lightweight HTTP endpoint for Streamlit to poll for refresh timestamps.

Endpoints:
- GET /api/last_refresh?group=<group>: Returns last refresh timestamp for a group
"""

from flask import Flask, request, jsonify
from omf2.backend.refresh import get_last_refresh, get_all_refresh_groups
from omf2.common.logger import get_logger

logger = get_logger(__name__)

# Create Flask app
app = Flask(__name__)


@app.route('/api/last_refresh', methods=['GET'])
def last_refresh():
    """
    Get last refresh timestamp for a group
    
    Query Parameters:
        group: Refresh group name (e.g., 'orders', 'modules', 'sensors')
    
    Returns:
        JSON response with timestamp or error
        
    Examples:
        GET /api/last_refresh?group=orders
        Response: {"group": "orders", "timestamp": 1234567890.123, "success": true}
    """
    try:
        # Get group from query parameters
        group = request.args.get('group')
        
        if not group:
            return jsonify({
                'success': False,
                'error': 'Missing required parameter: group'
            }), 400
        
        # Get last refresh timestamp
        timestamp = get_last_refresh(group)
        
        if timestamp is not None:
            return jsonify({
                'success': True,
                'group': group,
                'timestamp': timestamp
            }), 200
        else:
            # No timestamp found (group never refreshed or Redis unavailable)
            return jsonify({
                'success': True,
                'group': group,
                'timestamp': None
            }), 200
            
    except Exception as e:
        logger.error(f"❌ Error in /api/last_refresh: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/refresh_groups', methods=['GET'])
def refresh_groups():
    """
    Get all refresh groups currently tracked
    
    Returns:
        JSON response with list of group names
        
    Examples:
        GET /api/refresh_groups
        Response: {"success": true, "groups": ["orders", "modules", "sensors"]}
    """
    try:
        groups = get_all_refresh_groups()
        
        return jsonify({
            'success': True,
            'groups': groups
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in /api/refresh_groups: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint
    
    Returns:
        JSON response with status
    """
    return jsonify({
        'success': True,
        'status': 'ok',
        'service': 'omf2-refresh-api'
    }), 200


def run_api(host='0.0.0.0', port=5001, debug=False):
    """
    Run the Flask API server
    
    Args:
        host: Host to bind to (default: 0.0.0.0)
        port: Port to bind to (default: 5001)
        debug: Enable debug mode (default: False)
    """
    logger.info(f"🚀 Starting OMF2 Refresh API on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    # Run the API server
    run_api(debug=True)
