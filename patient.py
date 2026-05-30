import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from db_config import DB_CONFIG
from utils import get_patient_name


def open_patient_window(patient_id):
    patient_name = get_patient_name(patient_id)

    win = tk.Toplevel()
    win.title("病人界面")
    win.geometry("650x600")
    tk.Label(win, text=f"病人：{patient_name}", font=("Arial", 16)).pack(pady=10)

    # 门诊功能
    tk.Label(win, text="门诊功能", font=("Arial", 12, "bold")).pack(pady=5)
    tk.Button(win, text="挂号", command=lambda: registration(patient_id, patient_name), width=20).pack(pady=2)
    tk.Button(win, text="缴费", command=lambda: payment(patient_id), width=20).pack(pady=2)
    tk.Button(win, text="查询就诊记录", command=lambda: view_visits(patient_id), width=20).pack(pady=2)
    tk.Button(win, text="查询费用明细", command=lambda: view_prescription_detail(patient_id), width=20).pack(pady=2)

    # 住院功能
    tk.Label(win, text="住院功能", font=("Arial", 12, "bold")).pack(pady=5)
    tk.Button(win, text="缴纳预交费", command=lambda: pay_deposit(patient_id), width=20).pack(pady=2)
    tk.Button(win, text="查询住院档案", command=lambda: view_inpatient_archive(patient_id), width=20).pack(pady=2)
    tk.Button(win, text="查询住院记录", command=lambda: view_inpatient_records(patient_id), width=20).pack(pady=2)

    tk.Button(win, text="退出", command=win.destroy, width=20).pack(pady=20)


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


# ==================== 挂号 ====================

def registration(patient_id, patient_name):
    win = tk.Toplevel()
    win.title("挂号")
    win.geometry("500x400")

    tk.Label(win, text=f"病人：{patient_name}", font=("Arial", 12)).pack(pady=5)

    tk.Label(win, text="选择科室：").pack(pady=5)
    dept_combo = ttk.Combobox(win, width=30)
    dept_combo.pack()

    tk.Label(win, text="选择医生：").pack(pady=5)
    doctor_combo = ttk.Combobox(win, width=30)
    doctor_combo.pack()

    def load_depts():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT dept_id, name FROM department")
        depts = cursor.fetchall()
        cursor.close()
        conn.close()
        dept_dict = {name: dept_id for dept_id, name in depts}
        dept_combo['values'] = list(dept_dict.keys())
        return dept_dict

    dept_dict = load_depts()

    def on_dept_select(event):
        dept_name = dept_combo.get()
        dept_id = dept_dict.get(dept_name)
        if dept_id:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT doctor_id, name, title FROM doctor WHERE dept_id = %s", (dept_id,))
            doctors = cursor.fetchall()
            cursor.close()
            conn.close()
            doctor_combo['values'] = [f"{d[1]} ({d[2]})" for d in doctors]
            doctor_combo.doctor_ids = {f"{d[1]} ({d[2]})": d[0] for d in doctors}

    dept_combo.bind('<<ComboboxSelected>>', on_dept_select)

    tk.Label(win, text="挂号时间：").pack(pady=5)
    from datetime import datetime
    time_label = tk.Label(win, text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    time_label.pack()

    def do_registration():
        dept_name = dept_combo.get()
        doctor_display = doctor_combo.get()

        if not dept_name or not doctor_display:
            messagebox.showwarning("警告", "请选择科室和医生")
            return

        doctor_id = doctor_combo.doctor_ids.get(doctor_display)

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO registration (patient_id, doctor_id, reg_time, status) VALUES (%s, %s, NOW(), '待就诊')",
                (patient_id, doctor_id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("成功", "挂号成功！请按时就诊")
            win.destroy()
        except mysql.connector.Error as e:
            messagebox.showerror("错误", str(e))

    tk.Button(win, text="确认挂号", command=do_registration, bg="green", fg="white").pack(pady=20)


# ==================== 缴费 ====================

def payment(patient_id):
    win = tk.Toplevel()
    win.title("缴费")
    win.geometry("700x400")

    columns = ("pres_id", "create_time", "doctor_name", "total_fee", "status")
    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.heading("pres_id", text="处方号")
    tree.heading("create_time", text="开单时间")
    tree.heading("doctor_name", text="医生")
    tree.heading("total_fee", text="总费用")
    tree.heading("status", text="状态")
    tree.column("pres_id", width=80)
    tree.column("create_time", width=150)
    tree.column("doctor_name", width=100)
    tree.column("total_fee", width=100)
    tree.column("status", width=80)
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
                SELECT p.pres_id, p.create_time, d.name, p.total_fee, 
                       CASE WHEN pay.pay_id IS NULL THEN '未缴费' ELSE '已缴费' END as status
                FROM prescription p
                JOIN doctor d ON p.doctor_id = d.doctor_id
                LEFT JOIN payment pay ON p.pres_id = pay.pres_id
                WHERE p.patient_id = %s
                ORDER BY p.create_time DESC
            """, (patient_id,))
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            messagebox.showerror("错误", str(e))

    def pay_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要缴费的处方")
            return
        values = tree.item(selected[0])["values"]
        pres_id = values[0]
        total_fee = values[3]
        status = values[4]

        if status == "已缴费":
            messagebox.showinfo("提示", "该处方已经缴费过了")
            return

        if messagebox.askyesno("确认", f"确认支付 ¥{total_fee} 吗？"):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO payment (pres_id, amount, pay_time, pay_status) VALUES (%s, %s, NOW(), '已支付')",
                    (pres_id, total_fee)
                )
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("成功", f"缴费成功！金额：¥{total_fee}")
                refresh()
            except mysql.connector.Error as e:
                messagebox.showerror("错误", str(e))

    frame_buttons = tk.Frame(win)
    frame_buttons.pack(pady=10)
    tk.Button(frame_buttons, text="刷新", command=refresh, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_buttons, text="缴费", command=pay_selected, width=10, bg="green", fg="white").pack(side=tk.LEFT,
                                                                                                       padx=5)
    tk.Button(frame_buttons, text="关闭", command=win.destroy, width=10).pack(side=tk.LEFT, padx=5)

    refresh()


# ==================== 查询就诊记录 ====================

def view_visits(patient_id):
    win = tk.Toplevel()
    win.title("就诊记录")
    win.geometry("800x400")

    columns = ("reg_id", "reg_time", "doctor_name", "dept_name", "status", "pres_id", "total_fee")
    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.heading("reg_id", text="挂号单号")
    tree.heading("reg_time", text="挂号时间")
    tree.heading("doctor_name", text="医生")
    tree.heading("dept_name", text="科室")
    tree.heading("status", text="状态")
    tree.heading("pres_id", text="处方号")
    tree.heading("total_fee", text="总费用")
    tree.column("reg_id", width=80)
    tree.column("reg_time", width=150)
    tree.column("doctor_name", width=100)
    tree.column("dept_name", width=100)
    tree.column("status", width=80)
    tree.column("pres_id", width=80)
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
                SELECT r.reg_id, r.reg_time, doc.name, dept.name, r.status,
                       p.pres_id, p.total_fee
                FROM registration r
                JOIN doctor doc ON r.doctor_id = doc.doctor_id
                JOIN department dept ON doc.dept_id = dept.dept_id
                LEFT JOIN prescription p ON r.reg_id = p.reg_id
                WHERE r.patient_id = %s
                ORDER BY r.reg_time DESC
            """, (patient_id,))
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            messagebox.showerror("错误", str(e))

    refresh()
    tk.Button(win, text="刷新", command=refresh).pack(pady=10)


# ==================== 查询费用明细 ====================

def view_prescription_detail(patient_id):
    win = tk.Toplevel()
    win.title("费用明细")
    win.geometry("800x500")

    tk.Label(win, text="选择处方：").pack(pady=5)
    pres_combo = ttk.Combobox(win, width=50)
    pres_combo.pack()

    columns = ("drug_name", "quantity", "price", "subtotal")
    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.heading("drug_name", text="药品名称")
    tree.heading("quantity", text="数量")
    tree.heading("price", text="单价")
    tree.heading("subtotal", text="小计")
    tree.column("drug_name", width=200)
    tree.column("quantity", width=80)
    tree.column("price", width=100)
    tree.column("subtotal", width=100)
    tree.pack(pady=10, fill="both", expand=True)

    total_label = tk.Label(win, text="总计：0.00 元", font=("Arial", 12, "bold"))
    total_label.pack(pady=5)

    def load_prescriptions():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.pres_id, p.create_time, d.name, p.total_fee
            FROM prescription p
            JOIN doctor d ON p.doctor_id = d.doctor_id
            WHERE p.patient_id = %s
            ORDER BY p.create_time DESC
        """, (patient_id,))
        pres = cursor.fetchall()
        cursor.close()
        conn.close()
        pres_list = [f"{p[0]} - {p[1]} - 医生:{p[2]} - ¥{p[3]}" for p in pres]
        pres_combo['values'] = pres_list
        return {pres_list[i]: p[0] for i, p in enumerate(pres)}

    pres_dict = load_prescriptions()

    def on_pres_select(event):
        selected = pres_combo.get()
        pres_id = pres_dict.get(selected)
        if not pres_id:
            return

        for item in tree.get_children():
            tree.delete(item)

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.name, pi.quantity, pi.price_at_time, 
                       pi.quantity * pi.price_at_time as subtotal
                FROM prescription_item pi
                JOIN drug d ON pi.drug_id = d.drug_id
                WHERE pi.pres_id = %s
            """, (pres_id,))
            total = 0
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
                total += row[3]
            cursor.close()
            conn.close()
            total_label.config(text=f"总计：{total:.2f} 元")
        except mysql.connector.Error as e:
            messagebox.showerror("错误", str(e))

    pres_combo.bind('<<ComboboxSelected>>', on_pres_select)
    tk.Button(win, text="关闭", command=win.destroy).pack(pady=10)


# ==================== 缴纳预交费 ====================

def pay_deposit(patient_id):
    """缴纳住院预交费"""
    win = tk.Toplevel()
    win.title("缴纳预交费")
    win.geometry("600x400")

    # 查询当前住院中且 deposit=0 的住院档案
    tk.Label(win, text="选择住院档案：").pack(pady=5)
    archive_combo = ttk.Combobox(win, width=60)
    archive_combo.pack()

    archive_dict = {}

    def load_archives():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ia.archive_id, ia.admit_time, w.number, ia.bed_number, ia.deposit
            FROM inpatient_archive ia
            JOIN ward w ON ia.ward_id = w.ward_id
            WHERE ia.patient_id = %s AND ia.discharge_time IS NULL
        """, (patient_id,))
        archives = cursor.fetchall()
        cursor.close()
        conn.close()
        if not archives:
            archive_combo['values'] = ["暂无需要缴费的住院档案"]
        else:
            archive_list = [f"{a[0]} - 入院:{a[1]} - 病房:{a[2]} - 床位:{a[3]} - 当前预交:¥{a[4]}" for a in archives]
            archive_combo['values'] = archive_list
            for a in archives:
                archive_dict[f"{a[0]} - 入院:{a[1]} - 病房:{a[2]} - 床位:{a[3]} - 当前预交:¥{a[4]}"] = a[0]

    load_archives()

    tk.Label(win, text="缴纳金额：").pack(pady=5)
    entry_amount = tk.Entry(win, width=20)
    entry_amount.pack()

    def do_pay():
        selected = archive_combo.get()
        if not selected or selected == "暂无需要缴费的住院档案":
            messagebox.showwarning("警告", "请选择有效的住院档案")
            return
        try:
            amount = float(entry_amount.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("警告", "请输入有效的金额（大于0）")
            return

        archive_id = archive_dict.get(selected)
        if not archive_id:
            messagebox.showerror("错误", "未找到住院档案")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE inpatient_archive SET deposit = deposit + %s WHERE archive_id = %s
            """, (amount, archive_id))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("成功", f"预交费缴纳成功！¥{amount}")
            win.destroy()
        except mysql.connector.Error as e:
            messagebox.showerror("错误", str(e))

    tk.Button(win, text="确认缴纳", command=do_pay, bg="green", fg="white").pack(pady=20)
    tk.Button(win, text="关闭", command=win.destroy).pack()


# ==================== 住院查询功能 ====================

def view_inpatient_archive(patient_id):
    """查询住院档案"""
    win = tk.Toplevel()
    win.title("住院档案")
    win.geometry("800x300")

    columns = ("archive_id", "admit_time", "discharge_time", "ward", "bed", "deposit")
    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.heading("archive_id", text="档案号")
    tree.heading("admit_time", text="入院时间")
    tree.heading("discharge_time", text="出院时间")
    tree.heading("ward", text="病房")
    tree.heading("bed", text="床位")
    tree.heading("deposit", text="预缴费用")
    tree.column("archive_id", width=80)
    tree.column("admit_time", width=150)
    tree.column("discharge_time", width=150)
    tree.column("ward", width=100)
    tree.column("bed", width=60)
    tree.column("deposit", width=100)
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
                SELECT ia.archive_id, ia.admit_time, ia.discharge_time,
                       w.number, ia.bed_number, ia.deposit
                FROM inpatient_archive ia
                JOIN ward w ON ia.ward_id = w.ward_id
                WHERE ia.patient_id = %s
                ORDER BY ia.admit_time DESC
            """, (patient_id,))
            for row in cursor.fetchall():
                discharge = row[2] if row[2] else "住院中"
                tree.insert("", tk.END, values=(row[0], row[1], discharge, row[3], row[4], f"¥{row[5]}"))
            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            messagebox.showerror("错误", str(e))

    refresh()
    tk.Button(win, text="刷新", command=refresh).pack(pady=10)
    tk.Button(win, text="关闭", command=win.destroy).pack(pady=5)


def view_inpatient_records(patient_id):
    """查询住院记录（每日诊疗）"""
    win = tk.Toplevel()
    win.title("住院记录")
    win.geometry("900x500")

    tk.Label(win, text="选择住院档案：").pack(pady=5)
    archive_combo = ttk.Combobox(win, width=60)
    archive_combo.pack()

    archive_dict = {}

    def load_archives():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ia.archive_id, ia.admit_time, w.number, ia.bed_number
            FROM inpatient_archive ia
            JOIN ward w ON ia.ward_id = w.ward_id
            WHERE ia.patient_id = %s
            ORDER BY ia.admit_time DESC
        """, (patient_id,))
        archives = cursor.fetchall()
        cursor.close()
        conn.close()
        archive_list = [f"{a[0]} - 入院:{a[1]} - 病房:{a[2]} - 床位:{a[3]}" for a in archives]
        archive_combo['values'] = archive_list
        for a in archives:
            archive_dict[f"{a[0]} - 入院:{a[1]} - 病房:{a[2]} - 床位:{a[3]}"] = a[0]

    load_archives()

    columns = ("record_date", "symptoms", "treatment", "daily_cost")
    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.heading("record_date", text="日期")
    tree.heading("symptoms", text="症状")
    tree.heading("treatment", text="诊疗方案")
    tree.heading("daily_cost", text="当日费用")
    tree.column("record_date", width=120)
    tree.column("symptoms", width=250)
    tree.column("treatment", width=250)
    tree.column("daily_cost", width=100)
    tree.pack(pady=10, fill="both", expand=True)

    scrollbar = ttk.Scrollbar(win, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill="y")

    def on_archive_select(event):
        for item in tree.get_children():
            tree.delete(item)
        selected = archive_combo.get()
        archive_id = archive_dict.get(selected)
        if not archive_id:
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT record_date, symptoms, treatment, daily_cost
                FROM inpatient_record
                WHERE archive_id = %s
                ORDER BY record_date
            """, (archive_id,))
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            messagebox.showerror("错误", str(e))

    archive_combo.bind('<<ComboboxSelected>>', on_archive_select)
    tk.Button(win, text="关闭", command=win.destroy).pack(pady=10)