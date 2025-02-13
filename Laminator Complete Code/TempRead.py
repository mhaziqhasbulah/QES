import time
import re
import GetDate
import GetTime
import LaminatorGlobalVar as lg
import serial
import json
import asyncio

async def tempread():  # Change to accept websocket instead of socketio
    try:
        port = serial.Serial(
            # port='/dev/ttyACM2',
            # port='/dev/ttyACM0',
            port='COM3',
            baudrate=115200,
            timeout=0.1,  # Reduced timeout#5,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.EIGHTBITS
        )
        print("Serial port TempRead opened successfully!")
    except serial.SerialException as e:
        print(f"Failed to open port: {e}")
        return  # Exit the function if the port cannot be opened

    # Initialize `values` with default values
    values = [0.0] * 8

    while True:
        if lg.terminate_threads:
            # sys.exit()
            break

        data = port.readline().decode('utf-8')

        if "#DATA=" in data:
            pattern = r'S1:(\d+\.\d+),S2:(\d+\.\d+),S3:(\d+\.\d+),S4:(\d+\.\d+),S5:(\d+\.\d+),S6:(\d+\.\d+),S7:(\d+\.\d+),S8:(\d+\.\d+)'
            match = re.search(pattern, data)

            if match:
                values = [float(val) for val in match.groups()]

                for sensor_id, value in enumerate(values, start=1):
                    sensor_value = value if value != 'NA' else 0
                    sensor_key = f"sensor{sensor_id}"
                    lg.shared_state[sensor_key] = sensor_value
                    event_name = f'updateSensorData_sensor{sensor_id}'
                    response = {'action': event_name, 'value': sensor_value}
                    print(response)
                    await broadcast_message(response)
            else:
                continue

        # Check if recording is enabled and if two seconds have passed since the last record
        if lg.recording_status and (time.time() - lg.last_recorded_time >= 2):
            timestamp = GetTime.gettime()  # str(gettime())
            datestamp = GetDate.getdate()  # str(getdate())
            target_temperature = lg.user_target_temperature

            new_entry = {
                'Jobcard': lg.barcode_data,
                'Time': timestamp,
                'Date': datestamp,
                'Power (W/cm2)': lg.shared_state["energyOutput"], #0, #lg.Energy, lg.shared_state["energyOutput"]
                'Power (%)': lg.value1, #0, #lg.value1, #Power percent
                'Speed': lg.shared_state["speedValue"], #0, #lg.number, lg.shared_state["speedValue"]
                'Sensor 1': values[0],
                'Sensor 2': values[1],
                'Sensor 3': values[2],
                'Sensor 4': values[3],
                'Sensor 5': values[4],
                'Sensor 6': values[5],
                'Sensor 7': values[6],
                'Sensor 8': values[7],
                'Target Temperature': target_temperature,
                'Machine': lg.user_machinetype,
            }

            # Update recorded_data by removing duplicates based on 'Time'
            lg.recorded_data = {entry['Time']: entry for entry in lg.recorded_data}
            lg.recorded_data[timestamp] = new_entry
            lg.recorded_data = list(lg.recorded_data.values())
            lg.last_recorded_time = time.time()  # Update last recorded time

        await asyncio.sleep(0.1)  # Non-blocking sleep to prevent high CPU usage

async def broadcast_message(message):
    """Broadcast messages to all connected clients."""
    if lg.connected_clients:
        await asyncio.gather(
            *[client.send(json.dumps(message)) for client in lg.connected_clients]
        )