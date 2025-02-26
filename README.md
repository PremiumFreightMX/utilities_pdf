# utilities_pdf

Una aplicación en **Python con Tkinter** que permite **comprimir, unir y proteger archivos PDF** con una interfaz gráfica intuitiva.  

## Funcionalidades  
 **Compresión de PDFs** en tres niveles de calidad:  
   - **Alta** (Menos compresión, mejor calidad)  
   - **Media** (Balance entre calidad y peso)  
   - **Baja** (Máxima reducción de tamaño)  

 **Unir múltiples archivos PDF** en un solo documento.  
 **Proteger un PDF con contraseña** para restringir apertura e impresión.  
 **Interfaz gráfica** amigable desarrollada con **Tkinter**.  

---

## **Requisitos Previos**  
Antes de ejecutar la aplicación, instala los siguientes paquetes de Python:  

```bash
pip install pillow pdf2image pypdf tk

## **También necesitas Poppler para convertir PDFs a imágenes:**
Descárgalo desde [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows).

## **Agregar Poppler al PATH (para que funcione en cualquier lugar)**
Abre Explorador de archivos y copia la ruta donde extrajiste Poppler, por ejemplo:
C:\poppler-23.11.0\Library\bin
Presiona Win + R, escribe sysdm.cpl y presiona Enter.
En la ventana Propiedades del sistema, ve a la pestaña "Opciones avanzadas".
Haz clic en "Variables de entorno...".
En "Variables del sistema", selecciona la variable Path y haz clic en "Editar...".
Haz clic en "Nuevo" y pega la ruta copiada (C:\poppler-23.11.0\Library\bin).
Presiona "Aceptar" en todas las ventanas para guardar los cambios.
```

---

## **Desarrollado por:**
<ins>Ing. Edwin Chavez - Dept. Sistemas</ins>
Contacto: supervisor.sistemas@premiumfreightmx.com

## Contribuciones
Si quieres mejorar este proyecto, haz un fork y envía un pull request.
Repositorio: github.com/PremiumFreightMX/utilities_pdf

## ¡Gracias por usar esta herramienta!
