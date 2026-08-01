#pos.py
# Standard library imports
import os
import textwrap
from datetime import datetime

# Kivy imports
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.clock import Clock
from kivy.animation import Animation
from pos.pos_Facturar import FacturaPopup
from kivy.utils import platform
# Local imports
from pos.pos_productos import BackgroundColor, FacturarBackgroundColor, infoProductosPopup
from administrar.administrar import AdminScreen
from datos import obtener_ruta_assets

from cargardatos import obtener_productos_por_categoria_con_stock ,set_admin_screen, set_products_screen
from loggin import configurar_logger, agregar_log
from inicio_sesion import LoginScreen, obtener_usuario_actual

from configs import obtener_factura
Builder.load_file('pos/pos.kv')

facrura_pd = obtener_factura()

usuario_actual = None 
rango_usuario = None   


class ProductsScreen(Screen):
    def __init__(self, **kwargs):
        super(ProductsScreen, self).__init__(**kwargs)
        configurar_logger()  

        self.background_color = BackgroundColor(self)  # Configurar el color de fondo

        main_layout = BoxLayout(orientation='vertical', size_hint=(1, 1))  # Crear el resto de la interfaz

        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))  # Crear un layout para los botones

        # Añadir el botón "Administrar"
        boton_administrar = Button(text="=", size_hint_x=None, width=dp(100), background_color=(0, 0, 0, 0), color=(1, 1, 1, 1), font_size=32, on_release=self.open_admin_popup)
        button_layout.add_widget(boton_administrar)

        self.boton_de_prueva = Button(text='tets', size_hint_x=None, width=dp(100), background_color=(0, 0, 0, 0), color=(1, 1, 1, 1), font_size=16, on_release=self.boton_test)
        button_layout.add_widget(self.boton_de_prueva)

        main_layout.add_widget(button_layout)  # Añadir el layout de botones al layout principal

        # Crear el layout para la barra de búsqueda y el botón "Pagar"
        search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))

        # Añadir barra de búsqueda
        self.search_input = TextInput(hint_text='Buscar por ID, Nombre, Nota', size_hint=(1, None), height=dp(40), background_color=(0.2, 0.2, 0.2, 1), hint_text_color=(0.5, 0.5, 0.5, 1), foreground_color=(1, 1, 1, 1), multiline=False)
        self.search_input.bind(on_text_validate=self.buscar_productos)  # Vínculo de búsqueda
        self.search_input.bind(text=self.buscar_productos)  # Para la búsqueda en tiempo real
        search_layout.add_widget(self.search_input)

        # Crear el botón "Pagar"
        boton_pagar = Button(text="Pagar", size_hint_x=None, width=dp(100), background_color=(0, 1, 0, 1), on_release=self.pagar_factura)
        search_layout.add_widget(boton_pagar)

        main_layout.add_widget(search_layout)  # Añadir la barra de búsqueda y botón "Pagar" al layout principal

        recycle_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint=(1, 1))  # Crear un layout horizontal para contener ambas RecycleViews

        self.productos_recycle_view = ProductosRecycleView(size_hint=(1, 1))  # Crear y añadir la RecycleView para productos        
        recycle_layout.add_widget(self.productos_recycle_view)

        self.facturar_recycle_view = FacturarRecycleView(size_hint=(None, 1), width=dp(360))  # Crear y añadir la RecycleView para facturación         
        recycle_layout.add_widget(self.facturar_recycle_view)
        self.productos_recycle_view.set_facturar_recycle_view(self.facturar_recycle_view)

        main_layout.add_widget(recycle_layout)  # Añadir el layout de las RecycleViews al layout principal

        self.add_widget(main_layout)  # Añadir el layout principal a la pantalla


    def usuario_actual(self):
        global usuario_actual, rango_usuario 
        usuario_actual, rango_usuario = obtener_usuario_actual()



        
        self.boton_de_prueva.text = usuario_actual



    def pagar_factura(self, instance):
        self.facturar_recycle_view.mostrar_popup_factura()

    def boton_test(self, instance):
        print(f"Usuario actual: {usuario_actual}, Rango actual: {rango_usuario}")



##################################################

    def cargar_productos(self):
        self.search_input.text = ""
        if hasattr(self, 'productos_recycle_view') and self.productos_recycle_view:
            self.productos_recycle_view.data = []
            self.productos_por_categoria = obtener_productos_por_categoria_con_stock() 
            self.productos = [producto for categoria in self.productos_por_categoria.values() for producto in categoria]
            self.productos_recycle_view.actualizar_datos(self.productos)
            # Aquí estás configurando la referencia
            
            self.productos_recycle_view.set_facturar_recycle_view(self.facturar_recycle_view)
            set_products_screen(self)
        else:
            agregar_log("Error: 'productos_recycle_view' no está disponible.")



    def recargardatostablas(self):
        if hasattr(self, 'productos_recycle_view') and self.productos_recycle_view:
            self.productos_recycle_view.refresh_from_data()  # O cualquier lógica que necesites
            print("recargado la recicler")
        else:
            agregar_log("Error: 'productos_recycle_view' no está disponible.")
#########################################            

    def buscar_productos(self, instance, value):
        query = self.search_input.text.lower()  
        if query:           
            productos_filtrados = [
                producto for producto in self.productos 
                if query in producto[1].lower() or query in producto[0].lower() or query in (producto[4] or '').lower()
            ]
        else:            
            productos_filtrados = self.productos
        self.productos_recycle_view.actualizar_datos(productos_filtrados)





#########################################################################



    def open_admin_popup(self, instance):
        content = BoxLayout(orientation='vertical', padding=dp(10))

        box_admin = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(50))
        if rango_usuario in ["owner", "admin"]:
            self.btn_admin = Button(text="Administración", font_size=sp(16), size_hint_y=None, height=dp(50), background_color=(0, 0, 0, 0), color=(1, 1, 1, 1), on_release=self.pantalla_administrar)
            box_admin.add_widget(self.btn_admin)

        box_user = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(50))
        _user_info = Button(text="Información\nProductos", font_size=sp(16), bold=True, size_hint_y=None, height=dp(50), background_color=(0, 0, 0, 0), color=(1, 1, 1, 1), on_release=self.infoProductos_popup)
        box_user.add_widget(_user_info)

        box_nuevos_botones = BoxLayout(orientation='vertical', size_hint_y=1)  # Ocupa el resto del espacio
        btn_cerrar_secion = Button(text="Cerrar Sesion", size_hint_y=None, height=dp(50), background_color=(0, 0, 0, 0), color=(1, 1, 1, 1), on_release=self.cerrar_sesion)
        box_nuevos_botones.add_widget(btn_cerrar_secion)

        if rango_usuario in ["owner", "admin"]:
            content.add_widget(box_admin)
        content.add_widget(box_user)
        content.add_widget(box_nuevos_botones)

        self.popup = Popup(title="Opciones", content=content, size_hint=(None, 1), size=(dp(400), dp(300)), pos_hint={'x': -0.5, 'y': 0}, auto_dismiss=True)
        self.popup.open()
        Animation(pos_hint={'x': 0, 'y': 0}, duration=0.2).start(self.popup)



    def infoProductos_popup(self, instance):
        popup = infoProductosPopup(rango_usuario)  # Pasa el rango del usuario
        popup.open()


    def pantalla_administrar(self, *args):
        if hasattr(self, 'popup'):
            close_animation = Animation(opacity=0, duration=0.1)
            close_animation.bind(on_complete=lambda *x: self.popup.dismiss())
            close_animation.start(self.popup)

        if 'admin' not in self.manager.screen_names:
            self.manager.add_widget(AdminScreen(name='admin'))

        # Establecer admin_screen_global aquí
        set_admin_screen(self.manager.get_screen('admin'))  # Aquí se establece la variable global

        self.manager.current = 'admin' 



    def cerrar_sesion(self, instance):
        if hasattr(self, 'popup'):
            self.popup.dismiss()

        # Eliminar el LoginScreen si ya está en el ScreenManager
        if 'login' not in self.manager.screen_names:
            self.manager.add_widget(LoginScreen(name='login'))  # Añadir LoginScreen

        self.manager.current = 'login'  # Cambiar a la pantalla de inicio de sesión

































    def cambiar_factura_manera_global(self):
        global factura_pd  # Declarar que queremos usar la variable global
        factura_pd = '12'  # Cambiar el valor de la variable global
        print("Factura PD cambiada a:", factura_pd)

    def test_cambio_factura(self, dt): #quitar dt quita retraso
        self.cambiar_factura_manera_global() 
        




































































####################################### TABLA PRODUCTOS #############################################



class ProductosRecycleView(RecycleView):
    def __init__(self, **kwargs):
        super(ProductosRecycleView, self).__init__(**kwargs)
        self.data = []  # Inicializa la lista de datos
        self.bind(size=self.ajustar_columnas)  # Llama a la función de ajuste de columnas al cambiar el tamaño
        Clock.schedule_once(lambda dt: self.ajustar_columnas())  # Asegúrate de que se llame al inicio
        self.facturar_recycle_view = None  # Inicializa la referencia a FacturarRecycleView

    def actualizar_datos(self, productos):
        self.data = []
        ruta_assets = obtener_ruta_assets()        
        for producto in productos:
            image_source = producto[3]
            if image_source and os.path.exists(image_source):                
                pass
            else:                
                image_source = os.path.join(ruta_assets, 'predeterminada.jpg')
            self.data.append({
                'text': f'{producto[1]}\nPrecio: {producto[2]}',
                'image_source': image_source,
                'size_hint': (None, None),
                'size': (dp(155), dp(225)),
                'producto_id': producto[0],
                'nota': producto[4] if producto[4] else '',
                'stock_actual': str(int(producto[5])) if producto[5] else '0',
                'precio_minimo_venta': str(producto[6]) if producto[6] else '0',
                'precio_compra': str(producto[7]) if producto[7] else '0',
                'categoria': producto[8]
            })

        self.refresh_from_data()


    def ajustar_columnas(self, *args):
        ancho_recycle_view = self.width
        cols = max(1, int(ancho_recycle_view / dp(172)))
        self.ids.grid_layout.cols = cols

    def set_facturar_recycle_view(self, facturar_recycle_view):
        self.facturar_recycle_view = facturar_recycle_view



class ProductoButton(BoxLayout):
    text = StringProperty()
    image_source = StringProperty()
    color = ListProperty([1, 1, 1, 1])  # Color por defecto blanco
    producto_id = StringProperty()
    nota = StringProperty()
    stock_actual = StringProperty()
    precio_minimo_venta = StringProperty()
    precio_compra = StringProperty()
    categoria = StringProperty()


    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):            
            nombre = self.text.split('\n')[0]  # Extrae el nombre
            precio = self.text.split('Precio: ')[-1]  # Extrae el precio
            cantidad = 0 if int(self.stock_actual) <= 0 else 1 
            print(f"Producto agregado al tabla facturar: ID: {self.producto_id}, Stock actual: {self.stock_actual}, precio compra {self.precio_compra} ")
            self.agregar_producto_facturar(cantidad, self.precio_compra)
            return True 
        return super(ProductoButton, self).on_touch_down(touch)



    def agregar_producto_facturar(self, cantidad, precio_compra):
        current_widget = self.parent
        while current_widget:
            if hasattr(current_widget, 'facturar_recycle_view'):
                facturar_recycle_view = current_widget.facturar_recycle_view
                
                if isinstance(facturar_recycle_view.data, list):
                    nombre = self.text.split('\n')[0]
                    precio = self.text.split('Precio: ')[-1]

                    # Buscar si el producto ya existe en la lista
                    for producto in facturar_recycle_view.data:
                        if producto['producto_id'] == self.producto_id:
                            # Si el producto existe, verificar stock antes de incrementar
                            nuevo_stock = producto['cantidad'] + 1
                            stock_actual = int(self.stock_actual)  # Asegúrate de que stock_actual sea un entero

                            if nuevo_stock <= stock_actual:
                                # Incrementar la cantidad si no excede el stock
                                producto['cantidad'] = nuevo_stock
                                producto['text'] = f'{nombre}\nPrecio: {precio}, Cantidad: {producto["cantidad"]}'
                            break
                    else:
                        # Si el producto no existe, verificar el stock antes de agregar
                        if cantidad <= int(self.stock_actual):
                            fila_id = len(facturar_recycle_view.data)
                            facturar_recycle_view.data.append({
                                'text': f'{nombre}\nPrecio: {precio}, Cantidad: {cantidad}',
                                'fila_id': fila_id,
                                'stock_actual': self.stock_actual,
                                'precio_minimo_venta': self.precio_minimo_venta,
                                'cantidad': cantidad,
                                'producto_id': str(self.producto_id),  # Convertir a cadena aquí
                                'precio_compra': precio_compra,
                                'categoria': self.categoria 
                            })
                        # Aquí puedes manejar una situación en la que no se puede agregar, si lo deseas.
                    
                    facturar_recycle_view.refresh_from_data()
                else:
                    agregar_log("Error: 'facturar_recycle_view' no es una lista.")
                break
            
            current_widget = current_widget.parent
        else:
            agregar_log("Error: 'facturar_recycle_view' no está disponible o no es una lista.")






#######################################  TABLA FACTURAR         #########################

class FacturarRecycleView(RecycleView):
    def __init__(self, **kwargs):
        super(FacturarRecycleView, self).__init__(**kwargs)
        
        self.data = []  # Aquí irán los datos de los productos

        self.facturar_background = FacturarBackgroundColor(self)



    def mostrar_popup_factura(self):
        if not self.data:
            print("No hay datos para mostrar en la factura.")
            return
        for producto in self.data:
            if producto.get('cantidad', 0) <= 0:
                print("No se puede abrir el popup, hay productos con cantidad 0.")
                return
        factura_popup = FacturaPopup(self.data, self)  # Crear una instancia del Popup con los datos actuales
        factura_popup.open()  # Abrir el Popup



    def limpiar_tabla_facturar(self):
        current_widget = self.parent
        while current_widget:
            if hasattr(current_widget, 'facturar_recycle_view'):
                facturar_recycle_view = current_widget.facturar_recycle_view
                
                if isinstance(facturar_recycle_view.data, list):
                    facturar_recycle_view.data.clear()  # Limpiar todos los datos
                    facturar_recycle_view.refresh_from_data()  # Refrescar el RecycleView
                break
                
            current_widget = current_widget.parent
        else:
            print("Error: 'facturar_recycle_view' no está disponible o no es una lista.")



    def borrar_fila_por_id(self, fila_id):
        for i, fila in enumerate(self.data):
            if fila.get('fila_id') == fila_id:
                self.producto_id = fila.get('producto_id')
                self.cantidad_borrada = fila.get('cantidad')
                print(f'Borrando fila: {fila_id}, Producto ID: {self.producto_id}, Cantidad borrada: {self.cantidad_borrada}')             
                del self.data[i]  # Eliminar la fila de la lista
                self.refresh_from_data()  # Refrescar la vista
                return
            
        print(f'Error: Fila con ID {fila_id} no encontrada.')









#################### Filas de facturar #############################


class FacturaButton(BoxLayout):
    ruta_assets = obtener_ruta_assets()
    font_path = os.path.join(ruta_assets, 'materialicons-regular.ttf')
    text = StringProperty()
    fila_id = NumericProperty()
    stock_actual = StringProperty()
    precio_minimo_venta = StringProperty()    
    


    def __init__(self, **kwargs):
        super(FacturaButton, self).__init__(**kwargs)

    def boton_borrar(self):
        app = App.get_running_app()
        app.products_screen.facturar_recycle_view.borrar_fila_por_id(self.fila_id)


    def boton_cambiar_precio(self):
        app = App.get_running_app()
        
        # Obtener la fila correspondiente a la fila_id
        fila_seleccionada = None
        for item in app.products_screen.facturar_recycle_view.data:
            if item['fila_id'] == self.fila_id:
                fila_seleccionada = item
                break

        if fila_seleccionada:
            # Extraer el precio del texto
            precio_venta = fila_seleccionada['text'].split('Precio: ')[-1].split(',')[0].strip()
            precio_actual = precio_venta  # Aquí se usa el precio_venta extraído

            layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
            label = Label(text="Cambiar Precio")
            layout.add_widget(label)

            # Cargar el precio actual en el TextInput
            self.input_precio = TextInput(text=str(precio_actual), multiline=False, input_filter='float')
            layout.add_widget(self.input_precio)
            
            # Crear el Label para mostrar mensajes de error
            self.error_label = Label(text='', color=(1, 0, 0, 1), size_hint_y=None, height=10)
            layout.add_widget(self.error_label)

            btn_layout = BoxLayout(orientation='horizontal', spacing=10)
            btn_guardar = Button(text="Guardar")
            btn_cancelar = Button(text="Cancelar")

            btn_guardar.bind(on_release=self.verificacion_precio_guardado)
            btn_cancelar.bind(on_release=lambda *args: self.popup.dismiss())

            btn_layout.add_widget(btn_cancelar)
            btn_layout.add_widget(btn_guardar)

            layout.add_widget(btn_layout)

            self.popup = Popup(title='Cambiar Precio', content=layout, size_hint=(None, None), size=(dp(300), dp(215)))
            self.popup.open()


    def verificacion_precio_guardado(self, instance):
        nuevo_precio = self.input_precio.text
        if nuevo_precio.replace('.', '', 1).isdigit() and float(nuevo_precio) >= float(self.precio_minimo_venta):
            self.guardar_precio(instance)  # Llama al método para guardar el nuevo precio
        else:
            print(f"El precio ingresado no es válido o es menor que el precio mínimo {self.precio_minimo_venta}.")
            self.mostrar_error(f"El precio debe ser mayor o igual a {self.precio_minimo_venta}.")

    def guardar_precio(self, instance):
        nuevo_precio = float(self.input_precio.text)
        
        # Actualizar el precio en la RecycleView
        app = App.get_running_app()
        for item in app.products_screen.facturar_recycle_view.data:
            if item['fila_id'] == self.fila_id:
                # Actualizar el precio
                item['precio'] = nuevo_precio
                
                # Actualizar el texto que se muestra en la lista, si es necesario
                nombre = item['text'].split('\n')[0]
                cantidad = item.get('cantidad', '0')  # Usa '0' si no hay cantidad
                item['text'] = f'{nombre}\nPrecio: {nuevo_precio}, Cantidad: {cantidad}'  # Actualizar con el nuevo precio
                
                app.products_screen.facturar_recycle_view.refresh_from_data()  # Refrescar la vista
                break
        
        self.popup.dismiss()
        print(f"Precio actualizado a {nuevo_precio}")



############### Cambiar cantidad a vender ###############



    def boton_cambiar_cantidad(self):
        app = App.get_running_app()
        
        # Verificar si hay más de un producto agregado
        if len(app.products_screen.facturar_recycle_view.data) > 1:
            print("No se puede cambiar la cantidad, ya hay más de un producto agregado.")
            return  # No permitir cambiar la cantidad
        
        # Obtener la fila correspondiente a la fila_id
        fila_seleccionada = None
        for item in app.products_screen.facturar_recycle_view.data:
            if item['fila_id'] == self.fila_id:
                fila_seleccionada = item
                break

        if fila_seleccionada:
            cantidad_actual = fila_seleccionada.get('cantidad', '1')

            layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
            label = Label(text="Cambiar Cantidad")
            layout.add_widget(label)

            # Cargar la cantidad actual en el TextInput
            self.input_cantidad = TextInput(text=str(cantidad_actual), multiline=False, input_filter='int')
            layout.add_widget(self.input_cantidad)
            
            # Crear el Label para mostrar mensajes de error
            self.error_label = Label(text='', color=(1, 0, 0, 1), size_hint_y=None, height=10)  # Color rojo para los errores
            layout.add_widget(self.error_label)

            btn_layout = BoxLayout(orientation='horizontal', spacing=10)
            btn_guardar = Button(text="Guardar")
            btn_cancelar = Button(text="Cancelar")

            btn_guardar.bind(on_release=self.verificacion_pos_guardado)
            btn_cancelar.bind(on_release=lambda *args: self.popup.dismiss())

            btn_layout.add_widget(btn_cancelar)
            btn_layout.add_widget(btn_guardar)

            layout.add_widget(btn_layout)

            self.popup = Popup(title='Cambiar Cantidad', content=layout, size_hint=(None, None), size=(dp(300), dp(215)))
            self.popup.open()

    def mostrar_error(self, mensaje): 
        if hasattr(self, 'error_label'):
            self.error_label.text = mensaje
        else:
            pass
        Clock.schedule_once(lambda dt: setattr(self.error_label, 'text', ''), 5)  




    def verificacion_pos_guardado(self, instance):
        nueva_cantidad = self.input_cantidad.text
        if nueva_cantidad.isdigit() and int(nueva_cantidad) > 0:
            app = App.get_running_app()
            # Obtener el stock actual del item seleccionado
            stock_actual = 0
            for item in app.products_screen.facturar_recycle_view.data:
                if item['fila_id'] == self.fila_id:
                    stock_actual = int(item.get('stock_actual', '0') or 0)  # Asegúrate de manejar el caso vacío
                    break
            
            # Verificar que la nueva cantidad no exceda el stock actual
            if int(nueva_cantidad) <= stock_actual:
                self.guardar_cantidad(instance)  # Llama al método para guardar la cantidad
            else:
                 self.mostrar_error(f"cantidad, excede el stock actual: {stock_actual}.")
        else:
            self.mostrar_error("número inválido.")



    def guardar_cantidad(self, instance):
        nueva_cantidad = int(self.input_cantidad.text) 
        app = App.get_running_app()
        for item in app.products_screen.facturar_recycle_view.data:
            if item['fila_id'] == self.fila_id:
                # Actualizar la cantidad
                item['cantidad'] = nueva_cantidad
                # Actualiza el texto que se muestra en la lista, si es necesario
                nombre = item['text'].split('\n')[0]
                precio = item['text'].split('Precio: ')[-1].split(',')[0]
                item['text'] = f'{nombre}\nPrecio: {precio}, Cantidad: {nueva_cantidad}'
                app.products_screen.facturar_recycle_view.refresh_from_data()
                break
        self.popup.dismiss()




class ProductsApp(App):
    def build(self):
        return ProductsScreen()

if __name__ == "__main__":
    ProductsApp().run()
