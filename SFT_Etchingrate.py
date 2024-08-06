import tkinter as tk
from tkinter import font
import psycopg2
from datetime import datetime
from tkinter import *
import tkinter.messagebox as messagebox
from datetime import datetime, timedelta
import serial
from datetime import datetime
import time

window = tk.Tk()
window.option_add('*font','impack 15 bold') 
window.title("Eworking Calling Elgop Etchingrate")
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
# Configure rows and columns for automatic resizing
for i in range(20):
    window.grid_rowconfigure(i, weight=1)
for i in range(10):  
    window.grid_columnconfigure(i, weight=1)

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
        calculate_differences_upper()
        calculate_differences_lower()
    except serial.SerialException as e:
        messagebox.showerror("Serial Port Error", str(e))

def update_measurement():
    global measurement_data, measurement, is_measurement_ended, is_measurement_started
    if is_measurement_started and not is_measurement_ended:
        measurement_data = ser.readline()
        if measurement_data:
            measurement = float(measurement_data.decode())
            measurement_gui = "{:.3f}".format(measurement)
            for entry in [entry_fields1_upper, entry_fields1_lower, entry_fields2_upper, entry_fields2_lower]:
                entry.delete(0, tk.END)
                entry.insert(tk.END, measurement_gui)
            
            calculate_differences_upper()
            calculate_differences_lower()

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
            if selected_entry in entry_fields1_upper:
                entry_index = entry_fields1_upper.index(selected_entry)
                if entry_index < len(entry_fields1_upper):
                    entry_fields1_upper[entry_index].set(measurement_gui)
            elif selected_entry in entry_fields2_upper:
                entry_index = entry_fields2_upper.index(selected_entry)
                if entry_index < len(entry_fields2_upper):
                    entry_fields2_upper[entry_index].set(measurement_gui)
            elif selected_entry in entry_fields1_lower:
                entry_index = entry_fields1_lower.index(selected_entry)
                if entry_index < len(entry_fields1_lower):
                    entry_fields1_lower[entry_index].set(measurement_gui)
            elif selected_entry in entry_fields2_lower:
                entry_index = entry_fields2_lower.index(selected_entry)
                if entry_index < len(entry_fields2_lower):
                    entry_fields2_lower[entry_index].set(measurement_gui)

def handle_entry_focus_up(event=None):
    global selected_entry
    selected_entry = event.widget
    handle_measurement() 


def handle_entry_focus_lo(event=None):
    global selected_entry
    selected_entry = event.widget
    handle_measurement() 


label_machine_no = tk.Label(window, text="Machine no:")
label_machine_no.grid(row=0, column=2, sticky='E')
entry_machine_no = tk.Entry(window, width=25)
entry_machine_no.grid(row=0, column=3, sticky='WE') 

label_process = tk.Label(window, text="Process:")
label_process.grid(row=2, column=2, sticky='E')
entry_process = tk.Label(window, width=25)
entry_process.grid(row=2, column=3, sticky='WE') 

label_target = tk.Label(window, text="Target:")
label_target.grid(row=3, column=2, sticky='E')
entry_target = tk.Label(window, width=25)
entry_target.grid(row=3, column=3, sticky='WE') 

label_upper_limit = tk.Label(window, text="Upper limit:")
label_upper_limit.grid(row=4, column=2, sticky='E')
entry_upper_limit = tk.Label(window, width=25)
entry_upper_limit.grid(row=4, column=3, sticky='WE') 

label_lower_limit = tk.Label(window, text="Lower limit:")
label_lower_limit.grid(row=5, column=2, sticky='E')
entry_lower_limit = tk.Label(window, width=25)
entry_lower_limit.grid(row=5, column=3, sticky='WE') 
    
Label(window,text='Scan QR:').grid(row=1, column=2, sticky= E)
# input variable type
sc_qr=StringVar()
# automove cursor by if input > xx => focus next widget
def input_scqr(event):
    input_text = sc_qr.get()
    map_values = input_text.split(";")
    if len(map_values) >= 4: 
        entry_process.configure(text=map_values[0])
        entry_target.configure(text=map_values[1])
        entry_upper_limit.configure(text=map_values[2])
        entry_lower_limit.configure(text=map_values[3])

sc_qr=Entry(window,textvariable=sc_qr)
sc_qr.grid(row=1, column=3, sticky='WE')
sc_qr.bind('<Key>',input_scqr)

#_______________________________________________________________________________________________________________

label_machine_no = tk.Label(window, text="Weight (μm) Upper", font=('impack', 15, 'bold'), bg="#9999FF", width=15)
label_machine_no.grid(row=7, column=2, sticky='WE')

label_weight_before_upper = tk.Label(window, text="Weight before upper:")
label_weight_before_upper.grid(row=8, column=1, sticky='E')
entry_fields1_upper = tk.Entry(window, width=30)
entry_fields1_upper.grid(row=8, column=2, sticky='WE')
entry_fields1_upper.bind("<FocusIn>", handle_entry_focus_up)

label_weight_after_upper = tk.Label(window, text="Weight after upper:")
label_weight_after_upper.grid(row=9, column=1, sticky='E')
entry_fields2_upper = tk.Entry(window, width=30)
entry_fields2_upper.grid(row=9, column=2, sticky='WE')
entry_fields2_upper.bind("<FocusIn>", handle_entry_focus_up)

label_etching_rate_upper = tk.Label(window, text="Etching rate upper:")
label_etching_rate_upper.grid(row=10, column=1, sticky='E')  

calculate_button_clicked_upper = False
result_labels_upper = []
def calculate_button_click_upper():
    global calculate_button_clicked_upper
    calculate_button_clicked_upper = True
    calculate_differences_upper() 
    show_result_upper()

def calculate_differences_upper():
    try:
        entry_value1_upper = float(entry_fields1_upper.get())
        entry_value2_upper = float(entry_fields2_upper.get())

        if entry_value1_upper and entry_value2_upper:
            result_upper = ((entry_value1_upper - entry_value2_upper) / 8.93) * 100
            result_label_upper.config(text="{:.3f}".format(result_upper))
            return result_upper 
        else:
            result_label_upper.config(text="")
            return None  

    except ValueError as e:
        print("Error:", e) 
        result_label_upper.config(text="")
        return None
result_label_upper = tk.Label(window, text="", width=30, bg="#FFFF99")
result_label_upper.grid(row=10, column=2, sticky='WE')
window.bind("<ButtonRelease-1>", lambda event: calculate_differences_upper())

def show_result_upper():
    difference_upper = calculate_differences_upper()
    print("Difference Upper:", difference_upper)
    if difference_upper is not None:
        if difference_upper < 0.6 or difference_upper > 0.8:
            result_text = "FAIL"
            result_color = "red"
        elif difference_upper < 0.63 or difference_upper > 0.74:
            result_text = "WARNING"
            result_color = "orange"
        else:
            result_text = "PASS"
            result_color = "green"
        result_label1_upper.config(text=result_text, fg=result_color)

result_label1_upper = tk.Label(window, text="", width=10) 
result_label1_upper.grid(row=10, column=3, sticky='W')
result_label_upper.bind("<ButtonRelease-1>", lambda event: show_result_upper())


# ____________________________________________________________________________________

label_machine_no = tk.Label(window, text="Weight (μm) Lower", font=('impack', 15, 'bold'), bg="#9999FF", width=15)
label_machine_no.grid(row=7, column=5, sticky='WE')

label_weight_before_lower = tk.Label(window, text="Weight before lower:")
label_weight_before_lower.grid(row=8, column=4, sticky='E')
entry_fields1_lower = tk.Entry(window, textvariable=label_weight_before_lower, width=30)
entry_fields1_lower.grid(row=8, column=5, sticky='WE')
entry_fields1_lower.bind("<FocusIn>", handle_entry_focus_lo)

label_weight_after_lower = tk.Label(window, text="Weight after lower:")
label_weight_after_lower.grid(row=9, column=4, sticky='E')
entry_fields2_lower = tk.Entry(window, textvariable=label_weight_after_lower, width=30)
entry_fields2_lower.grid(row=9, column=5, sticky='WE')
entry_fields2_lower.bind("<FocusIn>", handle_entry_focus_lo)

label_etching_rate_lower = tk.Label(window, text="Etching rate lower:")
label_etching_rate_lower.grid(row=10, column=4, sticky='E')  


calculate_button_clicked_lower = False
result_labels_lower = []
def calculate_button_click_lower():
    global calculate_button_clicked_lower
    calculate_button_clicked_lower = True
    calculate_differences_lower() 
    show_result_lower()

def calculate_differences_lower():
    try:
        entry_value1_lower = float(entry_fields1_lower.get())
        entry_value11_lower = float(entry_fields2_lower.get())
        if entry_value1_lower and entry_value11_lower:
            result_lower = ((entry_value1_lower - entry_value11_lower) / 8.93) * 100
            result_label_lower.config(text="{:.3f}".format(result_lower))
            return result_lower 
        else:
            result_label_lower.config(text="")
            return None  

    except ValueError:
        result_label_lower.config(text="")
        return None  
result_label_lower = tk.Label(window, text="", width=30, bg="#FFFF99")
result_label_lower.grid(row=10, column=5, sticky='WE')
window.bind("<ButtonRelease-1>", lambda event: calculate_differences_lower())

def show_result_lower():
    difference_lower = calculate_differences_lower()
    if difference_lower is not None:
        if difference_lower < 0.6 or difference_lower > 0.8:
            result_text = "FAIL"
            result_color = "red"
        elif difference_lower < 0.63 or difference_lower > 0.74:
            result_text = "WARNING"
            result_color = "orange"
        else:
            result_text = "PASS"
            result_color = "green"
        result_label1_lower.config(text=result_text, fg=result_color)
result_label1_lower = tk.Label(window, text="", width=10) 
result_label1_lower.grid(row=10, column=6, sticky='E')
window.bind("<ButtonRelease-1>", lambda event: show_result_lower())


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

dt0 = None  # กำหนด dt0 เป็นค่าเริ่มต้นเป็น None
selected_entry = None

def handle_entry_focus_d(event):
    global dt0
    if event.widget == entry_fields1_upper:
        dt0 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if event.widget == entry_fields1_lower:
        dt0 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry_fields1_upper.bind("<FocusIn>", handle_entry_focus_d)
    entry_fields1_lower.bind("<FocusIn>", handle_entry_focus_d)

def save_to_database():
    global dt0
    if dt0 is None:
        dt0 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    before_upper = entry_fields1_upper.get()
    after_upper = entry_fields2_upper.get()

    before_lower = entry_fields1_lower.get()
    after_lower = entry_fields2_lower.get()
    machine_no = entry_machine_no.get()

    etching_rate_upper = calculate_differences_upper()
    etching_rate_lower = calculate_differences_lower()

    process = entry_process.cget("text")  
    upper_limit = entry_upper_limit.cget("text")
    lower_limit = entry_lower_limit.cget("text")
    target = entry_target.cget("text")

    if result_label1_upper.cget("text") == "PASS" and result_label1_lower.cget("text") == "PASS":
        er_judgment = "PASS"

    if result_label1_upper.cget("text") == "PASS" and result_label1_lower.cget("text") == "WARNING":
        er_judgment = "PASS"  

    if result_label1_upper.cget("text") == "WARNING" and result_label1_lower.cget("text") == "PASS":
        er_judgment = "PASS" 

    if result_label1_upper.cget("text") == "WARNING" and result_label1_lower.cget("text") == "WARNING":
        er_judgment = "PASS" 
          
    if result_label1_upper.cget("text") == "FAIL" and result_label1_lower.cget("text") == "PASS":
        er_judgment = "FAIL"

    if result_label1_upper.cget("text") == "PASS" and result_label1_lower.cget("text") == "FAIL":
        er_judgment = "FAIL"

    if result_label1_upper.cget("text") == "PASS" and (result_label1_lower.cget("text") is None or result_label1_lower.cget("text") == '' or result_label1_lower.cget("text") == ' '):
        er_judgment = "PASS"

    elif result_label1_upper.cget("text") == "FAIL" and (result_label1_lower.cget("text") is None or result_label1_lower.cget("text") == ''or result_label1_lower.cget("text") == ' '):
        er_judgment = "FAIL"

    try:
        before_upper = float(before_upper) if before_upper else None
        after_upper = float(after_upper) if after_upper else None
        etching_rate_upper = ((before_upper - after_upper) / 8.93) * 100 if before_upper and after_upper else None

        before_lower = float(before_lower) if before_lower else None
        after_lower = float(after_lower) if after_lower else None
        etching_rate_lower = ((before_lower - after_lower) / 8.93) * 100 if before_lower and after_lower else None

        connection = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="jumanji",
            database="smart_factory_palm"
        )
        cursor = connection.cursor()
        dt1 = datetime.now()
        next_measure_time = dt1 + timedelta(hours=2)
        # Insert data into the table with the current timestamp
        cursor.execute(
            "INSERT INTO public.\"eworking_calling_elgop_chs_etchingrate\""
            "(measure_time, mc_no, before_upper, after_upper, er_upper, create_at, process, "
            "upper_limit, lower_limit, \"target\", next_measure_time, er_judmemt, "
            "before_lower, after_lower, er_lower)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (dt0, machine_no, before_upper, after_upper, etching_rate_upper, dt1, process, 
            upper_limit, lower_limit, target, next_measure_time, er_judgment, 
            before_lower, after_lower, etching_rate_lower)
        )

        connection.commit()
        connection.close()
        messagebox.showinfo("Success", "Saved to databases table eworking_calling_elgop_chs_etchingrate.")

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numeric values for Weight Before and Weight After.")
    except Exception as e:
        print("Error:", e)

    dt0 = None
    selected_entry = None
    result_label1_upper.config(text=" ") 
    result_label1_lower.config(text=" ")
    entry_fields1_upper.config(text=" ")
    result_label_upper.config(text=" ")
    result_label_lower.config(text=" ")
    entry_process.config(text=" ")
    entry_target.config(text=" ")
    entry_upper_limit.config(text=" ")
    entry_lower_limit.config(text=" ")
    for widget in window.winfo_children():
            if isinstance(widget,Entry):  
                widget.delete(0,'end') 
                widget.insert(0,'') 
    pass

# Function to clear all input fields
def reset_inputs():
    result_label1_upper.config(text=" ") 
    result_label1_lower.config(text=" ") 
    entry_fields1_upper.config(text=" ")
    result_label_upper.config(text=" ")
    result_label_lower.config(text=" ")
    entry_process.config(text=" ")
    entry_target.config(text=" ")
    entry_upper_limit.config(text=" ")
    entry_lower_limit.config(text=" ")
    for widget in window.winfo_children():
            if isinstance(widget,Entry):  
                widget.delete(0,'end') 
                widget.insert(0,'') 
    pass
# Buttons
b7 = tk.Button(window, text="SAVE", width=12, bg="#32CD32", command=save_to_database, font=('impack', 15, 'bold'))
b7.grid(row=14, column=2, padx=3, pady=3, ipadx=3, ipady=3, sticky='E') 

b8 = tk.Button(window, text="RESET", width=12, bg="#FF7F00", command=reset_inputs, font=('impack', 15, 'bold'))
b8.grid(row=14, column=4, padx=3, pady=3, ipadx=3, ipady=3) 

window.mainloop()