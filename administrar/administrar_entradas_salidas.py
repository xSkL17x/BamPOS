#administrar_editar_agregar_eliminar.py
import os

import random

from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from datetime import datetime
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

from datos import conectar_db
from loggin import configurar_logger, agregar_log, agregar_log_auditoria, configurar_logger_auditoria
from extras import CalendarPopup
from cargardatos import recargar_tabla_productos, recargardatostablas




class Agregar_Entradas(Popup):
    def __init__(self, admin_screen, codigo, nombre, categoria, precio_compra, precio_venta, **kwargs): 
        super().__init__(**kwargs)
        
        self.title = 'Agregar Entrada'
        self.size = (570, 640) 
        self.size_hint = None, None  
        self.auto_dismiss = False
        self.admin_screen = admin_screen
        self.producto_seleccionado = codigo
        self.nombre_producto_seleccionado = nombre       
        self.categoria_producto_seleccionado = categoria
        self.precio_compra_producto_seleccionado = precio_compra
        self.precio_venta_producto_seleccionado = precio_venta

        layout = GridLayout(cols=1, padding=10, spacing=10)
        self.inputs = {}

        campos = [('Fecha', 'fecha'), ('Cantidad', 'cantidad'), ('Precio de Compra', 'precio_compra'), ('Precio de Venta', 'precio_venta')]

        layout.add_widget(Label(text=f"ID: {codigo}\n\n{nombre}\n", halign='center', valign='middle', size_hint=(1, None), height=80, bold=True, font_size='20sp'))

        for label_text, key in campos:
            layout.add_widget(Label(text=label_text, size_hint=(1, None), height=40, bold=True))
            
            if key == 'fecha':
                self.boton_fecha = Button(text=datetime.now().strftime('%d-%m-%Y'), size_hint=(1, None), height=50, background_color=(0.5, 0.5, 0.5, 1), color=(1, 1, 1, 1), font_size='18sp', on_release=self.mostrar_selector_fecha)
                layout.add_widget(self.boton_fecha)
                self.inputs[key] = self.boton_fecha
            
            elif key == 'precio_compra':
                # Rellenar el campo de "Precio de Compra" con el valor pasado al popup
                self.inputs[key] = TextInput(text=str(self.precio_compra_producto_seleccionado),  # Aquí cargamos el precio de compra
                                            hint_text=label_text, background_color=(0.3, 0.3, 0.3, 1),
                                            foreground_color=(1, 1, 1, 1), multiline=False, 
                                            size_hint_y=None, height=35, font_size='15sp', input_filter='float')
                layout.add_widget(self.inputs[key])

            elif key == 'precio_venta':
                # Rellenar el campo de "Precio de Venta" con el valor pasado al popup
                self.inputs[key] = TextInput(text=str(self.precio_venta_producto_seleccionado),  # Aquí cargamos el precio de venta
                                            hint_text=label_text, background_color=(0.3, 0.3, 0.3, 1),
                                            foreground_color=(1, 1, 1, 1), multiline=False, 
                                            size_hint_y=None, height=35, font_size='15sp', input_filter='float')
                layout.add_widget(self.inputs[key])

            else:
                self.inputs[key] = TextInput(hint_text=label_text, background_color=(0.3, 0.3, 0.3, 1), foreground_color=(1, 1, 1, 1), multiline=False, size_hint_y=None, height=50, font_size='18sp', input_filter='float')
                layout.add_widget(self.inputs[key])

        # Label para mostrar errores
        self.error_label = Label(text='', color=(1, 0, 0, 1), size_hint=(0.5, None), height=20, bold=True)
        layout.add_widget(self.error_label)

        botones_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        botones_layout.add_widget(Button(text='Cancelar', size_hint=(0.5, None), height=50, background_color=(1, 0, 0, 1), on_press=self.dismiss))
        botones_layout.add_widget(Button(text='Guardar', size_hint=(0.5, None), height=50, background_color=(0, 1, 0, 1), on_press=self.verificacion_pos_guardado))
        
        main_layout = BoxLayout(orientation='vertical')
        main_layout.add_widget(layout)
        main_layout.add_widget(botones_layout)
        self.content = main_layout



        ############ Inicialicaciones y errores #############
    def set_fecha(self, fecha):
        self.inputs['fecha'].text = fecha.strftime('%d-%m-%Y')

    def mostrar_error(self, mensaje): 
        if hasattr(self, 'error_label'):
            self.error_label.text = mensaje
        else:
            pass
        Clock.schedule_once(lambda dt: setattr(self.error_label, 'text', ''), 5)  

        #########   calendario    ##########
    def fecha_seleccionada(self, fecha):
        self.inputs['fecha'].text = fecha  

    def mostrar_selector_fecha(self, instance):
        CalendarPopup(parent=self).open()



    ############  Guardado  ###########


    def verificacion_pos_guardado(self, instance):
        cantidad_text = self.inputs['cantidad'].text
        precio_compra_text = self.inputs['precio_compra'].text
        precio_venta_text = self.inputs['precio_venta'].text  # Obtener el precio de venta

        # Comprobación de validación
        if not cantidad_text or not precio_compra_text or not precio_venta_text:
            self.mostrar_error('Cantidad, Precio de Compra y Precio de Venta no pueden estar vacíos.')
            return

        cantidad = float(cantidad_text)
        precio_compra = float(precio_compra_text)
        precio_venta = float(precio_venta_text)  # Convertir a float el precio de venta

        # Verificar si cantidad y precios son válidos
        if cantidad <= 0 or precio_compra <= 0 or precio_venta <= 0:
            self.mostrar_error('La cantidad y los precios deben ser mayores que cero.')
            return

        # Validar que el precio de venta no sea mayor que el de compra
        if precio_venta < precio_compra:
            self.mostrar_error('El Precio de Venta no puede ser menor que el Precio de Compra.')
            return

        
        self.guardar_entradas()




    def actualizar_stock_productos(self):
        try:
            conn, cursor = conectar_db()

            cursor.execute('SELECT stock_actual FROM productos WHERE id = ?', (self.producto_seleccionado,))
            resultado = cursor.fetchone()
            
            stock_actual = resultado[0] if resultado and resultado[0] is not None else 0
            
            cantidad_a_agregar = int(self.inputs['cantidad'].text)
            nuevo_stock = stock_actual + cantidad_a_agregar
            
            precio_compra = float(self.inputs['precio_compra'].text)  # Obtener el precio de compra del TextInput
            precio_venta = float(self.inputs['precio_venta'].text)  # Obtener el precio de venta del TextInput

            nueva_ganancia = precio_venta - precio_compra
            
            cursor.execute('UPDATE productos SET stock_actual = ?, precio_compra = ?, ganancia = ?, precio_venta = ? WHERE id = ?', 
                        (nuevo_stock, precio_compra, nueva_ganancia, precio_venta, self.producto_seleccionado))

            conn.commit()
        except Exception as e:
            print(f"Error al actualizar el stock: {e}")
        finally:
            conn.close()







    def guardar_entradas(self):
        id_transaccion = str(random.randint(10000000, 99999999))
        try:
            cantidad = int(self.inputs['cantidad'].text)
            precio_compra = float(self.inputs['precio_compra'].text)
            fecha = f"{self.inputs['fecha'].text} {datetime.now().strftime('%H:%M:%S')}"
            
            usuario = 'UsuarioEjemplo'
            dispositivos = 'DispositivoEjemplo'

            conn, cursor = conectar_db()
            cursor.execute('''
                INSERT INTO entradas (id_transaccion, id, nombre, categoria, cantidad, precio_compra, fecha, usuario, dispositivos) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (id_transaccion, self.producto_seleccionado, self.nombre_producto_seleccionado,
                self.categoria_producto_seleccionado, cantidad, precio_compra, fecha, usuario, dispositivos))

            conn.commit()
            self.actualizar_stock_productos()
            global products_screen
            global admin_screen           
            recargardatostablas()       

        except Exception:
            pass
        finally:
            conn.close()
            self.dismiss()







    def on_dismiss(self):
        super().on_dismiss()









class ConfirmDeleteEntradaPopup(Popup):
    def __init__(self, parent, admin_screen, id_transaccion, codigo, **kwargs): 
        super(ConfirmDeleteEntradaPopup, self).__init__(**kwargs)    
        self.title = "Confirmar Eliminación"
        self.size_hint = (0.6, 0.4)
        self.size = (400, 200)  # Establecer tamaño específico en píxeles
        self.size_hint = None, None  # Desactivar el ajuste de tamaño relativo
        self.auto_dismiss = False
        self.admin_screen = admin_screen
        self.parent_window = parent        
        self.id_transaccion_seleccionada=id_transaccion
        self.producto_seleccionado=codigo
        self.popup_instance = self
        configurar_logger()  


        content = BoxLayout(orientation='vertical', padding=10)
        message = Label(text=f"¿Estás seguro que quieres eliminar el producto con código '{id_transaccion}'?", size_hint_y=None, halign='center', valign='middle', text_size=(self.width - 20, None))

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
        try:
            conn, cursor = conectar_db()

            cursor.execute("SELECT cantidad FROM entradas WHERE id_transaccion = ?", (self.id_transaccion_seleccionada,))
            entrada = cursor.fetchone()

            if entrada:
                cantidad = int(entrada[0])
                cursor.execute("SELECT stock_actual FROM productos WHERE id = ?", (self.producto_seleccionado,))
                producto = cursor.fetchone()

                if producto:
                    stock_actual = producto[0]
                    nuevo_stock = max(0, (stock_actual if stock_actual is not None else 0) - cantidad)

                    cursor.execute("UPDATE productos SET stock_actual = ? WHERE id = ?", (nuevo_stock, self.producto_seleccionado))
                    conn.commit()

                cursor.execute("DELETE FROM entradas WHERE id_transaccion = ?", (self.id_transaccion_seleccionada,))
                conn.commit()

            cursor.close()
            conn.close()

            self.admin_screen.cargar_entradas_en_tabla()
            global products_screen
            recargar_tabla_productos()            

            agregar_log_auditoria(f"Entrada con ID {self.id_transaccion_seleccionada} eliminada. de Producto con ID {self.producto_seleccionado}, Cantidad eliminada: {cantidad}, Nuevo stock: {nuevo_stock}.")
            self.cerrar_popup(instance)

        except Exception as e:
            agregar_log(f"Error al eliminar la entrada o actualizar el stock: {e}")
            if cursor:
                cursor.close()
            if conn:
                conn.close()





    def cerrar_popup(self, instance):
        self.dismiss()  
        if hasattr(self, 'popup_instance'):           
            del self.popup_instance  









########################### salidas ################

class ConfirmDeleteSalidasPopup(Popup):
    def __init__(self, parent, admin_screen, id_transaccion, codigo, **kwargs): 
        super(ConfirmDeleteSalidasPopup, self).__init__(**kwargs)    
        self.title = "Confirmar Eliminación"
        self.size_hint = (0.6, 0.4)
        self.size = (400, 200)  # Establecer tamaño específico en píxeles
        self.size_hint = None, None  # Desactivar el ajuste de tamaño relativo
        self.auto_dismiss = False
        self.admin_screen = admin_screen
        self.parent_window = parent        
        self.id_transaccion_seleccionada=id_transaccion
        self.producto_seleccionado=codigo
        self.popup_instance = self
        configurar_logger()  
        configurar_logger_auditoria()


        content = BoxLayout(orientation='vertical', padding=10)
        message = Label(text=f"¿Estás seguro que quieres eliminar entrada '{id_transaccion}' el producto con código '{codigo}', idtran?", size_hint_y=None, halign='center', valign='middle', text_size=(self.width - 20, None))

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
        try:
            conn, cursor = conectar_db()

            # Buscar la entrada con la ID proporcionada
            cursor.execute("SELECT cantidad FROM salidas WHERE id_venta = ?", (self.id_transaccion_seleccionada,))
            entrada = cursor.fetchone()
            if entrada:
                cantidad = int(entrada[0])
                cursor.execute("SELECT stock_actual FROM productos WHERE id = ?", (self.producto_seleccionado,))
                producto = cursor.fetchone()
                if producto:
                    stock_actual = producto[0]
                    nuevo_stock = max(0, (stock_actual if stock_actual is not None else 0) + cantidad)

                    # Actualizar el stock en la tabla 'productos'
                    cursor.execute("UPDATE productos SET stock_actual = ? WHERE id = ?", (nuevo_stock, self.producto_seleccionado))
                    conn.commit()

                # Eliminar la entrada después de actualizar el stock
                cursor.execute("DELETE FROM salidas WHERE id_venta = ?", (self.id_transaccion_seleccionada,))
                conn.commit()

                # Actualizar la tabla de salidas
                
            cursor.close()
            conn.close()


            self.admin_screen.cargar_salidas_en_tabla()  
            global products_screen
            recargar_tabla_productos()                                    
            agregar_log_auditoria(f"Venta eiminada  con ID de transacción: {self.id_transaccion_seleccionada} del Producto con ID {self.producto_seleccionado}, Cantidad eliminada: {cantidad}, Nuevo stock: {nuevo_stock}.")
            self.cerrar_popup(instance)

        except Exception as e:
            agregar_log(f"Error al eliminar la entrada o actualizar el stock: {e}")
            if cursor:
                cursor.close()
            if conn:
                conn.close()




    def cerrar_popup(self, instance):
        self.dismiss()  
        if hasattr(self, 'popup_instance'):           
            del self.popup_instance  
