import os
import threading
import tkinter as tk
import hashlib
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from pdf2image import convert_from_path
from pypdf import PdfWriter, PdfReader

# Configuración de niveles de compresión (DPI)
compression_levels = {
    "Alta": 180,  # Menos compresión (mejor calidad)
    "Media": 120,  # Compresión intermedia
    "Baja": 80     # Más compresión (máxima reducción)
}

# Ruta del logo (debe estar en la misma carpeta que el script)
LOGO_PATH = "logo.png"
MARKER_TEXT = "PDF_COMPRESSED_BY_TOOL"

# Generar una firma oculta en los metadatos del pdf indicando que ya fue comprimido, bloqueando la operacion.
def calculate_pdf_hash(pdf_path):
    """Calcula un hash SHA256 del archivo PDF."""
    hasher = hashlib.sha256()
    with open(pdf_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def is_pdf_compressed(pdf_path):
    """Verifica si el PDF ya ha sido comprimido."""
    try:
        reader = PdfReader(pdf_path)
        return any(MARKER_TEXT in (meta or "") for meta in reader.metadata.values())
    except Exception:
        return False

def compress_pdf(dpi):
    def run_compression():
        input_path = filedialog.askopenfilename(title="Selecciona un archivo PDF", filetypes=[("Archivos PDF", "*.pdf")])
        if not input_path:
            messagebox.showerror("Error", "No seleccionaste ningún archivo.")
            return

        if is_pdf_compressed(input_path):
            messagebox.showwarning("Advertencia", "Este archivo ya ha sido comprimido y no se puede volver a procesar.")
            return

        output_path = filedialog.asksaveasfilename(title="Guardar archivo comprimido", defaultextension=".pdf", filetypes=[("Archivos PDF", "*.pdf")])
        if not output_path:
            messagebox.showerror("Error", "No especificaste una ruta de salida.")
            return

        try:
            progress_bar["value"] = 10
            root.update_idletasks()

            images = convert_from_path(input_path, dpi=dpi)

            progress_bar["value"] = 50
            root.update_idletasks()

            writer = PdfWriter()
            for img in images:
                writer.add_blank_page(width=img.width, height=img.height)
            
            writer.add_metadata({"/Title": MARKER_TEXT})
            with open(output_path, "wb") as out_file:
                writer.write(out_file)

            progress_bar["value"] = 100
            root.update_idletasks()

            messagebox.showinfo("Éxito", f"PDF comprimido guardado en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            progress_bar["value"] = 0

    threading.Thread(target=run_compression, daemon=True).start()

def merge_pdfs():
    """Función para unir múltiples archivos PDF en uno solo usando PdfWriter"""
    def run_merge():
        files = filedialog.askopenfilenames(title="Selecciona los archivos PDF", filetypes=[("Archivos PDF", "*.pdf")])
        if not files:
            messagebox.showerror("Error", "No seleccionaste archivos.")
            return
        
        output_path = filedialog.asksaveasfilename(title="Guardar PDF combinado", defaultextension=".pdf",
                                                   filetypes=[("Archivos PDF", "*.pdf")])
        if not output_path:
            messagebox.showerror("Error", "No especificaste una ruta de salida.")
            return

        try:
            progress_bar["value"] = 10  # Inicia la barra de progreso
            root.update_idletasks()

            writer = PdfWriter()
            for file in files:
                reader = PdfReader(file)
                for page in reader.pages:
                    writer.add_page(page)

            progress_bar["value"] = 50  # Mitad del proceso
            root.update_idletasks()

            with open(output_path, "wb") as out_file:
                writer.write(out_file)

            progress_bar["value"] = 100  # Finaliza
            root.update_idletasks()

            messagebox.showinfo("Éxito", f"PDF combinado guardado en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            progress_bar["value"] = 0  # Reinicia la barra

    # Crear un hilo para ejecutar la unión sin bloquear la interfaz
    threading.Thread(target=run_merge, daemon=True).start()

def protect_pdf():
    """Protege un PDF con contraseña para abrirlo e imprimirlo."""

    def run_protection(input_path, output_path, password):
        try:
            progress_bar["value"] = 10  
            root.update_idletasks()

            reader = PdfReader(input_path)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            # Configurar permisos para que requiera contraseña al abrir y al imprimir
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

        password = tk.simpledialog.askstring("Contraseña", "Introduce la contraseña para proteger el PDF:", show="*")
        if not password:
            messagebox.showerror("Error", "Debes ingresar una contraseña.")
            return

        threading.Thread(target=run_protection, args=(input_path, output_path, password), daemon=True).start()

    root.after(100, ask_password)

# Crear la ventana principal
root = tk.Tk()
root.title("Compresor y Unificador de PDFs")
root.geometry("400x480")
root.resizable(False, False)

# Cargar y mostrar el logo
if os.path.exists(LOGO_PATH):
    img = Image.open(LOGO_PATH)
    img = img.resize((150, 100), Image.Resampling.LANCZOS)
    logo = ImageTk.PhotoImage(img)
    logo_label = tk.Label(root, image=logo)
    logo_label.pack(pady=10)

# Etiqueta de bienvenida
label = tk.Label(root, text="Selecciona una opción", font=("Arial", 12))
label.pack(pady=10)

# Botones de nivel de compresión
btn_high = tk.Button(root, text="Calidad Alta 180 DPI (Menos compresión)", command=lambda: compress_pdf(compression_levels["Alta"]),
                     font=("Arial", 10), bg="lightgreen", width=35)
btn_high.pack(pady=5)

btn_medium = tk.Button(root, text="Calidad Media 120 DPI (Compresión equilibrada)", command=lambda: compress_pdf(compression_levels["Media"]),
                       font=("Arial", 10), bg="yellow", width=35)
btn_medium.pack(pady=5)

btn_low = tk.Button(root, text="Calidad Baja 80 DPI (Máxima compresión)", command=lambda: compress_pdf(compression_levels["Baja"]),
                    font=("Arial", 10), bg="red", width=35)
btn_low.pack(pady=5)

# Botón para unir PDFs
btn_merge = tk.Button(root, text="Unir Múltiples PDFs", command=merge_pdfs,
                      font=("Arial", 10), bg="blue", fg="white", width=35)
btn_merge.pack(pady=10)

# Botón para proteger PDFs
btn_protect = tk.Button(root, text="Proteger PDF con Contraseña", command=protect_pdf,
                        font=("Arial", 10), bg="purple", fg="white", width=35)
btn_protect.pack(pady=10)

# Barra de progreso
progress_bar = ttk.Progressbar(root, length=300, mode="determinate")
progress_bar.pack(pady=15)

# Etiqueta del autor
author_label = tk.Label(root, text="Desarrollado por [Ing. Edwin Chavez - Dept. sistemas]", font=("Arial", 10, "italic"), fg="gray")
author_label.pack(side="bottom", pady=10)

# Ejecutar la interfaz
root.mainloop()
