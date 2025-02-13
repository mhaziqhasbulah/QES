from gevent import monkey
monkey.patch_all()
from flask import Flask, render_template, request, jsonify
import pyodbc
import time
import LaminatorGlobalVar as lg
from flask_socketio import SocketIO
from flask_cors import CORS
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'quantum!'
socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins='*')
CORS(app)  # Enable CORS for all routes

def connect_db():
    try:
        conn = pyodbc.connect(lg.MSSQL_CONNECTION_STRING)
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def update_row(cursor, connection, designerfile_row, preset_row):
    """Update the designerfile row with data from the preset_list."""

    try:
        update_query = f"""
            UPDATE {lg.UPDATE_TABLE_NAME}
            SET low_power = ?, medium_low_power = ?, medium_power = ?, medium_high_power = ?, high_power = ?,
                speed_low = ?, speed_medium_low = ?, speed_medium = ?, speed_medium_high = ?, speed_high = ?,
                target_temperature = ?
            WHERE jobcard = ? AND rig = ? AND sail_type = ? AND product_m = ?
        """
        cursor.execute(update_query, (
            preset_row[9],  # Power_Low
            preset_row[10], # Power_Medium_Low
            preset_row[11], # Power_Medium
            preset_row[12], # Power_Medium_High
            preset_row[13], # Power_High
            preset_row[14], # Speed_Low
            preset_row[15], # Speed_Medium_Low
            preset_row[16], # Speed_Medium
            preset_row[17], # Speed_Medium_High
            preset_row[18], # Speed_High
            preset_row[19], # Target_Internal_Temp_C
            designerfile_row[0],  # jobcard
            designerfile_row[3],  # rig
            designerfile_row[6],  # sail_type
            designerfile_row[7]   # product_m
        ))
        connection.commit()
        print(f"Row for jobcard {designerfile_row[0]} updated successfully.")
    except pyodbc.Error as err:
        print(f"SQL Error during update: {err}")

def find_matching_preset(cursor, designerfile_row):
    """Find a matching preset based on rig, sail_type, product_m, and other conditions."""
    try:
        rig = designerfile_row[3] if designerfile_row[3] in ['MOTH', 'MELGES 32', 'LUETJE 47', 'TP52'] else None
        sail_type = designerfile_row[6] if designerfile_row[6] in ['MAINSAIL', 'LGT MAINSAIL'] else None
        product_m = designerfile_row[7] if designerfile_row[7] in ['M9', 'M7'] else None

        #print(f"Rig: {rig}, Sail Type: {sail_type}, Product: {product_m}")

        query = f"""
            SELECT * FROM {lg.READ_TABLE_NAME}
            WHERE (Rig = ? OR ? IS NULL) AND
                (Sail_Type = ? OR ? IS NULL) AND
                (Product = ? OR ? IS NULL) AND
                Film_Laminate = ? AND
                Laminator_Yellow_Blue = ? AND
                DPI_At_1_2_Leech_MIN <= ? AND
                DPI_At_1_2_Leech_MAX >= ?
        """

        # Print the final query and parameters for debugging
        #print(f"Executing query: {query}")
        #print(f"With parameters: {rig}, {rig}, {sail_type}, {sail_type}, {product_m}, {product_m}, "
        #      f"{designerfile_row[17]}, {designerfile_row[25]}, {designerfile_row[14]}, {designerfile_row[15]}")

        cursor.execute(query, (
            rig,  # Rig
            rig,  # Rig (again to check if rig is NULL)
            sail_type,  # Sail_Type
            sail_type,  # Sail_Type (again to check if sail_type is NULL)
            product_m,  # Product
            product_m,  # Product (again to check if product_m is NULL)
            designerfile_row[17],  # Film_Laminate
            designerfile_row[25],  # Laminator_Yellow_Blue
            designerfile_row[14],  # DPI min
            designerfile_row[14]  # DPI max
        ))
        preset_row = cursor.fetchone()
        return preset_row
    except pyodbc.Error as err:
        print(f"SQL Error during preset search: {err}")
        return None

def update_designerfile():
    """Continuously fetch and update designerfile rows with preset data."""
    while True:
        try:
            connection = pyodbc.connect(lg.MSSQL_CONNECTION_STRING)
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {lg.UPDATE_TABLE_NAME}")
            designerfile_values = cursor.fetchall()

            for designerfile_row in designerfile_values:
                if len(designerfile_row) >= 25:
                    preset_row = find_matching_preset(cursor, designerfile_row)

                    if preset_row:
                        update_row(cursor, connection, designerfile_row, preset_row)
                    else:
                        print(f"No update performed for jobcard {designerfile_row[0]}.")
                else:
                    print(f"Skipping invalid designerfile row: {designerfile_row[0]} (insufficient data).")

            time.sleep(5)  # Adjust sleep time as needed

        except pyodbc.Error as err:
            print(f"SQL Error during main loop: {err}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                
# New code for transferring highest temperature
def transfer_highest_temperature_for_latest_jobcard(cursor, connection):
    try:
        latest_jobcard_query = """
        SELECT TOP 1 jobcard FROM logs ORDER BY date DESC, time DESC
        """
        cursor.execute(latest_jobcard_query)
        latest_jobcard_row = cursor.fetchone()

        if latest_jobcard_row:
            jobcard = latest_jobcard_row[0]
            print(f"Latest jobcard fetched: {jobcard}")

            fetch_logs_query = "SELECT * FROM logs WHERE jobcard = ?"
            cursor.execute(fetch_logs_query, (jobcard,))
            logs_rows = cursor.fetchall()

            highest_temp_row = None
            highest_temp_value = float('-inf')

            for row in logs_rows:
                max_temp = max(row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13])
                if max_temp > highest_temp_value:
                    highest_temp_value = max_temp
                    highest_temp_row = row

            if highest_temp_row:
                rig_query = "SELECT rig FROM designerfile WHERE jobcard = ?"
                cursor.execute(rig_query, (jobcard,))
                rig_row = cursor.fetchone()
                sail_name = rig_row[0] if rig_row else None

                insert_query = """
                INSERT INTO process_data (TIME, DATE, JOBCARD_NUMBER, SAIL_NAME, POWER_DENSITY, POWER_SET, SPEED_SET, MACHINE_ID, TARGET_TEMP, 
                                          TEMP1A, TEMP1B, TEMP2A, TEMP2B, TEMP3A, TEMP3B, TEMP4A, TEMP4B)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(insert_query, (
                    highest_temp_row[1], highest_temp_row[2], highest_temp_row[0], sail_name,
                    highest_temp_row[3], highest_temp_row[4], highest_temp_row[5], highest_temp_row[15],
                    highest_temp_row[14], highest_temp_row[6], highest_temp_row[7], highest_temp_row[8],
                    highest_temp_row[9], highest_temp_row[10], highest_temp_row[11], highest_temp_row[12],
                    highest_temp_row[13]
                ))
                connection.commit()
                print(f"Data transferred for jobcard {jobcard} with highest temp {highest_temp_value}.")
    except pyodbc.Error as err:
        print(f"SQL Error: {err}")

def temperature_transfer_thread():
    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        transfer_highest_temperature_for_latest_jobcard(cursor, connection)
        cursor.close()
        connection.close()
    else:
        print("Could not connect to the database in temperature_transfer_thread.")

# Serve the HTML form
@app.route('/')
def index():
    return render_template('DesignerInterface2.html')  # Ensure the HTML file is named correctly

@app.route('/submit_data', methods=['POST'])
def submit_data():
    print("Submit data route accessed")  # Log for debugging
    data = request.json
    print(f"Data received: {data}")  # Log the received data
    try:
        # Connect to the database
        conn = connect_db()
        if not conn:
            return jsonify({"success": False, "message": "Could not connect to the database."})

        cursor = conn.cursor()

        # SQL Insert Query
        query = """
        INSERT INTO designerfile (
            jobcard, week, date, rig, finish_facilities, salesperson, sail_type, product_m, layout_m_mx, 
            patches_internal_external, xply_angle, transverse_angle, number_of_panel, area_m_2, dpi, 
            stringing_film, stringing_film_code, laminate_film, laminate_film_code, 
            i_pure_corner, i_pure_starfish, batten_end, jellyfish, remark, stringer_id, laminate_id, presetid
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # Execute the query
        cursor.execute(query, (
            data['jobcard'], data['week'], data['date'], data['rig'], data['finish_facilities'], data['salesperson'],
            data['sail_type'], data['product_m'], data['layout_m_mx'], data['patches_internal_external'], 
            data['xply_angle'], data['transverse_angle'], data['number_of_panel'], data['area_m_2'], 
            data['dpi'], data['stringing_film'], data['stringing_film_code'], data['laminate_film'], 
            data['laminate_film_code'], data['i_pure_corner'], data['i_pure_starfish'], data['batten_end'], 
            data['jellyfish'], data['remark'], data['stringer_id'], data['laminate_id'], data['presetid']
        ))

        # Commit the transaction
        conn.commit()

        return jsonify({"success": True, "message": "Data successfully submitted to SQL!"})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

    finally:
        if conn:
            conn.close()

@app.route('/fetch_data', methods=['GET'])
def fetch_data():
    try:
        conn = connect_db()
        if not conn:
            return jsonify({"success": False, "message": "Could not connect to the database."})

        cursor = conn.cursor()
        # Fetch data ordered by the id column in ascending order
        query = "SELECT * FROM designerfile ORDER BY id ASC"  # Adjust 'id' based on your table's primary key
        cursor.execute(query)
        rows = cursor.fetchall()

        data = []
        for row in rows:
            data.append(dict(zip([column[0] for column in cursor.description], row)))

        return jsonify({"success": True, "data": data})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

    finally:
        if conn:
            conn.close()
            
@app.route('/transfer_highest_temp', methods=['POST'])
def transfer_highest_temp():
    try:
        conn = connect_db()
        if not conn:
            return jsonify({"success": False, "message": "Could not connect to the database."})

        cursor = conn.cursor()
        transfer_highest_temperature_for_latest_jobcard(cursor, conn)
        return jsonify({"success": True, "message": "Highest temperature transferred successfully."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        if conn:
            conn.close()

# Start the update process in a background thread
update_thread = threading.Thread(target=update_designerfile, daemon=True)
update_thread.start()

# Start the temperature transfer process in a separate background thread
temperature_thread = threading.Thread(target=temperature_transfer_thread, daemon=True)
temperature_thread.start()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='192.168.42.48', port=5500)
