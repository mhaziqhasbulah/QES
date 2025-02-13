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

async def websocket_handler(websocket, path):
    # Register client connection
    lg.connected_clients.add(websocket)
    print(f"Client connected: {websocket.remote_address}")

    try:
        # Send current shared state to the newly connected client
        await send_shared_state(websocket)

        # Start background tasks (if not already running)
        with thread_lock:
            if lg.thread is None:
                lg.thread = asyncio.create_task(TempRead.tempread())  # Use async instead of background task for gevent
        with thread2_lock:
            if lg.thread2 is None:
                lg.thread2 = asyncio.create_task(SpeedControl.speedcontrol())  # Same here
        with thread3_lock:
            if lg.thread3 is None:
                lg.thread3 = asyncio.create_task(PowerControl.powercontrol())

        # Handle incoming messages
        #async for message in websocket:
        while True:
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
                await handle_slider2_update(data)
            elif data.get("action") == "updateSlider1":
                await handle_slider1_update(data)
            elif data.get("action") == "updateSlider3":
                await handle_slider3_update(data)
            elif data.get("action") == "processBarcode":
                await handle_process_barcode(data)
            elif data.get("action") == "upload_data":
                await upload_data()
            elif data.get("action") == "start_recording":
                await start_recording()
            elif data.get("action") == "stop_recording":
                await stop_recording()
            elif data.get("action") == "machinetype_recording":
                await machinetype_recording()
            elif data.get("action") == "set_target_value":
                await set_target_value(data)
            elif data.get("action") == "fetch_data":
                await fetch_data(data)
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
        # De-register client connection on close
        lg.connected_clients.remove(websocket)

# Slider update handlers
async def handle_slider_update(slider_id, value):
    lg.shared_state[slider_id] = value
    await broadcast_message({"action": f"update{slider_id.capitalize()}", "value": value})

# Slider update handler for Slider 1
async def handle_slider2_update(data):
    """Updates slider2 value and broadcasts the new state."""
    lg.value2 = data['value']
    await handle_slider_update("slider2", data["value"])

# Slider update handler for Slider 2
async def handle_slider1_update(data):
    """Updates slider1 value and broadcasts the new state."""
    lg.value1 = data['value']
    await handle_slider_update("slider1", data["value"])

# Slider update handler for Slider 3
async def handle_slider3_update(data):
    """Handles slider3 updates and broadcasts them."""
    lg.value2 = data['value']
    lg.value1 = data['value']
    lg.shared_state["slider1"] = data["value1"]
    lg.shared_state["slider2"] = data["value2"]
    await broadcast_message({"action": "updateSlider3", "value1": data["value1"], "value2": data["value2"]})

# Process barcode data
async def handle_process_barcode(data):
    lg.barcode_data = data['barcode']
    await broadcast_message({"action": "processBarcode", "barcode": lg.barcode_data})

# Upload data (stop recording and save data)
async def upload_data():
    lg.shared_state["recordingStatus"] = False
    data_to_upload = lg.recorded_data.copy()
    print(data_to_upload)
    TestLogGS.savelog_bulk(data_to_upload)

    # Clear recorded data after writing to the file
    lg.recorded_data = []
    await broadcast_message({"action": "uploadData", "status": "success"})

# Start recording
async def start_recording():
    lg.shared_state["recordingStatus"] = True
    await broadcast_message({"action": "updateRecordingState", "recordingStatus": True})

# Stop recording
async def stop_recording():
    lg.shared_state["recordingStatus"] = False
    await broadcast_message({"action": "updateRecordingState", "recordingStatus": False})

# Set machine type for recording
async def machinetype_recording():
    lg.user_machinetype = "Blue"
    # Update shared state
    lg.shared_state["machinetype"] = lg.user_machinetype
    await broadcast_message({"action": "updateMachineType", "machinetype": lg.user_machinetype})

# Set target value
async def set_target_value(data):
    lg.shared_state["targetValue"] = data["targetValue"]
    await broadcast_message({"action": "updateState", "state": lg.shared_state})

# Fetch data from a module
async def fetch_data(data):
    user_input = data['user_input']
    database = TestExtractPresetGS.data_fetch(user_input)
    #if database:
    #    combinedValues = {
    #        "Low": {"optionValue": database[0]["Low"], "speedValue": database[0]["SpeedLow"]},
    #        "MediumLow": {"optionValue": database[0]["MediumLow"], "speedValue": database[0]["SpeedMediumLow"]},
    #        "Medium": {"optionValue": database[0]["Medium"], "speedValue": database[0]["SpeedMedium"]},
    #        "MediumHigh": {"optionValue": database[0]["MediumHigh"], "speedValue": database[0]["SpeedMediumHigh"]},
    #        "High": {"optionValue": database[0]["High"], "speedValue": database[0]["SpeedHigh"]},
    #    }
    #lg.shared_state["combinedValues"] = database
    await broadcast_message({"status": "fetch", "data": database})
    #else:
    #await websocket.send(json.dumps({"action": "fetch_data", "status": "error", "message": "No data found."}))

async def send_shared_state(websocket):
    """Sends the current shared state to a connected client."""
    message = {"action": "updateState", "state": lg.shared_state}
    await websocket.send(json.dumps(message))

# Broadcast a message to all connected clients
async def broadcast_updates():
    """Continuously broadcasts shared state to all clients."""
    while True:
        if lg.connected_clients:
            await broadcast_message({"action": "updateState", "state": lg.shared_state})
        await asyncio.sleep(1)  # Adjust the interval as needed

async def broadcast_message(message):
    """Broadcasts a message to all connected clients."""
    if lg.connected_clients:
        await asyncio.gather(*[client.send(json.dumps(message)) for client in lg.connected_clients])

# Start the WebSocket server
async def start_server():
    server = await websockets.serve(websocket_handler, "192.168.42.48", 5500)
    print("WebSocket server started at ws://192.168.42.48:5500")
    asyncio.create_task(broadcast_updates())  # Start broadcasting updates
    await server.wait_closed()

# Main entry point to run the server
if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("Server interrupted. Closing...")
