import pyodbc
import LaminatorGlobalVar as lg

def data_fetch(target_id):
    try:
        # Connect to the MSSQL database using Trusted Connection
        conn = pyodbc.connect(lg.MSSQL_CONNECTION_STRING)
        cursor = conn.cursor()

        # Query to fetch data based on target_id
        query = """
        SELECT 
            low_power, medium_low_power, medium_power, medium_high_power, high_power,
            speed_low, speed_medium_low, speed_medium, speed_medium_high, speed_high,
            target_temperature, jobcard
        FROM designerfile
        WHERE jobcard = ?
        """
    
        #cursor.execute(query, (int(target_id),))
        cursor.execute(query, target_id)
        result = cursor.fetchone()  # Fetch one row
    
        if result:
                print("Row found with ID:", target_id)
                output = {
                    "Low": result[0],
                    "MediumLow": result[1],
                    "Medium": result[2],
                    "MediumHigh": result[3],
                    "High": result[4],
                    "SpeedLow": result[5],
                    "SpeedMediumLow": result[6],
                    "SpeedMedium": result[7],
                    "SpeedMediumHigh": result[8],
                    "SpeedHigh": result[9],
                    "TargetTemperature": result[10],
                    "Jobcard": result[11]
                }
                print([output])  # Output as a list of dictionaries
                return [output]
        else:
                print("Row with ID", target_id, "not found.")
                return None

    except pyodbc.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()