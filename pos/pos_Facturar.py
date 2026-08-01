# factura.py
from cargardatos import recargar_tabla_productos
from extras import opcion_imprimir_tickets_dispositivo, opcion_imprimir_Factura_dispositivo
from inicio_sesion import obtener_usuario_actual
from datos import  conectar_db, obtener_ruta_assets
from configs import obtener_info_dispositivo, obtener_nombre_negocio,obtener_telefono_empresa,obtener_direccion_empresa, obtener_imprimir_facturas, obtener_imprimir_ticket
from loggin import configurar_logger, agregar_log


from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from datetime import datetime
import textwrap
from kivy.metrics import dp  
from kivy.graphics import Color, Rectangle
from kivy.uix.image import Image
import os




####### assets #######
ruta_assets = obtener_ruta_assets()
billete_assets = os.path.join(ruta_assets, 'billete.png')
venta_realizada_assets = os.path.join(ruta_assets, 'venta_realizada.png')     

####### detalles a factura #############
fecha_actual = f'Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'

class FacturaPopup(Popup):
    def __init__(self, data, facturar_recycle_view, **kwargs):
        super(FacturaPopup, self).__init__(**kwargs)
        
        self.no_facturas = self.obtener_ultimo_no_factura()      
        
        self.data = data
        self.facturar_recycle_view = facturar_recycle_view
        self.total = 0
        self.vuelto_label = None
        
        self.title = 'Factura'
        self.size_hint = (None, None)
        self.size = (880, 580)
        self.auto_dismiss = False
        
        self.content = self.crear_contenido()
        configurar_logger()

    def crear_contenido(self):
        layout = BoxLayout(orientation='horizontal', padding=[10, 10])
        izquierdo_layout = BoxLayout(orientation='vertical', size_hint=(0.5, 1))
        encabezado_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        encabezados = ['Producto', 'Cantidad', 'Precio', 'Total']
        anchos = [0.4, 0.2, 0.2, 0.4]

        for encabezado_text, ancho in zip(encabezados, anchos):
            encabezado_label = Label(text=encabezado_text, bold=True, color=(1, 1, 0, 1), font_size='16sp', size_hint_x=ancho)
            encabezado_label.bind(size=encabezado_label.setter('text_size'))
            encabezado_label.halign = 'center'
            encabezado_label.valign = 'middle'
            encabezado_layout.add_widget(encabezado_label)

        izquierdo_layout.add_widget(encabezado_layout)
        scrollview = ScrollView(size_hint=(1, 1))
        productos_layout = GridLayout(cols=4, size_hint_y=None, padding=[0, dp(10)], spacing=dp(20))
        productos_layout.bind(minimum_height=productos_layout.setter('height'))

        with scrollview.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.scroll_rect = Rectangle(size=scrollview.size, pos=scrollview.pos)

        scrollview.bind(size=lambda instance, value: setattr(self.scroll_rect, 'size', instance.size))
        scrollview.bind(pos=lambda instance, value: setattr(self.scroll_rect, 'pos', instance.pos))

        for producto in self.data:
            nombre = producto['text'].split('\n')[0]
            cantidad = producto.get('cantidad', 1)
            precio_venta = float(producto['text'].split('Precio: ')[-1].split(',')[0].strip())
            total_producto = precio_venta * cantidad
            self.total += total_producto
            nombre_envuelto = textwrap.fill(nombre, width=15)

            productos_layout.add_widget(Label(text=nombre_envuelto, halign='center', valign='middle', size_hint_x=0.5, size_hint_y=None, height=dp(40)))
            productos_layout.add_widget(Label(text=str(cantidad), size_hint_y=None, size_hint_x=0.2, height=dp(40)))
            productos_layout.add_widget(Label(text=f"${precio_venta:.2f}", size_hint_x=0.2, size_hint_y=None, height=dp(40)))
            productos_layout.add_widget(Label(text=f"${total_producto:.2f}", size_hint_x=0.5, size_hint_y=None, height=dp(40)))

        scrollview.add_widget(productos_layout)
        izquierdo_layout.add_widget(scrollview)

        derecha_layout = BoxLayout(orientation='vertical', size_hint=(0.5, 1), padding=dp(10))
        informacion = BoxLayout(orientation='vertical', size_hint_y=None)
        imagen_billete = Image(source=billete_assets, size_hint=(1, None), height=dp(100))
        informacion.add_widget(imagen_billete)
        self.total_pagar_label = Label(text=f"Total a pagar:  ${self.total:.2f}", size_hint_y=None, height=dp(80), bold=True, font_size='26sp')
        informacion.add_widget(self.total_pagar_label)
        informacion.add_widget(Label(text="", size_hint_y=None, height=dp(80)))
        self.pagado_input = TextInput(size_hint_y=None, height=dp(60), halign='center', font_size='30sp', multiline=False, input_filter='float', foreground_color=(0.7, 0.7, 0.7, 1), background_color=(0.3, 0.3, 0.3, 1))
        self.pagado_label = Label(text='Vuelto: $0.00', size_hint_y=None, font_size='22sp', height=dp(60))
        informacion.add_widget(Label(text='Pagado con:', size_hint_y=None, height=dp(60)))
        informacion.add_widget(self.pagado_input)
        informacion.add_widget(self.pagado_label)
        derecha_layout.add_widget(informacion)



        # Botones
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        cancelar_button = Button(text='Cancelar', size_hint_x=0.5, on_release=self.dismiss, background_color=(1, 0.5, 0, 1))
        pagar_button = Button(text='Pagar', size_hint_x=0.5, on_release=lambda x: self.guardar_salida(x, derecha_layout, informacion, button_layout), background_color=(0, 1, 0, 1))
        button_layout.add_widget(cancelar_button)
        button_layout.add_widget(pagar_button)

        derecha_layout.add_widget(button_layout)

        self.pagado_input.bind(text=self.calcular_vuelto)
        self.vuelto_label = self.pagado_label

        layout.add_widget(izquierdo_layout)
        layout.add_widget(derecha_layout)

        return layout



    def mandar_tickets_imprimir(self):
        #ancho en caracteres
        ancho_centrado = 32
        producto_ancho = int(ancho_centrado * 0.47)  # 47%
        cantidad_ancho = int(ancho_centrado * 0.18)  # 18%
        total_ancho = int(ancho_centrado * 0.35)     # 35%
        #variables del negocio
        nombre_negocio = obtener_nombre_negocio()
        direccion_negocio = textwrap.fill(obtener_direccion_empresa(), width=25, replace_whitespace=False)
        direccion_negocio = '\n'.join(linea.center(ancho_centrado) for linea in direccion_negocio.split('\n'))
        telefono_negocio = f"Telefono: {obtener_telefono_empresa()}"


        ##Tabla Productos
        encabezado = f"{'Producto':^{producto_ancho}}{'Cantidad':^{cantidad_ancho}}{'Total':^{total_ancho}}"
       # encabezado += "\n" + "-" * ancho_centrado  # Línea de separación

        encabezado += "-" * 30 + "\n"  
        tabla_productos = encabezado


        total_texto = "-" * 30 + "\n" 
        total_texto += (f"        TOTAL  : ${self.total_pagar_label.text.split('$')[-1]}\n\n"  
                        f"      Pagado con : ${self.pagado_input.text if self.pagado_input.text else '0.00'}\n"  # Sin centrar "Pagado con"
                        f"        {self.pagado_label.text}"  # Sin centrar la etiqueta
                        )        

        for producto in self.data:
            nombre = textwrap.fill(producto['text'].split('\n')[0], width=15)
            nombre = '\n'.join(line.ljust(15) for line in nombre.split('\n'))                    
            cantidad = producto.get('cantidad', 1)
            precio_venta = float(producto['text'].split('Precio: ')[-1].split(',')[0].strip())     
            total_producto = precio_venta * cantidad

            tabla_productos += f"{nombre:<{producto_ancho}} {cantidad:^{cantidad_ancho}} {total_producto:^{total_ancho}}\n\n"
            

                                

        ## Orden Contenido a imprimir
        contenido_factura = f"{nombre_negocio:^{ancho_centrado}}\n\n" 
        contenido_factura += f"{direccion_negocio}\n" 
        contenido_factura += f"{telefono_negocio:^{ancho_centrado}}\n\n" 
        contenido_factura += f"{fecha_actual}\n"  
        contenido_factura += f"No: {self.no_facturas}\n\n"  
        contenido_factura += tabla_productos 
        contenido_factura += total_texto
        
        contenido_factura += "\n" + "-" * 30 + "\n\n"  


        opcion_imprimir_tickets_dispositivo(contenido_factura)







    def guardar_salida(self, instance, derecha_layout, informacion, button_layout):
        for widget in button_layout.children:
            if isinstance(widget, Button) and widget.text == 'Pagar':
                widget.disabled = True  # Desactivar el botón
                break               
        self.pagado_input_value = None
        for widget in informacion.children:
            if isinstance(widget, TextInput):
                self.pagado_input_value = widget.text
                break

        # Verificar si el valor pagado es menor que el total
        if self.pagado_input_value and float(self.pagado_input_value) < self.total:
            # Limpiar el TextInput
            for widget in informacion.children:
                if isinstance(widget, TextInput):
                    widget.text = ''
            return 
        
        for widget in derecha_layout.children:
            if isinstance(widget, BoxLayout):  
                for child in widget.children:
                    if isinstance(child, Image):  # Verificamos si es una imagen
                        child.source = venta_realizada_assets  # Cambiar la fuente de la imagen
                        child.reload()  
                        break 

        self.guardar_productos_en_db()
        button_layout.clear_widgets()
        button_layout.orientation = 'vertical'
        button_layout.height = dp(100)
        self.error_label = Label(text='', size_hint_y=None, height=dp(30), color=(1, 0.5, 0.5, 1), font_size='18sp', bold=True)        
        self.imprimir_recibo_button = Button(text='Imprimir Factura', size_hint_y=None, height=dp(50), background_color=(0.2, 0.3, 1, 1), on_release=lambda instance: self.imprimir_documento(instance, "factura"))
        self.imprimir_button = Button(text='Imprimir Ticket', size_hint_y=None, height=dp(50), background_color=(0.5, 0.8, 1, 1), on_release=lambda instance: self.imprimir_documento(instance, "ticket"))
        cerrar_button = Button(text='Cerrar', size_hint_y=None, height=dp(50), background_color=(0, 1, 0, 1), on_release=self.cerrar_popup)
        
        #button_layout.add_widget(self.imprimir_recibo_button)
        button_layout.add_widget(self.imprimir_button)
        button_layout.add_widget(cerrar_button)
        button_layout.add_widget(self.error_label)       
        self.limpiar_informacion_ventana(informacion)


    def imprimir_documento(self, instance, tipo_documento): 
        if tipo_documento == "factura":
            if obtener_imprimir_facturas() == "desactivada":
                self.error_label.text = "Impresora de Factura desactivada"
                Clock.schedule_once(lambda dt: setattr(self.error_label, 'text', ''), 3)
                self.imprimir_recibo_button.disabled = True
                return  
            self.mandar_factura_imprimir()
            
        elif tipo_documento == "ticket":
            if obtener_imprimir_ticket() == "desactivada":
                self.error_label.text = "Impresora de ticket desactivada"
                Clock.schedule_once(lambda dt: setattr(self.error_label, 'text', ''), 3)
                self.imprimir_button.disabled = True
                return  
            self.mandar_tickets_imprimir()
























    def mandar_factura_imprimir(self):
        # Encabezado de la tabla de productos
        tabla_productos = f"{'Producto':<25}{'Cantidad':<10}{'Precio':<10}{'Total':<10}\n"
        tabla_productos += f"{'=' * 55}\n"  # Separador para la tabla

        for producto in self.data:
            nombre = producto['text'].split('\n')[0]  # Nombre completo
            cantidad = producto.get('cantidad', 1)
            precio_venta = float(producto['text'].split('Precio: ')[-1].split(',')[0].strip())
            total_producto = precio_venta * cantidad
            tabla_productos += f"{nombre:<25}{cantidad:<10}{precio_venta:<10.2f}{total_producto:<10.2f}\n"

        # Total de la factura
        total_factura = f"\n{'Total:':<35}${self.total:.2f}\n"

        # Combina todo en contenido final
        contenido_factura = tabla_productos + total_factura

        # Imprimir la factura en la terminal
        opcion_imprimir_Factura_dispositivo(contenido_factura)






#afacturar.py


            

################## Funciona pero me centra las lineas que se dividen en 2
    # def mandar_recibo_imprimir(self): 
    #     datos_negocio = [
    #         obtener_nombre_negocio(), 
    #         "",
    #         textwrap.fill(obtener_direccion_empresa(), width=25, replace_whitespace=False), 
    #         "",
    #         f"Telefono: {obtener_telefono_empresa()}",  
    #         ""
    #     ]    

    #     # Crear encabezados centrados
    #     encabezados = ['   Producto    ', 'Cantidad', '    Precio   ', 'Total']
    #     encabezados_texto = " | ".join(encabezados)



    #     productos_texto = []
    #     for producto in self.data:
    #         nombre = textwrap.fill(producto['text'].split('\n')[0], width=15)
    #         lineas = nombre.split('\n')
    #         cantidad_imprimir = str(producto.get('cantidad', 1)).ljust(6, ' ') if len(str(producto.get('cantidad', 1))) < 6 else str(producto.get('cantidad', 1))
    #         precio_venta = float(producto['text'].split('Precio: ')[-1].split(',')[0].strip())     
    #         precio_venta_imprimir = "{:.2f}".format(precio_venta).ljust(9, ' ') if len("{:.2f}".format(precio_venta)) < 9 else "{:.2f}".format(precio_venta)
    #         total_producto = precio_venta * producto.get('cantidad', 1)

    #         if len(lineas[0]) < 15:
    #             lineas[0] = lineas[0].ljust(15, ' ')
    #         if len(lineas) > 1 and len(lineas[1]) < 15:
    #             lineas[1] = lineas[1].ljust(15, ' ')
    #         nombre = '\n'.join(lineas)        

    #         productos_texto.append(f"{nombre} |   {cantidad_imprimir} |   ${precio_venta_imprimir}  | ${total_producto:.2f}")

    #     # Unir todas las partes en un solo texto para imprimir
    #     factura_texto = "\n".join([f'{fecha_actual}\nNo: {factura_no}\n\n'] + datos_negocio + ['', encabezados_texto, ''] + productos_texto + ['', total_texto])
        
    #     # Imprimir
    #     opcion_imprimir_dispositivo(factura_texto)

























    def obtener_ultimo_no_factura(self):
        conn, cursor = conectar_db()
        ultimo_no_factura = cursor.execute("SELECT no_factura FROM facturas WHERE id = 1").fetchone()[0] + 1
        conn.close()
        return ultimo_no_factura





#############  👍👍👍👍👍👍👍👍👍👍👍👍👍 ##############


    def guardar_productos_en_db(self):
        usuario = obtener_usuario_actual()[0]
        dispositivo = obtener_info_dispositivo()
        fecha_actuals = datetime.now().strftime("%d-%m-%Y %H:%M:%S")        

        conn, cursor = conectar_db()
        productos = self.data

        for producto in productos:
            try:
                nombre = producto['text'].split('\n')[0]
                precio_venta = producto['text'].split('Precio: ')[-1].split(',')[0].strip()
                precio_compra = float(producto['precio_compra'])
                cantidad_vendida = producto.get('cantidad', 1)
                categoria = producto.get('categoria')
                ganancia_total = (float(precio_venta.replace(',', '.')) - precio_compra) * cantidad_vendida
                id_venta = f"venta_{fecha_actuals}_{producto['fila_id']}"
                producto_id = producto.get('producto_id', "")

                cursor.execute('''SELECT stock_actual FROM productos WHERE id = ?''', (producto_id,))
                stock_actual = cursor.fetchone()

                if stock_actual and stock_actual[0] >= cantidad_vendida:
                    cursor.execute(''' 
                        INSERT INTO salidas (id_venta, fecha, id_producto, nombre, categoria, precio_venta, 
                        cantidad, ganancia_total, cliente, estado, n_factura, usuario, dispositivos)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                        id_venta, fecha_actuals, producto_id, nombre, categoria, float(precio_venta.replace(',', '.')),
                        cantidad_vendida, ganancia_total, " ", "Vendido", self.no_facturas, usuario, dispositivo
                    ))

                    # Actualizamos el stock del producto
                    cursor.execute('''UPDATE productos SET stock_actual = stock_actual - ? WHERE id = ?''', 
                                (cantidad_vendida, producto_id))

            except Exception as e:
                agregar_log("Error al guardar el producto:", e)

        # Actualizamos el número de factura una vez que todos los productos se han guardado
        cursor.execute('UPDATE facturas SET no_factura = ? WHERE id = 1', (self.no_facturas,))

        conn.commit()
        conn.close()

        global products_screen
        recargar_tabla_productos()






#############  👍👍👍👍👍👍👍👍👍👍👍👍👍 ##############

    def limpiar_informacion_ventana(self, informacion):
        self.pagado_input_value = None 

        for widget in informacion.children[:]:  # Iterar sobre una copia de los widgets
            if isinstance(widget, Label) and widget.text == 'Pagado con:':
                informacion.remove_widget(widget)
            elif isinstance(widget, TextInput):
                self.pagado_input_value = widget.text  # Guardar el valor del input
                informacion.remove_widget(widget)
            elif isinstance(widget, Label) and widget.text == 'Vuelto: $0.00':
                informacion.remove_widget(widget)  # Eliminar el label de vuelto si su valor es $0.00

        if self.pagado_input_value:
            nuevo_label = Label(text=f'Pagado: C$ {self.pagado_input_value}', size_hint_y=None, height=40)
            informacion.add_widget(nuevo_label)        



    def calcular_vuelto(self, instance, value):
        try:
            pagado = float(value)
            vuelto = pagado - self.total
            
            # Si el vuelto es negativo, mostrar como $0.00
            if vuelto < 0:
                self.vuelto_label.text = 'Vuelto: $0.00'
            else:
                self.vuelto_label.text = f'Vuelto: ${vuelto:.2f}'
        except ValueError:
            self.vuelto_label.text = 'Vuelto: $0.00'



    def cerrar_popup(self, *args):
        self.facturar_recycle_view.limpiar_tabla_facturar()  
        self.dismiss()    