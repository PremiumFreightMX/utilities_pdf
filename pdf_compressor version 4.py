import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from pdf2image import convert_from_path

# Configuración de niveles de compresión (DPI)
compression_levels = {
    "Alta": 200,  # Menos compresión (mejor calidad)
    "Media": 130,  # Compresión intermedia
    "Baja": 90     # Más compresión (máxima reducción)
}

# Ruta del logo (debe estar en la misma carpeta que el script)
LOGO_PATH = "logo.png"

def compress_pdf(dpi):
    """Función que maneja la compresión en un hilo separado"""
    def run_compression():
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
            progress_bar["value"] = 10  # Inicia la barra de progreso
            root.update_idletasks()

            # Convertir PDF a imágenes
            images = convert_from_path(input_path, dpi=dpi)

            progress_bar["value"] = 50  # Mitad del proceso
            root.update_idletasks()

            # Guardar imágenes comprimidas como PDF
            images[0].save(output_path, save_all=True, append_images=images[1:], quality=70)

            progress_bar["value"] = 100  # Finaliza
            root.update_idletasks()

            messagebox.showinfo("Éxito", f"PDF comprimido guardado en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            progress_bar["value"] = 0  # Reinicia la barra

    # Crear un hilo para ejecutar la compresión sin bloquear la interfaz
    threading.Thread(target=run_compression, daemon=True).start()

# Crear la ventana principal
root = tk.Tk()
root.title("Compresor de PDF")
root.geometry("400x380")
root.resizable(False, False)

# Cargar y mostrar el logo
if os.path.exists(LOGO_PATH):
    img = Image.open(LOGO_PATH)
    img = img.resize((150, 100), Image.Resampling.LANCZOS)
    logo = ImageTk.PhotoImage(img)
    logo_label = tk.Label(root, image=logo)
    logo_label.pack(pady=10)

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

# Barra de progreso
progress_bar = ttk.Progressbar(root, length=300, mode="determinate")
progress_bar.pack(pady=15)

# Etiqueta del autor
author_label = tk.Label(root, text="Desarrollado por [Ing. Edwin Chavez - Dept. sistemas]", font=("Arial", 10, "italic"), fg="gray")
author_label.pack(side="bottom", pady=10)

# Ejecutar la interfaz
root.mainloop()
