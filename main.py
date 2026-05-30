import tkinter as tk
from tkinter import messagebox
import mysql.connector
from db_config import DB_CONFIG
from admin import open_admin_window
from doctor import open_doctor_window
from patient import open_patient_window


def login():
    username = entry_username.get()
    password = entry_password.get()

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, person_id FROM user WHERE username = %s AND password = %s",
            (username, password)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            role = result[0]
            person_id = result[1]
            root.destroy()

            if role == "admin":
                open_admin_window()
            elif role == "doctor":
                open_doctor_window(person_id)
            else:
                open_patient_window(person_id)
        else:
            messagebox.showerror("错误", "用户名或密码错误")
    except mysql.connector.Error as e:
        messagebox.showerror("数据库错误", str(e))


# 主窗口
root = tk.Tk()
root.title("医院管理系统 - 登录")
root.geometry("300x200")

tk.Label(root, text="用户名").pack(pady=5)
entry_username = tk.Entry(root)
entry_username.pack()

tk.Label(root, text="密码").pack(pady=5)
entry_password = tk.Entry(root, show="*")
entry_password.pack()

tk.Button(root, text="登录", command=login).pack(pady=20)

root.mainloop()