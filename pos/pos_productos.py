#posproductos.py

import os  # Importar para verificar si el archivo existe

from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from datos import conectar_db
from datos import obtener_ruta_assets
#posproductos.py

def update_rect(rectangle, parent):
    """Actualiza el rectángulo para que cubra toda el área del widget."""
    rectangle.pos = parent.pos
    rectangle.size = parent.size

class BackgroundColor:
    """Clase para establecer un color de fondo en una pantalla."""
    
    def __init__(self, parent):
        self.parent = parent
        with self.parent.canvas.before:
            Color(0.1, 0.1, 0.1, 1)  # Color de fondo
            self.rect = Rectangle(size=self.parent.size, pos=self.parent.pos)

        self.parent.bind(size=lambda *args: update_rect(self.rect, self.parent), 
                         pos=lambda *args: update_rect(self.rect, self.parent))  # Actualizar el rectángulo en caso de redimensionamiento

class FacturarBackgroundColor:
    """Clase para establecer un color de fondo en el FacturarRecycleView."""
    
    def __init__(self, parent):
        self.parent = parent
        with self.parent.canvas.before:
            Color(0.25, 0.25, 0.25, 1)  # Color de fondo específico para FacturarRecycleView
            self.rect = Rectangle(size=self.parent.size, pos=self.parent.pos)

        self.parent.bind(size=lambda *args: update_rect(self.rect, self.parent), 
                         pos=lambda *args: update_rect(self.rect, self.parent))
















class infoProductosPopup(Popup):
    def __init__(self, rango_usuario, **kwargs):
        super(infoProductosPopup, self).__init__(**kwargs)
        self.title = "Info Productos"
        self.size_hint = None, None
        self.size = (900, 600)
        self.auto_dismiss = False
        self.area = BoxLayout(orientation="vertical")
        self.add_widget(self.area)

        ruta_assets = obtener_ruta_assets()
        self.ImagenPRED = os.path.join(ruta_assets, 'predeterminada.jpg')



        # Barra de búsqueda
        self.barra_busqueda = BoxLayout(size_hint_y=0.15)
        self.area.add_widget(self.barra_busqueda)

        self.search_input = TextInput(hint_text='Buscar por ID, Nombre, Nota', size_hint=(1, None), height=dp(40), background_color=(0.2, 0.2, 0.2, 1), hint_text_color=(0.5, 0.5, 0.5, 1), foreground_color=(1, 1, 1, 1), multiline=False)
        self.search_input.bind(on_text_validate=self.filtrar_productos)  
        self.search_input.bind(text=self.filtrar_productos)    
        self.barra_busqueda.add_widget(self.search_input)

        # Spinner para visibilidad
        if rango_usuario in ["owner", "admin"]:
            self.spinner = Spinner(text='Visibles', values=('Visibles', 'Todos'), size_hint=(None, None), size=(dp(100), dp(40)))
            self.spinner.bind(text=lambda spinner, _: self.cargar_productos_por_categoria())
            self.barra_busqueda.add_widget(self.spinner)

        # Contenedor inferior con GridLayout para encabezado
        self.contenedor_inferior = BoxLayout(orientation="vertical", size_hint_y=1)
        self.area.add_widget(self.contenedor_inferior)

        # Encabezado con GridLayout
        self.encabezaloyaud = GridLayout(cols=6, size_hint_y=None, height=dp(40))
        encabezados = [" ", "ID", "Nombre", "Precio Venta", "Precio Mínimo", "Stock Actual"]
        for encabezado in encabezados:
            self.encabezaloyaud.add_widget(Label(text=encabezado))
        self.contenedor_inferior.add_widget(self.encabezaloyaud)

        # ScrollView para los productos
        self.scroll_view = ScrollView(size_hint=(1, 1))  
        self.productos_layout = GridLayout(cols=6, size_hint_y=None) 
        self.productos_layout.bind(minimum_height=self.productos_layout.setter('height'))  # Permite que el contenido crezca
        self.scroll_view.add_widget(self.productos_layout)
        self.contenedor_inferior.add_widget(self.scroll_view)

        # Cargar datos ficticios
        self.cargar_productos_por_categoria()

        # Botón de cerrar
        close_button = Button(text='Cerrar', size_hint_y=None, height=50, background_color=(0.6, 0, 0, 1))
        close_button.bind(on_press=self.dismiss)  # Cierra el popup al presionar el botón
        self.area.add_widget(close_button)  # Añadir el botón al área del popup




    def cargar_productos_por_categoria(self):
        self.productos_layout.clear_widgets()
        self.search_input.text = ""
        def agregar_label(texto, altura=dp(40)):
            return Label(text=texto, size_hint_y=None, height=altura)

        productos_por_categoria = self.obtener_productos_por_categoria()

        for categoria, productos in productos_por_categoria.items():
            self.productos_layout.add_widget(agregar_label(""))
            self.productos_layout.add_widget(agregar_label(""))     
            self.productos_layout.add_widget(Label(text=categoria, font_size='20sp', bold=True, size_hint_y=None, height=dp(40)))                    
            self.productos_layout.add_widget(agregar_label(""))             
            self.productos_layout.add_widget(agregar_label(""))             
            self.productos_layout.add_widget(agregar_label("")) 

            for producto in productos:
                ruta_imagen = producto[3]  
                img = Image(source=ruta_imagen if ruta_imagen and os.path.exists(ruta_imagen) else self.ImagenPRED, size_hint_y=None, height=dp(40))
                self.productos_layout.add_widget(img) 
                # Agregar los detalles del producto
                self.productos_layout.add_widget(agregar_label(producto[0]))  # ID
                self.productos_layout.add_widget(agregar_label(producto[1]))  # Nombre
                self.productos_layout.add_widget(agregar_label(str(producto[2])))  # Precio de venta
                self.productos_layout.add_widget(agregar_label(str(producto[6])))  # Precio mínimo
                self.productos_layout.add_widget(agregar_label(str(producto[5])))  # Stock actual


    def obtener_productos_por_categoria(self):
        conn, cursor = conectar_db()         
        spinner_value = self.spinner.text if hasattr(self, 'spinner') else 'Visibles'        
        cursor.execute("SELECT DISTINCT categoria FROM productos")
        categorias = cursor.fetchall()

        productos_por_categoria = {}

        for categoria in categorias:
            cat_name = categoria[0]
            if spinner_value == 'Visibles':
                cursor.execute("SELECT id, nombre, precio_venta, ruta_imagen, nota, stock_actual , precio_minimo_venta, precio_compra FROM productos WHERE categoria=? AND visible='SI' ORDER BY LOWER(nombre)", (cat_name,))
            else:
                cursor.execute("SELECT id, nombre, precio_venta, ruta_imagen, nota, stock_actual , precio_minimo_venta, precio_compra FROM productos WHERE categoria=? ORDER BY LOWER(nombre)", (cat_name,))            
            productos = cursor.fetchall()
            
            # Añadir solo las categorías que tienen productos
            if productos:
                productos_por_categoria[cat_name] = productos

        return productos_por_categoria



    def filtrar_productos(self, instancia_texto, texto_actualizado):
        texto_busqueda = instancia_texto.text.lower()
        self.productos_layout.clear_widgets()

        productos_por_categoria = self.obtener_productos_por_categoria()
        encontrado = False 

        for categoria, productos in productos_por_categoria.items():
            productos_filtrados = [
                producto for producto in productos
                if texto_busqueda in str(producto[0]).lower() or texto_busqueda in str(producto[1]).lower() or texto_busqueda in str(producto[4]).lower()
            ]
            
            if productos_filtrados:
                encontrado = True 
                self.productos_layout.add_widget(Label(text="", size_hint_y=None, height=dp(10)))
                self.productos_layout.add_widget(Label(text="", size_hint_y=None, height=dp(10)))
                self.productos_layout.add_widget(Label(text=categoria, font_size='20sp', bold=True, size_hint_y=None, height=dp(40)))
                self.productos_layout.add_widget(Label(text="", size_hint_y=None, height=dp(10)))
                self.productos_layout.add_widget(Label(text="", size_hint_y=None, height=dp(10)))
                self.productos_layout.add_widget(Label(text="", size_hint_y=None, height=dp(10)))

                for producto in productos_filtrados:
                    ruta_imagen = producto[3] if producto[3] and os.path.exists(producto[3]) else self.ImagenPRED
                    self.productos_layout.add_widget(Image(source=ruta_imagen, size_hint_y=None, height=dp(40)))
                    for detalle in [producto[0], producto[1], producto[2], producto[6], producto[5]]:
                        self.productos_layout.add_widget(Label(text=str(detalle), size_hint_y=None, height=dp(40)))
        if not encontrado:
            self.productos_layout.add_widget(Label(text="Producto no encontrado", size_hint_y=None, height=dp(40), color=(1, 0, 0, 1))) 



    def dismiss(self, *args):
        super(infoProductosPopup, self).dismiss(*args)