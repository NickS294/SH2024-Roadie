from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
import asyncio
import json
import logging
from hypercorn.config import Config
from hypercorn.asyncio import serve
import base64
from utils import *
import ssl

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

conversation_task = None
speech_task = None

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

@app.route('/grant_permission', methods=['POST'])
def grant_permission():
    global conversation_task, speech_task
    
    try:
        if conversation_task is None or conversation_task.done():
            conversation_task = asyncio.run_coroutine_threadsafe(manage_conversation(), loop)
            speech_task = asyncio.run_coroutine_threadsafe(speech_worker(), loop)
            logger.info("Conversation and speech tasks started successfully")
            return jsonify({"message": "Conversation started"}), 202
        else:
            logger.warning("Attempted to start conversation while one is already in progress")
            return jsonify({"message": "Conversation already in progress"}), 400
    except Exception as e:
        logger.error(f"Error in grant_permission: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to start conversation: {str(e)}"}), 500

@app.route('/stream_audio', methods=['POST'])
def stream_audio():
    content_type = request.headers.get('Content-Type', '')
    if content_type.startswith('audio/'):
        try:
            chunk = request.get_data()
            loop.call_soon_threadsafe(audio_queue.put_nowait, (content_type, chunk))
            return "", 204
        except Exception as e:
            logger.error(f"Error in stream_audio: {str(e)}", exc_info=True)
            return jsonify({"error": f"Failed to process audio: {str(e)}"}), 500
    else:
        return "Unsupported Media Type", 415
    
@app.route('/stop_listening', methods=['POST'])
def stop_listening():
    try:
        loop.call_soon_threadsafe(audio_queue.put_nowait, None)
        return jsonify({"message": "Stopped listening"}), 200
    except Exception as e:
        logger.error(f"Error in stop_listening: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to stop listening: {str(e)}"}), 500

@app.route('/get_ai_response', methods=['GET'])
def get_ai_response():
    def generate():
        while True:
            try:
                message = speech_queue.get(timeout=1)
                message_data = json.loads(message)
                if message_data['type'] == 'audio':
                    # Convert binary audio data to base64
                    audio_base64 = base64.b64encode(message_data['content'].encode('latin1')).decode('utf-8')
                    message_data['content'] = audio_base64
                yield f"data: {json.dumps(message_data)}\n\n"
                if message_data['type'] == 'end':
                    break
            except asyncio.TimeoutError:
                yield f"data: {json.dumps({'type': 'keepalive'})}\n\n"
            except Exception as e:
                logger.error(f"Error in get_ai_response generator: {str(e)}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
                break

    return Response(generate(), mimetype="text/event-stream")

@app.route('/')
def serve_html():
    return send_from_directory('.', 'index.html')

def run_app():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain('/home/aalmonte/workspace/fullchain.pem', '/home/aalmonte/workspace/privkey.pem')
    app.run(host='0.0.0.0', port=5001, ssl_context=ssl_context, debug=True, use_reloader=False)

if __name__ == "__main__":
    import threading
    
    # Start the Flask app in a separate thread
    flask_thread = threading.Thread(target=run_app)
    flask_thread.start()
    
    # Run the event loop in the main thread
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()