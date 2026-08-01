import tkinter as tk
from tkinter import ttk
import win32print

def open_printer_selection(update_printer_callback):
    def get_printers():
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        return [printer[2] for printer in printers]

    def select_printer():
        printer = selected_printer.get()
        if printer and printer != "Seleccionar impresora":
            update_printer_callback(printer)  # Llama al callback con la impresora seleccionada
            root.destroy()  # Cierra la ventana de selección de impresoras
        elif printer == "Desactivar impresora":
            update_printer_callback("desactivada")  # Llama al callback con "desactivada"
            root.destroy()  # Cierra la ventana de selección de impresoras
        else:
            pass 

    root = tk.Tk()
    root.title("Seleccionar Impresora")

    root.attributes("-topmost", True)
    root.focus_force() 


    window_width = 400
    window_height = 200
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    label = tk.Label(root, text="Seleccione una impresora de la lista:", font=("Helvetica", 14, "bold"))
    label.pack(pady=10)

    printer_list = get_printers()
    printer_list.append("Desactivar impresora")  # Añadir opción para desactivar
    selected_printer = tk.StringVar(value="Seleccionar impresora")
    printer_combobox = ttk.Combobox(root, textvariable=selected_printer, values=printer_list, state='readonly', font=("Helvetica", 12))
    printer_combobox.pack(pady=10)

    select_button = tk.Button(root, text="Seleccionar", command=select_printer, font=("Helvetica", 12))
    select_button.pack(pady=10)

    root.mainloop()
