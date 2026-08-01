#administrar_editar_agregar_eliminar.py
import os
import sqlite3
import random

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock



from imagenes import seleccionar_y_procesar_imagen, renombrar_imagen
from datos import conectar_db
from loggin import configurar_logger, agregar_log
from cargardatos import recargardatostablas

      
def AgregarProducto(popup_instance):
    id_producto = popup_instance.id_input.text
    nombre = popup_instance.nombre_input.text
    categoria = popup_instance.categoria_spinner.text    
    precio_compra = popup_instance.precio_compra_input.text
    precio_venta = popup_instance.precio_venta_input.text
    ganancia = popup_instance.ganancia_input.text  
    stock_minimo = popup_instance.stock_minimo_input.text
    visible = popup_instance.visible_value
    nota = popup_instance.nota_input.text
    stock_actual = 0
    imagen_ID = f"file/{id_producto}.jpg"
    usuario = ""
    dispositivos = ""
    precio_minimo_venta = popup_instance.precio_minimo_venta_input.text


        
    # Validacion de datos antes de Guardar
    if categoria == 'Seleccionar categoría':
        popup_instance.mostrar_error("Por favor, selecciona una categoría válida")    
        return

    if not id_producto or not nombre or not precio_compra or not precio_venta:
        popup_instance.mostrar_error('Campos: ID, Nombre, Categoria, Precios obligatorios')
        return    
    
    
    conn = None
    try:
        conn, cursor = conectar_db()  # Conectar a la base de datos
        cursor.execute("SELECT COUNT(*) FROM productos WHERE id = ?", (id_producto,))
        existe = cursor.fetchone()[0] > 0
        if existe:
            id_producto = popup_instance.generar_id_aleatorio()  # Generar un nuevo ID
            popup_instance.mostrar_error(f'El ID ya existe. Se ha generado un nuevo ID: {id_producto}')  # Mensaje informativo
            popup_instance.id_input.text = id_producto  # Actualizar el campo de entrada con el nuevo ID
            return
    except Exception as e:
        popup_instance.mostrar_error(f'Error al verificar ID del producto: {str(e)}')
        return 
    finally:
        if conn:
            conn.close()


    try:
        # Convertir precios a float y validar
        precio_compra = float(precio_compra)
        precio_venta = float(precio_venta)      
        if precio_venta <= precio_compra:
            popup_instance.mostrar_error("Revisar Precio de Compra y Precio de Venta")              
            return
    except ValueError:
        popup_instance.mostrar_error('Por favor, ingrese precios válidos.')
        return    

    # Verificar si el precio mínimo de venta está vacío o es menor al precio de compra
    if not precio_minimo_venta or float(precio_minimo_venta) < precio_compra:
        precio_minimo_venta = precio_compra
    else:
        precio_minimo_venta = float(precio_minimo_venta)


    def guardar_producto_post_verificacion():
        conn = None 
        try:           
            conn, cursor = conectar_db()
            
            cursor.execute('''INSERT INTO productos (id, nombre, categoria, precio_compra, precio_venta, precio_minimo_venta, ganancia, stock_minimo, stock_actual, visible, nota, ruta_imagen, usuario, dispositivos)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (id_producto, nombre, categoria, precio_compra, precio_venta, precio_minimo_venta, ganancia, stock_minimo, stock_actual, visible, nota, imagen_ID, usuario, dispositivos))

            conn.commit()
            renombrar_imagen(id_producto)     
            global products_screen
            global admin_screen
            recargardatostablas()                      
            popup_instance.dismiss()             
        except Exception as e:
            agregar_log(f'Error al insertar el producto: {e}')
        finally:
            if conn:
                conn.close()  
            

    # Llamar a la función para guardar el producto
    guardar_producto_post_verificacion()

###########################   POPUP PARA LLENAR          ################################################

def Editar_Productos(popup_instance):
    id_producto = popup_instance.id_input.text.strip() 
    nombre = popup_instance.nombre_input.text.strip() 
    categoria = popup_instance.categoria_spinner.text.strip() 
    precio_compra = popup_instance.precio_compra_input.text.strip() 
    precio_venta = popup_instance.precio_venta_input.text.strip()   
    ganancia = popup_instance.ganancia_input.text.strip()
    precio_minimo_venta = popup_instance.precio_minimo_venta_input.text.strip()
    stock_minimo = popup_instance.stock_minimo_input.text.strip()  
    nota = popup_instance.nota_input.text.strip() 
    visible = popup_instance.visible_value.strip()
    precio_minimo_venta = popup_instance.precio_minimo_venta_input.text.strip()  
    imagen_ID = f"file/{id_producto}.jpg"   
    usuario = ""
    dispositivos = ""
    precio_minimo_venta = popup_instance.precio_minimo_venta_input.text



    # Validación de datos antes de guardar
    if categoria == 'Seleccionar categoría':
        popup_instance.mostrar_error("Por favor, selecciona una categoría válida")    
        return

    if not id_producto or not nombre or not precio_compra or not precio_venta:
        popup_instance.mostrar_error('Campos: ID, Nombre, Categoria, Precios obligatorios')
        return      

    try:
        # Convertir precios a float y validar
        precio_compra = float(precio_compra)
        precio_venta = float(precio_venta)

        
        if precio_venta <= precio_compra:
            popup_instance.mostrar_error("Revisar Precio de Compra y Precio de Venta")              
            return
    except ValueError:
        popup_instance.mostrar_error('Por favor, ingrese precios válidos.')
        return    
    # Verificar si el precio mínimo de venta está vacío o es menor al precio de compra
    if not precio_minimo_venta or float(precio_minimo_venta) < precio_compra:
        precio_minimo_venta = precio_compra
    else:
        precio_minimo_venta = float(precio_minimo_venta)

    # Lógica para actualizar el producto
    def actualizar_producto():
        try:       
            conn, cursor = conectar_db()
            
            cursor.execute(''' 
                UPDATE productos 
                SET nombre = ?, categoria = ?, precio_compra = ?, precio_venta = ?, 
                    precio_minimo_venta = ?, ganancia = ?, stock_minimo = ?, visible = ?, nota = ?, 
                    ruta_imagen = ?, usuario = ?, dispositivos = ? 
                WHERE id = ?''', 
                (nombre, categoria, precio_compra, precio_venta, 
                precio_minimo_venta, ganancia, stock_minimo,
                visible, nota, imagen_ID, usuario, dispositivos, id_producto))

            conn.commit() # Lógica para renombrar la imagen
            global products_screen
            global admin_screen
            recargardatostablas()
            renombrar_imagen(id_producto)  

            popup_instance.dismiss()
        except Exception as e:
            agregar_log(f'Error al actualizar el producto: {e}')
            popup_instance.mostrar_error('Error al actualizar el producto. Inténtalo de nuevo.')
        finally:
            if conn:
                conn.close()  # Asegurarse de cerrar la conexión


               

    actualizar_producto()


###########################   POPUP PARA LLENAR          ################################################
class crearpopupproductos(Popup):
    def __init__(self, parent, editando, admin_screen, codigo, **kwargs): 
        super(crearpopupproductos, self).__init__(**kwargs)
    
        self.title = 'Agregar Producto'
        self.size = (800, 600) 
        self.size_hint = None, None  
        self.auto_dismiss = False
        self.admin_screen = admin_screen
        self.parent_window = parent        
        self.editando = editando
        self.producto_seleccionado = codigo
        configurar_logger()

        
        main_layout = BoxLayout(orientation='vertical')
        
        # Crear ScrollView para permitir desplazamiento
        scroll_view = ScrollView(do_scroll_x=False, do_scroll_y=True)
        scroll_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        # Campos de entrada
        if editando:  # Verifica si está en modo de edición
            self.id_input = Label(text=self.producto_seleccionado, font_size=16, size_hint_y=None, height=40, color=(1, 1, 1, 1), halign='left', text_size=(780, None), padding=(10, 0))
        else:
            self.id_input = TextInput(hint_text='ID del producto', font_size=16, text=self.generar_id_aleatorio(), size_hint_y=None, height=40, background_color=(0.5, 0.5, 0.5, 1), foreground_color=(1, 1, 1, 1), multiline=False)
                
        self.nombre_input = TextInput(hint_text='Nombre del producto', font_size=16, size_hint_y=None, height=40, background_color=(0.5, 0.5, 0.5, 1), foreground_color=(1, 1, 1, 1), multiline=False)        
        self.nombre_input.bind(text=self.on_nombre_text)
        self.precio_compra_input = TextInput(hint_text='Precio de compra', input_filter='float', font_size=16, size_hint_y=None, height=40, background_color=(0.5, 0.5, 0.5, 1), foreground_color=(1, 1, 1, 1), multiline=False)
        self.precio_venta_input = TextInput(hint_text='Precio de venta', input_filter='float', font_size=16, size_hint_y=None, height=40, background_color=(0.5, 0.5, 0.5, 1), foreground_color=(1, 1, 1, 1), multiline=False)

        # Añadir el campo de Precio Mínimo de Venta
        self.precio_minimo_venta_input = TextInput(hint_text='Precio mínimo de venta', input_filter='float', font_size=16, size_hint_y=None, height=40, background_color=(0.5, 0.5, 0.5, 1), foreground_color=(1, 1, 1, 1), multiline=False)

        self.ganancia_input = Label(text='0.00', font_size=16, size_hint_y=None, height=40, color=(1, 1, 1, 1), halign='left', text_size=(780, None), padding=(10, 0))
        self.stock_minimo_input = TextInput(hint_text='Stock mínimo', input_filter='int', font_size=16, size_hint_y=None, height=40, background_color=(0.5, 0.5, 0.5, 1), foreground_color=(1, 1, 1, 1), multiline=False)
        self.nota_input = TextInput(hint_text='Nota', font_size=16, size_hint_y=None, height=40, background_color=(0.5, 0.5, 0.5, 1), foreground_color=(1, 1, 1, 1), multiline=False)

        self.categoria_spinner = Spinner(text='Seleccionar categoría', size_hint_y=None, height=40, font_size=16, background_color=(0.5, 0.5, 0.5, 1), color=(1, 1, 1, 1))
        self.cargar_categorias()

        # Añadir etiquetas y campos al layout de desplazamiento
        scroll_layout.add_widget(Label(text='ID del producto', font_size=16, size_hint_y=None, height=30, halign='left', text_size=(780, None), padding=(10, 0)))
        scroll_layout.add_widget(self.id_input)

        scroll_layout.add_widget(Label(text='Nombre del producto', font_size=16, size_hint_y=None, height=30, halign='left', text_size=(780, None), padding=(10, 0)))
        scroll_layout.add_widget(self.nombre_input)

        scroll_layout.add_widget(Label(text='Categoría', font_size=16, size_hint_y=None, height=30, halign='left', text_size=(780, None), padding=(10, 0)))
        scroll_layout.add_widget(self.categoria_spinner)

        scroll_layout.add_widget(Label(text='Precio de compra', font_size=16, size_hint_y=None, height=30, halign='left', text_size=(780, None), padding=(10, 0)))
        scroll_layout.add_widget(self.precio_compra_input)

        scroll_layout.add_widget(Label(text='Precio de venta', font_size=16, size_hint_y=None, height=30, halign='left', text_size=(780, None), padding=(10, 0)))
        scroll_layout.add_widget(self.precio_venta_input)

        # Añadir el campo de Precio Mínimo de Venta al layout
        scroll_layout.add_widget(Label(text='Precio mínimo de venta', font_size=16, size_hint_y=None, height=30, halign='left', text_size=(780, None), padding=(10, 0)))
        scroll_layout.add_widget(self.precio_minimo_venta_input)

        scroll_layout.add_widget(Label(text='Ganancia', font_size=16, size_hint_y=None, height=30, halign='left', text_size=(780, None), padding=(10, 0)))
        scroll_layout.add_widget(self.ganancia_input)

        scroll_layout.add_widget(Label(text='Stock mínimo', font_size=16, size_hint_y=None, height=30, halign='left', text_size=(780, None), padding=(10, 0)))
        scroll_layout.add_widget(self.stock_minimo_input)

        scroll_layout.add_widget(Label(text='Nota', font_size=16, size_hint_y=None, height=30, halign='left', text_size=(780, None), padding=(10, 0)))
        scroll_layout.add_widget(self.nota_input)



       # Toggle buttons para el campo 'Visible'
        self.visible_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        self.visible_si = ToggleButton(text='Sí', group='visible', state='down', background_color=(78/255, 188/255, 255/255, 1))
        self.visible_no = ToggleButton(text='No', group='visible', state='normal', background_color=(1, 0.6667, 0.4235, 1))

        # Bind de eventos para manejar cambios de estado
        self.visible_si.bind(on_press=self.on_visible_change)
        self.visible_no.bind(on_press=self.on_visible_change)

        self.visible_layout.add_widget(self.visible_si)
        self.visible_layout.add_widget(self.visible_no)

        
        scroll_layout.add_widget(Label(text='Visible', font_size=16, size_hint_y=None, height=30))
        scroll_layout.add_widget(self.visible_layout)


        # Botón para agregar imagen
        btn_agregar_imagen = Button(text='Agregar Imagen', size_hint=(1, None), height=40, font_size=16)
        btn_agregar_imagen.bind(on_press=self.abrir_selector_imagen)
        scroll_layout.add_widget(btn_agregar_imagen)

        # Mostrar imagen seleccionada o imagen por defecto
        self.imagen_input = Image(size_hint=(None, None), size=(200, 200))
        scroll_layout.add_widget(self.imagen_input)

        # Añadir un espacio entre los campos adicionales
        scroll_layout.add_widget(Label(size_hint_y=None, height=10))  # Espacio vacío


        scroll_view.add_widget(scroll_layout)
        main_layout.add_widget(scroll_view)

        # Layout para mostrar errores en los campos adicionales (siempre visible)
        self.error_layout_2 = BoxLayout(size_hint_y=None, height=30)
        self.error_label_2 = Label(text='', color=(1, 0, 0, 1))  # Label rojo para errores
        self.error_layout_2.add_widget(self.error_label_2)
        main_layout.add_widget(self.error_layout_2)  # Colocar fuera del scroll

        # Botones "Guardar" y "Cancelar"
        btn_layout = BoxLayout(size_hint_y=None, height=50)
        btn_guardar = Button(text='Guardar', size_hint=(0.5, None), height=50, font_size=16, background_color=(0, 1, 0, 1))  # Verde
        btn_guardar.bind(on_press=self.guardar_o_editar_producto)

        btn_cancelar = Button(text='Cancelar', size_hint=(0.5, None), height=50, font_size=16, background_color=(1, 0, 0, 1))  # Rojo
        btn_cancelar.bind(on_press=self.dismiss)

        btn_layout.add_widget(btn_cancelar)
        btn_layout.add_widget(btn_guardar)

        # Añadir el layout de botones al layout principal
        main_layout.add_widget(btn_layout)

        # Establecer el contenido del Popup
        self.content = main_layout

        # Variables para almacenar datos
        self.selected_image_path = None
        
        # Inicializar ganancia en 0
        self.ganancia_input.text = '0'
        
        # Bind de los campos de precio para calcular ganancia
        self.precio_compra_input.bind(text=self.calcular_ganancia)
        self.precio_venta_input.bind(text=self.calcular_ganancia)
        self.visible_value = 'SI'


        # Cargar el producto solo si estamos en modo edición
        if self.editando:
            self.cargar_producto_y_campos(self.producto_seleccionado)




    def on_nombre_text(self, instance, value):
    # Limitar a 40 caracteres
        if len(value) > 40:
            # Si hay más de 40 caracteres, recortar el texto a los primeros 40
            self.nombre_input.text = value[:40]
        
    def cargar_categorias(self):
        # Método para cargar las categorías desde la base de datos
        conn = sqlite3.connect('pt/pts.db')  # Cambia la ruta según sea necesario
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM categorias")
        categorias = cursor.fetchall()
        conn.close()

        # Actualizar opciones en el Spinner
        self.categoria_spinner.values = [categoria[0] for categoria in categorias]

    def on_visible_change(self, instance):
        if instance == self.visible_no:
            self.mostrar_error('Producto no sera Visible en Punto de Ventas ')# Aquí puedes realizar cualquier acción que necesites cuando se selecciona "No"
            self.visible_value = 'No'
            pass
        elif instance == self.visible_si:
            self.mostrar_error('Producto sera Visible en el POS')
            self.visible_value = 'SI'
            pass

    def calcular_ganancia(self, *args):
        """Calcula la ganancia y actualiza el campo de ganancia."""
        try:
            precio_compra = float(self.precio_compra_input.text) if self.precio_compra_input.text else 0.0
            precio_venta = float(self.precio_venta_input.text) if self.precio_venta_input.text else 0.0
            
            ganancia = precio_venta - precio_compra
            
            # Mostrar 0 si la ganancia es negativa
            if ganancia < 0:
                ganancia = 0
            
            # Determinar si se deben mostrar decimales
            if precio_compra.is_integer() and precio_venta.is_integer():
                self.ganancia_input.text = str(int(ganancia))  # Mostrar sin decimales
            else:
                self.ganancia_input.text = str(ganancia)  # Mostrar con decimales

        except ValueError:
            self.ganancia_input.text = '0'  # En caso de error, mostrar 0



    def mostrar_error(self, mensaje): 
        # Mostrar el mensaje de error en el layout correspondiente
        if hasattr(self, 'error_label_2'):
            self.error_label_2.text = mensaje
        else:
            pass

        # Asegurarse de que el mensaje se vea durante un tiempo o hasta que se actualice
        Clock.schedule_once(lambda dt: setattr(self.error_label_2, 'text', ''), 5)  # Borra el mensaje después de 5 segundos


    def abrir_selector_imagen(self, instance):
        # Lógica para seleccionar una imagen
        nuevo_path = seleccionar_y_procesar_imagen()

        if nuevo_path:
            self.selected_image_path = nuevo_path  # Almacenar el path de la imagen seleccionada
            self.imagen_input.source = nuevo_path  # Actualizar la imagen en pantalla
            self.imagen_input.reload()  # Asegurarse de que la imagen se vuelva a cargar
            print(f"administrarproducto.py: -def abrir_selector_imagen: Ruta de la imagen seleccionada: {self.selected_image_path}")

    def generar_id_aleatorio(self):
        id_aleatorio = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        return id_aleatorio
    

    def guardar_o_editar_producto(self, instance):
        """Método para guardar o editar un producto."""
        if not self.editando:  # Si no estamos editando
            AgregarProducto(self)  # Llama a la función para agregar el producto
        else:
            # Aquí puedes implementar la lógica para editar el producto
            Editar_Productos(self)


    def cargar_producto_y_campos(self, codigo):
        try:
            conn, cursor = conectar_db()  # Usamos la función conectar_db que ya maneja la conexión
            cursor.execute(""" 
                SELECT nombre, categoria, precio_compra, precio_venta, precio_minimo_venta, nota, stock_minimo, ruta_imagen, visible 
                FROM productos 
                WHERE id = ? 
            """, (codigo,))
            row = cursor.fetchone()
            conn.close()

            if row:
                agregar_log(f'Producto cargado: {codigo}')
                # Cargar los datos directamente en los campos correspondientes
                self.id_input.text = codigo
                self.nombre_input.text = row[0]
                self.categoria_spinner.text = row[1]
                
                # Convertir precios y eliminar decimales si son enteros
                self.precio_compra_input.text = str(int(row[2])) if row[2].is_integer() else str(row[2])
                self.precio_venta_input.text = str(int(row[3])) if row[3].is_integer() else str(row[3])
                self.precio_minimo_venta_input.text = str(int(row[4])) if row[4].is_integer() else str(row[4])  # Agregamos el precio mínimo de venta
                
                self.nota_input.text = row[5]
                self.stock_minimo_input.text = str(int(row[6]))  # También puedes quitar los decimales de stock_minimo si es necesario

                # Cargar la imagen solo si existe
                ruta_imagen = row[7]
                if ruta_imagen:  # Verificamos si la ruta de la imagen no está vacía
                    self.imagen_input.source = ruta_imagen
                    self.imagen_input.reload()
                else:
                    # Si no hay imagen, puedes cargar una imagen por defecto o dejarla vacía
                    self.imagen_input.source = ''  # O una imagen por defecto
                    self.imagen_input.reload()

                # Ajustar el estado del toggle de visibilidad
                visible = row[8]  # Valor de la base de datos
                if visible == 'SI':  # Verificar si visible es 'SI'
                    self.visible_value = 'SI'
                    self.mostrar_error('Producto Visible en el POS')
                else:  # De lo contrario, es 'No'
                    self.visible_value = 'No'
                    self.mostrar_error('Producto no Visible en Punto de Ventas')

        except Exception as e:
            agregar_log(f'Error al cargar el producto: {e}')




############################################################################################################################ delete

#administrar_editar_agregar_eliminar.py
class ConfirmDeletePopup(Popup):
    def __init__(self, parent, admin_screen, codigo, **kwargs): 
        super(ConfirmDeletePopup, self).__init__(**kwargs)    
        self.title = "Confirmar Eliminación"
        self.size_hint = (0.6, 0.4)
        self.size = (400, 200)  # Establecer tamaño específico en píxeles
        self.size_hint = None, None  # Desactivar el ajuste de tamaño relativo
        self.auto_dismiss = False
        self.admin_screen = admin_screen
        self.parent_window = parent        
        self.producto_seleccionado = codigo
        self.popup_instance = self
        configurar_logger()  


        content = BoxLayout(orientation='vertical', padding=10)
        message = Label(text=f"¿Estás seguro que quieres eliminar esta entrada? '{codigo}'?, accion no es reversible", size_hint_y=None, halign='center', valign='middle', text_size=(self.width - 20, None))

        message.bind(size=message.setter('text_size'))
        content.add_widget(message)

        button_layout = BoxLayout(size_hint_y=None, height=50)
        cancel_button = Button(text='Cancelar', background_color=(0.678, 0.847, 0.902, 1), on_press=self.cerrar_popup)
        confirm_button = Button(text='Eliminar', background_color=(1, 0, 0, 1), on_press=lambda x: self.confirm_delete(self))
        
        button_layout.add_widget(cancel_button)
        button_layout.add_widget(confirm_button)
        content.add_widget(button_layout)

        self.add_widget(content)

    def confirm_delete(self, instance):
        self.eliminar_producto()
        self.dismiss() 
        #recargartablas
        global products_screen 
        global admin_screen  
        recargardatostablas()   

        if hasattr(self, 'popup_instance'):   
            del self.popup_instance 

     

    def cerrar_popup(self, instance):
        self.dismiss()  
        print("cerrndo  popup")
        if hasattr(self, 'popup_instance'):
            print("eliminando popup")            
            del self.popup_instance  # Eliminar el objeto solo si existe

    def eliminar_producto(self):
        directorio_actual = os.getcwd()
        codigo = self.producto_seleccionado
        agregar_log(f"El producto con código {codigo} ha sido eliminado.")
        
        # Ruta de la imagen del producto
        image_path = os.path.join(directorio_actual, 'file', f'{codigo}.jpg')
        print(f'Imprimir directorio actual antes de eliminar: {directorio_actual}')

        # Intentar eliminar la imagen asociada al producto
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
                agregar_log(f"Imagen {image_path} eliminada con éxito.")
            except Exception as e:
                agregar_log(f"Error al eliminar la imagen: {e}")
        else:
            agregar_log(f"No se encontró la imagen {image_path}, no se realizó ninguna acción.")

        # Conectar a la base de datos y eliminar el producto
        try:
            conn, cursor = conectar_db()  # Obtener conexión y cursor
            cursor.execute("DELETE FROM productos WHERE id = ?", (codigo,))
            if cursor.rowcount > 0:
                agregar_log(f"Producto {codigo} eliminado con éxito.")
            else:
                agregar_log(f"No se encontró el producto con código {codigo}.")
            conn.commit()
        except sqlite3.Error as e:
            agregar_log(f"Error al eliminar el producto: {e}")
        finally:
            cursor.close()  # Asegúrate de cerrar el cursor
            conn.close()  # Asegúrate de cerrar la conexión
        