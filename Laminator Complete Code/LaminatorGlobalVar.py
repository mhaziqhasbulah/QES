import asyncio
#classA-----------------------------------------------------------------------------------------------------------------
# Threads and controls
thread = None
thread2 = None
thread3 = None
terminate_threads = False
# Define a flag to control background_thread2 and background_thread3 recording
recording_status = False
# Global data storage
value1 = 0
value2 = 0
barcode_data = 0
number = 0
# Define global variables for data arrays and target temperature
recorded_data = []
target_temperature = 0  # Replace with the actual target temperature
user_target_temperature = None
user_machinetype = None

# Shared state for persistent data across WebSocket disconnections
shared_state = {
    "slider1": 0,
    "slider2": 0,
    "speedOutput": 0,
    "combinedValues": None,
    "targetValue": None,
    "jobcard": None,
    "powerOutput": 0,  # Latest power value
    "energyOutput": 0,  # Latest energy value
    "speedValue": 0,  # Current speed value
    "powerPercentage": 0,  # Current power percentage
    "machinetype": None,  # Added for machine type state
    # Add sensor keys
    "sensor1": 0.0,
    "sensor2": 0.0,
    "sensor3": 0.0,
    "sensor4": 0.0,
    "sensor5": 0.0,
    "sensor6": 0.0,
    "sensor7": 0.0,
    "sensor8": 0.0,
}

# Add serial_data to store the latest serial communication values
serial_data = {"values": [0.0] * 8}  # Initialize with default sensor values

# WebSocket clients management
connected_clients = set()  # Store connected WebSocket clients
connected_clients_lock = asyncio.Lock()  # Lock to ensure thread-safety when modifying the clients set

#classB-----------------------------------------------------------------------------------------------------------------
last_recorded_time = 0  # Initialize last recorded time

#classD-----------------------------------------------------------------------------------------------------------------
Length = 220
Width = 100
Power = 0
Wattage = 5500
percent = 0
Energy = 0

#classE-----------------------------------------------------------------------------------------------------------------
template = 'index.html'
host = '192.168.42.48'
port = 5500

#classG-----------------------------------------------------------------------------------------------------------------
bulk_data = []

#classH-----------------------------------------------------------------------------------------------------------------
# Database Connection Settings
MSSQL_CONNECTION_STRING = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'  # Update with your server details
    'DATABASE=laminatordatabase;'
    'Trusted_Connection=yes;'
)
# Table names
READ_TABLE_NAME = "preset_list"
UPDATE_TABLE_NAME = "designerfile"