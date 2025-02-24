import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pikepdf
from pdf2image import convert_from_path
from PIL import Image

# Configuración de niveles de compresión (resolución en DPI)
compression_levels = {
    "Alta": 200,   # Menos compresión (mejor calidad)
    "Media": 100,  # Compresión intermedia
    "Baja": 72     # Más compresión (máxima reducción)
}

def compress_pdf(dpi):
    input_path = filedialog.askopenfilename(title="Selecciona un archivo PDF", filetypes=[("Archivos PDF", "*.pdf")])
    if not input_path:
        messagebox.showerror("Error", "No seleccionaste ningún archivo.")
        return
    
    output_path = filedialog.asksaveasfilename(title="Guardar archivo comprimido", defaultextension=".pdf",
                                               filetypes=[("Archivos PDF", "*.pdf")])
    if not output_path:
        messagebox.showerror("Error", "No especificaste una ruta de salida.")
        return

    try:
        # Convertir PDF a imágenes
        images = convert_from_path(input_path, dpi=dpi)
        
        # Guardar imágenes comprimidas como PDF
        images[0].save(output_path, save_all=True, append_images=images[1:], quality=70)

        messagebox.showinfo("Éxito", f"PDF comprimido guardado en:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Crear la ventana principal
root = tk.Tk()
root.title("Compresor de PDF")
root.geometry("400x250")
root.resizable(False, False)

# Etiqueta de bienvenida
label = tk.Label(root, text="Selecciona un nivel de compresión", font=("Arial", 12))
label.pack(pady=20)

# Botones de nivel de compresión
btn_high = tk.Button(root, text="Alta (Menos compresión)", command=lambda: compress_pdf(compression_levels["Alta"]),
                     font=("Arial", 10), bg="lightgreen", width=25)
btn_high.pack(pady=5)

btn_medium = tk.Button(root, text="Media (Compresión equilibrada)", command=lambda: compress_pdf(compression_levels["Media"]),
                       font=("Arial", 10), bg="yellow", width=25)
btn_medium.pack(pady=5)

btn_low = tk.Button(root, text="Baja (Máxima compresión)", command=lambda: compress_pdf(compression_levels["Baja"]),
                    font=("Arial", 10), bg="red", width=25)
btn_low.pack(pady=5)

# Ejecutar la interfaz
root.mainloop()
