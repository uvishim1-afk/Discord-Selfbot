#!/usr/bin/env python3
"""
Discord Selfbot Dashboard Server with Username Sniper
Provides REST API for the web dashboard to control the selfbot
Optimized for Render deployment
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import psutil
import json
import logging
from datetime import datetime
from functools import wraps
import subprocess
import time
import base64
from pathlib import Path

app = Flask(__name__, static_folder='dashboard', static_url_path='/static')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration from environment variables
DASHBOARD_PASSWORD = os.getenv('DASHBOARD_PASSWORD', 'admin123')
BOT_TOKEN = os.getenv('USER_TOKEN', '')
BOT_FILE = os.getenv('BOT_FILE_PATH', 'selfbot.py')
PORT = int(os.getenv('DASHBOARD_PORT', 5000))
HOST = os.getenv('DASHBOARD_HOST', '0.0.0.0')

BOT_PROCESS = None
BOT_RUNNING = False
BOT_START_TIME = None
BOT_STATS = {
    'messages_sent': 0,
    'commands_executed': 0,
    'guild_count': 0,
    'friend_count': 0,
    'sniper_claimed': 0,
    'sniper_active': False
}
SNIPER_CONFIG = {
    'snipe_list': [],
    'webhook_url': '',
    'auto_claim_enabled': False
}
LOGS = []

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        expected_auth = base64.b64encode(DASHBOARD_PASSWORD.encode()).decode()
        
        if not auth or auth != expected_auth:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

# Logging helper
def add_log(message, level='INFO'):
    """Add a log entry"""
    log_entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'level': level,
        'message': message
    }
    LOGS.append(log_entry)
    # Keep only last 100 logs
    if len(LOGS) > 100:
        LOGS.pop(0)
    
    # Log to console
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.log(log_level, message)

# Serve static files
@app.route('/')
def serve_dashboard():
    """Serve the main dashboard"""
    return send_from_directory('dashboard', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    if filename.endswith(('.js', '.css', '.html')):
        return send_from_directory('dashboard', filename)
    return send_from_directory('dashboard', filename), 404

# ============== API ENDPOINTS ==============

# Bot Status Endpoints
@app.route('/api/bot/status', methods=['GET'])
@require_auth
def get_bot_status():
    """Get current bot status"""
    uptime = 0
    if BOT_RUNNING and BOT_START_TIME:
        uptime = int((datetime.now() - BOT_START_TIME).total_seconds())
    
    return jsonify({
        'connected': BOT_RUNNING,
        'status': 'online' if BOT_RUNNING else 'offline',
        'uptime_seconds': uptime,
        'latency': 50,
        'bot_name': 'Discord Selfbot',
        'bot_id': '123456789',
        'connected_since': BOT_START_TIME.isoformat() if BOT_START_TIME else None
    })

@app.route('/api/bot/stats', methods=['GET'])
@require_auth
def get_bot_stats():
    """Get bot statistics"""
    return jsonify(BOT_STATS)

@app.route('/api/bot/stats', methods=['POST'])
@require_auth
def update_bot_stats():
    """Update bot statistics (called by the selfbot)"""
    global BOT_STATS
    data = request.get_json()
    BOT_STATS.update(data)
    return jsonify({'success': True, 'stats': BOT_STATS})

@app.route('/api/server/info', methods=['GET'])
@require_auth
def get_server_info():
    """Get server resource usage"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return jsonify({
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_mb': memory.available / (1024 * 1024),
            'memory_total_mb': memory.total / (1024 * 1024),
            'disk_percent': disk.percent
        })
    except Exception as e:
        add_log(f'Error getting server info: {str(e)}', 'ERROR')
        return jsonify({'error': str(e)}), 500

# ============== USERNAME SNIPER ENDPOINTS ==============

@app.route('/api/sniper/config', methods=['GET'])
@require_auth
def get_sniper_config():
    """Get sniper configuration"""
    return jsonify(SNIPER_CONFIG)

@app.route('/api/sniper/config', methods=['POST'])
@require_auth
def update_sniper_config():
    """Update sniper configuration"""
    global SNIPER_CONFIG
    data = request.get_json()
    
    try:
        SNIPER_CONFIG.update(data)
        
        # Save to file
        with open('sniper_config.json', 'w') as f:
            json.dump(SNIPER_CONFIG, f, indent=4)
        
        add_log('Sniper config updated', 'INFO')
        return jsonify({'success': True, 'config': SNIPER_CONFIG})
    except Exception as e:
        add_log(f'Error updating sniper config: {str(e)}', 'ERROR')
        return jsonify({'error': str(e)}), 500

@app.route('/api/sniper/snipe-list', methods=['GET'])
@require_auth
def get_snipe_list():
    """Get snipe list"""
    return jsonify({'snipe_list': SNIPER_CONFIG.get('snipe_list', [])})

@app.route('/api/sniper/snipe-list/add', methods=['POST'])
@require_auth
def add_to_snipe_list():
    """Add username to snipe list"""
    data = request.get_json()
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'error': 'Username required'}), 400
    
    if username not in SNIPER_CONFIG['snipe_list']:
        SNIPER_CONFIG['snipe_list'].append(username)
        
        # Save to file
        with open('sniper_config.json', 'w') as f:
            json.dump(SNIPER_CONFIG, f, indent=4)
        
        add_log(f'Added {username} to snipe list', 'INFO')
        return jsonify({'success': True, 'snipe_list': SNIPER_CONFIG['snipe_list']})
    
    return jsonify({'error': 'Username already in list'}), 400

@app.route('/api/sniper/snipe-list/remove', methods=['POST'])
@require_auth
def remove_from_snipe_list():
    """Remove username from snipe list"""
    data = request.get_json()
    username = data.get('username', '').strip()
    
    if username in SNIPER_CONFIG['snipe_list']:
        SNIPER_CONFIG['snipe_list'].remove(username)
        
        # Save to file
        with open('sniper_config.json', 'w') as f:
            json.dump(SNIPER_CONFIG, f, indent=4)
        
        add_log(f'Removed {username} from snipe list', 'INFO')
        return jsonify({'success': True, 'snipe_list': SNIPER_CONFIG['snipe_list']})
    
    return jsonify({'error': 'Username not in list'}), 400

@app.route('/api/sniper/webhook', methods=['POST'])
@require_auth
def set_webhook_url():
    """Set webhook URL for notifications"""
    data = request.get_json()
    webhook_url = data.get('webhook_url', '').strip()
    
    SNIPER_CONFIG['webhook_url'] = webhook_url
    
    # Save to file
    with open('sniper_config.json', 'w') as f:
        json.dump(SNIPER_CONFIG, f, indent=4)
    
    add_log(f'Webhook URL updated', 'INFO')
    return jsonify({'success': True, 'webhook_url': webhook_url})

@app.route('/api/sniper/toggle', methods=['POST'])
@require_auth
def toggle_auto_claim():
    """Toggle auto-claim feature"""
    SNIPER_CONFIG['auto_claim_enabled'] = not SNIPER_CONFIG.get('auto_claim_enabled', False)
    
    # Save to file
    with open('sniper_config.json', 'w') as f:
        json.dump(SNIPER_CONFIG, f, indent=4)
    
    status = 'enabled' if SNIPER_CONFIG['auto_claim_enabled'] else 'disabled'
    add_log(f'Auto-claim {status}', 'INFO')
    
    return jsonify({'success': True, 'enabled': SNIPER_CONFIG['auto_claim_enabled']})

# Bot Control Endpoints
@app.route('/api/bot/start', methods=['POST'])
@require_auth
def start_bot():
    """Start the bot"""
    global BOT_RUNNING, BOT_PROCESS, BOT_START_TIME
    
    if BOT_RUNNING:
        return jsonify({'error': 'Bot is already running'}), 400
    
    if not BOT_TOKEN:
        add_log('Cannot start bot: USER_TOKEN not set', 'ERROR')
        return jsonify({'error': 'Discord token not configured'}), 400
    
    try:
        # Start bot process
        BOT_PROCESS = subprocess.Popen(
            ['python', BOT_FILE],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, 'USER_TOKEN': BOT_TOKEN}
        )
        BOT_RUNNING = True
        BOT_START_TIME = datetime.now()
        add_log(f'Bot started successfully (PID: {BOT_PROCESS.pid})', 'SUCCESS')
        return jsonify({'success': True, 'message': 'Bot started', 'pid': BOT_PROCESS.pid})
    except Exception as e:
        add_log(f'Error starting bot: {str(e)}', 'ERROR')
        return jsonify({'error': str(e)}), 500

@app.route('/api/bot/stop', methods=['POST'])
@require_auth
def stop_bot():
    """Stop the bot"""
    global BOT_RUNNING, BOT_PROCESS, BOT_START_TIME
    
    if not BOT_RUNNING:
        return jsonify({'error': 'Bot is not running'}), 400
    
    try:
        if BOT_PROCESS:
            BOT_PROCESS.terminate()
            try:
                BOT_PROCESS.wait(timeout=5)
            except subprocess.TimeoutExpired:
                BOT_PROCESS.kill()
                BOT_PROCESS.wait()
        
        BOT_RUNNING = False
        BOT_START_TIME = None
        add_log('Bot stopped', 'INFO')
        return jsonify({'success': True, 'message': 'Bot stopped'})
    except Exception as e:
        add_log(f'Error stopping bot: {str(e)}', 'ERROR')
        return jsonify({'error': str(e)}), 500

# Commands Endpoint
@app.route('/api/bot/commands', methods=['GET'])
@require_auth
def get_commands():
    """Get available bot commands"""
    commands = [
        {'name': 'help', 'description': 'Display help information'},
        {'name': 'ping', 'description': 'Check bot latency'},
        {'name': 'status', 'description': 'Get bot status'},
        {'name': 'clear', 'description': 'Clear messages from chat'},
        {'name': 'dm', 'description': 'Send a direct message'},
        {'name': 'echo', 'description': 'Echo text'},
        {'name': 'user', 'description': 'Get user information'},
        {'name': 'snipe', 'description': 'Claim a username'},
    ]
    return jsonify({'commands': commands})

# Logs Endpoints
@app.route('/api/bot/logs', methods=['GET'])
@require_auth
def get_logs():
    """Get bot logs"""
    limit = request.args.get('limit', 50, type=int)
    return jsonify({'logs': LOGS[-limit:]})

@app.route('/api/bot/logs/clear', methods=['POST'])
@require_auth
def clear_logs():
    """Clear all logs"""
    global LOGS
    LOGS = []
    add_log('Logs cleared by user', 'INFO')
    return jsonify({'success': True, 'message': 'Logs cleared'})

# Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'bot_running': BOT_RUNNING,
        'version': '1.1.0',
        'features': ['selfbot', 'dashboard', 'username_sniper']
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    add_log(f'Server error: {str(error)}', 'ERROR')
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    add_log('=' * 50, 'INFO')
    add_log('Discord Selfbot Dashboard Server Starting', 'INFO')
    add_log('Features: Selfbot Control + Username Sniper', 'INFO')
    add_log('=' * 50, 'INFO')
    add_log(f'Host: {HOST}', 'INFO')
    add_log(f'Port: {PORT}', 'INFO')
    add_log(f'Environment: {os.getenv("FLASK_ENV", "development")}', 'INFO')
    add_log('=' * 50, 'INFO')
    
    print(f"\n{chr(27)}[1;32m")
    print("\n" + "="*60)
    print("  Discord Selfbot Dashboard - Render Edition")
    print("  with Username Sniper & Auto-Claim")
    print("="*60)
    print(f"  🌐 URL: http://{HOST}:{PORT}")
    print(f"  🔐 Default Password: {DASHBOARD_PASSWORD}")
    print(f"  🤖 Selfbot Token: {'SET' if BOT_TOKEN else 'NOT SET'}")
    print("="*60 + "\n")
    print(f"{chr(27)}[0m")
    
    try:
        app.run(
            host=HOST,
            port=PORT,
            debug=os.getenv('FLASK_ENV') != 'production',
            threaded=True,
            use_reloader=False
        )
    except Exception as e:
        add_log(f'Failed to start server: {str(e)}', 'ERROR')
        raise