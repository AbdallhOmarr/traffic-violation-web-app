import pandas as pd
import sqlite3


sqlite_database = 'db.sqlite3'
try:
    connection = sqlite3.connect(sqlite_database)
    if connection:
        print("Connected to SQLite database")

except sqlite3.Error as err:
    print(f"Error: {err}")

finally:
    # Close the connection when done
    if 'connection' in locals() and connection:
        connection.close()
        print("Connection closed")



df = pd.read_excel(r"Strcuctre sheet.xlsx")

df.rename(
    columns={
        "PTC ID":"ptc_id",
        "NAME":"employee_name",
        "ID NUMBER":"ID_number"
    },inplace=True
)


try:
    connection = sqlite3.connect(sqlite_database)

    if connection:
        print("Connected to SQLite database")
        cursor = connection.cursor()

        for i, row in df.iterrows():
            query = f"""
                INSERT INTO website_employee (ptc_id, employee_name, ID_number)
                VALUES (?, ?, ?);
            """
            cursor.execute(query, (row['ptc_id'], row['employee_name'], row['ID_number']))

        connection.commit()

except sqlite3.Error as err:
    print(f"Error: {err}")

finally:
    # Close the connection when done
    if 'connection' in locals() and connection:
        connection.close()
        print("Connection closed")



df = pd.read_excel(r"vehicle_data.xlsx",sheet_name="Sheet2")
df.head()



# Establish a connection

# Establish a connection
try:
    connection = sqlite3.connect(sqlite_database)

    if connection:
        print("Connected to SQLite database")
        cursor = connection.cursor()

        table_name = "website_vehicle"

        for i, row in df.iterrows():
            query = f"""
                INSERT INTO website_vehicle (fleet_no, vehicle_user, plate_eng, plate_ar, vehicle_type)
                VALUES ('{row['fleet_no']}', '{row['vehicle_user']}', '{row['plate_eng']}', '{row['plate_ar']}', 'Bus');
            """
            cursor.execute(query)

        connection.commit()

        print("Vehicle data successfully updated")

except Exception as err:
    print(f"Error: {err}")

finally:
    # Close the connection when done
    connection.close()
    print("Connection closed")
