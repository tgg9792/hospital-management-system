import mysql.connector
from db_config import DB_CONFIG

def get_doctor_name(doctor_id):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM doctor WHERE doctor_id = %s", (doctor_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else f"医生{doctor_id}"
    except:
        return f"医生{doctor_id}"

def get_patient_name(patient_id):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM patient WHERE patient_id = %s", (patient_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else f"病人{patient_id}"
    except:
        return f"病人{patient_id}"