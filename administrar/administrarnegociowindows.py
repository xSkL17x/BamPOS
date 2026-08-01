# negocio.py
import os
import sqlite3
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.metrics import dp, sp
from kivy.uix.scrollview import ScrollView

from kivy.uix.button import Button
from kivy.clock import Clock


from datos import obtener_ruta_assets
from cargardatos import conectar_db_config
from configs import cargar_datos_impresion, obtener_imprimir_facturas, obtener_imprimir_ticket, cargar_datos_empresa, obtener_nombre_negocio, obtener_direccion_empresa, obtener_telefono_empresa, obtener_correo_empresa
from imagenes import cambiar_logo_empresa
from administrar.seleccionimpresora import open_printer_selection

class ConfigNegocio(BoxLayout):
    ruta_assets = obtener_ruta_assets()
    font_path = os.path.join(ruta_assets, 'materialicons-regular.ttf')
    obtener_logo = os.path.join(ruta_assets, 'logo.png')
    obtener_logo_empresa = os.path.join(ruta_assets, 'logo_empresa.png')
    empresa_icono = os.path.join(ruta_assets, 'empresa.png') 



    def __init__(self, admin_screen_instance, **kwargs):
        super().__init__(orientation='vertical', padding=dp(10), spacing=dp(10), **kwargs)
        self.admin_screen_instance = admin_screen_instance  # Guardar referencia a AdminScreen
        self.config_negocio()
        cargar_datos_empresa() 


    def config_negocio(self):
        self.admin_screen_instance.area_principal.clear_widgets()


        scroll_view = ScrollView(do_scroll_x=False, do_scroll_y=False, size_hint=(None, 1), size=(dp(600), self.admin_screen_instance.area_principal.height))

        layout_encabezado = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        layout_encabezado.add_widget(Label(text='[b]Opciones\nde Negocio[/b]', size_hint=(None, 1), width=dp(150), font_size=sp(24), markup=True, color=(0.7, 0.7, 0.7, 1)))
        layout_encabezado.add_widget(Image(source=self.empresa_icono, size_hint_x=None, size_hint_y=1, width=dp(80)))

        layout_contenido = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(15), size_hint_y=None)
        layout_contenido.bind(minimum_height=layout_contenido.setter('height'))

        logo_label = Label(text='Logo', size_hint_y=None, height=dp(20))
        logo_image = Image(source=self.obtener_logo_empresa, size_hint_y=None, height=dp(256))
        cambiar_logo_btn = Button(text='Cambiar Logo', size_hint_x=0.3, size_hint_y=None, height=dp(30), 
                           on_press=lambda x: cambiar_logo_empresa(self.espacio_label, logo_image))



        negocio_label = Label(text="Nombre del negocio", size_hint_y=None, height=dp(20), halign='left', valign='middle')
        self.negocio_input = TextInput(text=obtener_nombre_negocio(), multiline=False, size_hint_y=None, height=dp(30), background_color=(0.3, 0.3, 0.3, 1), foreground_color=(1, 1, 1, 1))

        direccion_label = Label(text="Dirección", size_hint_y=None, height=dp(20), halign='left', valign='middle')
        self.direccion_input = TextInput(text=obtener_direccion_empresa(), multiline=False, size_hint_y=None, height=dp(30), background_color=(0.3, 0.3, 0.3, 1), foreground_color=(1, 1, 1, 1))

        telefono_label = Label(text="Teléfono", size_hint_y=None, height=dp(20), halign='left', valign='middle')
        self.telefono_input = TextInput(text=obtener_telefono_empresa(), multiline=False, size_hint_y=None, height=dp(30), background_color=(0.3, 0.3, 0.3, 1), foreground_color=(1, 1, 1, 1))

        correo_label = Label(text="Correo electrónico", size_hint_y=None, height=dp(20), halign='left', valign='middle')
        self.correo_input = TextInput(text=obtener_correo_empresa(), multiline=False, size_hint_y=None, height=dp(30), background_color=(0.3, 0.3, 0.3, 1), foreground_color=(1, 1, 1, 1))

        self.espacio_label = Label(text='', size_hint_y=None, height=dp(10))

        guardar_cambios_btn = Button(text='Guardar Cambios', size_hint_x=0.3, size_hint_y=None, height=dp(40), on_press=self.guardar_datos_de_negocio)

        layout_contenido.add_widget(logo_label)
        layout_contenido.add_widget(logo_image)
        layout_contenido.add_widget(cambiar_logo_btn)        
        layout_contenido.add_widget(negocio_label)
        layout_contenido.add_widget(self.negocio_input)
        layout_contenido.add_widget(direccion_label)
        layout_contenido.add_widget(self.direccion_input) 
        layout_contenido.add_widget(telefono_label)
        layout_contenido.add_widget(self.telefono_input)  
        layout_contenido.add_widget(correo_label)
        layout_contenido.add_widget(self.correo_input)
        layout_contenido.add_widget(self.espacio_label)
        layout_contenido.add_widget(guardar_cambios_btn)

        scroll_view.add_widget(layout_contenido)

        self.admin_screen_instance.area_principal.add_widget(layout_encabezado)
        self.admin_screen_instance.area_principal.add_widget(scroll_view)






    def guardar_datos_de_negocio(self, instance):
        conn, cursor = conectar_db_config()
        try:
            nombre_negocio = self.negocio_input.text
            direccion = self.direccion_input.text
            telefono = self.telefono_input.text
            correo = self.correo_input.text
            cursor.execute("""UPDATE configuraciones SET valor1 = ?, valor2 = ?, valor3 = ?, valor4 = ? WHERE accion = 'config negocio'""", (nombre_negocio, direccion, telefono, correo))
            conn.commit()
            self.espacio_label.text = "Datos de negocio actualizados correctamente."
            cargar_datos_empresa()
            Clock.schedule_once(lambda dt: setattr(self.espacio_label, 'text', ''), 5)  # Borrar mensaje después de 3 segundos
        except sqlite3.Error as e:
            self.espacio_label.text = f"Error al guardar los datos de la empresa: {e}"
        finally:
            if conn:
                conn.close()


















class Configwindows(BoxLayout):
    
    ruta_assets = obtener_ruta_assets()
    windows_icono = os.path.join(ruta_assets, 'windows.png')
    font_path = os.path.join(ruta_assets, 'materialicons-regular.ttf')    

    def __init__(self, admin_screen_instance, **kwargs):
        super().__init__(orientation='vertical', padding=dp(10), spacing=dp(10), **kwargs)
        self.admin_screen_instance = admin_screen_instance  # Guardar referencia a AdminScreen
        self.config_negocio()

    def config_negocio(self):
        self.admin_screen_instance.area_principal.clear_widgets()

        scroll_view = ScrollView(do_scroll_x=False, do_scroll_y=False, size_hint=(None, 1), size=(dp(600), self.admin_screen_instance.area_principal.height))

        layout_encabezado = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        layout_encabezado.add_widget(Label(text='[b]Opciones\nde Windows[/b]', size_hint=(None, 1), width=dp(150), font_size=sp(24), markup=True, color=(0.7, 0.7, 0.7, 1)))
        layout_encabezado.add_widget(Image(source=self.windows_icono, size_hint_x=None, size_hint_y=1, width=dp(80)))

        layout_contenido = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(50), size_hint_y=None)
        layout_contenido.bind(minimum_height=layout_contenido.setter('height'))

        Opciones_imprecion_label = Label(text='Opciones de Impresoras', size_hint_y=None, height=dp(20), valign='middle')

        # Centrar labels y botones en el mismo BoxLayout
        impresoras_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        
        Impresora_Ticket_label = Label(text="[b]Impresora Ticket[/b]\n(formato RAW)", size_hint_x=0.5, halign='left', valign='middle', markup=True, font_size=sp(16))

        self.Impresora_Ticket_boton = Button(text=obtener_imprimir_ticket(), size_hint_x=0.5, height=dp(40), background_color=(0.5, 0.5, 0.5, 1), 
                                              on_press=lambda x: open_printer_selection(self.update_printer_button_ticket))  # Gris oscuro
        test_impresora_Ticket_boton =  Button(text='description', size_hint_x=0.05, height=dp(20), background_color=(0.5, 0.5, 0.5, 1), font_name=self.font_path)

        impresoras_layout.add_widget(Impresora_Ticket_label)
        impresoras_layout.add_widget(self.Impresora_Ticket_boton)
        impresoras_layout.add_widget(test_impresora_Ticket_boton)

        impresoras_factura_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        
        Impresora_factura_label = Label(text="[b]Impresora de Facturas[/b]", size_hint_x=0.5, halign='left', valign='middle', markup=True, font_size=sp(16))
        self.Impresora_factura_boton = Button(text=obtener_imprimir_facturas(), size_hint_x=0.5, height=dp(40), background_color=(0.5, 0.5, 0.5, 1), 
                                               on_press=lambda x: open_printer_selection(self.update_printer_button_factura)) 

        test_impresora_factura_boton =  Button(text='description', size_hint_x=0.05, height=dp(20), background_color=(0.5, 0.5, 0.5, 1), font_name=self.font_path)        

        impresoras_factura_layout.add_widget(Impresora_factura_label)
        impresoras_factura_layout.add_widget(self.Impresora_factura_boton)
        impresoras_factura_layout.add_widget(test_impresora_factura_boton)

        self.espacio_label = Label(text='', size_hint_y=None, height=dp(10))

        guardar_cambios_btn = Button(text='Guardar Cambios', size_hint_x=0.3, size_hint_y=None, height=dp(40), on_press=self.guardar_nuevas_impresoras)

        layout_contenido.add_widget(Opciones_imprecion_label)    
        layout_contenido.add_widget(impresoras_layout)  # Añadir layout de impresoras
        layout_contenido.add_widget(impresoras_factura_layout)  # Añadir layout de impresoras de factura
        layout_contenido.add_widget(self.espacio_label)
        layout_contenido.add_widget(guardar_cambios_btn)

        scroll_view.add_widget(layout_contenido)

        self.admin_screen_instance.area_principal.add_widget(layout_encabezado)
        self.admin_screen_instance.area_principal.add_widget(scroll_view)


    def update_printer_button_ticket(self, printer_name):
        self.Impresora_Ticket_boton.text = printer_name

    def update_printer_button_factura(self, printer_name):
        self.Impresora_factura_boton.text = printer_name


    def guardar_nuevas_impresoras(self, instance):
        impresora_ticket = self.Impresora_Ticket_boton.text
        impresora_factura = self.Impresora_factura_boton.text

        if impresora_ticket == "Desactivar impresora":
            impresora_ticket = "desactivada"
        if impresora_factura == "Desactivar impresora":
            impresora_factura = "desactivada"        


        if (obtener_imprimir_ticket() == impresora_ticket and
            obtener_imprimir_facturas() == impresora_factura):
            return             

        conn, cursor = conectar_db_config()
        try:
            # Actualizar la base de datos con las nuevas impresoras
            cursor.execute("UPDATE configuraciones SET valor1 = ?, valor2 = ? WHERE accion = 'impresoras'", (impresora_ticket, impresora_factura))            
            conn.commit()

            self.espacio_label.text = "Impresoras actualizadas"
            cargar_datos_impresion()
        except sqlite3.Error as e:
            self.espacio_label.text = f"Error al actualizar las impresoras: {e}"
        finally:
            if conn:
                conn.close()
