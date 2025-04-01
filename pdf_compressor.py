import os
import threading
import tkinter as tk
import hashlib
import subprocess
import platform
from tkinter import filedialog, messagebox, ttk, simpledialog
from PIL import Image, ImageTk
from pdf2image import convert_from_path
from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

# Configuración de niveles de compresión (DPI)
compression_levels = {
    "Alta": 180,
    "Media": 120,
    "Baja": 80
}

# Ruta del logo
LOGO_PATH = "logo.png"
MARKER_TEXT = "PDF_COMPRESSED_BY_TOOL"

# Verificar si el PDF ya fue comprimido
def is_pdf_compressed(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        metadata = reader.metadata
        title = metadata.get("/Title", "")
        return MARKER_TEXT in title
    except Exception:
        return False

# Detectar si el PDF es escaneado (solo imágenes)
def is_scanned_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            xobjects = page.resources.get("/XObject", {})
            if not xobjects:
                return False
        return True
    except Exception:
        return False

# Obtener el comando de Ghostscript según el sistema operativo
def get_gs_command():
    if platform.system() == "Windows":
        return "gswin64c"
    else:
        return "gs"

# Comprimir PDF con Ghostscript
def compress_pdf_with_ghostscript(input_path, output_path, quality="media"):
    quality_options = {
        "alta": "/ebook",
        "media": "/screen",
        "baja": "/screen"
    }
    gs_quality = quality_options.get(quality.lower(), "/screen")
    try:
        subprocess.run([
            get_gs_command(),
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={gs_quality}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_path}",
            input_path
        ], check=True)

        # Agregar marcador de compresión
        writer = PdfWriter()
        reader = PdfReader(output_path)
        for page in reader.pages:
            writer.add_page(page)
        writer.add_metadata({"/Title": MARKER_TEXT})
        with open(output_path, "wb") as f:
            writer.write(f)

        return True
    except subprocess.CalledProcessError as e:
        print("Ghostscript error:", e)
        return False
    except FileNotFoundError:
        messagebox.showerror("Error", "No se encontró Ghostscript. Asegúrate de que esté instalado y agregado al PATH.")
        return False

# Convertir imágenes a PDF (optimizado)
def images_to_pdf(images, output_path):
    temp_output = output_path + ".tmp"
    c = canvas.Canvas(temp_output, pagesize=letter)
    width, height = letter

    for img in images:
        img_width, img_height = img.size
        aspect = img_height / img_width

        if img_width > img_height:
            new_width = width
            new_height = width * aspect
        else:
            new_height = height
            new_width = height / aspect

        x = (width - new_width) / 2
        y = (height - new_height) / 2

        c.drawImage(ImageReader(img), x, y, width=new_width, height=new_height)
        c.showPage()

    c.save()

    writer = PdfWriter()
    reader = PdfReader(temp_output)
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata({"/Title": MARKER_TEXT})

    with open(output_path, "wb") as f_out:
        writer.write(f_out)

    os.remove(temp_output)

# Compresión inteligente

def compress_pdf(dpi, quality_name="media"):
    def run_compression():
        input_path = filedialog.askopenfilename(title="Selecciona un archivo PDF", filetypes=[("Archivos PDF", "*.pdf")])
        if not input_path:
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

            if is_scanned_pdf(input_path):
                images = convert_from_path(input_path, dpi=dpi)
                progress_bar["value"] = 50
                root.update_idletasks()
                images_to_pdf(images, output_path)
            else:
                success = compress_pdf_with_ghostscript(input_path, output_path, quality_name)
                if not success:
                    raise Exception("Ghostscript falló al comprimir el PDF.")

            progress_bar["value"] = 100
            root.update_idletasks()
            messagebox.showinfo("Éxito", f"PDF comprimido guardado en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            progress_bar["value"] = 0

    threading.Thread(target=run_compression, daemon=True).start()

# Función para unir múltiples PDFs (sin cambios)
def merge_pdfs():
    def run_merge():
        files = filedialog.askopenfilenames(title="Selecciona los archivos PDF", filetypes=[("Archivos PDF", "*.pdf")])
        if not files:
            messagebox.showerror("Error", "No seleccionaste archivos.")
            return

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

# Función para proteger un PDF con contraseña (sin cambios)
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
root.geometry("475x520")
root.resizable(False, False)

if os.path.exists(LOGO_PATH):
    img = Image.open(LOGO_PATH)
    img = img.resize((205, 115), Image.Resampling.LANCZOS)
    logo = ImageTk.PhotoImage(img)
    logo_label = tk.Label(root, image=logo)
    logo_label.pack(pady=10)

tk.Label(root, text="Selecciona una opción", font=("Arial", 16)).pack(pady=10)
tk.Button(root, text="Unir Múltiples PDFs", command=merge_pdfs, bg="blue", fg="white", width=40, font=("Arial", 12)).pack(pady=10)
tk.Button(root, text="Calidad Alta (180 DPI)", command=lambda: compress_pdf(compression_levels["Alta"], "alta"), bg="lightgreen", width=40, font=("Arial", 12)).pack(pady=5)
tk.Button(root, text="Calidad Media (120 DPI)", command=lambda: compress_pdf(compression_levels["Media"], "media"), bg="yellow", width=40, font=("Arial", 12)).pack(pady=5)
tk.Button(root, text="Calidad Baja (80 DPI)", command=lambda: compress_pdf(compression_levels["Baja"], "baja"), bg="red", width=40, font=("Arial", 12)).pack(pady=5)
tk.Button(root, text="Proteger PDF con Contraseña", command=protect_pdf, bg="purple", fg="white", width=40, font=("Arial", 12)).pack(pady=15)

progress_bar = ttk.Progressbar(root, length=300, mode="determinate")
progress_bar.pack(pady=15)

author_label = tk.Label(root, text="Desarrollado por [Ing. Edwin Chavez - Dept. sistemas]", font=("Arial", 10, "italic"), fg="gray")
author_label.pack(side="bottom", pady=10)

root.mainloop()
