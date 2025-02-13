import asyncio
import websockets
import json
from threading import Lock
import TestLogGS
import TestExtractPresetGS
import TempRead
import SpeedControl
import PowerControl
import LaminatorGlobalVar as lg

# Background threads with locks
thread_lock = Lock()
thread2_lock = Lock()
thread3_lock = Lock()

# Initialize WebSocket server
connected_clients = set()

async def websocket_handler(websocket, path):
    # Register client connection
    connected_clients.add(websocket)
    print(f"Client connected: {websocket.remote_address}")

    try:
        # Start background tasks (if not already running)
        with thread_lock:
            if lg.thread is None:
                lg.thread = asyncio.create_task(TempRead.tempread(websocket))  # Use async instead of background task for gevent
        with thread2_lock:
            if lg.thread2 is None:
                lg.thread2 = asyncio.create_task(SpeedControl.speedcontrol(websocket))  # Same here
        with thread3_lock:
            if lg.thread3 is None:
                lg.thread3 = asyncio.create_task(PowerControl.powercontrol(websocket))

        while True:
            # Wait for a message from the client
            message = await websocket.recv()
            print(f"Received message: {message}")

            # Process the received message (Assuming JSON format)
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                response = {
                    "status": "error",
                    "message": "Invalid JSON format"
                }
                await websocket.send(json.dumps(response))
                continue

            # Handle different actions based on the received data
            if data.get("action") == "updateSlider2":
                handle_slider_update(data, websocket)
            elif data.get("action") == "updateSlider1":
                handle_slider1_update(data, websocket)
            elif data.get("action") == "updateSlider3":
                handle_slider3_update(data, websocket)
            elif data.get("action") == "processBarcode":
                process_barcode(data, websocket)
            elif data.get("action") == "upload_data":
                upload_data(websocket)
            elif data.get("action") == "start_recording":
                start_recording(websocket)
            elif data.get("action") == "stop_recording":
                stop_recording(websocket)
            elif data.get("action") == "machinetype_recording":
                machinetype_recording(websocket)
            elif data.get("action") == "set_target_value":
                set_target_value(data, websocket)
            elif data.get("action") == "fetch_data":
                fetch_data(data, websocket)
            elif data.get("action") == "broadcastUpdate":
                message = {"action": "broadcastUpdate", "value": data.get("value")}
                await broadcast_message(message)
            else:
                response = {
                    "status": "error",
                    "message": "Unknown action"
                }
                await websocket.send(json.dumps(response))

    except websockets.ConnectionClosed:
        print(f"Connection with client {websocket.remote_address} closed.")
    finally:
        # Deregister client connection on close
        connected_clients.remove(websocket)


# Slider update handler for Slider 1
def handle_slider_update(data, websocket):
    lg.value2 = data['value']
    response = {
        "action": "updateSlider2",
        "value": data['value']
    }
    asyncio.create_task(websocket.send(json.dumps(response)))


# Slider update handler for Slider 2
def handle_slider1_update(data, websocket):
    lg.value1 = data['value']
    response = {
        "action": "updateSlider1",
        "value": data['value']
    }
    asyncio.create_task(websocket.send(json.dumps(response)))


# Slider update handler for Slider 3
def handle_slider3_update(data, websocket):
    lg.value2 = data['value']
    lg.value1 = data['value']
    response = {
        "action": "updateSlider3",
        "value1": lg.value1,
        "value2": lg.value2
    }
    asyncio.create_task(websocket.send(json.dumps(response)))


# Process barcode data
def process_barcode(data, websocket):
    lg.barcode_data = data['barcode']
    response = {
        "action": "processBarcode",
        "barcode": lg.barcode_data
    }
    asyncio.create_task(websocket.send(json.dumps(response)))


# Upload data (stop recording and save data)
def upload_data(websocket):
    lg.recording_status = False
    data_to_upload = lg.recorded_data.copy()
    TestLogGS.savelog_bulk(data_to_upload)

    # Clear recorded data after writing to the file
    lg.recorded_data = []

    response = {
        "status": "success",
        "message": "Recording stopped & Data uploaded successfully"
    }
    asyncio.create_task(websocket.send(json.dumps(response)))


# Start recording
def start_recording(websocket):
    lg.recording_status = True
    response = {
        "status": "success",
        "message": "Recording started"
    }
    asyncio.create_task(websocket.send(json.dumps(response)))


# Stop recording
def stop_recording(websocket):
    lg.recording_status = False
    response = {
        "status": "success",
        "message": "Recording stopped"
    }
    asyncio.create_task(websocket.send(json.dumps(response)))


# Set machine type for recording
def machinetype_recording(websocket):
    lg.user_machinetype = "Blue"
    response = {
        "status": "success",
        "message": "Machine set successfully"
    }
    asyncio.create_task(websocket.send(json.dumps(response)))


# Set target value
def set_target_value(data, websocket):
    try:
        lg.user_target_temperature = data.get('targetValue')
        response = {
            "status": "success",
            "message": "Target value set successfully"
        }
        asyncio.create_task(websocket.send(json.dumps(response)))
    except Exception as e:
        response = {
            "status": "error",
            "message": str(e)
        }
        asyncio.create_task(websocket.send(json.dumps(response)))

# Fetch data from a module
def fetch_data(data, websocket):
    user_input = data['user_input']
    database = TestExtractPresetGS.data_fetch(user_input)
    response = {
        "status": "success",
        "data": database
    }
    asyncio.create_task(websocket.send(json.dumps(response)))

async def broadcast_message(message):
    if connected_clients:
        await asyncio.wait([client.send(json.dumps(message)) for client in connected_clients])

# Start the WebSocket server
async def start_server():
    server = await websockets.serve(websocket_handler, "192.168.42.48", 5500)
    print("WebSocket server started at ws://192.168.42.48:5500")
    await server.wait_closed()

# Main entry point to run the server
if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("Server interrupted. Closing...")
