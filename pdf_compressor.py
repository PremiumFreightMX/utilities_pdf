import os
import threading
import tkinter as tk
import hashlib
from tkinter import filedialog, messagebox, ttk, simpledialog
from PIL import Image, ImageTk
from pdf2image import convert_from_path
from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Configuración de niveles de compresión (DPI)
compression_levels = {
    "Alta": 180,  # Menos compresión (mejor calidad)
    "Media": 120,  # Compresión intermedia
    "Baja": 80     # Más compresión (máxima reducción)
}

# Ruta del logo
LOGO_PATH = "logo.png"
MARKER_TEXT = "PDF_COMPRESSED_BY_TOOL"

# Función para verificar si el PDF ya fue comprimido
def is_pdf_compressed(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        return any(MARKER_TEXT in (meta or "") for meta in reader.metadata.values())
    except Exception:
        return False

# Nueva función para convertir imágenes en PDF y agregar las páginas correctamente
def images_to_pdf(images, output_path):
    """Convierte imágenes a un archivo PDF."""
    writer = PdfWriter()
    
    for img in images:
        temp_pdf_path = "temp_page.pdf"
        img.save(temp_pdf_path, "PDF", resolution=100)  # Se guarda temporalmente como PDF
        reader = PdfReader(temp_pdf_path)
        writer.add_page(reader.pages[0])  # Se añade la página correctamente

    # Agregar metadatos de compresión
    writer.add_metadata({"/Title": MARKER_TEXT})
    
    with open(output_path, "wb") as out_file:
        writer.write(out_file)

    os.remove(temp_pdf_path)  # Eliminar archivo temporal

# Función para comprimir PDFs
def compress_pdf(dpi):
    def run_compression():
        input_path = filedialog.askopenfilename(title="Selecciona un archivo PDF", filetypes=[("Archivos PDF", "*.pdf")])
        if not input_path:
            messagebox.showerror("Error", "No seleccionaste ningún archivo.")
            return

        if is_pdf_compressed(input_path):
            messagebox.showwarning("Advertencia", "Este archivo ya ha sido comprimido y no se puede volver a procesar.")
            return

        output_path = filedialog.asksaveasfilename(title="Guardar archivo comprimido", defaultextension=".pdf",
                                                   filetypes=[("Archivos PDF", "*.pdf")])
        if not output_path:
            messagebox.showerror("Error", "No especificaste una ruta de salida.")
            return

        try:
            progress_bar["value"] = 10
            root.update_idletasks()

            images = convert_from_path(input_path, dpi=dpi)  # Convertir PDF en imágenes

            progress_bar["value"] = 50
            root.update_idletasks()

            # Llamar a la función corregida que genera un PDF desde imágenes
            images_to_pdf(images, output_path)

            progress_bar["value"] = 100
            root.update_idletasks()

            messagebox.showinfo("Éxito", f"PDF comprimido guardado en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            progress_bar["value"] = 0

    threading.Thread(target=run_compression, daemon=True).start()

# Función para unir múltiples PDFs
def merge_pdfs():
    def run_merge():
        files = filedialog.askopenfilenames(title="Selecciona los archivos PDF", filetypes=[("Archivos PDF", "*.pdf")])
        if not files:
            messagebox.showerror("Error", "No seleccionaste archivos.")
            return

# Verificar si los archivos ya fueron comprimidos
        compressed_files = [file for file in files if is_pdf_compressed(file)]
        if compressed_files:
            messagebox.showerror("Error", "No puedes unir archivos que ya han sido comprimidos.\n\n"
                                          "Orden correcto: UNIR → COMPRIMIR → PROTEGER.")
            return

        output_path = filedialog.asksaveasfilename(title="Guardar PDF combinado", defaultextension=".pdf",
                                                   filetypes=[("Archivos PDF", "*.pdf")])
        if not output_path:
            messagebox.showerror("Error", "No especificaste una ruta de salida.")
            return

        try:
            progress_bar["value"] = 10
            root.update_idletasks()

            writer = PdfWriter()
            for file in files:
                reader = PdfReader(file)
                for page in reader.pages:
                    writer.add_page(page)

            progress_bar["value"] = 50
            root.update_idletasks()

            with open(output_path, "wb") as out_file:
                writer.write(out_file)

            progress_bar["value"] = 100
            root.update_idletasks()

            messagebox.showinfo("Éxito", f"PDF combinado guardado en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            progress_bar["value"] = 0

    threading.Thread(target=run_merge, daemon=True).start()

# Función para proteger un PDF con contraseña
def protect_pdf():
    def run_protection(input_path, output_path, password):
        try:
            progress_bar["value"] = 10  
            root.update_idletasks()

            reader = PdfReader(input_path)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            writer.encrypt(user_password=password, owner_password=None, permissions_flag=0)

            progress_bar["value"] = 50  
            root.update_idletasks()

            with open(output_path, "wb") as out_file:
                writer.write(out_file)

            progress_bar["value"] = 100  
            root.update_idletasks()

            messagebox.showinfo("Éxito", f"PDF protegido guardado en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            progress_bar["value"] = 0  

    def ask_password():
        input_path = filedialog.askopenfilename(title="Selecciona un archivo PDF", filetypes=[("Archivos PDF", "*.pdf")])
        if not input_path:
            return

        output_path = filedialog.asksaveasfilename(title="Guardar PDF protegido", defaultextension=".pdf",
                                                   filetypes=[("Archivos PDF", "*.pdf")])
        if not output_path:
            return

        password = simpledialog.askstring("Contraseña", "Introduce la contraseña para proteger el PDF:", show="*")
        if not password:
            messagebox.showerror("Error", "Debes ingresar una contraseña.")
            return

        threading.Thread(target=run_protection, args=(input_path, output_path, password), daemon=True).start()

    root.after(100, ask_password)

# Interfaz gráfica con Tkinter
root = tk.Tk()
root.title("Compresor y Unificador de PDFs")
root.geometry("470x500")
root.resizable(False, False)

# Cargar logo
if os.path.exists(LOGO_PATH):
    img = Image.open(LOGO_PATH)
    img = img.resize((170, 120), Image.Resampling.LANCZOS)
    logo = ImageTk.PhotoImage(img)
    logo_label = tk.Label(root, image=logo)
    logo_label.pack(pady=10)

# Botones
tk.Label(root, text="Selecciona una opción", font=("Arial", 12)).pack(pady=10)
tk.Button(root, text="Calidad Alta (180 DPI)", command=lambda: compress_pdf(compression_levels["Alta"]), bg="lightgreen", width=35).pack(pady=5)
tk.Button(root, text="Calidad Media (120 DPI)", command=lambda: compress_pdf(compression_levels["Media"]), bg="yellow", width=35).pack(pady=5)
tk.Button(root, text="Calidad Baja (80 DPI)", command=lambda: compress_pdf(compression_levels["Baja"]), bg="red", width=35).pack(pady=5)
tk.Button(root, text="Unir Múltiples PDFs", command=merge_pdfs, bg="blue", fg="white", width=35).pack(pady=10)
tk.Button(root, text="Proteger PDF con Contraseña", command=protect_pdf, bg="purple", fg="white", width=35).pack(pady=15)

# Barra de progreso
progress_bar = ttk.Progressbar(root, length=300, mode="determinate")
progress_bar.pack(pady=15)

# Etiqueta del autor
author_label = tk.Label(root, text="Desarrollado por [Ing. Edwin Chavez - Dept. sistemas]", font=("Arial", 10, "italic"), fg="gray")
author_label.pack(side="bottom", pady=10)

root.mainloop()
