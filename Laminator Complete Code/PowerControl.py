import time
import serial
import LaminatorGlobalVar as lg
import asyncio
import json
import GetTime
import GetDate

#def powercontrol(socketio):
#async def powercontrol(websocket):
async def powercontrol():
    # Start the timer
    start_time = time.time()

    portser = serial.Serial(
        #port='/dev/ttyACM1',
        port='COM9',
        baudrate=9600,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )

    while True:
        if lg.terminate_threads:
            break

        lg.percent = str(lg.value1) + "\n"
        portser.write(str(lg.percent).encode('utf-8'))

        await asyncio.sleep(0.1)  # Non-blocking sleep to prevent high CPU usage

        if int(lg.value1) == 0:
            # Reset energy when percent is zero
            lg.shared_state["energyOutput"] = 0
            start_time = time.time()
            # Broadcast updated state
            response = {"action": "updateOtherSensorData_sensorOther1", "value": lg.shared_state["energyOutput"]}
            await broadcast_message(response)
            await asyncio.sleep(1)
            continue
        else:
            # Calculate the elapsed time
            elapsed_time = time.time() - start_time
            lg.Power = round((((float(lg.percent) / 100) * lg.Wattage)))
            lg.Energy = ((lg.Power * elapsed_time) / (lg.Length * lg.Width))

            # Update shared state
            lg.shared_state["energyOutput"] = lg.Energy

            response = {"action": "updateOtherSensorData_sensorOther1", "value": lg.shared_state["energyOutput"]}
            await broadcast_message(response)
            await asyncio.sleep(1)  # Small delay to manage the rate of data emission

        if lg.recording_status:
            timestamp = str(GetTime.gettime())
            datestamp = str(GetDate.getdate())
            lg.recorded_data[-1]['Power (W/cm2)'] = lg.Energy
            lg.recorded_data[-1]['Power (%)'] = lg.value1

        await asyncio.sleep(0.1)  # Non-blocking sleep to prevent high CPU usage

async def broadcast_message(message):
    """Broadcast messages to all connected clients."""
    if lg.connected_clients:
        await asyncio.gather(
            *[client.send(json.dumps(message)) for client in lg.connected_clients]
        )