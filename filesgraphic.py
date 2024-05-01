import os
import shutil
import re
import csv
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import sys

def extract_info(filename):
    match = re.match(r'^(.*?)\s(\d{2}-\d{2})\.(pdf|jpg|jpeg|png)$', filename, re.IGNORECASE)
    if match:
        return match.group(1), match.group(2), match.group(3)
    else:
        return None, None, None

def process_files(source_dir, destination_dir, progress_bar, console_text):
    moved_count = 0
    total_files = sum(1 for _ in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, _)))
    progress_bar["maximum"] = total_files
    
    patients_dir = os.path.join(destination_dir, "Pacientes")
    
    if not os.path.exists(patients_dir):
        os.makedirs(patients_dir)
    
    for filename in os.listdir(source_dir):
        if os.path.isfile(os.path.join(source_dir, filename)):
            patient_name, date, extension = extract_info(filename)
            
            if patient_name and date and extension:
                source_path = os.path.join(source_dir, filename)
                day_dir = os.path.join(destination_dir, date)
                if not os.path.exists(day_dir):
                    os.makedirs(day_dir)
                
                patient_dir = os.path.join(patients_dir, patient_name)
                if not os.path.exists(patient_dir):
                    os.makedirs(patient_dir)
                
                shutil.copy(source_path, os.path.join(day_dir, filename))
                
                shutil.copy(source_path, os.path.join(patient_dir, filename))
                
                moved_count += 1
                
                csv_file = os.path.join(data_dir, "registros.csv")
                file_exists = os.path.exists(csv_file)
                
                with open(csv_file, mode='a', newline='') as file:
                    fieldnames = ['nombre_archivo', 'ruta_fecha', 'ruta_pacientes', 'nombre_paciente', 'fecha_servicio']
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    
                    if not file_exists:
                        writer.writeheader()
                    
                    writer.writerow({
                        'nombre_archivo': filename,
                        'ruta_fecha': os.path.join(day_dir, filename),
                        'ruta_pacientes': os.path.join(patient_dir, filename),
                        'nombre_paciente': patient_name,
                        'fecha_servicio': date
                    })
                
                console_text.insert(tk.END, f"{filename} movido a {day_dir}\n")
                
                os.remove(source_path)
                console_text.insert(tk.END, f"{filename} eliminado del directorio original\n")
                
                progress_bar["value"] += 1
                root.update_idletasks()
    
    return moved_count

def select_source_dir():
    source_dir = filedialog.askdirectory()
    source_entry.delete(0, tk.END)
    source_entry.insert(0, source_dir)

def select_destination_dir():
    destination_dir = filedialog.askdirectory()
    destination_entry.delete(0, tk.END)
    destination_entry.insert(0, destination_dir)

def relocate_files():
    source_dir = source_entry.get()
    destination_dir = destination_entry.get()
    
    if not source_dir or not destination_dir:
        messagebox.showerror("Error", "Por favor seleccione tanto la carpeta de origen como la carpeta de destino.")
        return
    
    moved_count = process_files(source_dir, destination_dir, progress_bar, console_text)
    messagebox.showinfo("Proceso completado", f"Se movieron {moved_count} archivos.")

if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(__file__)

data_dir = os.path.join(script_dir, "data")

if not os.path.exists(data_dir):
    os.makedirs(data_dir)

root = tk.Tk()
root.title("Reubicación de archivos")

source_frame = tk.Frame(root)
source_frame.pack(pady=10)

source_label = tk.Label(source_frame, text="Carpeta de origen:")
source_label.grid(row=0, column=0)

source_entry = tk.Entry(source_frame, width=50)
source_entry.grid(row=0, column=1)

source_button = tk.Button(source_frame, text="Seleccionar carpeta", command=select_source_dir)
source_button.grid(row=0, column=2)

destination_frame = tk.Frame(root)
destination_frame.pack(pady=10)

destination_label = tk.Label(destination_frame, text="Carpeta de destino:")
destination_label.grid(row=0, column=0)

destination_entry = tk.Entry(destination_frame, width=50)
destination_entry.grid(row=0, column=1)

destination_button = tk.Button(destination_frame, text="Seleccionar carpeta", command=select_destination_dir)
destination_button.grid(row=0, column=2)

relocate_button = tk.Button(root, text="Reubicar archivos", command=relocate_files)
relocate_button.pack(pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

console_text = tk.Text(root, height=10, width=50)
console_text.pack(pady=10)

root.mainloop()
