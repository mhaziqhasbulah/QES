import pyodbc
from datetime import datetime
import LaminatorGlobalVar as lg

def savelog_bulk(data_list):
    """Insert log data into the logs table, ensuring new rows are always inserted."""
    
    connection = None  # Initialize connection variable
    try:
        # Connect to the MS SQL Server database
        connection = pyodbc.connect(lg.MSSQL_CONNECTION_STRING)
        cursor = connection.cursor()
            
        # SQL Insert query
        sql_insert_query = """
        INSERT INTO logs 
        (jobcard, time, date, power_w_cm2, power_percent, speed, 
         sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, 
         sensor7, sensor8, target_temperature, machine) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Prepare bulk data for insertion
        #bulk_data = []
        for data_point in data_list:
            time_str = data_point['Time']
            date_str = data_point['Date']
            new_data = (
                data_point['Jobcard'],
                datetime.strptime(time_str, "%H:%M:%S").time(),  # Assuming Time is in HH:MM:SS
                datetime.strptime(date_str, "%d%m%Y").date(),    # Assuming Date is in DDMMYYYY
                data_point['Power (W/cm2)'],
                data_point['Power (%)'],
                data_point['Speed'],
                data_point['Sensor 1'],
                data_point['Sensor 2'],
                data_point['Sensor 3'],
                data_point['Sensor 4'],
                data_point['Sensor 5'],
                data_point['Sensor 6'],
                data_point['Sensor 7'],
                data_point['Sensor 8'],
                data_point['Target Temperature'],
                data_point['Machine']
            )
            lg.bulk_data.append(new_data)
            
            print(lg.bulk_data)

        if not lg.bulk_data:
            print("lg.bulk_data is empty.")
        else:
            print(f"Inserting {len(lg.bulk_data)} records.")

        # Execute the insert query for all data points
        cursor.executemany(sql_insert_query, lg.bulk_data)
        
        # Commit the transaction
        connection.commit()
        print(f"{cursor.rowcount} rows inserted successfully.")
        
    except pyodbc.Error as e:
        print(f"Error: {e}")
        
    finally:
        # Close connection if it was established
        if connection:
            cursor.close()
            connection.close()
            print("MSSQL connection is closed.")