#!/usr/bin/env python3
"""
Discord Selfbot Dashboard Server
Provides REST API for the web dashboard to control the selfbot
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import psutil
import json
import logging
from datetime import datetime
from functools import wraps
import subprocess
import time

app = Flask(__name__)
CORS(app)

# Configuration
DASHBOARD_PASSWORD = os.getenv('DASHBOARD_PASSWORD', 'admin123')
BOT_TOKEN = os.getenv('DISCORD_TOKEN', '')
BOT_PROCESS = None
BOT_RUNNING = False
BOT_STATS = {
    'messages_sent': 0,
    'commands_executed': 0,
    'guild_count': 0,
    'friend_count': 0
}
LOGS = []

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or auth != __import__('base64').b64encode(DASHBOARD_PASSWORD.encode()).decode():
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

# Logging helper
def add_log(message, level='INFO'):
    log_entry = {
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'level': level,
        'message': message
    }
    LOGS.append(log_entry)
    if len(LOGS) > 100:  # Keep only last 100 logs
        LOGS.pop(0)
    logger.log(getattr(logging, level), message)

# Bot Control Endpoints
@app.route('/api/bot/status', methods=['GET'])
@require_auth
def get_bot_status():
    """Get current bot status"""
    return jsonify({
        'connected': BOT_RUNNING,
        'status': 'online' if BOT_RUNNING else 'offline',
        'uptime_seconds': get_bot_uptime(),
        'latency': 50,  # Should be fetched from actual bot
        'bot_name': 'Selfbot',
        'bot_id': '123456789',
        'connected_since': datetime.now().isoformat()
    })

@app.route('/api/bot/stats', methods=['GET'])
@require_auth
def get_bot_stats():
    """Get bot statistics"""
    return jsonify(BOT_STATS)

@app.route('/api/server/info', methods=['GET'])
@require_auth
def get_server_info():
    """Get server resource usage"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        return jsonify({
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_mb': memory.available / (1024 * 1024),
            'disk_percent': psutil.disk_usage('/').percent
        })
    except Exception as e:
        add_log(f'Error getting server info: {str(e)}', 'ERROR')
        return jsonify({'error': str(e)}), 500

@app.route('/api/bot/start', methods=['POST'])
@require_auth
def start_bot():
    """Start the bot"""
    global BOT_RUNNING, BOT_PROCESS
    
    if BOT_RUNNING:
        return jsonify({'error': 'Bot is already running'}), 400
    
    try:
        # Start bot process - adjust command based on your bot setup
        BOT_PROCESS = subprocess.Popen(
            ['python3', 'selfbot.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        BOT_RUNNING = True
        add_log('Bot started successfully', 'SUCCESS')
        return jsonify({'success': True, 'message': 'Bot started'})
    except Exception as e:
        add_log(f'Error starting bot: {str(e)}', 'ERROR')
        return jsonify({'error': str(e)}), 500

@app.route('/api/bot/stop', methods=['POST'])
@require_auth
def stop_bot():
    """Stop the bot"""
    global BOT_RUNNING, BOT_PROCESS
    
    if not BOT_RUNNING:
        return jsonify({'error': 'Bot is not running'}), 400
    
    try:
        if BOT_PROCESS:
            BOT_PROCESS.terminate()
            BOT_PROCESS.wait(timeout=5)
        BOT_RUNNING = False
        add_log('Bot stopped', 'INFO')
        return jsonify({'success': True, 'message': 'Bot stopped'})
    except Exception as e:
        add_log(f'Error stopping bot: {str(e)}', 'ERROR')
        return jsonify({'error': str(e)}), 500

# Bot Commands Endpoint
@app.route('/api/bot/commands', methods=['GET'])
@require_auth
def get_commands():
    """Get available bot commands"""
    commands = [
        {'name': 'help', 'description': 'Display help information'},
        {'name': 'ping', 'description': 'Check bot latency'},
        {'name': 'status', 'description': 'Get bot status'},
        {'name': 'stats', 'description': 'Display bot statistics'},
        # Add more commands as needed
    ]
    return jsonify({'commands': commands})

# Messaging Endpoint
@app.route('/api/bot/send-message', methods=['POST'])
@require_auth
def send_message():
    """Send a message through the bot"""
    data = request.get_json()
    channel_id = data.get('channel_id')
    message = data.get('message')
    
    if not channel_id or not message:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # This would integrate with actual bot to send message
        BOT_STATS['messages_sent'] += 1
        add_log(f'Message sent to channel {channel_id}', 'INFO')
        return jsonify({'success': True, 'message': 'Message sent'})
    except Exception as e:
        add_log(f'Error sending message: {str(e)}', 'ERROR')
        return jsonify({'error': str(e)}), 500

# Settings Endpoint
@app.route('/api/bot/settings', methods=['POST'])
@require_auth
def save_settings():
    """Save bot settings"""
    data = request.get_json()
    
    try:
        settings = {
            'prefix': data.get('prefix', '.'),
            'auto_start': data.get('auto_start', False),
            'debug_mode': data.get('debug_mode', False)
        }
        
        # Save to file
        with open('bot_settings.json', 'w') as f:
            json.dump(settings, f, indent=4)
        
        add_log('Settings saved', 'INFO')
        return jsonify({'success': True, 'message': 'Settings saved'})
    except Exception as e:
        add_log(f'Error saving settings: {str(e)}', 'ERROR')
        return jsonify({'error': str(e)}), 500

# Logs Endpoints
@app.route('/api/bot/logs', methods=['GET'])
@require_auth
def get_logs():
    """Get bot logs"""
    return jsonify({'logs': LOGS[-50:]})

@app.route('/api/bot/logs/clear', methods=['POST'])
@require_auth
def clear_logs():
    """Clear all logs"""
    global LOGS
    LOGS = []
    return jsonify({'success': True, 'message': 'Logs cleared'})

# Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'bot_running': BOT_RUNNING
    })

# Helper functions
def get_bot_uptime():
    """Get bot uptime in seconds"""
    # This would integrate with actual bot uptime tracking
    return 0

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    add_log(f'Server error: {str(error)}', 'ERROR')
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    add_log('Dashboard server starting...', 'INFO')
    print("""\n
    ╔════════════════════════════════════════╗
    ║  Discord Selfbot Dashboard Server      ║
    ║  Starting on http://localhost:5000     ║
    ║  Visit http://localhost:5000/dashboard ║
    ╚════════════════════════════════════════╝
    
    Default Password: admin123
    Change it with DASHBOARD_PASSWORD env var
    
    """)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )