import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from db_config import DB_CONFIG


#管理科室按键

def manage_departments():
    """管理科室窗口"""
    win = tk.Toplevel()
    win.title("管理科室")
    win.geometry("600x500")

    # 添加科室区域
    frame_add = tk.LabelFrame(win, text="添加科室", padx=10, pady=10)
    frame_add.pack(pady=10, padx=10, fill="x")

    tk.Label(frame_add, text="科室名称:").grid(row=0, column=0, padx=5, pady=5)
    entry_name = tk.Entry(frame_add, width=20)
    entry_name.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_add, text="位置:").grid(row=0, column=2, padx=5, pady=5)
    entry_location = tk.Entry(frame_add, width=20)
    entry_location.grid(row=0, column=3, padx=5, pady=5)

    def add_department():
        name = entry_name.get().strip()
        location = entry_location.get().strip()
        if not name or not location:
            messagebox.showwarning("警告", "请填写完整信息")
            return
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO department (name, location) VALUES (%s, %s)", (name, location))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("成功", "科室添加成功")
            entry_name.delete(0, tk.END)
            entry_location.delete(0, tk.END)
            refresh_tree()
        except mysql.connector.Error as e:
            if "Duplicate" in str(e):
                messagebox.showerror("错误", "科室名称已存在")
            else:
                messagebox.showerror("错误", str(e))

    tk.Button(frame_add, text="添加", command=add_department, bg="green", fg="white").grid(row=1, column=0,
                                                                                           columnspan=4, pady=10)

    # 科室列表区域
    frame_list = tk.LabelFrame(win, text="科室列表", padx=10, pady=10)
    frame_list.pack(pady=10, padx=10, fill="both", expand=True)

    columns = ("dept_id", "name", "location")
    tree = ttk.Treeview(frame_list, columns=columns, show="headings")
    tree.heading("dept_id", text="编号")
    tree.heading("name", text="科室名称")
    tree.heading("location", text="位置")
    tree.column("dept_id", width=50)
    tree.column("name", width=150)
    tree.column("location", width=150)
    tree.pack(side=tk.LEFT, fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame_list, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill="y")

    def refresh_tree():
        for item in tree.get_children():
            tree.delete(item)
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT dept_id, name, location FROM department")
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            messagebox.showerror("错误", str(e))

    def delete_department():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的科室")
            return
        dept_id = tree.item(selected[0])["values"][0]
        if messagebox.askyesno("确认", "确定要删除该科室吗？"):
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM department WHERE dept_id = %s", (dept_id,))
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("成功", "科室删除成功")
                refresh_tree()
            except mysql.connector.Error as e:
                messagebox.showerror("错误", f"删除失败：{e}")

    def update_department():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要修改的科室")
            return
        values = tree.item(selected[0])["values"]
        dept_id = values[0]
        old_name = values[1]
        old_location = values[2]

        update_win = tk.Toplevel(win)
        update_win.title("修改科室")
        update_win.geometry("300x200")

        tk.Label(update_win, text="科室名称:").pack(pady=5)
        entry_new_name = tk.Entry(update_win, width=20)
        entry_new_name.insert(0, old_name)
        entry_new_name.pack()

        tk.Label(update_win, text="位置:").pack(pady=5)
        entry_new_location = tk.Entry(update_win, width=20)
        entry_new_location.insert(0, old_location)
        entry_new_location.pack()

        def do_update():
            new_name = entry_new_name.get().strip()
            new_location = entry_new_location.get().strip()
            if not new_name or not new_location:
                messagebox.showwarning("警告", "请填写完整信息")
                return
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("UPDATE department SET name=%s, location=%s WHERE dept_id=%s",
                               (new_name, new_location, dept_id))
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("成功", "科室修改成功")
                update_win.destroy()
                refresh_tree()
            except mysql.connector.Error as e:
                messagebox.showerror("错误", str(e))

        tk.Button(update_win, text="保存", command=do_update, bg="blue", fg="white").pack(pady=20)

    frame_buttons = tk.Frame(win)
    frame_buttons.pack(pady=10)
    tk.Button(frame_buttons, text="修改", command=update_department, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_buttons, text="删除", command=delete_department, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_buttons, text="刷新", command=refresh_tree, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_buttons, text="关闭", command=win.destroy, width=10).pack(side=tk.LEFT, padx=5)

    refresh_tree()


#管理医生按键

def manage_doctors():
    """管理医生窗口"""
    win = tk.Toplevel()
    win.title("管理医生")
    win.geometry("750x550")

    # 添加医生区域
    frame_add = tk.LabelFrame(win, text="添加医生", padx=10, pady=10)
    frame_add.pack(pady=10, padx=10, fill="x")

    tk.Label(frame_add, text="姓名:").grid(row=0, column=0, padx=5, pady=5)
    entry_name = tk.Entry(frame_add, width=12)
    entry_name.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_add, text="性别:").grid(row=0, column=2, padx=5, pady=5)
    gender_var = tk.StringVar(value="男")
    tk.Radiobutton(frame_add, text="男", variable=gender_var, value="男").grid(row=0, column=3, padx=2)
    tk.Radiobutton(frame_add, text="女", variable=gender_var, value="女").grid(row=0, column=4, padx=2)

    tk.Label(frame_add, text="职称:").grid(row=0, column=5, padx=5, pady=5)
    entry_title = tk.Entry(frame_add, width=12)
    entry_title.grid(row=0, column=6, padx=5, pady=5)

    tk.Label(frame_add, text="电话:").grid(row=1, column=0, padx=5, pady=5)
    entry_phone = tk.Entry(frame_add, width=12)
    entry_phone.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame_add, text="所属科室:").grid(row=1, column=2, padx=5, pady=5)
    dept_combo = ttk.Combobox(frame_add, width=12)
    dept_combo.grid(row=1, column=3, padx=5, pady=5)

    def load_depts():
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT dept_id, name FROM department")
            depts = cursor.fetchall()
            cursor.close()
            conn.close()
            dept_dict = {name: dept_id for dept_id, name in depts}
            dept_combo['values'] = list(dept_dict.keys())
            return dept_dict
        except:
            return {}

    dept_dict = load_depts()

    def add_doctor():
        name = entry_name.get().strip()
        gender = gender_var.get()
        title = entry_title.get().strip()
        phone = entry_phone.get().strip()
        dept_name = dept_combo.get()

        if not name or not title or not phone or not dept_name:
            messagebox.showwarning("警告", "请填写完整信息")
            return

        dept_id = dept_dict.get(dept_name)
        if not dept_id:
            messagebox.showerror("错误", "请选择有效的科室")
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO doctor (name, gender, title, phone, dept_id) VALUES (%s, %s, %s, %s, %s)",
                (name, gender, title, phone, dept_id)
            )
            conn.commit()

            doctor_id = cursor.lastrowid
            try:
                cursor.execute(
                    "INSERT INTO user (username, password, role, person_id) VALUES (%s, %s, 'doctor', %s)",
                    (phone, '123456', doctor_id)
                )
                conn.commit()
                messagebox.showinfo("成功", f"医生 {name} 添加成功\n登录账号: {phone} 密码: 123456")
            except:
                messagebox.showinfo("成功", f"医生 {name} 添加成功\n(登录账号创建失败，请手动添加)")

            cursor.close()
            conn.close()
            entry_name.delete(0, tk.END)
            entry_title.delete(0, tk.END)
            entry_phone.delete(0, tk.END)
            dept_combo.set('')
            refresh_tree()
        except mysql.connector.Error as e:
            messagebox.showerror("错误", str(e))

    tk.Button(frame_add, text="添加", command=add_doctor, bg="green", fg="white").grid(row=2, column=0, columnspan=7,
                                                                                       pady=10)

    # 医生列表区域
    frame_list = tk.LabelFrame(win, text="医生列表", padx=10, pady=10)
    frame_list.pack(pady=10, padx=10, fill="both", expand=True)

    columns = ("doctor_id", "name", "gender", "title", "phone", "dept_name")
    tree = ttk.Treeview(frame_list, columns=columns, show="headings")
    tree.heading("doctor_id", text="编号")
    tree.heading("name", text="姓名")
    tree.heading("gender", text="性别")
    tree.heading("title", text="职称")
    tree.heading("phone", text="电话")
    tree.heading("dept_name", text="所属科室")
    tree.column("doctor_id", width=50)
    tree.column("name", width=80)
    tree.column("gender", width=50)
    tree.column("title", width=100)
    tree.column("phone", width=120)
    tree.column("dept_name", width=100)
    tree.pack(side=tk.LEFT, fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame_list, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill="y")

    def refresh_tree():
        for item in tree.get_children():
            tree.delete(item)
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.doctor_id, d.name, d.gender, d.title, d.phone, dept.name
                FROM doctor d
                JOIN department dept ON d.dept_id = dept.dept_id
            """)
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            messagebox.showerror("错误", str(e))

    def delete_doctor():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的医生")
            return
        doctor_id = tree.item(selected[0])["values"][0]
        name = tree.item(selected[0])["values"][1]
        if messagebox.askyesno("确认", f"确定要删除医生 {name} 吗？\n对应的登录账号也会被删除。"):
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM user WHERE role='doctor' AND person_id=%s", (doctor_id,))
                cursor.execute("DELETE FROM doctor WHERE doctor_id=%s", (doctor_id,))
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("成功", "医生删除成功")
                refresh_tree()
            except mysql.connector.Error as e:
                messagebox.showerror("错误", f"删除失败：{e}")

    def update_doctor():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要修改的医生")
            return
        values = tree.item(selected[0])["values"]
        doctor_id = values[0]
        old_name = values[1]
        old_gender = values[2]
        old_title = values[3]
        old_phone = values[4]
        old_dept_name = values[5]

        update_win = tk.Toplevel(win)
        update_win.title("修改医生")
        update_win.geometry("400x350")

        tk.Label(update_win, text="姓名:").pack(pady=5)
        entry_new_name = tk.Entry(update_win, width=20)
        entry_new_name.insert(0, old_name)
        entry_new_name.pack()

        tk.Label(update_win, text="性别:").pack(pady=5)
        gender_var_new = tk.StringVar(value=old_gender)
        tk.Radiobutton(update_win, text="男", variable=gender_var_new, value="男").pack()
        tk.Radiobutton(update_win, text="女", variable=gender_var_new, value="女").pack()

        tk.Label(update_win, text="职称:").pack(pady=5)
        entry_new_title = tk.Entry(update_win, width=20)
        entry_new_title.insert(0, old_title)
        entry_new_title.pack()

        tk.Label(update_win, text="电话:").pack(pady=5)
        entry_new_phone = tk.Entry(update_win, width=20)
        entry_new_phone.insert(0, old_phone)
        entry_new_phone.pack()

        tk.Label(update_win, text="所属科室:").pack(pady=5)
        dept_combo_new = ttk.Combobox(update_win, width=20)
        dept_combo_new['values'] = list(dept_dict.keys())
        dept_combo_new.set(old_dept_name)
        dept_combo_new.pack()

        def do_update():
            new_name = entry_new_name.get().strip()
            new_gender = gender_var_new.get()
            new_title = entry_new_title.get().strip()
            new_phone = entry_new_phone.get().strip()
            new_dept_name = dept_combo_new.get()

            if not new_name or not new_title or not new_phone or not new_dept_name:
                messagebox.showwarning("警告", "请填写完整信息")
                return

            new_dept_id = dept_dict.get(new_dept_name)
            if not new_dept_id:
                messagebox.showerror("错误", "请选择有效的科室")
                return

            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE doctor SET name=%s, gender=%s, title=%s, phone=%s, dept_id=%s WHERE doctor_id=%s",
                    (new_name, new_gender, new_title, new_phone, new_dept_id, doctor_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("成功", "医生修改成功")
                update_win.destroy()
                refresh_tree()
            except mysql.connector.Error as e:
                messagebox.showerror("错误", str(e))

        tk.Button(update_win, text="保存", command=do_update, bg="blue", fg="white").pack(pady=20)

    frame_buttons = tk.Frame(win)
    frame_buttons.pack(pady=10)
    tk.Button(frame_buttons, text="修改", command=update_doctor, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_buttons, text="删除", command=delete_doctor, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_buttons, text="刷新", command=refresh_tree, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_buttons, text="关闭", command=win.destroy, width=10).pack(side=tk.LEFT, padx=5)

    refresh_tree()


#管理药品按键

def manage_drugs():
    """管理药品窗口"""
    win = tk.Toplevel()
    win.title("管理药品")
    win.geometry("700x550")

    # 添加药品区域
    frame_add = tk.LabelFrame(win, text="添加药品", padx=10, pady=10)
    frame_add.pack(pady=10, padx=10, fill="x")

    tk.Label(frame_add, text="药品名称:").grid(row=0, column=0, padx=5, pady=5)
    entry_name = tk.Entry(frame_add, width=15)
    entry_name.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_add, text="单价:").grid(row=0, column=2, padx=5, pady=5)
    entry_price = tk.Entry(frame_add, width=10)
    entry_price.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(frame_add, text="库存:").grid(row=0, column=4, padx=5, pady=5)
    entry_stock = tk.Entry(frame_add, width=10)
    entry_stock.grid(row=0, column=5, padx=5, pady=5)

    tk.Label(frame_add, text="单位:").grid(row=1, column=0, padx=5, pady=5)
    entry_unit = tk.Entry(frame_add, width=15)
    entry_unit.grid(row=1, column=1, padx=5, pady=5)

    def add_drug():
        name = entry_name.get().strip()
        try:
            price = float(entry_price.get().strip())
            stock = int(entry_stock.get().strip())
        except ValueError:
            messagebox.showwarning("警告", "单价请输入数字，库存请输入整数")
            return
        unit = entry_unit.get().strip()

        if not name or not unit:
            messagebox.showwarning("警告", "请填写完整信息")
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO drug (name, price, stock, unit) VALUES (%s, %s, %s, %s)",
                (name, price, stock, unit)
            )
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("成功", "药品添加成功")
            entry_name.delete(0, tk.END)
            entry_price.delete(0, tk.END)
            entry_stock.delete(0, tk.END)
            entry_unit.delete(0, tk.END)
            refresh_tree()
        except mysql.connector.Error as e:
            if "Duplicate" in str(e):
                messagebox.showerror("错误", "药品名称已存在")
            else:
                messagebox.showerror("错误", str(e))

    tk.Button(frame_add, text="添加", command=add_drug, bg="green", fg="white").grid(row=2, column=0, columnspan=6,
                                                                                     pady=10)

    # 药品列表区域
    frame_list = tk.LabelFrame(win, text="药品列表", padx=10, pady=10)
    frame_list.pack(pady=10, padx=10, fill="both", expand=True)

    columns = ("drug_id", "name", "price", "stock", "unit")
    tree = ttk.Treeview(frame_list, columns=columns, show="headings")
    tree.heading("drug_id", text="编号")
    tree.heading("name", text="药品名称")
    tree.heading("price", text="单价")
    tree.heading("stock", text="库存")
    tree.heading("unit", text="单位")
    tree.column("drug_id", width=50)
    tree.column("name", width=150)
    tree.column("price", width=80)
    tree.column("stock", width=80)
    tree.column("unit", width=80)
    tree.pack(side=tk.LEFT, fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame_list, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill="y")

    def refresh_tree():
        for item in tree.get_children():
            tree.delete(item)
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT drug_id, name, price, stock, unit FROM drug")
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            messagebox.showerror("错误", str(e))

    def delete_drug():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的药品")
            return
        drug_id = tree.item(selected[0])["values"][0]
        name = tree.item(selected[0])["values"][1]
        if messagebox.askyesno("确认", f"确定要删除药品 {name} 吗？"):
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM drug WHERE drug_id=%s", (drug_id,))
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("成功", "药品删除成功")
                refresh_tree()
            except mysql.connector.Error as e:
                messagebox.showerror("错误", f"删除失败：{e}")

    def update_drug():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要修改的药品")
            return
        values = tree.item(selected[0])["values"]
        drug_id = values[0]
        old_name = values[1]
        old_price = values[2]
        old_stock = values[3]
        old_unit = values[4]

        update_win = tk.Toplevel(win)
        update_win.title("修改药品")
        update_win.geometry("350x300")

        tk.Label(update_win, text="药品名称:").pack(pady=5)
        entry_new_name = tk.Entry(update_win, width=20)
        entry_new_name.insert(0, old_name)
        entry_new_name.pack()

        tk.Label(update_win, text="单价:").pack(pady=5)
        entry_new_price = tk.Entry(update_win, width=20)
        entry_new_price.insert(0, old_price)
        entry_new_price.pack()

        tk.Label(update_win, text="库存:").pack(pady=5)
        entry_new_stock = tk.Entry(update_win, width=20)
        entry_new_stock.insert(0, old_stock)
        entry_new_stock.pack()

        tk.Label(update_win, text="单位:").pack(pady=5)
        entry_new_unit = tk.Entry(update_win, width=20)
        entry_new_unit.insert(0, old_unit)
        entry_new_unit.pack()

        def do_update():
            new_name = entry_new_name.get().strip()
            try:
                new_price = float(entry_new_price.get().strip())
                new_stock = int(entry_new_stock.get().strip())
            except ValueError:
                messagebox.showwarning("警告", "单价请输入数字，库存请输入整数")
                return
            new_unit = entry_new_unit.get().strip()

            if not new_name or not new_unit:
                messagebox.showwarning("警告", "请填写完整信息")
                return

            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE drug SET name=%s, price=%s, stock=%s, unit=%s WHERE drug_id=%s",
                    (new_name, new_price, new_stock, new_unit, drug_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("成功", "药品修改成功")
                update_win.destroy()
                refresh_tree()
            except mysql.connector.Error as e:
                messagebox.showerror("错误", str(e))

        tk.Button(update_win, text="保存", command=do_update, bg="blue", fg="white").pack(pady=20)

    frame_buttons = tk.Frame(win)
    frame_buttons.pack(pady=10)
    tk.Button(frame_buttons, text="修改", command=update_drug, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_buttons, text="删除", command=delete_drug, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_buttons, text="刷新", command=refresh_tree, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_buttons, text="关闭", command=win.destroy, width=10).pack(side=tk.LEFT, padx=5)

    refresh_tree()


#主界面

def open_admin_window():
    win = tk.Toplevel()
    win.title("管理员界面")
    win.geometry("500x400")
    tk.Label(win, text="管理员功能", font=("Arial", 16)).pack(pady=10)

    tk.Button(win, text="管理科室", command=manage_departments, width=20).pack(pady=5)
    tk.Button(win, text="管理医生", command=manage_doctors, width=20).pack(pady=5)
    tk.Button(win, text="管理药品", command=manage_drugs, width=20).pack(pady=5)
    tk.Button(win, text="退出", command=win.destroy, width=20).pack(pady=20)