import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from db_config import DB_CONFIG
from utils import get_doctor_name


def open_doctor_window(doctor_id):
    doctor_name = get_doctor_name(doctor_id)

    win = tk.Toplevel()
    win.title("医生界面")
    win.geometry("600x550")
    tk.Label(win, text=f"医生：{doctor_name}", font=("Arial", 16)).pack(pady=10)

    # 门诊功能
    tk.Label(win, text="门诊功能", font=("Arial", 12, "bold")).pack(pady=5)
    tk.Button(win, text="查看排班", command=lambda: view_schedule(doctor_id), width=20).pack(pady=2)
    tk.Button(win, text="接诊病人", command=lambda: treat_patient(doctor_id, doctor_name), width=20).pack(pady=2)
    tk.Button(win, text="查看历史处方", command=lambda: view_history(doctor_id), width=20).pack(pady=2)

    # 住院功能
    tk.Label(win, text="住院功能", font=("Arial", 12, "bold")).pack(pady=5)
    tk.Button(win, text="办理住院", command=lambda: admit_patient(doctor_id), width=20).pack(pady=2)
    tk.Button(win, text="每日诊疗", command=lambda: daily_treatment(doctor_id), width=20).pack(pady=2)

    tk.Button(win, text="退出", command=win.destroy, width=20).pack(pady=20)


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


# ==================== 查看排班 ====================

def view_schedule(doctor_id):
    win = tk.Toplevel()
    win.title("我的排班")
    win.geometry("600x300")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, dept_id FROM doctor WHERE doctor_id = %s", (doctor_id,))
    doctor = cursor.fetchone()
    cursor.close()
    conn.close()

    tk.Label(win, text=f"医生：{doctor[0]}", font=("Arial", 12)).pack(pady=5)

    columns = ("日期", "时间段", "科室", "状态")
    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.heading("日期", text="日期")
    tree.heading("时间段", text="时间段")
    tree.heading("科室", text="科室")
    tree.heading("状态", text="状态")
    tree.column("日期", width=150)
    tree.column("时间段", width=150)
    tree.column("科室", width=150)
    tree.column("状态", width=100)
    tree.pack(pady=10, fill="both", expand=True)

    from datetime import datetime, timedelta
    today = datetime.now().date()
    schedule_data = [
        (today.strftime("%Y-%m-%d"), "09:00-12:00", "门诊", "正常"),
        (today.strftime("%Y-%m-%d"), "14:00-17:00", "门诊", "正常"),
        ((today + timedelta(days=1)).strftime("%Y-%m-%d"), "09:00-12:00", "门诊", "正常"),
        ((today + timedelta(days=2)).strftime("%Y-%m-%d"), "14:00-17:00", "门诊", "正常"),
    ]
    for row in schedule_data:
        tree.insert("", tk.END, values=row)

    tk.Button(win, text="关闭", command=win.destroy).pack(pady=10)


# ==================== 接诊病人 ====================

def treat_patient(doctor_id, doctor_name):
    win = tk.Toplevel()
    win.title("接诊病人")
    win.geometry("800x600")

    # 左侧：待就诊列表
    frame_left = tk.LabelFrame(win, text="待就诊病人", padx=10, pady=10)
    frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    columns = ("reg_id", "patient_name", "reg_time")
    tree = ttk.Treeview(frame_left, columns=columns, show="headings")
    tree.heading("reg_id", text="挂号单号")
    tree.heading("patient_name", text="病人姓名")
    tree.heading("reg_time", text="挂号时间")
    tree.column("reg_id", width=80)
    tree.column("patient_name", width=100)
    tree.column("reg_time", width=150)
    tree.pack(fill=tk.BOTH, expand=True)

    # 右侧：接诊区域
    frame_right = tk.LabelFrame(win, text="开处方", padx=10, pady=10)
    frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # 当前选中的病人信息
    current_reg_id = None
    current_patient_id = None
    current_patient_name = tk.StringVar()

    tk.Label(frame_right, text="当前病人：").grid(row=0, column=0, sticky="e", pady=5)
    tk.Label(frame_right, textvariable=current_patient_name, fg="blue", font=("Arial", 12, "bold")).grid(row=0,
                                                                                                         column=1,
                                                                                                         sticky="w",
                                                                                                         pady=5)

    tk.Label(frame_right, text="症状描述：").grid(row=1, column=0, sticky="ne", pady=5)
    text_symptoms = tk.Text(frame_right, width=30, height=5)
    text_symptoms.grid(row=1, column=1, pady=5)

    # 药品选择区域
    tk.Label(frame_right, text="选择药品：").grid(row=2, column=0, sticky="e", pady=5)
    drug_combo = ttk.Combobox(frame_right, width=20)
    drug_combo.grid(row=2, column=1, sticky="w", pady=5)

    tk.Label(frame_right, text="数量：").grid(row=3, column=0, sticky="e", pady=5)
    spin_quantity = tk.Spinbox(frame_right, from_=1, to=100, width=10)
    spin_quantity.grid(row=3, column=1, sticky="w", pady=5)

    tk.Button(frame_right, text="添加药品", command=lambda: add_drug_to_list(), width=12).grid(row=4, column=0,
                                                                                               columnspan=2, pady=5)

    # 药品清单
    tk.Label(frame_right, text="药品清单：").grid(row=5, column=0, columnspan=2, sticky="w")

    drug_list_frame = tk.Frame(frame_right)
    drug_list_frame.grid(row=6, column=0, columnspan=2, pady=5)

    drug_columns = ("name", "quantity", "price", "subtotal")
    drug_tree = ttk.Treeview(drug_list_frame, columns=drug_columns, show="headings", height=6)
    drug_tree.heading("name", text="药品")
    drug_tree.heading("quantity", text="数量")
    drug_tree.heading("price", text="单价")
    drug_tree.heading("subtotal", text="小计")
    drug_tree.column("name", width=100)
    drug_tree.column("quantity", width=50)
    drug_tree.column("price", width=60)
    drug_tree.column("subtotal", width=70)
    drug_tree.pack()

    total_var = tk.StringVar(value="总费用：0.00 元")
    tk.Label(frame_right, textvariable=total_var, fg="red", font=("Arial", 12, "bold")).grid(row=7, column=0,
                                                                                             columnspan=2, pady=5)

    # 药品数据
    drug_list = []
    drug_dict = {}

    def load_drugs():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT drug_id, name, price, stock FROM drug WHERE stock > 0")
        drugs = cursor.fetchall()
        cursor.close()
        conn.close()
        drug_names = [f"{d[1]} - ¥{d[2]}" for d in drugs]
        drug_combo['values'] = drug_names
        for d in drugs:
            drug_dict[f"{d[1]} - ¥{d[2]}"] = {"id": d[0], "price": d[2], "stock": d[3]}

    def add_drug_to_list():
        drug_selected = drug_combo.get()
        try:
            quantity = int(spin_quantity.get())
        except ValueError:
            messagebox.showwarning("警告", "数量请输入整数")
            return
        if not drug_selected or quantity <= 0:
            messagebox.showwarning("警告", "请选择药品并输入有效数量")
            return

        drug_info = drug_dict.get(drug_selected)
        if not drug_info:
            return

        for i, item in enumerate(drug_list):
            if item[1] == drug_selected:
                new_qty = item[2] + quantity
                new_subtotal = new_qty * item[4]
                drug_list[i] = (item[0], item[1], new_qty, item[4], new_subtotal)
                break
        else:
            drug_list.append(
                (drug_info["id"], drug_selected, quantity, drug_info["price"], quantity * drug_info["price"]))

        refresh_drug_list()

    def refresh_drug_list():
        for item in drug_tree.get_children():
            drug_tree.delete(item)
        total = 0
        for drug in drug_list:
            drug_tree.insert("", tk.END, values=(drug[1], drug[2], f"¥{drug[3]}", f"¥{drug[4]}"))
            total += drug[4]
        total_var.set(f"总费用：{total:.2f} 元")

    def remove_selected_drug():
        selected = drug_tree.selection()
        if selected:
            index = drug_tree.index(selected[0])
            drug_list.pop(index)
            refresh_drug_list()

    tk.Button(frame_right, text="移除选中药品", command=remove_selected_drug, width=12, bg="orange").grid(row=8,
                                                                                                          column=0,
                                                                                                          columnspan=2,
                                                                                                          pady=5)

    def get_diagnosis_fee():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM doctor WHERE doctor_id = %s", (doctor_id,))
        title = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        if "主任" in title:
            return 50
        elif "副主任" in title:
            return 40
        else:
            return 30

    def confirm_prescription():
        nonlocal current_reg_id, current_patient_id

        if current_reg_id is None:
            messagebox.showwarning("警告", "请先选择一个病人")
            return

        symptoms = text_symptoms.get("1.0", tk.END).strip()
        if not symptoms:
            messagebox.showwarning("警告", "请填写症状描述")
            return
        if not drug_list:
            messagebox.showwarning("警告", "请至少添加一种药品")
            return

        drugs_total = sum(d[4] for d in drug_list)
        diagnosis_fee = get_diagnosis_fee()
        total_fee = drugs_total + diagnosis_fee

        if messagebox.askyesno("确认",
                               f"确认开处方？\n药品费用：¥{drugs_total}\n诊疗费：¥{diagnosis_fee}\n总计：¥{total_fee}"):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO prescription (reg_id, patient_id, doctor_id, diagnosis, total_fee) VALUES (%s, %s, %s, %s, %s)",
                    (current_reg_id, current_patient_id, doctor_id, symptoms, total_fee)
                )
                pres_id = cursor.lastrowid

                for drug in drug_list:
                    cursor.execute(
                        "INSERT INTO prescription_item (pres_id, drug_id, quantity, price_at_time) VALUES (%s, %s, %s, %s)",
                        (pres_id, drug[0], drug[2], drug[3])
                    )
                    cursor.execute("UPDATE drug SET stock = stock - %s WHERE drug_id = %s", (drug[2], drug[0]))

                cursor.execute("UPDATE registration SET status = '已就诊' WHERE reg_id = %s", (current_reg_id,))

                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("成功", f"处方开具成功！总费用：¥{total_fee}")
                text_symptoms.delete("1.0", tk.END)
                drug_list.clear()
                refresh_drug_list()
                load_pending_patients()
                current_patient_name.set("")
                current_reg_id = None
                current_patient_id = None
            except mysql.connector.Error as e:
                messagebox.showerror("错误", str(e))

    tk.Button(frame_right, text="确认开处方", command=confirm_prescription, width=15, bg="green", fg="white").grid(
        row=9, column=0, columnspan=2, pady=10)

    def load_pending_patients():
        for item in tree.get_children():
            tree.delete(item)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.reg_id, p.name, r.reg_time
                FROM registration r
                JOIN patient p ON r.patient_id = p.patient_id
                WHERE r.doctor_id = %s AND r.status = '待就诊'
                ORDER BY r.reg_time
            """, (doctor_id,))
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            messagebox.showerror("错误", str(e))

    def on_patient_select(event):
        nonlocal current_reg_id, current_patient_id
        selected = tree.selection()
        if selected:
            values = tree.item(selected[0])["values"]
            current_reg_id = values[0]
            current_patient_name.set(values[1])
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT patient_id FROM registration WHERE reg_id = %s", (current_reg_id,))
            current_patient_id = cursor.fetchone()[0]
            cursor.close()
            conn.close()

    tree.bind('<<TreeviewSelect>>', on_patient_select)

    load_drugs()
    load_pending_patients()

    tk.Button(win, text="关闭", command=win.destroy).pack(side=tk.BOTTOM, pady=10)


# ==================== 查看历史处方 ====================

def view_history(doctor_id):
    win = tk.Toplevel()
    win.title("历史处方")
    win.geometry("900x500")

    columns = ("pres_id", "create_time", "patient_name", "diagnosis", "total_fee")
    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.heading("pres_id", text="处方号")
    tree.heading("create_time", text="开单时间")
    tree.heading("patient_name", text="病人")
    tree.heading("diagnosis", text="症状")
    tree.heading("total_fee", text="总费用")
    tree.column("pres_id", width=80)
    tree.column("create_time", width=150)
    tree.column("patient_name", width=100)
    tree.column("diagnosis", width=300)
    tree.column("total_fee", width=80)
    tree.pack(side=tk.LEFT, fill="both", expand=True)

    scrollbar = ttk.Scrollbar(win, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill="y")

    def refresh():
        for item in tree.get_children():
            tree.delete(item)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.pres_id, p.create_time, pat.name, p.diagnosis, p.total_fee
                FROM prescription p
                JOIN patient pat ON p.patient_id = pat.patient_id
                WHERE p.doctor_id = %s
                ORDER BY p.create_time DESC
            """, (doctor_id,))
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            messagebox.showerror("错误", str(e))

    refresh()
    tk.Button(win, text="刷新", command=refresh).pack(pady=10)
    tk.Button(win, text="关闭", command=win.destroy).pack(pady=5)


# ==================== 住院功能 ====================

def admit_patient(doctor_id):
    """办理住院（不收取预交费，预交费由病人自己缴纳）"""
    win = tk.Toplevel()
    win.title("办理住院")
    win.geometry("700x450")

    tk.Label(win, text="选择病人：").pack(pady=5)
    patient_combo = ttk.Combobox(win, width=40)
    patient_combo.pack()

    patient_dict = {}

    def load_patients():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT p.patient_id, p.name, p.phone
            FROM prescription pr
            JOIN patient p ON pr.patient_id = p.patient_id
            WHERE pr.doctor_id = %s
            AND p.patient_id NOT IN (SELECT patient_id FROM inpatient_archive WHERE discharge_time IS NULL)
        """, (doctor_id,))
        patients = cursor.fetchall()
        cursor.close()
        conn.close()
        patient_list = [f"{p[1]} (电话:{p[2]})" for p in patients]
        patient_combo['values'] = patient_list
        for p in patients:
            patient_dict[f"{p[1]} (电话:{p[2]})"] = p[0]

    load_patients()

    tk.Label(win, text="选择病房：").pack(pady=5)
    ward_combo = ttk.Combobox(win, width=40)
    ward_combo.pack()

    ward_dict = {}

    def load_wards():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT w.ward_id, w.number, w.location, w.daily_fee, d.name
            FROM ward w
            JOIN department d ON w.dept_id = d.dept_id
        """)
        wards = cursor.fetchall()
        cursor.close()
        conn.close()
        ward_list = [f"{w[1]} - {w[4]} - {w[2]} (¥{w[3]}/天)" for w in wards]
        ward_combo['values'] = ward_list
        for w in wards:
            ward_dict[f"{w[1]} - {w[4]} - {w[2]} (¥{w[3]}/天)"] = {"ward_id": w[0], "daily_fee": w[3]}

    load_wards()

    tk.Label(win, text="选择床位：").pack(pady=5)
    bed_combo = ttk.Combobox(win, width=20)
    bed_combo.pack()

    def on_ward_select(event):
        selected = ward_combo.get()
        ward_info = ward_dict.get(selected)
        if ward_info:
            ward_id = ward_info["ward_id"]
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.bed_number
                FROM bed b
                WHERE b.ward_id = %s
                AND NOT EXISTS (
                    SELECT 1 FROM inpatient_archive ia
                    WHERE ia.ward_id = b.ward_id AND ia.bed_number = b.bed_number
                    AND ia.discharge_time IS NULL
                )
            """, (ward_id,))
            beds = cursor.fetchall()
            cursor.close()
            conn.close()
            bed_combo['values'] = [b[0] for b in beds]

    ward_combo.bind('<<ComboboxSelected>>', on_ward_select)

    tk.Label(win, text="预交费将在病人登录后自行缴纳", fg="gray").pack(pady=5)

    def do_admit():
        patient_selected = patient_combo.get()
        ward_selected = ward_combo.get()
        bed_number = bed_combo.get()

        if not patient_selected or not ward_selected or not bed_number:
            messagebox.showwarning("警告", "请填写完整信息")
            return

        patient_id = patient_dict.get(patient_selected)
        ward_info = ward_dict.get(ward_selected)

        if not patient_id or not ward_info:
            messagebox.showerror("错误", "请选择有效的数据")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO inpatient_archive (patient_id, ward_id, bed_number, admit_time, deposit)
                VALUES (%s, %s, %s, NOW(), 0)
            """, (patient_id, ward_info["ward_id"], bed_number))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("成功", "办理住院成功！\n请提醒病人登录系统缴纳预交费")
            win.destroy()
        except mysql.connector.Error as e:
            messagebox.showerror("错误", str(e))

    tk.Button(win, text="确认办理住院", command=do_admit, bg="green", fg="white").pack(pady=20)
    tk.Button(win, text="关闭", command=win.destroy).pack()


def daily_treatment(doctor_id):
    """每日诊疗"""
    win = tk.Toplevel()
    win.title("每日诊疗")
    win.geometry("800x600")

    tk.Label(win, text="选择住院病人：").pack(pady=5)
    patient_combo = ttk.Combobox(win, width=50)
    patient_combo.pack()

    patient_dict = {}
    archive_dict = {}

    def load_inpatients():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ia.archive_id, p.patient_id, p.name, p.phone, w.number, ia.admit_time
            FROM inpatient_archive ia
            JOIN patient p ON ia.patient_id = p.patient_id
            JOIN ward w ON ia.ward_id = w.ward_id
            WHERE ia.discharge_time IS NULL
            AND EXISTS (
                SELECT 1 FROM prescription pr 
                WHERE pr.patient_id = p.patient_id AND pr.doctor_id = %s
            )
        """, (doctor_id,))
        patients = cursor.fetchall()
        cursor.close()
        conn.close()
        patient_list = [f"{p[2]} (电话:{p[3]}) - 病房:{p[4]} - 入院:{p[5]}" for p in patients]
        patient_combo['values'] = patient_list
        for p in patients:
            key = f"{p[2]} (电话:{p[3]}) - 病房:{p[4]} - 入院:{p[5]}"
            patient_dict[key] = p[1]
            archive_dict[key] = p[0]

    load_inpatients()

    frame_info = tk.LabelFrame(win, text="诊疗记录", padx=10, pady=10)
    frame_info.pack(pady=10, padx=10, fill="both", expand=True)

    tk.Label(frame_info, text="症状描述：").grid(row=0, column=0, sticky="ne", pady=5)
    text_symptoms = tk.Text(frame_info, width=40, height=5)
    text_symptoms.grid(row=0, column=1, pady=5)

    tk.Label(frame_info, text="诊疗方案：").grid(row=1, column=0, sticky="ne", pady=5)
    text_treatment = tk.Text(frame_info, width=40, height=5)
    text_treatment.grid(row=1, column=1, pady=5)

    tk.Label(frame_info, text="添加药品（可选）：").grid(row=2, column=0, sticky="e", pady=5)
    drug_combo = ttk.Combobox(frame_info, width=25)
    drug_combo.grid(row=2, column=1, sticky="w", pady=5)

    tk.Label(frame_info, text="数量：").grid(row=3, column=0, sticky="e", pady=5)
    spin_quantity = tk.Spinbox(frame_info, from_=1, to=100, width=10)
    spin_quantity.grid(row=3, column=1, sticky="w", pady=5)

    drug_list = []
    drug_dict = {}

    def load_drugs():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT drug_id, name, price FROM drug WHERE stock > 0")
        drugs = cursor.fetchall()
        cursor.close()
        conn.close()
        drug_names = [f"{d[1]} - ¥{d[2]}" for d in drugs]
        drug_combo['values'] = drug_names
        for d in drugs:
            drug_dict[f"{d[1]} - ¥{d[2]}"] = {"id": d[0], "price": d[2]}

    load_drugs()

    drug_tree_frame = tk.LabelFrame(frame_info, text="药品清单")
    drug_tree_frame.grid(row=4, column=0, columnspan=2, pady=10)

    drug_columns = ("name", "quantity", "price", "subtotal")
    drug_tree = ttk.Treeview(drug_tree_frame, columns=drug_columns, show="headings", height=4)
    drug_tree.heading("name", text="药品")
    drug_tree.heading("quantity", text="数量")
    drug_tree.heading("price", text="单价")
    drug_tree.heading("subtotal", text="小计")
    drug_tree.column("name", width=150)
    drug_tree.column("quantity", width=60)
    drug_tree.column("price", width=80)
    drug_tree.column("subtotal", width=80)
    drug_tree.pack()

    med_total_var = tk.StringVar(value="药品费用：0.00 元")
    tk.Label(frame_info, textvariable=med_total_var, fg="blue").grid(row=5, column=0, columnspan=2)

    def refresh_med_list():
        for item in drug_tree.get_children():
            drug_tree.delete(item)
        total = 0
        for d in drug_list:
            drug_tree.insert("", tk.END, values=(d[1], d[2], f"¥{d[3]}", f"¥{d[4]}"))
            total += d[4]
        med_total_var.set(f"药品费用：{total:.2f} 元")
        calculate_daily_fee()

    def add_med():
        drug_selected = drug_combo.get()
        try:
            quantity = int(spin_quantity.get())
        except ValueError:
            messagebox.showwarning("警告", "请输入有效数量")
            return
        if not drug_selected or quantity <= 0:
            messagebox.showwarning("警告", "请选择药品并输入数量")
            return
        drug_info = drug_dict.get(drug_selected)
        if not drug_info:
            return
        # 检查是否已存在
        for i, item in enumerate(drug_list):
            if item[1] == drug_selected:
                new_qty = item[2] + quantity
                new_subtotal = new_qty * item[4]
                drug_list[i] = (item[0], item[1], new_qty, item[4], new_subtotal)
                break
        else:
            drug_list.append(
                (drug_info["id"], drug_selected, quantity, drug_info["price"], quantity * drug_info["price"]))
        refresh_med_list()

    def remove_med():
        selected = drug_tree.selection()
        if selected:
            idx = drug_tree.index(selected[0])
            drug_list.pop(idx)
            refresh_med_list()

    tk.Button(frame_info, text="添加药品", command=add_med, width=12).grid(row=2, column=2, padx=5)
    tk.Button(frame_info, text="移除药品", command=remove_med, width=12).grid(row=3, column=2, padx=5)

    daily_fee_var = tk.StringVar(value="当日总费用：0.00 元（床位费 + 药品费）")
    tk.Label(frame_info, textvariable=daily_fee_var, fg="red", font=("Arial", 12, "bold")).grid(row=6, column=0,
                                                                                                columnspan=3, pady=10)

    def calculate_daily_fee():
        selected = patient_combo.get()
        if not selected:
            return 0
        archive_id = archive_dict.get(selected)
        if not archive_id:
            return 0
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT w.daily_fee
            FROM inpatient_archive ia
            JOIN ward w ON ia.ward_id = w.ward_id
            WHERE ia.archive_id = %s
        """, (archive_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        bed_fee = result[0] if result else 0
        med_fee = sum(d[4] for d in drug_list)
        total = bed_fee + med_fee
        daily_fee_var.set(f"当日总费用：{total:.2f} 元（床位费 ¥{bed_fee} + 药品费 ¥{med_fee}）")
        return total

    def on_patient_select(event):
        calculate_daily_fee()

    patient_combo.bind('<<ComboboxSelected>>', on_patient_select)

    def save_record():
        selected = patient_combo.get()
        if not selected:
            messagebox.showwarning("警告", "请选择病人")
            return
        symptoms = text_symptoms.get("1.0", tk.END).strip()
        treatment = text_treatment.get("1.0", tk.END).strip()
        if not symptoms or not treatment:
            messagebox.showwarning("警告", "请填写症状和诊疗方案")
            return

        archive_id = archive_dict.get(selected)
        if not archive_id:
            messagebox.showerror("错误", "未找到住院档案")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT w.daily_fee
            FROM inpatient_archive ia
            JOIN ward w ON ia.ward_id = w.ward_id
            WHERE ia.archive_id = %s
        """, (archive_id,))
        bed_fee = cursor.fetchone()[0]
        med_fee = sum(d[4] for d in drug_list)
        daily_cost = bed_fee + med_fee

        try:
            cursor.execute("""
                INSERT INTO inpatient_record (archive_id, record_date, symptoms, treatment, daily_cost)
                VALUES (%s, CURDATE(), %s, %s, %s)
            """, (archive_id, symptoms, treatment, daily_cost))

            for drug in drug_list:
                cursor.execute("UPDATE drug SET stock = stock - %s WHERE drug_id = %s", (drug[2], drug[0]))

            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("成功", f"诊疗记录已保存\n当日费用：¥{daily_cost}")

            text_symptoms.delete("1.0", tk.END)
            text_treatment.delete("1.0", tk.END)
            drug_list.clear()
            refresh_med_list()
        except mysql.connector.Error as e:
            messagebox.showerror("错误", str(e))

    tk.Button(win, text="保存诊疗记录", command=save_record, bg="green", fg="white", width=20).pack(pady=10)
    tk.Button(win, text="关闭", command=win.destroy).pack(pady=5)