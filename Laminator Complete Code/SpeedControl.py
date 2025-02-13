import serial
import LaminatorGlobalVar as lg
import asyncio
import json
import GetDate
import GetTime

async def speedcontrol():
    ser = serial.Serial(
        # port='/dev/ttyACM0',
        #port='/dev/ttyACM2',
        port='COM10',
        baudrate=9600,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )

    while True:
        if lg.terminate_threads:
            break

        temp2 = str(lg.value2) + "\n"
        ser.write(str(temp2).encode('utf-8'))

        await asyncio.sleep(0.1)  # Non-blocking sleep to prevent high CPU usage

        data = ser.readline().decode('utf-8').strip()
        data = data.replace('\r', '')
        #print(data)
        if not data:  # Check if data is empty
            print("Skipping...")
            continue  # Skip the loop iteration if data is empty

        lg.number = data
        if lg.number == "0":
            # Reset value when number is zero
            lg.shared_state["speedValue"] = 0  # Update shared state with speed
            response = {'action': 'updateOtherSensorData_sensorOther3', 'value': lg.shared_state["speedValue"]}
            await broadcast_message(response)  # Broadcast to all connected clients
            await asyncio.sleep(0.1)
            continue
        else:
            # Update shared state with the current speed
            lg.shared_state["speedValue"] = lg.number
            response = {'action': 'updateOtherSensorData_sensorOther3', 'value': lg.shared_state["speedValue"]} #lg.number}
            await broadcast_message(response)
            await asyncio.sleep(0.1)  # Small delay to manage the rate of data emission

        if lg.recording_status:
            timestamp = str(GetTime.gettime())
            datestamp = str(GetDate.getdate())
            lg.recorded_data[-1]['Speed'] = lg.number

        await asyncio.sleep(0.1)  # Non-blocking sleep to prevent high CPU usage

async def broadcast_message(message):
    """Broadcast messages to all connected clients."""
    if lg.connected_clients:
        await asyncio.gather(
            *[client.send(json.dumps(message)) for client in lg.connected_clients]
        )