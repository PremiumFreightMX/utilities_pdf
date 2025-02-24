import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pikepdf
from pdf2image import convert_from_path

# Configuración de niveles de compresión
compression_levels = {
    "Alta": 250,  # Menos compresión (mejor calidad)
    "Media": 150,  # Compresión intermedia
    "Baja": 100     # Más compresión (máxima reducción)
}

# Ruta del logo (debe estar en la misma carpeta que el script)
LOGO_PATH = "logo.png"

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
root.geometry("400x350")
root.resizable(False, False)

# Cargar y mostrar el logo
if os.path.exists(LOGO_PATH):
    img = Image.open(LOGO_PATH)
    img = img.resize((150, 100), Image.Resampling.LANCZOS)  # Ajusta el tamaño del logo
    logo = ImageTk.PhotoImage(img)
    logo_label = tk.Label(root, image=logo)
    logo_label.pack(pady=10)  # Agregar espacio entre el logo y los botones

# Etiqueta de bienvenida
label = tk.Label(root, text="Selecciona un nivel de compresión", font=("Arial", 12))
label.pack(pady=10)

# Botones de nivel de compresión
btn_high = tk.Button(root, text="Calidad Alta (Menos compresión)", command=lambda: compress_pdf(compression_levels["Alta"]),
                     font=("Arial", 10), bg="lightgreen", width=30)
btn_high.pack(pady=5)

btn_medium = tk.Button(root, text="Calidad Media (Compresión equilibrada)", command=lambda: compress_pdf(compression_levels["Media"]),
                       font=("Arial", 10), bg="yellow", width=30)
btn_medium.pack(pady=5)

btn_low = tk.Button(root, text="Calidad Baja (Máxima compresión)", command=lambda: compress_pdf(compression_levels["Baja"]),
                    font=("Arial", 10), bg="red", width=30)
btn_low.pack(pady=5)

# Etiqueta del autor
author_label = tk.Label(root, text="Desarrollado por [Ing. Edwin Chavez - Dept. sistemas]", font=("Arial", 10, "italic"), fg="gray")
author_label.pack(side="bottom", pady=10)

# Ejecutar la interfaz
root.mainloop()
