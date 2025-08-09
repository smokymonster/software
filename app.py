from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/uploadlogjson', methods=['POST'])
def upload_log_json():
    """
    Upload JSON log data with name and exam parameters
    Expected URL format: /uploadlogjson?name=<name>&exam=<exam>
    """
    try:
        # Get query parameters
        name = request.args.get('name', 'unknown')
        exam = request.args.get('exam', 'unknown')
        
        # Get JSON data from request body
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Create logs directory if it doesn't exist
        logs_dir = 'logs'
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{name}_{exam}_{timestamp}.json"
        filepath = os.path.join(logs_dir, filename)
        
        # Add metadata to the JSON data
        log_entry = {
            'metadata': {
                'name': name,
                'exam': exam,
                'timestamp': timestamp,
                'upload_time': datetime.now().isoformat()
            },
            'data': json_data
        }
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(log_entry, f, indent=2)
        
        print(f"[INFO] Uploaded log data: {filename}")
        
        return jsonify({
            'status': 'success',
            'message': 'JSON data uploaded successfully',
            'filename': filename,
            'name': name,
            'exam': exam
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Failed to upload JSON data: {str(e)}")
        return jsonify({'error': f'Failed to upload data: {str(e)}'}), 500

@app.route('/askgemini', methods=['POST'])
def ask_gemini():
    """
    Ask Gemini AI for question answers
    Expected JSON body: {
        'question': str,
        'is_frq': bool,
        'service': str,
        'exam': str,
        'code': str
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        question = data.get('question', '')
        is_frq = data.get('is_frq', False)
        service = data.get('service', '')
        exam = data.get('exam', '')
        code = data.get('code', '')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        print(f"[INFO] Gemini request - Service: {service}, Exam: {exam}, FRQ: {is_frq}")
        print(f"[INFO] Question: {question[:100]}...")
        
        # Mock response for demonstration - in real implementation, integrate with Gemini API
        if is_frq:
            # Free Response Question format
            response = {
                'initialAttempt': 'This is a sample reasoning for the FRQ question.',
                'finalAnswer': 'This is the final answer to the free response question.'
            }
        else:
            # Multiple Choice Question format
            response = {
                'rationale': 'This is the reasoning behind the answer selection.',
                'selectedChoice': 'A'
            }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"[ERROR] Gemini request failed: {str(e)}")
        return jsonify({'error': f'Failed to process question: {str(e)}'}), 500

@app.route('/checkthis', methods=['GET'])
def check_this():
    """
    Check deletion status and quit commands
    Expected query parameters: code, hwid, name
    """
    try:
        code = request.args.get('code', '')
        hwid = request.args.get('hwid', '')
        name = request.args.get('name', '')
        
        print(f"[INFO] Check request - Code: {code}, HWID: {hwid[:10]}..., Name: {name}")
        
        # Mock response - in real implementation, check against database
        response = {
            'delete': False,  # Set to True to trigger script deletion
            'quit': False     # Set to True to trigger quit command
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"[ERROR] Check request failed: {str(e)}")
        return jsonify({'error': f'Failed to process check: {str(e)}'}), 500

@app.route('/downloadproxy', methods=['GET'])
def download_proxy():
    """
    Automatic proxy configuration endpoint
    Returns a PAC (Proxy Auto-Configuration) file
    """
    try:
        # PAC file content for automatic proxy configuration
        pac_content = """
function FindProxyForURL(url, host) {
    // Proxy configuration
    var proxy = "PROXY 127.0.0.1:8080";

    // Send all traffic through the proxy
    return proxy;
}
"""

        print("[INFO] Serving proxy configuration file")

        return pac_content, 200, {
            'Content-Type': 'application/x-ns-proxy-autoconfig',
            'Content-Disposition': 'inline; filename="proxy.pac"'
        }

    except Exception as e:
        print(f"[ERROR] Proxy config request failed: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information"""
    return jsonify({
        'name': 'Backend API Server',
        'version': '1.0.0',
        'endpoints': [
            'POST /uploadlogjson?name=<name>&exam=<exam>',
            'POST /askgemini',
            'GET /checkthis?code=<code>&hwid=<hwid>&name=<name>',
            'GET /downloadproxy',
            'GET /health'
        ],
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    print("[INFO] Starting Flask server...")
    print("[INFO] Available endpoints:")
    print("  - POST /uploadlogjson?name=<name>&exam=<exam>")
    print("  - POST /askgemini")
    print("  - GET /checkthis?code=<code>&hwid=<hwid>&name=<name>")
    print("  - GET /downloadproxy")
    print("  - GET /health")
    print("  - GET /")
    
    # Get port from environment variable (for Render deployment) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Use debug=False for production
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
