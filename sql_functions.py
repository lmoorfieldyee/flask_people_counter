import mysql.connector
import config

def insert_all_pedestrian_detections_row(data_to_save):
    db_config = {
        'host': str(config.host_name),
        'user': str(config.user_name),
        'password': str(config.password),
        'database': str(config.database),
    }
    try:
        # Establish a connection to the database
        connection = mysql.connector.connect(**db_config)

        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # SQL query to insert data into a table
        table_to_update = config.table_name # set table name in config settings
        insert_query = "INSERT INTO all_pedestrian_detections (pedestrian_uuid, bbox_top_left_x, bbox_top_left_y, " \
                       "bbox_bottom_right_x, bbox_bottom_right_y, time_of_detection) " \
                       "VALUES (%s, %s, %s, %s, %s, %s)"

        cursor.execute(insert_query, data_to_save)

        # Commit the changes to the database
        connection.commit()

        print("Data inserted successfully!")

    except mysql.connector.Error as error:
        print(f"Error: {error}")

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def insert_pedestrian_summary_row(data_to_save):
    # print(data_to_save)
    db_config = {
        'host': str(config.host_name),
        'user': str(config.user_name),
        'password': str(config.password),
        'database': str(config.database),
    }
    try:
        # Establish a connection to the database
        connection = mysql.connector.connect(**db_config)

        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # SQL query to insert data into a table
        table_to_update = config.table_name # set table name in config settings
        insert_query = "INSERT INTO pedestrian_summary_stats (pedestrian_uuid, first_bbox_cords, last_bbox_cords, " \
                       "first_detection_time, last_detection_time, elapsed_time, store_id, classification, campaign) " \
                       "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        # insert row into table
        cursor.execute(insert_query, data_to_save)

        # Commit the changes to the database
        connection.commit()

        print("Data inserted successfully!")

    except mysql.connector.Error as error:
        print(f"Error: {error}")

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()