#administrarproductos.py


import sqlite3
import random
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.properties import BooleanProperty
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout

from datos import conectar_db


class AddCategoryPopup(Popup):
    def __init__(self, admin_screen, **kwargs):
        super(AddCategoryPopup, self).__init__(**kwargs)
        self.admin_screen = admin_screen
        self.title = "Agregar Nueva Categoría"
        self.size_hint = (0.6, 0.4)
        self.size = (400, 200)
        self.size_hint = None, None
        self.auto_dismiss = False

        layout = BoxLayout(orientation='vertical')

        self.category_input = TextInput(hint_text='Nombre de la categoría', multiline=False)
        self.category_input.bind(text=self.limit_text_length)  # Vincular el método para limitar caracteres
        layout.add_widget(self.category_input)

        # Label para mostrar mensajes de error
        self.error_label = Label(text='', color=(1, 0, 0, 1))  # Color rojo para el texto
        layout.add_widget(self.error_label)

        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        
        save_button = Button(text='Guardar', on_press=self.save_category)
        cancel_button = Button(text='Cancelar', on_press=self.dismiss)

        button_layout.add_widget(save_button)
        button_layout.add_widget(cancel_button)

        layout.add_widget(button_layout)

        self.add_widget(layout)

    def limit_text_length(self, instance, value):
        """ Limitar el número de caracteres a 20 """
        if len(value) > 20:
            self.category_input.text = value[:20]  # Corta el texto a 20 caracteres


    def save_category(self, instance):
        category_name = self.category_input.text.strip()
        if category_name:
            if self.save_to_database(category_name):  # Llama a la función de guardado
                self.admin_screen.cargar_categorias()
                self.dismiss()  # Cierra el popup
                self.error_label.text = ''  # Limpiar el mensaje de error
            else:
                self.error_label.text = "Error: la categoría ya existe."  # Actualizar el texto del Label
        else:
            self.error_label.text = "El nombre de la categoría no puede estar vacío."

    def save_to_database(self, category_name):
        # Conectar a la base de datos
        conn = sqlite3.connect('pt/pts.db')
        cursor = conn.cursor()

        # Crear la tabla si no existe
        cursor.execute("CREATE TABLE IF NOT EXISTS categorias (id TEXT PRIMARY KEY, nombre TEXT)")

        # Comprobar si la categoría ya existe
        cursor.execute("SELECT * FROM categorias WHERE nombre = ?", (category_name,))
        if cursor.fetchone() is not None:
            conn.close()
            return False  # La categoría ya existe, no se guarda

        # Generar un ID único
        unique_id = f"{random.randint(10000, 99999)}-{category_name}"

        # Insertar la nueva categoría con el ID único
        cursor.execute("INSERT INTO categorias (id, nombre) VALUES (?, ?)", (unique_id, category_name))
        conn.commit()
        conn.close()
        return True  # La categoría se guardó exitosamente


#---------------------------------------------------
class EditCategoryPopup(Popup):
    def __init__(self, admin_screen, selected_category, **kwargs):
        super().__init__(**kwargs)
        self.admin_screen = admin_screen
        self.selected_category = selected_category
        self.title = 'Editar Categoría'
        self.size_hint = (0.6, 0.4)
        self.size = (400, 200)
        self.size_hint = None, None
        self.auto_dismiss = False
        
        layout = BoxLayout(orientation='vertical')

        # Campo de texto para el nuevo nombre de la categoría
        self.category_name_input = TextInput(hint_text='Nuevo nombre de categoría', multiline=False, size_hint_y=None, height=40)

        self.category_name_input.text = selected_category  # Cargar el nombre actual

        # Label para mostrar mensajes de error
        self.error_label = Label(text='', color=(1, 0, 0, 1))  # Color rojo para el texto
        layout.add_widget(self.error_label)

        # Botón para guardar
        save_button = Button(text='Guardar', size_hint_y=None, height=40)
        save_button.bind(on_press=self.save_category)

        # Botón para cancelar
        cancel_button = Button(text='Cancelar', size_hint_y=None, height=40)
        cancel_button.bind(on_press=self.dismiss)

        # Agregar widgets al layout
        layout.add_widget(self.category_name_input)
        layout.add_widget(save_button)
        layout.add_widget(cancel_button)

        self.content = layout

    def save_category(self, instance):
        new_category_name = self.category_name_input.text.strip()
        if new_category_name:
            if self.update_category_in_database(self.selected_category, new_category_name):
                self.admin_screen.cargar_categorias()
                #self.admin_screen.mostrar_productos(instance)
                print("Categoría Editada")
                self.dismiss()  # Cierra el popup
                self.error_label.text = ''  # Limpiar el mensaje de error
            else:
                self.error_label.text = "Error: la categoría ya existe."  # Actualizar el texto del Label
        else:
            self.error_label.text = "El nombre de la categoría no puede estar vacío."

    def update_category_in_database(self, old_category_name, new_category_name):
        conn, cursor = conectar_db()
        cursor.execute("SELECT * FROM categorias WHERE nombre = ?", (new_category_name,))
        if cursor.fetchone() is not None:
            conn.close()
            return False  

        # Actualizar la categoría en la base de datos
        cursor.execute("UPDATE categorias SET nombre = ? WHERE nombre = ?", (new_category_name, old_category_name))
        cursor.execute("UPDATE productos SET categoria = ? WHERE categoria = ?", (new_category_name, old_category_name))
        conn.commit()
        conn.close()
        return True  # La categoría se actualizó exitosamente

class DeleteCategoryPopup(Popup):
    def __init__(self, admin_screen, selected_category, **kwargs):
        super().__init__(**kwargs)
        self.admin_screen = admin_screen
        self.selected_category = selected_category
        self.title = 'Borrar Categoría'
        self.size_hint = (0.6, 0.4)
        self.size = (400, 200)
        self.auto_dismiss = False
        
        layout = BoxLayout(orientation='vertical')

        # Mensaje de confirmación
        message_label = Label(text=f"¿Estás seguro de que deseas borrar la categoría '{self.selected_category}'?")
        layout.add_widget(message_label)

        # Botón para confirmar la eliminación
        delete_button = Button(text='Borrar', size_hint_y=None, height=40)
        delete_button.bind(on_press=self.delete_category)

        # Botón para cancelar
        cancel_button = Button(text='Cancelar', size_hint_y=None, height=40)
        cancel_button.bind(on_press=self.dismiss)

        # Agregar widgets al layout
        layout.add_widget(delete_button)
        layout.add_widget(cancel_button)

        self.content = layout

    def delete_category(self, instance):
        # Lógica para borrar la categoría en la base de datos
        self.delete_category_from_database(self.selected_category)
        print(f"Categoría '{self.selected_category}' borrada.")
        self.admin_screen.cargar_categorias()  # Actualiza la lista de categorías
        self.dismiss()  # Cierra el popup

    def delete_category_from_database(self, category_name):
        conn = sqlite3.connect('pt/pts.db')  # Cambia la ruta según sea necesario
        cursor = conn.cursor()
        cursor.execute("UPDATE productos SET categoria = '' WHERE categoria = ?", (category_name,))
        cursor.execute("DELETE FROM categorias WHERE nombre = ?", (category_name,))        
        conn.commit()
        conn.close()
###############################################################################

class ProductosOcultos(Popup):
    def __init__(self, parent, **kwargs):
        super(ProductosOcultos, self).__init__(**kwargs)
        self.title = 'Productos Ocultos'
        self.size = (800, 600)  # Tamaño del popup
        self.size_hint = None, None  # Desactivar el ajuste de tamaño relativo
        self.auto_dismiss = False
        self.parentis = parent  # Guardar referencia al padre

        # Crear el layout principal del popup
        layout = BoxLayout(orientation='vertical')

        # Crear un layout para la cabecera (incluyendo los botones)
        header_layout = BoxLayout(size_hint_y=None, height=50, padding=[0, 20, 0, 0])  # Aumentar padding superior

        # Crear un Label para el título (vacío)
        title_label = Label(text='', size_hint_x=1)  # Label vacío
        header_layout.add_widget(title_label)

        # Agregar el botón "Desocultar"
        unhide_button = Button(text='Desocultar', size_hint_x=None, width=100, pos_hint={'right': 1}, background_color=(0.8, 0.8, 0.8, 1))  # Color gris
        unhide_button.bind(on_press=self.desocultar_boton)  # Vincular la función al botón
        unhide_button.bold = True  # Texto en negrita
        unhide_button.color = (0, 1, 0, 1)  # Color del texto en verde
        header_layout.add_widget(unhide_button)

        # Agregar el botón "Editar"
        header_button = Button(text='Editar', size_hint_x=None, width=100, pos_hint={'right': 1}, background_color=(0.8, 0.8, 0.8, 1))  # Color gris

        header_button.bind(on_press=self.on_header_button_press)  # Vincular una función al botón
        header_button.bold = True  # Texto en negrita
        header_button.color = (1, 1, 0, 1)  # Color del texto en amarillo
        header_layout.add_widget(header_button)

        layout.add_widget(header_layout)

        # Crear un ScrollView para la tabla
        self.scrollview = ScrollView(size_hint=(1, None), size=(800, 500))
        self.table_layout = GridLayout(cols=1, size_hint_y=None)
        self.table_layout.bind(minimum_height=self.table_layout.setter('height'))

        self.scrollview.add_widget(self.table_layout)

        layout.add_widget(self.scrollview)

        # Botón de cerrar
        close_button = Button(text='Cerrar', size_hint_y=None, height=50, background_color=(0.6, 0, 0, 1))
        close_button.bind(on_press=lambda x: (self.dismiss(), setattr(self.parent, 'productos_ocultos_popup', None)))


        layout.add_widget(close_button)
        self.add_widget(layout)

        # Cargar los productos ocultos al abrir el popup
        self.cargar_productos_ocultos()


    def desocultar_boton(self, instance):
        # Verificar que hay un producto seleccionado
        if hasattr(self, 'selected_product_id'):
            product_id = self.selected_product_id  # Obtener el ID del producto seleccionado
            
            # Crear el contenido del popup de confirmación
            content = BoxLayout(orientation='vertical', padding=10)
            message = Label(text=f"¿Deseas desocultar el producto con ID: {product_id}?", size_hint_y=None, halign='center', valign='middle', text_size=(self.width - 20, None))
            message.bind(size=message.setter('text_size'))
            content.add_widget(message)

            # Crear el popup
            popup = Popup(title="Confirmar Desocultación", content=content, size_hint=(None, None), size=(400, 200))

            # Crear botones para el popup
            button_layout = BoxLayout(size_hint_y=None, height=50)
            cancel_button = Button(text='Cancelar', on_press=lambda x: (popup.dismiss(), self.parent.remove_widget(popup)))
            confirm_button = Button(text='Desocultar', on_press=lambda x: self.confirmar_desocultar(product_id, popup))

            button_layout.add_widget(cancel_button)
            button_layout.add_widget(confirm_button)
            content.add_widget(button_layout)

            popup.open()
        else:
            print("No hay producto seleccionado para desocultar.")

    def confirmar_desocultar(self, product_id, popup):
        conn = sqlite3.connect('PT/pts.db')
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE productos SET visible = 'SI' WHERE id = ?", (product_id,))
            conn.commit() 
            popup.dismiss()  # Cierra el popup
            self.parent.remove_widget(popup)  # Elimina el popup del padre
            self.recargar_tabla()  # Recargar la tabla para reflejar los cambios      
        except Exception as e:
            print(f"Ocurrió un error al desocultar el producto: {e}")
        finally:
            conn.close() 


            
    def on_header_button_press(self, instance):
        print('vincular edicion')
       # product_codigo = self.selected_product_id
        #edit_popup = EditProductPopup(self.parentis, product_codigo)
       # edit_popup.open()  # Abrir el popup de edición



    def cargar_productos_ocultos(self):
        """Carga los productos ocultos desde la base de datos, ordenados por nombre."""
        print("Cargando productos ocultos de la base de datos...")
        conn = sqlite3.connect('PT/pts.db')
        cursor = conn.cursor()

        try:
            # Ordenar los productos ocultos por nombre
            cursor.execute("SELECT id, nombre, categoria, precio_compra, precio_venta, stock_actual FROM productos WHERE visible != 'SI' ORDER BY LOWER(nombre)")
            productos = cursor.fetchall()

            # Limpiar tabla antes de agregar nuevos productos
            self.table_layout.clear_widgets()

            if productos:
                # Agregar el encabezado de la tabla
                header = BoxLayout(size_hint_y=None, height=50)
                codigo_header = Label(text='Código', font_size=14, bold=True, size_hint_x=0.2, halign='center')
                product_header = Label(text='Producto', font_size=16, bold=True, size_hint_x=0.3, halign='center')
                categoria_header = Label(text='Categoría', font_size=16, bold=True, size_hint_x=0.2, halign='center')
                compra_header = Label(text='Precio Compra', font_size=16, bold=True, size_hint_x=0.2, halign='center')
                price_header = Label(text='Precio Venta', font_size=16, bold=True, size_hint_x=0.2, halign='center')
                stock_header = Label(text='Stock Actual', font_size=16, bold=True, size_hint_x=0.2, halign='center')

                header.add_widget(codigo_header)
                header.add_widget(product_header)
                header.add_widget(categoria_header)
                header.add_widget(compra_header)
                header.add_widget(price_header)
                header.add_widget(stock_header)
                self.table_layout.add_widget(header)

                # Agregar los productos ocultos
                for producto in productos:
                    product_id, nombre, categoria, precio_compra, precio_venta, stock_actual = producto
                    product_box = BoxLayout(size_hint_y=None, height=50)
                    product_box.bind(on_touch_down=self.on_product_select)

                    codigo_label = Label(text=product_id, font_size=14, size_hint_x=0.2, halign='center')
                    product_label = Label(text=nombre, font_size=14, size_hint_x=0.3, halign='center')
                    categoria_label = Label(text=categoria, font_size=14, size_hint_x=0.2, halign='center')
                    compra_label = Label(text=str(precio_compra), font_size=14, size_hint_x=0.2, halign='center')
                    price_label = Label(text=str(precio_venta), font_size=14, size_hint_x=0.2, halign='center')
                    stock_label = Label(text=str(stock_actual), font_size=14, size_hint_x=0.2, halign='center')

                    product_box.add_widget(codigo_label)
                    product_box.add_widget(product_label)
                    product_box.add_widget(categoria_label)
                    product_box.add_widget(compra_label)
                    product_box.add_widget(price_label)
                    product_box.add_widget(stock_label)

                    self.table_layout.add_widget(product_box)
            else:
                no_products_label = Label(text='No hay productos ocultos', size_hint_y=None, height=50, font_size=16)
                self.table_layout.add_widget(no_products_label)
                print("No hay productos ocultos en la base de datos.")
        except Exception as e:
            print(f"Ocurrió un error al cargar los productos: {e}")
        finally:
            print("Cerrando la conexión a la base de datos.")
            conn.close()


    def on_product_select(self, instance, touch):
        if instance.collide_point(*touch.pos):
            product_id = instance.children[5].text
            self.selected_product_id = product_id
            #print(f"Producto seleccionado: {self.selected_product_id}")
            
            for child in instance.children:
                child.color = (0.7, 0.7, 1, 1)

            for child in self.table_layout.children:
                if child != instance:
                    for subchild in child.children:
                        subchild.color = (1, 1, 1, 1)


    def recargar_tabla(self):
        """Recarga los datos de la tabla de productos ocultos, solo si el popup está abierto."""
        if self.parent:
            # Limpiar el contenido de la tabla
            self.table_layout.clear_widgets()
            
            # Cargar los productos nuevamente
            self.cargar_productos_ocultos()
        else:
            print("El popup no está abierto, no se puede recargar la tabla.")

#################################################################################################################################################

