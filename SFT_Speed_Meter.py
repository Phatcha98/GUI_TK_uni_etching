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
window.option_add('*font','impack 20') 
window.title("SFT Speed Meter")
window.geometry("850x310")
# รับขนาดหน้าจอจริงของเครื่องคอมพิวเตอร์

# screen_width = window.winfo_screenwidth()
# screen_height = window.winfo_screenheight()
# # Configure rows and columns for automatic resizing
# for i in range(13):
#     window.grid_rowconfigure(i, weight=1)
# for i in range(9):  
#     window.grid_columnconfigure(i, weight=1)

# # กำหนดขนาดหน้าต่าง GUI เท่ากับขนาดหน้าจอ
# window.geometry(f"{screen_width}x{screen_height}")

options = tk.StringVar(window)
options.set("Process") # default value

l1 = tk.Label(window,  text='Process:', width=10)  
l1.grid(row=0,column=2, sticky='E') 

om1 =tk.OptionMenu(window, options, "SCHS", "ELGOP", "SGOP", "GOP", "RMI")
om1.config(bg="#FFCC33")
om1.grid(row=0,column=3, sticky='W') 

Label34 =tk.Label(window)
Label34.grid(row=0, column=1)

label_machine_no = tk.Label(window, text="Machine no:")
label_machine_no.grid(row=1, column=2, sticky='E')
entry_machine_no = tk.Entry(window, width=30)
entry_machine_no.grid(row=1, column=3, sticky='WE') 

label_target= tk.Label(window, text="Target :")
label_target.grid(row=2, column=2, sticky='E')
entry_target = tk.Entry(window, width=30)
entry_target.grid(row=2, column=3, sticky='WE') 

label_Uniformity= tk.Label(window, text="Result :")
label_Uniformity.grid(row=3, column=2, sticky='E')
entry_result = tk.Entry(window, width=30)
entry_result.grid(row=3, column=3, sticky='WE') 

# def calculate_uniformity():
#     # คำนวณค่า MAX, MIN, และ AVG จากข้อมูลในตาราง
#     data = [float(row[5]) for row in data_rows]
#     if data:
#         max_value = max(data)
#         min_value = min(data)
#         avg_value = sum(data) / len(data)
#         uniformity_percent = (1 - ((max_value - min_value) / (2 * avg_value))) * 100

#         # แสดงผลลัพธ์ใน GUI
#         uniformity_label.config(text="{:.2f}".format(uniformity_percent))
#         sh_result(uniformity_percent)

# uniformity_label = tk.Label(window, text="", width=20)
# uniformity_label.grid(row=3, column=3, sticky='W')

def sh_result(uniformity_percent):
    if uniformity_percent >= 90:
        result_text1 = "PASS"
        result_color1 = "green"
    else:
        result_text1 = "FAIL"
        result_color1 = "red"
    result_label2.config(text=result_text1, fg=result_color1)
result_label2 = tk.Label(window, text="") 
result_label2.grid(row=3, column=4, sticky='WE')


ym = time.strftime("%Y/%m/%d")
class Clock:
    def __init__(self):
        self.time1 = ''
        self.time2 = time.strftime('%H:%M:%S')
        self.mFrame = Frame()
        self.mFrame.grid(row=0,column=4,sticky='E') 

        self.watch = Label(self.mFrame, text=self.time2)
        self.watch.pack()

        self.changeLabel() 

    def changeLabel(self): 
        self.time2 = time.strftime('%H:%M:%S')
        self.watch.configure(text=self.time2)
        self.mFrame.after(200, self.changeLabel) 

C=Clock()
Label(window,text=ym).grid(row=1, column=4,sticky='E') 

def save_to_database():
    global data_rows
    # uniformity_result =  uniformity_label.cget("text")
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
                (no, measure_time, machine_no, before, after, er, create_at, process, uniformity_judgement)
            )
        connection.commit()
        connection.close()
        messagebox.showinfo("Success", "Saved to databases table eworking_calling_elgop_etchingrate_uniformity.")

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numeric values for Weight Before and Weight After.")
    except Exception as e:
        print("Error:", e)


    # uniformity_label.config(text=" ")
    # result_label1.config(text=" ")
    # result_label.config(text=" ")
    # result_label2.config(text=" ")
    # om1.configure(text="Process", bg='#FFCC33')
    for widget in window.winfo_children():
            if isinstance(widget, Entry):  
                widget.delete(0,'end') 
                widget.insert(0,'') 
    pass

# Function to clear all input fields
def reset_inputs():
   pass


b7 = tk.Button(window, text="SAVE", width=15, bg="#32CD32", command=save_to_database, font=('impack', 18, 'bold'))
# b7.grid(row=9, column=4, padx=3, pady=3, ipadx=3, ipady=3) 
b7.place(x=150, y=200)

b8 = tk.Button(window, text="RESET", width=15, bg="#FF7F00", command=reset_inputs, font=('impack', 18, 'bold'))
# b8.grid(row=9, column=2, padx=3, pady=3, ipadx=3, ipady=3) 
b8.place(x=480, y=200)

window.mainloop()