from cProfile import label

from psycopg2.extras import execute_values

import tkinter as tk

from tkinter import ttk

import psycopg2

import threading

import tkcalendar as Calendar

from tkinter import messagebox

from datetime import datetime, date

import pandas as pd

 

class window():

 

    def __init__(self,root):

        self.root = root

        self.render_threading()

        self.rendertk()

        screen_width = self.root.winfo_screenwidth()

        screen_height = self.root.winfo_screenheight()

 

     # Configure rows and columns for automatic resizing

        for i in range(50):

            self.root.grid_rowconfigure(i, weight=1)

        for i in range(30):  

            self.root.grid_columnconfigure(i, weight=1)

        self.root.geometry(f"{screen_width}x{screen_height}")

 

        self.data_entry = tk.Entry(root, width=20, font=("Arial", 20))

        self.data_entry.place(x=70, y=427)  # ตำแหน่งตรงกลางใน column 0 และ 1

        self.data_entry.focus()

 

        self.data_entry.bind('<Return>', self.on_submit_auto)

   

    def on_submit_auto(self, event):

        self.on_submit()

 

    def on_submit(self):

        selected_option = self.selected_option.get()

        data_value = self.data_entry.get().upper()

        data_department = self.datatext_entry.get()

        day_ns = self.condition.get()

        data_date = self.datelabel_entry.get()

 

        date_sum = day_ns+"_"+data_date

       

        try:

            connection = psycopg2.connect(

                database="postgres",

                user="postgres",

                password="postgres",

                host="127.0.0.1",

                port="5432"

            )

           

            cursor = connection.cursor()

 

            input_query = "INSERT INTO scan_id (con_wk, id_no,department, ds_ns,data_date) VALUES (%s, %s, %s, %s, %s)"

            data_insert = (selected_option, data_value, data_department, day_ns, data_date)

            cursor.execute(input_query, data_insert)

 

            connection.commit()

            cursor.close()

 

            self.result_label.config(text="Data saved successfully.", fg="green")

            self.data_entry.delete(0, tk.END)

            self.data_entry.focus()

 

 

            self.show_last_saved_data()

 

            connection = psycopg2.connect(

                database="postgres",

                user="postgres",

                password="postgres",

                host="127.0.0.1",

                port="5432"

            )

 

            cursor3 = connection.cursor()

            cursor2 = connection.cursor()

            cursor4 = connection.cursor()

 

            cursor2.execute("SELECT * FROM smart_hr_man_car WHERE id_code = %s", (data_value,))

            master = cursor2.fetchall()

            df_master = pd.DataFrame(master)

 

            # cursor4.execute("SELECT * FROM scan_id")

            # scan_id = cursor4.fetchall()

            # df_scan_id = pd.DataFrame(scan_id)

            # df_scan_id_date_now = df_scan_id[df_scan_id.iloc[:,3].dt.date == date.today()]

 

            df_fin = pd.DataFrame({

                "id_code": df_master[0],

                "name": df_master[1],

                "surname": df_master[2],

                "cost_center": df_master[3],

                "ds_ns": day_ns,

                "con_wk": selected_option,

                "department": data_department,

                "date_time": datetime.now(),

                "car_infor": df_master[4],

                "stop_car": df_master[5],

                "select_date": date_sum

            })

 

            date_now = date.today().strftime("%Y%m%d")

 

            if not df_fin.empty:

                table_name = "newtable"

                columns = ", ".join(df_fin.columns)

                conn = connection

                cur = conn.cursor()

 

                query = ("SELECT COUNT(*) FROM newtable WHERE id_code = %s AND select_date = %s")

                params = (data_value, date_sum)

                cur.execute(query, params)

                row_count = cur.fetchone()[0]

 

                if row_count > 0:

                    update_query = "UPDATE newtable SET date_time = %s, con_wk = %s WHERE id_code = %s AND select_date = %s"

                    data_values = (datetime.now(), selected_option, data_value, date_sum)

                    cur.execute(update_query, data_values)

                else:            

                    insert_query = f'INSERT INTO {table_name} ({columns}) VALUES %s'

                    data_values = [tuple(row) for row in df_fin.to_numpy()]

                    execute_values(cur, insert_query, data_values)

 

                # Commit the changes to the database

                conn.commit()

                cur.close()

 

            query = "SELECT * FROM newtable WHERE select_date = %s OR select_date = %s"

            params = (f"DS_{date_now}", f"NS_{date_now}")

            cursor3.execute(query, params)

            records = cursor3.fetchall()

            df_record = pd.DataFrame(records)

 

            self.count_normal_working = len(df_record[df_record[5] == 'Normal working'])

            self.count_ot = len(df_record[df_record[5] == 'OT'])

            self.count_holiday = len(df_record[df_record[5] == 'Holiday'])

            self.count_leave = len(df_record[df_record[5] == 'Leave'])

            self.count_leave_2hr = len(df_record[df_record[5] == 'Leave 2Hr'])

            self.count_leave_4hr = len(df_record[df_record[5] == 'Leave 4Hr'])

            self.count_roving = len(df_record[df_record[5] == 'Roving'])

            self.count_repair = len(df_record[df_record[5] == 'Repair'])

            self.count_working_in_line = len(df_record[df_record[5] == 'Working in line'])

            self.count_other = len(df_record[df_record[5] == 'Other'])

            self.count_total = len(df_record[df_record[5].notna()])

 

            self.normal_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#B6E3E9")  

            self.normal_entry.place(x=1050, y=100)

            self.normal_entry.config(text=str(self.count_normal_working))  # ปรับตำแหน่ง

 

            self.ot_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#A1CAE2")  

            self.ot_entry.place(x=1050, y=150)

            self.ot_entry.config(text=str(self.count_ot))

 

            self.holiday_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#A1CAE2")  

            self.holiday_entry.place(x=1050, y=200)

            self.holiday_entry.config(text=str(self.count_holiday))

 

            self.leave_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#A1CAE2")  

            self.leave_entry.place(x=1050, y=250)

            self.leave_entry.config(text=str(self.count_leave))

 

            self.leave2_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#A1CAE2")  

            self.leave2_entry.place(x=1050, y=300)

            self.leave2_entry.config(text=str(self.count_leave_2hr))

 

            self.leave4_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#A1CAE2")  

            self.leave4_entry.place(x=1050, y=350)

            self.leave4_entry.config(text=str(self.count_leave_4hr))

 

            self.roving_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#A1CAE2")  

            self.roving_entry.place(x=1050, y=400)

            self.roving_entry.config(text=str(self.count_roving))

 

            self.repair_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#A1CAE2")  

            self.repair_entry.place(x=1050, y=450)

            self.work_entry.config(text=str(self.count_repair))

 

            self.work_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#A1CAE2")  

            self.work_entry.place(x=1050, y=500)

            self.work_entry.config(text=str(self.count_working_in_line))

 

            self.other_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#A1CAE2")  

            self.other_entry.place(x=1050, y=550)

            self.other_entry.config(text=str(self.count_other))

 

            self.op_total_entry = tk.Label(root, width=5, font=("Arial", 30),bg="#E4DBBE")  

            self.op_total_entry.place(x=1400, y=30)

            self.op_total_entry.config(text=str(self.count_total))

 

            cursor2.close()

            cursor3.close()

            cursor4.close()

       

        except Exception as e:

            print("Error:", str(e))

            self.result_label.config(text="Error saving data.",fg="red")

           

    def show_last_saved_data(self):

        try:

            connection = psycopg2.connect(

                database="postgres",

                user="postgres",

                password="postgres",

                host="127.0.0.1",

                port="5432"

            )

 

            cursor1 = connection.cursor()

 

            # Modify the SQL query to select all records for the current day

            current_date = datetime.now().date()

            cursor1.execute("SELECT * FROM scan_id WHERE date_time::date = %s ORDER BY date_time DESC", (current_date,))

            scan = cursor1.fetchall()

 

            self.result_text.config(state=tk.NORMAL)

            self.result_text.delete(1.0, tk.END)

 

   

            # เพิ่มหัวข้อคอลัมน์

            self.result_text.insert(tk.END, "  ID NO.\tShift\tDepartment\n")

            # self.result_text.insert(tk.END, "  ID NO.\t Shift  \t\t\t     Date_Timestamp\n")

 

            for scan in scan:

                id = scan[0]

                data = scan[1]

                times = scan[3].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Format time with 3 decimal places

                dsns = scan[4]

                work = scan[2]

                depart = scan[5]

                self.result_text.insert(tk.END, f"{data} | {dsns} | {depart}  {work} {times}\n")

 

            cursor1.close()

 

            # df = pd.DataFrame(records, columns=["id_code", "name", "surname", "cost_center", "ds_ns", "con_wk", "department", "date_time", "สายรถ", "จุดจอด"])

 

        except Exception as e:

            print("Error:", str(e))

 

        finally:

            self.result_text.config(state=tk.DISABLED)

 

    def render_threading(self):

        render = threading.Thread(target=self.rendertk)

        render.start()

 

   

    def rendertk(self):

        # self.root.title("PostgreSQL Data Entry")

 

        self.id_label = tk.Label(root, text="ID No.", font=20)  

        self.id_label.place(x=5, y=430)  

 

        self.count_label = tk.Label(root, text="COUNT", font=("Helvetica", 40, "bold"))

        self.count_label.place(x=740, y=20)

 

        self.normal_label = tk.Label(root, text="Normal Working", font=("Helvetica", 20, "bold"))

        self.normal_label.place(x=800, y=100)

        self.normal_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#A1CAE2")  

        self.normal_entry.place(x=1050, y=100)  # ปรับตำแหน่ง

 

        self.ot_label = tk.Label(root, text="OT", font=("Helvetica", 20, "bold"))

        self.ot_label.place(x=800, y=150)

        self.ot_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#A1CAE2")  

        self.ot_entry.place(x=1050, y=150)

 

        self.holiday_label = tk.Label(root, text="Holiday", font=("Helvetica", 20, "bold"))

        self.holiday_label.place(x=800, y=200)

        self.holiday_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#A1CAE2")  

        self.holiday_entry.place(x=1050, y=200)

 

        self.leave_label = tk.Label(root, text="Leave", font=("Helvetica", 20, "bold"))

        self.leave_label.place(x=800, y=250)

        self.leave_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#A1CAE2")  

        self.leave_entry.place(x=1050, y=250)

 

        self.leave2_label = tk.Label(root, text="Leave 2Hr", font=("Helvetica", 20, "bold"))

        self.leave2_label.place(x=800, y=300)

        self.leave2_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#A1CAE2")  

        self.leave2_entry.place(x=1050, y=300)

 

        self.leave4_label = tk.Label(root, text="Leave 4Hr", font=("Helvetica", 20, "bold"))

        self.leave4_label.place(x=800, y=350)

        self.leave4_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#A1CAE2")  

        self.leave4_entry.place(x=1050, y=350)

 

        self.roving_label = tk.Label(root, text="Roving", font=("Helvetica", 20, "bold"))

        self.roving_label.place(x=800, y=400)

        self.roving_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#A1CAE2")  

        self.roving_entry.place(x=1050, y=400)

 

        self.repair_label = tk.Label(root, text="Repair", font=("Helvetica", 20, "bold"))

        self.repair_label.place(x=800, y=450)

        self.repair_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#A1CAE2")  

        self.repair_entry.place(x=1050, y=450)

 

        self.work_label = tk.Label(root, text="Working in line", font=("Helvetica", 20, "bold"))

        self.work_label.place(x=800, y=500)

        self.work_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#A1CAE2")  

        self.work_entry.place(x=1050, y=500)

 

        self.other_label = tk.Label(root, text="Other", font=("Helvetica", 20, "bold"))

        self.other_label.place(x=800, y=550)

        self.other_entry = tk.Label(root, width=10, font=("Arial", 20),bg="#A1CAE2")  

        self.other_entry.place(x=1050, y=550)

 

        self.condition = tk.StringVar()  # Variable to store the selected condition

        # self.condition.set("")  # Set the default condition to empty

 

    # button DS and NS

        self.button_ds = tk.Radiobutton(root, text="DS", variable=self.condition, value="DS", command=self.update_button_colors, indicator=0, width=17, height=2)

        self.button_ds.configure(font=("Arial", 20))

        self.button_ds.configure(relief="raised", bd=3) # Configure button-like appearance

        self.button_ds.place(x=20, y=125)

 

        self.button_ns = tk.Radiobutton(root, text="NS", variable=self.condition, value="NS", command=self.update_button_colors, indicator=0, width=17, height=2)

        self.button_ns.configure(font=("Arial", 20))

        self.button_ns.configure(relief="raised", bd=3)  # Configure button-like appearance

        self.button_ns.place(x=330, y=125)

 

        # กำหนดการเชื่อมต่อกับเมท็อด enable_conditions

        self.button_ds.configure(command=lambda: self.enable_conditions("DS"))

        self.button_ns.configure(command=lambda: self.enable_conditions("NS"))

 

        self.button_ds.configure(command=self.enable_conditions)  # Set command to enable conditions

   

 

    #chec

        self.conditions_frame = tk.Frame(root)

        self.conditions_frame.place(x=13, y=150)

 

        # self.condition_buttons = []

 

        self.options_column1 = [

            ("Normal working", "Normal working"),

            ("OT", "OT"),

            ("Work on Holiday", "Work on Holiday")

        ]

 

        self.options_column2 = [

            ("Leave", "Leave"),

            ("Leave 2Hr", "Leave 2Hr"),

            ("Leave 4Hr", "Leave 4Hr")

        ]

 

        self.options_column3 = [

            ("Roving", "Roving"),

            ("Other", "Other"),

            ("Repair", "Repair"),

            ("Working in line", "Working in line")

        ]

 

        self.selected_option = tk.StringVar()

        self.selected_option.set("DS normal working")

 

        for i, (text, value) in enumerate(self.options_column1):

            tk.Radiobutton(root, text=text, variable=self.selected_option, value=value, font=("Arial", 20)).place(x=10, y=225 + i * 43)

 

        for i, (text, value) in enumerate(self.options_column2):

            tk.Radiobutton(root, text=text, variable=self.selected_option, value=value, font=("Arial", 20)).place(x=270, y=225 + i * 43)

 

        for i, (text, value) in enumerate(self.options_column3):

            tk.Radiobutton(root, text=text, variable=self.selected_option, value=value, font=("Arial", 20)).place(x=460, y=225 + i * 43)

 

    #Text: Department

        self.depart_label = tk.Label(root, text="Department", font=("Helvetica", 20, "bold"))

        self.depart_label.place(x=53, y=15)

        self.datatext_entry = tk.Entry(root, width=8, font=("Arial", 40),bg="#A1CAE2")  

        self.datatext_entry.place(x=20, y=55)  # ปรับตำแหน่ง

   

    #Text: Date

        self.date_label = tk.Label(root, text="Date", font=("Helvetica", 20, "bold"))

        self.date_label.place(x=440, y=15)

        self.datelabel_entry = tk.Entry(root, width=8, font=("Arial", 40),bg="#A1CAE2")  

        self.datelabel_entry.place(x=350, y=55)  

 

   

    #Text: op total

        self.id_label = tk.Label(root, text="Total", font=("Helvetica", 10, "bold"))

        self.id_label.place(x=1440, y=10)

 

        self.op_total_entry = tk.Label(root, width=5, font=("Arial", 30),bg="#E4DBBE")  

        self.op_total_entry.place(x=1400, y=30)  # ปรับตำแหน่ง

 

        self.submit_button = tk.Button(root,width=7, font=("Arial", 15), text="Submit", command=self.on_submit)

        self.submit_button.place(x=390, y=425)

 

       

 

 

    #Show all data

        self.result_label = tk.Label(root, text="",font=("Arial", 12)) #label success

        self.result_label.place(x=490, y=430)

        # self.result_label.grid(row=20, column=0, columnspan=1, sticky="n")

        self.result_text = tk.Text(root, height=14, width=65,font=("Arial", 14))

        self.result_text.place(x=10, y=469)  # ปรับขนาด

 

 

    def enable_conditions(self, condition_type):

        self.condition.set(condition_type)  # Set the condition to DS or NS

        self.update_button_colors()  # อัปเดตสีของปุ่ม

 

        for button in self.condition_buttons:

            button.configure(state="normal")  # Enable condition buttons

 

        if self.condition.get() != "":

            for button in self.condition_buttons:

                if button.instate(['selected']):

                    self.condition.set(self.condition.get() + " " + button.cget("text"))

 

        if self.condition.get() != "DS" and self.condition.get() != "NS":

            for button in self.condition_buttons:

                button.pack_forget()  # Hide condition buttons

        else:

            for button in self.condition_buttons:

                button.pack(anchor=tk.W)  # Show condition buttons

 

    def update_button_colors(self):

        if self.condition.get() == "DS":

            self.button_ds.configure(bg=self.color_ds_selected)  # ตั้งสีเหลืองสำหรับปุ่ม DS

            self.button_ns.configure(bg="SystemButtonFace")  # ตั้งสีพื้นหลังปกติสำหรับปุ่ม NS

        elif self.condition.get() == "NS":

            self.button_ns.configure(bg=self.color_ns_selected)  # ตั้งสีน้ำเงินสำหรับปุ่ม NS

            self.button_ds.configure(bg="SystemButtonFace")  # ตั้งสีพื้นหลังปกติสำหรับปุ่ม DS

        else:

            self.button_ds.configure(bg="SystemButtonFace")

            self.button_ns.configure(bg="SystemButtonFace")

 

    # def connect_data_master():

    #         connection = psycopg2.connect(

    #             database="postgres",

    #             user="postgres",

    #             password="postgres",

    #             host="127.0.0.1",

    #             port="5432"

    #         )

 

    #         cursor = connection.cursor()

    #         cursor2 = connection.cursor()

           

    #         cursor.execute("SELECT * FROM newtable")

    #         records = cursor.fetchall()

    #         df_record = pd.DataFrame(records)

 

    #         cursor2.execute("SELECT * FROM smart_hr_man_car")

    #         master = cursor2.fetchall()

    #         df_master = pd.DataFrame(master)

 

    #         df_fin = pd.DataFrame({

               

    #         })

   

        # self.data_entry.bind('<Return>', self.on_submit_auto)

 

root = tk.Tk()

app = window(root)

root.mainloop()