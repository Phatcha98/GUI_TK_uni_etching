import tkinter as tk
from tkinter import font
import psycopg2
from datetime import datetime
from tkinter import *
import tkinter.messagebox as messagebox
from screeninfo import get_monitors
import serial
from datetime import datetime, timedelta
from tkinter import ttk
import time

window = tk.Tk()
window.option_add('*font','impack 12') 
window.title("Eworking Calling Elgop Uniformity")
# รับขนาดหน้าจอจริงของเครื่องคอมพิวเตอร์
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
# Configure rows and columns for automatic resizing
for i in range(13):
    window.grid_rowconfigure(i, weight=1)
for i in range(9):  
    window.grid_columnconfigure(i, weight=1)

# กำหนดขนาดหน้าต่าง GUI เท่ากับขนาดหน้าจอ
window.geometry(f"{screen_width}x{screen_height}")

port = 'COM3'
baudrate = 9600
bytesize = serial.EIGHTBITS
parity = serial.PARITY_NONE
stopbits = serial.STOPBITS_ONE

measurement_data = None
measurement = None
ser = None
is_measurement_ended = False
is_measurement_started = False
selected_entry = None

def read_measurement():
    try:
        global ser, measurement_data, is_measurement_ended, is_measurement_started 
        ser = serial.Serial(port, baudrate, bytesize, parity, stopbits, xonxoff=True)
        measurement_data = ser.readline()
        ser.close()
        if is_measurement_started and not is_measurement_ended:
            update_measurement()
        if measurement_data:
            measurement = float(measurement_data.decode())
        measurement_gui = "{:.2f}".format(measurement)
        selected_entry.delete(0, tk.END)
        selected_entry.insert(tk.END, measurement_gui)
        calculate_differences()
    except serial.SerialException as e:
        messagebox.showerror("Serial Port Error", str(e))

def update_measurement():
    global measurement_data, measurement, is_measurement_ended, is_measurement_started
    if is_measurement_started and not is_measurement_ended:
        measurement_data = ser.readline()
        if measurement_data:
            measurement = float(measurement_data.decode())
            measurement_gui = "{:.3f}".format(measurement)
            for entry in [entry_fields1, entry_fields2]:
                entry.delete(0, tk.END)
                entry.insert(tk.END, measurement_gui)
            
            calculate_differences()
            window.after_idle(update_measurement)

def handle_measurement(event=None):
    global measurement_data, measurement, is_measurement_started, selected_entry, ser
    if selected_entry is not None:
        ser = serial.Serial(port, baudrate, bytesize, parity, stopbits, xonxoff=True)
        measurement_data = ser.readline()
        ser.close()
        if measurement_data:
            measurement = float(measurement_data.decode())
            measurement_gui = "{:.3f}".format(measurement)
            selected_entry.delete(0, tk.END)
            selected_entry.insert(tk.END, measurement_gui)
            if selected_entry in entry_fields1:
                entry_index = entry_fields1.index(selected_entry)
                if entry_index < len(entry_fields1):
                    entry_fields1[entry_index].set(measurement_gui)
            elif selected_entry in entry_fields2:
                entry_index = entry_fields2.index(selected_entry)
                if entry_index < len(entry_fields2):
                    entry_fields2[entry_index].set(measurement_gui)

def handle_entry_focus(event=None):
    global selected_entry
    selected_entry = event.widget
    handle_measurement() 

label_machine_no = tk.Label(window, text="Machine no:")
label_machine_no.grid(row=0, column=0, sticky='E')
entry_machine_no = tk.Entry(window, width=30)
entry_machine_no.grid(row=0, column=1, sticky='WE') 

win = tk.Label(window)
win.grid(row=1, column=0)

label_machine_no = tk.Label(window, text="Weight (μm)", font=('impack', 14, 'bold'))
label_machine_no.grid(row=2, column=0,sticky='E')

win = tk.Label(window)
win.grid(row=4, column=0)

label_weight_before = tk.Label(window, text="Weight before:")
label_weight_before.grid(row=3, column=0, sticky='E')
entry_fields1 = tk.Entry(window, textvariable=label_weight_before, width=30)
entry_fields1.grid(row=3, column=1, sticky='WE')
entry_fields1.bind("<FocusIn>", handle_entry_focus)

label_weight_after = tk.Label(window, text="Weight after:")
label_weight_after.grid(row=5, column=0, sticky='E')
entry_fields2 = tk.Entry(window, textvariable=label_weight_after, width=30)
entry_fields2.grid(row=5, column=1, sticky='WE')
entry_fields2.bind("<FocusIn>", handle_entry_focus)

label_etching_rate = tk.Label(window, text="Etching rate:")
label_etching_rate.grid(row=6, column=0, sticky='E')  

# win = tk.Label(window)
# win.grid(row=7, column=0)

calculate_button_clicked = False
result_labels = []
def calculate_button_click():
    global calculate_button_clicked
    calculate_button_clicked = True
    calculate_differences() 
    show_result()

def calculate_differences():
    try:
        entry_value1 = float(entry_fields1.get())
        entry_value11 = float(entry_fields2.get())
        if entry_value1 and entry_value11:
            result = ((entry_value1 - entry_value11) / 8.93) * 100
            result_label.config(text="{:.3f}".format(result))
            return result 
        else:
            result_label.config(text="")
            return None  

    except ValueError:
        result_label.config(text="")
        return None  
result_label = tk.Label(window, text="", width=30, bg="#FFFF99")
result_label.grid(row=6, column=1, sticky='WE')
window.bind("<Button-1>", lambda event: calculate_differences())

def show_result():
    difference = calculate_differences()
    if difference is not None:
        if difference < 0.6 or difference > 0.8:
            result_text = "FAIL"
            result_color = "red"
        elif difference < 0.63 or difference > 0.74:
            result_text = "WARNING"
            result_color = "orange"
        else:
            result_text = "PASS"
            result_color = "green"
        result_label1.config(text=result_text, fg=result_color)
result_label1 = tk.Label(window, text="") 
result_label1.grid(row=6, column=2, sticky='W')
window.bind("<Button-1>", lambda event: show_result())

ym = time.strftime("%Y/%m/%d")
class Clock:
    def __init__(self):
        self.time1 = ''
        self.time2 = time.strftime('%H:%M:%S')
        self.mFrame = Frame()
        self.mFrame.grid(row=0,column=5,sticky='E') 

        self.watch = Label(self.mFrame, text=self.time2)
        self.watch.pack()

        self.changeLabel() 

    def changeLabel(self): 
        self.time2 = time.strftime('%H:%M:%S')
        self.watch.configure(text=self.time2)
        self.mFrame.after(200, self.changeLabel) 

C=Clock()
Label(window,text=ym).grid(row=1, column=5,sticky='E') 

dt0 = None  
selected_entry = None

def handle_entry_focus(event):
    global dt0
    if event.widget == entry_fields1:
        dt0 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    entry_fields1.bind("<FocusIn>", handle_entry_focus)

def save_to_database():
    global data_rows
    uniformity_result =  uniformity_label.cget("text")
    uniformity_judgement = result_label2.cget("text")

    connection = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="postgres"
    )
    cursor = connection.cursor()

    try:
        for data_row in data_rows:
            no, measure_time, machine_no, before, after, er, create_at, process, er_judmemt= data_row
            cursor.execute(
                "INSERT INTO public.\"eworking_calling_elgop_etchingrate_uniformity\"(no, measure_time, mc_no, \"before\", \"after\", er, create_at, process, uniformity_judgement, uniformity_result)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (no, measure_time, machine_no, before, after, er, create_at, process, uniformity_judgement, uniformity_result)
            )
        connection.commit()
        connection.close()
        messagebox.showinfo("Success", "Saved to databases table eworking_calling_elgop_etchingrate_uniformity.")

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numeric values for Weight Before and Weight After.")
    except Exception as e:
        print("Error:", e)

    data_rows = []  # Clear data after saving
    update_table()  # Update the table GUI
    uniformity_label.config(text=" ")
    result_label1.config(text=" ")
    result_label.config(text=" ")
    result_label2.config(text=" ")
    om1.configure(text="Process", bg='#FFCC33')
    for widget in window.winfo_children():
            if isinstance(widget, Entry):  
                widget.delete(0,'end') 
                widget.insert(0,'') 
    pass

# Function to clear all input fields
def reset_inputs():
    uniformity_label.config(text=" ")
    result_label1.config(text=" ")
    result_label.config(text=" ")
    result_label2.config(text=" ")
    om1.configure(text="Process", bg='#FFCC33')

    for item in tree.get_children():
        tree.delete(item)

    for widget in window.winfo_children():
            if isinstance(widget,Entry):  
                widget.delete(0,'end') 
                widget.insert(0,'') 
    pass

columns = ("No.", "Measure Time", "Machine No.", "Weight Before", "Weight After", "Etching Rate", "Create At", "Process", "Etching Rate Judmemt")
data_rows = []
current_row_index = 1

# Create a Treeview widget to display the data
tree = ttk.Treeview(window, columns=columns, show="headings", height=15, style="Custom.Treeview")
style = ttk.Style()
style.configure("Custom.Treeview.Heading", font=("Arial", 10, "bold"))  
style.configure("Custom.Treeview", font=("Arial", 10, "bold"))  

# Create a vertical scrollbar
tree_scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=tree_scrollbar.set)
tree_scrollbar.grid(row=10, column=8, sticky="ns")

for idx, col in enumerate(columns, start=1):
    column_width = 150  # เพิ่มความกว้างของคอลัมน์ในแนว Y
    tree.column(col, width=column_width, anchor=tk.W)
    tree.heading(col, text=col, anchor=tk.W)
    tree.column(col, width=column_width, anchor=tk.W, stretch=True)

# Set the Treeview widget to expand both vertically and horizontally
tree.grid(row=10, column=0, columnspan=8, padx=10, pady=50, sticky="ns")
tree_scrollbar.grid(row=10, column=8, sticky="ns")

# Configure rows and columns for automatic resizing
window.grid_rowconfigure(6, weight=1)  # Row with the Treeview
window.grid_columnconfigure(0, weight=1)  # Column with the Treeview

def update_table():
    # Clear existing data in the Treeview
    for item in tree.get_children():
        tree.delete(item)

    for idx, data_row in enumerate(data_rows, start=1):
        no, measure_time, machine_no, before, after, er, create_at, process, er_judmemt  = data_row
        etching_rate_formatted = "{:.3f}".format(er)  # Format etching rate with 3 decimal places
        tree.insert("", "end", values=(no, measure_time, machine_no, before, after, etching_rate_formatted, create_at, process, er_judmemt))

    tree_scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=tree_scrollbar.set)
    tree_scrollbar.grid(row=10, column=8, sticky="ns")

def save_to_table():
    global dt0
    global data_rows
    machine_no = entry_machine_no.get()
    weight_before = entry_fields1.get()
    weight_after = entry_fields2.get()
    er_judmemt = result_label1.cget("text")
    etching_rate = calculate_differences()
    process = options.get()  # Use options.get() to retrieve the selected value
    measure_time = dt0 
    create_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    no = len(data_rows) + 1  
    
    if machine_no and weight_before and weight_after:
        data_rows.append((no, measure_time, machine_no, weight_before, weight_after, etching_rate, create_at, process,er_judmemt))
        update_table()

label_Uniformity= tk.Label(window, text="Uniformity (%):")
label_Uniformity.grid(row=7, column=0, sticky='E')
def calculate_uniformity():
    # คำนวณค่า MAX, MIN, และ AVG จากข้อมูลในตาราง
    data = [float(row[5]) for row in data_rows]
    if data:
        max_value = max(data)
        min_value = min(data)
        avg_value = sum(data) / len(data)
        uniformity_percent = (1 - ((max_value - min_value) / (2 * avg_value))) * 100

        # แสดงผลลัพธ์ใน GUI
        uniformity_label.config(text="{:.2f}".format(uniformity_percent))
        sh_result(uniformity_percent)

uniformity_label = tk.Label(window, text="", width=20)
uniformity_label.grid(row=7, column=1, sticky='W')

options = tk.StringVar(window)
options.set("Process") # default value

l1 = tk.Label(window,  text='Process:', width=10)  
l1.grid(row=8,column=0, sticky='E') 

om1 =tk.OptionMenu(window, options, "A-ELGOP","A-SCHS")
om1.config(bg="#FFCC33")
om1.grid(row=8,column=1, sticky='W') 

def sh_result(uniformity_percent):
    if uniformity_percent >= 90:
        result_text1 = "PASS"
        result_color1 = "green"
    else:
        result_text1 = "FAIL"
        result_color1 = "red"
    result_label2.config(text=result_text1, fg=result_color1)
result_label2 = tk.Label(window, text="") 
result_label2.grid(row=5, column=2, sticky='WE')

uniformity_button = tk.Button(window, text="UNIFORMITY PERCENT", width=18, bg="#FF6666", command=calculate_uniformity, font=('impack', 12, 'bold'))
uniformity_button.grid(row=9, column=5, padx=3, pady=3, ipadx=3, ipady=3)

b7 = tk.Button(window, text="SAVE TO TABLE", width=15, bg="#00bcd4", command=save_to_table, font=('impack', 12, 'bold'))
b7.grid(row=9, column=1, padx=3, pady=3, ipadx=3, ipady=3)

b7 = tk.Button(window, text="SAVE TO DATABASE", width=18, bg="#32CD32", command=save_to_database, font=('impack', 12, 'bold'))
b7.grid(row=9, column=4, padx=3, pady=3, ipadx=3, ipady=3) 

b8 = tk.Button(window, text="RESET", width=15, bg="#FF7F00", command=reset_inputs, font=('impack', 12, 'bold'))
b8.grid(row=9, column=2, padx=3, pady=3, ipadx=3, ipady=3) 

window.mainloop()