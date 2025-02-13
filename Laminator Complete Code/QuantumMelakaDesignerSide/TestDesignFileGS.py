import pyodbc
import time

# SQL connection details
server = 'localhost'
database = 'laminatordatabase'
connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"

# Table names
READ_TABLE_NAME = "preset_list"
UPDATE_TABLE_NAME = "designerfile"

def update_row(cursor, connection, designerfile_row, preset_row):
    """Update the designerfile row with data from the preset_list."""
    try:
        update_query = f"""
            UPDATE {UPDATE_TABLE_NAME}
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
        # Validate rig
        rig = designerfile_row[3] if designerfile_row[3] in ['MOTH', 'MELGES 32', 'LUETJE 47', 'TP52'] else None
        
        # Validate sail_type
        sail_type = designerfile_row[6] if designerfile_row[6] in ['MAINSAIL', 'LGT MAINSAIL'] else None
        
        # Validate product_m
        product_m = designerfile_row[7] if designerfile_row[7] in ['M9', 'M7'] else None
        
        query = f"""
            SELECT * FROM {READ_TABLE_NAME}
            WHERE (Rig = ? OR Rig IS NULL) AND (Sail_Type = ? OR Sail_Type IS NULL) AND 
                  (Product = ? OR Product IS NULL) AND Film_Laminate = ? AND
                  Laminator_Yellow_Blue = ? AND DPI_At_1_2_Leech_MIN <= ? AND DPI_At_1_2_Leech_MAX >= ?
        """
        
        print(f"Searching for matching preset for jobcard {designerfile_row[0]}...")
        print(f"Search criteria: Rig: {rig}, Sail_Type: {sail_type}, Product: {product_m}, Film_Laminate: {designerfile_row[17]}, Laminator: {designerfile_row[25]}, DPI: {designerfile_row[14]}")
        
        cursor.execute(query, (
            rig,  # rig
            sail_type,  # sail_type
            product_m,  # product_m
            designerfile_row[17],  # laminate_film
            designerfile_row[25],  # Laminator_Yellow_Blue
            designerfile_row[14],  # dpi (min)
            designerfile_row[14]   # dpi (max)
        ))
        
        preset_row = cursor.fetchone()
        if preset_row:
            print(f"Matching preset found for jobcard {designerfile_row[0]}.")
        else:
            print(f"No matching preset found for jobcard {designerfile_row[0]}.")
        
        return preset_row
    except pyodbc.Error as err:
        print(f"SQL Error during preset search: {err}")
        return None

def main():
    # Connect to the database
    try:
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
    except pyodbc.Error as err:
        print(f"SQL Connection Error: {err}")
        return

    while True:
        try:
            ## Fetch the last 20 rows from designerfile
            #print(f"Fetching the last 20 rows from {UPDATE_TABLE_NAME}...")
            #cursor.execute(f"""
            #    SELECT TOP 20 * 
            #    FROM {UPDATE_TABLE_NAME} 
            #    ORDER BY jobcard DESC  -- Replace with an appropriate column for ordering if needed
            #""")
            # Fetch all rows from designerfile
            print(f"Fetching all rows from {UPDATE_TABLE_NAME}...")
            cursor.execute(f"""
                SELECT * 
                FROM {UPDATE_TABLE_NAME}
            """)
            designerfile_values = cursor.fetchall()
            print(f"Fetched {len(designerfile_values)} rows from {UPDATE_TABLE_NAME}.")

            # Process each row from designerfile
            for designerfile_row in designerfile_values:
                if len(designerfile_row) >= 25:
                    print(f"Processing jobcard {designerfile_row[0]}...")
                    # Find the corresponding row in preset_list
                    preset_row = find_matching_preset(cursor, designerfile_row)

                    if preset_row:
                        # Update designerfile if the preset matches
                        update_row(cursor, connection, designerfile_row, preset_row)
                    else:
                        print(f"No update performed for jobcard {designerfile_row[0]}.")
                else:
                    print(f"Skipping invalid designerfile row: {designerfile_row[0]} (insufficient data).")

            time.sleep(5)

        except pyodbc.Error as err:
            print(f"SQL Error during main loop: {err}")

if __name__ == "__main__":
    main()