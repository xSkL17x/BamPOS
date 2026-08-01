import os
import shutil
from PIL import Image
from tkinter import Tk, filedialog
from datos import obtener_ruta_assets
from kivy.core.window import Window



ruta_assets = obtener_ruta_assets()




def cambiar_logo_empresa(espacio_label, logo_image):
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.focus_force()


    # Esperar a que se cierre la ventana de selección de archivo
    nueva_imagen = filedialog.askopenfilename(
        title="Selecciona un Logo", filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    
    if nueva_imagen:
        destino = os.path.join(ruta_assets, 'logo_empresa.png')
        if os.path.exists(destino):
            os.remove(destino)
        try:
            with Image.open(nueva_imagen) as img:
                if img.mode in ("RGBA", "LA") or (img.format == "PNG" and "transparency" in img.info):
                    img = img.convert("RGB")

                nueva_altura = 256
                relacion_aspecto = img.width / img.height
                nuevo_ancho = int(nueva_altura * relacion_aspecto)

                img = img.resize((nuevo_ancho, nueva_altura))
                img.save(destino, optimize=True)

            espacio_label.text = "Logo cambiado correctamente."
            logo_image.source = destino
            logo_image.reload()
        
        except Exception as e:
            espacio_label.text = f"Error al cambiar el logo: {e}"

    root.destroy()




def seleccionar_y_procesar_imagen():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.focus_force() 


    seleccion = filedialog.askopenfilename(title="Seleccionar imagen", filetypes=[("Imágenes", "*.jpg;*.jpeg;*.png;*.webp;*.gif;*.bmp;*.tiff;*.tif;*.svg")])

    if seleccion:
        imagen_path = seleccion
        try:
            temp_dir = os.path.join('File')
            os.makedirs(temp_dir, exist_ok=True)

            imagen_copia_path = os.path.join(temp_dir, 'imgtemp.jpg')
            shutil.copy(imagen_path, imagen_copia_path)

            with Image.open(imagen_copia_path) as imagen:
                if imagen.mode in ("RGBA", "LA") or (imagen.format == "PNG" and "transparency" in imagen.info):
                    imagen = imagen.convert("RGB")

                # Redimensionar la imagen a 340 píxeles de alto
                nueva_altura = 340
                relacion_aspecto = imagen.width / imagen.height
                nuevo_ancho = int(nueva_altura * relacion_aspecto)

                imagen = imagen.resize((nuevo_ancho, nueva_altura))
                imagen.save(imagen_copia_path, optimize=True)

            return imagen_copia_path
        except FileNotFoundError as e:
            print(f"Imagenes.py: Archivo no encontrado: {e}")
        except Exception as e:
            print(f"Imagenes.py: Error al procesar la imagen: {e}")
        finally:
            root.destroy()

    return None






def renombrar_imagen(nuevo_nombre):
    imagen_temp = os.path.join('File', 'imgtemp.jpg')

    if not os.path.exists(imagen_temp):
        #print(f"Imagenes.py: La imagen {imagen_temp} no existe. No se realizará ninguna acción.")
        return None  # No hacer nada si la imagen no existe

    ruta_imagen = os.path.join('File', f"{nuevo_nombre}.jpg")

    if os.path.exists(ruta_imagen):
        os.remove(ruta_imagen)

    os.rename(imagen_temp, ruta_imagen)   
    return ruta_imagen  








