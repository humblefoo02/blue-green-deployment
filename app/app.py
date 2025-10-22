from flask import Flask, jsonify, render_template_string, request
import os
import socket
from datetime import datetime
import random
import time
import threading

app = Flask(__name__)

VERSION = os.getenv('APP_VERSION', '1.0')
COLOR = os.getenv('APP_COLOR', 'blue')
PORT = int(os.getenv('PORT', 5000))

# Dynamic data storage
app_data = {
    'request_count': 0,
    'start_time': time.time(),
    'visitors': [],
    'api_calls': [],
    'health_checks': 0,
    'errors': 0
}

# Thread-safe counter
from threading import Lock
data_lock = Lock()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ color|upper }} - Dynamic Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, 
                {% if color == 'blue' %}
                    #1e3c72 0%, #2a5298 50%, #7e22ce 100%
                {% else %}
                    #134e4a 0%, #059669 50%, #10b981 100%
                {% endif %}
            );
            min-height: 100vh;
            padding: 20px;
            color: white;
        }
        .dashboard {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            margin-bottom: 30px;
            border: 2px solid rgba(255, 255, 255, 0.2);
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        h1 {
            font-size: 3.5em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 5px;
            animation: glow 2s ease-in-out infinite alternate;
        }
        @keyframes glow {
            from { text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #fff; }
            to { text-shadow: 0 0 20px #fff, 0 0 30px #fff, 0 0 40px #fff, 0 0 50px #fff; }
        }
        .version-badge {
            display: inline-block;
            padding: 10px 25px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50px;
            font-size: 1.2em;
            font-weight: bold;
            margin-top: 10px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s, box-shadow 0.3s;
            animation: slideIn 0.5s ease-out;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-30px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        .card-title {
            font-size: 1.3em;
            margin-bottom: 15px;
            font-weight: bold;
            opacity: 0.9;
            border-bottom: 2px solid rgba(255, 255, 255, 0.3);
            padding-bottom: 10px;
        }
        .card-value {
            font-size: 2.5em;
            font-weight: bold;
            margin: 15px 0;
            text-align: center;
            animation: pulse 2s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        .info-item:last-child { border-bottom: none; }
        .label { font-weight: 600; opacity: 0.8; }
        .value { font-weight: bold; }
        .status-indicator {
            width: 15px;
            height: 15px;
            border-radius: 50%;
            background: #10b981;
            display: inline-block;
            margin-right: 10px;
            animation: blink 1s ease-in-out infinite;
        }
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        .chart-container {
            grid-column: 1 / -1;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .progress-bar {
            width: 100%;
            height: 30px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #10b981, #059669);
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            background: rgba(255, 255, 255, 0.3);
            color: white;
        }
        .btn:hover {
            background: rgba(255, 255, 255, 0.5);
            transform: scale(1.05);
        }
        .log-container {
            max-height: 300px;
            overflow-y: auto;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        .log-entry {
            padding: 5px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .timestamp { color: #fbbf24; }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .metric-box {
            background: rgba(255, 255, 255, 0.15);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .metric-label { font-size: 0.9em; opacity: 0.8; margin-bottom: 8px; }
        .metric-value { font-size: 1.8em; font-weight: bold; }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1><span class="status-indicator"></span>{{ color }} Environment</h1>
            <div class="version-badge">Version {{ version }}</div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="card-title">🔄 Total Requests</div>
                <div class="card-value" id="requests">{{ request_count }}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ (request_count % 100) }}%">
                        {{ (request_count % 100) }}%
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-title">⏱️ Uptime</div>
                <div class="card-value" id="uptime">{{ uptime }}s</div>
                <div style="text-align: center; margin-top: 10px; opacity: 0.8;">
                    {{ uptime_formatted }}
                </div>
            </div>

            <div class="card">
                <div class="card-title">💚 Health Checks</div>
                <div class="card-value">{{ health_checks }}</div>
            </div>

            <div class="card">
                <div class="card-title">📊 System Info</div>
                <div class="info-item">
                    <span class="label">Hostname:</span>
                    <span class="value">{{ hostname }}</span>
                </div>
                <div class="info-item">
                    <span class="label">Environment:</span>
                    <span class="value">{{ color|upper }}</span>
                </div>
                <div class="info-item">
                    <span class="label">Timestamp:</span>
                    <span class="value">{{ current_time }}</span>
                </div>
            </div>

            <div class="card">
                <div class="card-title">🌐 Recent Visitors</div>
                <div class="log-container">
                    {% for visitor in recent_visitors %}
                    <div class="log-entry">
                        <span class="timestamp">{{ visitor.time }}</span> - {{ visitor.ip }}
                    </div>
                    {% endfor %}
                </div>
            </div>

            <div class="card">
                <div class="card-title">📈 Live Metrics</div>
                <div class="metric-grid">
                    <div class="metric-box">
                        <div class="metric-label">Random ID</div>
                        <div class="metric-value">{{ random_id }}</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Load</div>
                        <div class="metric-value">{{ load }}%</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="chart-container">
            <div class="card-title">🎯 API Endpoints</div>
            <div class="button-group">
                <button class="btn" onclick="location.href='/api'">📡 JSON API</button>
                <button class="btn" onclick="location.href='/health'">💚 Health Check</button>
                <button class="btn" onclick="location.href='/info'">ℹ️ System Info</button>
                <button class="btn" onclick="location.href='/stats'">📊 Statistics</button>
                <button class="btn" onclick="location.reload()">🔄 Refresh</button>
            </div>
        </div>
    </div>

    <script>
        // Auto-refresh every 5 seconds
        setTimeout(() => location.reload(), 5000);
        
        // Dynamic counter animation
        let counter = {{ uptime }};
        setInterval(() => {
            counter++;
            document.getElementById('uptime').innerText = counter + 's';
        }, 1000);

        // Request counter animation
        let reqCounter = {{ request_count }};
        setInterval(() => {
            reqCounter++;
            document.getElementById('requests').innerText = reqCounter;
        }, 3000);
    </script>
</body>
</html>
'''

def format_uptime(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f'{hours}h {minutes}m {secs}s'

@app.route('/')
def home():
    with data_lock:
        app_data['request_count'] += 1
        
        # Track visitor
        visitor_ip = request.remote_addr or 'unknown'
        app_data['visitors'].append({
            'ip': visitor_ip,
            'time': datetime.now().strftime('%H:%M:%S'),
            'timestamp': time.time()
        })
        
        # Keep only last 10 visitors
        app_data['visitors'] = app_data['visitors'][-10:]
        
        uptime = int(time.time() - app_data['start_time'])
        
        return render_template_string(
            HTML_TEMPLATE,
            color=COLOR,
            version=VERSION,
            hostname=socket.gethostname(),
            request_count=app_data['request_count'],
            health_checks=app_data['health_checks'],
            uptime=uptime,
            uptime_formatted=format_uptime(uptime),
            current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            recent_visitors=app_data['visitors'][::-1],
            random_id=random.randint(1000, 9999),
            load=random.randint(10, 90)
        )

@app.route('/api')
def api():
    with data_lock:
        app_data['request_count'] += 1
        app_data['api_calls'].append(time.time())
        
        return jsonify({
            'status': 'success',
            'message': f'Dynamic API from {COLOR} deployment',
            'data': {
                'version': VERSION,
                'color': COLOR,
                'hostname': socket.gethostname(),
                'timestamp': datetime.now().isoformat(),
                'request_count': app_data['request_count'],
                'api_calls': len(app_data['api_calls']),
                'uptime_seconds': int(time.time() - app_data['start_time']),
                'random_data': {
                    'id': random.randint(1, 1000000),
                    'value': random.random() * 100,
                    'items': [random.randint(1, 100) for _ in range(5)]
                }
            }
        })

@app.route('/health')
def health():
    with data_lock:
        app_data['health_checks'] += 1
        
    uptime = int(time.time() - app_data['start_time'])
    
    return jsonify({
        'status': 'healthy',
        'color': COLOR,
        'version': VERSION,
        'uptime_seconds': uptime,
        'checks': app_data['health_checks'],
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/info')
def info():
    return jsonify({
        'application': 'Blue-Green Deployment - Dynamic Flask App',
        'framework': 'Flask 3.0.0',
        'version': VERSION,
        'environment': COLOR,
        'hostname': socket.gethostname(),
        'port': PORT,
        'start_time': datetime.fromtimestamp(app_data['start_time']).isoformat(),
        'python_version': os.sys.version
    })

@app.route('/stats')
def stats():
    with data_lock:
        uptime = int(time.time() - app_data['start_time'])
        
        return jsonify({
            'statistics': {
                'total_requests': app_data['request_count'],
                'health_checks': app_data['health_checks'],
                'api_calls': len(app_data['api_calls']),
                'unique_visitors': len(set(v['ip'] for v in app_data['visitors'])),
                'uptime_seconds': uptime,
                'uptime_formatted': format_uptime(uptime),
                'requests_per_minute': round(app_data['request_count'] / (uptime / 60), 2) if uptime > 0 else 0
            },
            'environment': {
                'color': COLOR,
                'version': VERSION,
                'hostname': socket.gethostname()
            },
            'timestamp': datetime.now().isoformat()
        })

@app.route('/reset')
def reset():
    with data_lock:
        app_data['request_count'] = 0
        app_data['visitors'] = []
        app_data['api_calls'] = []
        app_data['health_checks'] = 0
        app_data['start_time'] = time.time()
        
    return jsonify({'status': 'reset', 'message': 'All counters reset successfully'})

if __name__ == '__main__':
    print(f'Starting Dynamic {COLOR} Flask Application')
    print(f'Version: {VERSION}')
    print(f'Port: {PORT}')
    print(f'Environment: {COLOR.upper()}')
    print('=' * 50)
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)