import os
import sqlite3
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import sp, dp
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle
from cargardatos import obtener_usuarios_db, conectar_db_config
from loggin import configurar_logger, configurar_logger_auditoria, agregar_log, agregar_log_auditoria
from datos import obtener_ruta_assets
from kivy.uix.image import Image
#administrarusuarios.py

usuario_seleccionado = None

class ListaUsuarios(BoxLayout):

    ruta_assets = obtener_ruta_assets()
    usuarios_icono = os.path.join(ruta_assets, 'usuarios.png')
    font_path = os.path.join(ruta_assets, 'materialicons-regular.ttf')    
    def __init__(self, admin_screen_instance, **kwargs):
        super(ListaUsuarios, self).__init__(orientation='vertical', **kwargs)
        self.admin_screen_instance = admin_screen_instance
        self.setup_layout()
        configurar_logger()
        configurar_logger_auditoria()


    def setup_layout(self):
        self.admin_screen_instance.area_principal.clear_widgets()

        # Layout de botones con fondo gris oscuro
        layout_botones_usuarios = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))

        
        espacio_texto = Label(text='[b]Administrar\nUsuarios[/b]', size_hint=(None, 1), width=dp(50), font_size=sp(14), markup=True, color=(0.7, 0.7, 0.7, 1))
        espacio_logo = Image(source=self.usuarios_icono, size_hint_x=None, size_hint_y=1, width=dp(80))        
        espacio_vacio = Label(text='|', size_hint=(None, 1), width=dp(50), color=(0.7, 0.7, 0.7, 1))


        btn_agregar_usuario = Button(text='add_circle', size_hint_x=None, width=dp(100), background_color=(1, 1, 1, 0), font_size='20sp', bold=True, font_name=self.font_path)
        btn_agregar_usuario.bind(on_release=lambda x: self.abrir_popup_agregar_usuario())

        btn_editar_usuario = Button(text='edit', size_hint_x=None, width=dp(100), background_color=(1, 1, 1, 0), font_size='20sp', bold=True, font_name=self.font_path)
        btn_editar_usuario.bind(on_release=lambda x: self.abrir_popup_editar_usuario())

        btn_borrar_usuario = Button(text='delete', size_hint_x=None, width=dp(100), background_color=(1, 1, 1, 0), font_size='20sp', bold=True, font_name=self.font_path)
        btn_borrar_usuario.bind(on_release=self.confirmar_borrar_usuario)

        layout_botones_usuarios.add_widget(espacio_logo) 
        layout_botones_usuarios.add_widget(espacio_texto)   
        layout_botones_usuarios.add_widget(espacio_vacio)      
        layout_botones_usuarios.add_widget(btn_agregar_usuario)
        layout_botones_usuarios.add_widget(btn_editar_usuario)
        layout_botones_usuarios.add_widget(btn_borrar_usuario)

        self.add_widget(layout_botones_usuarios)

        # Layout del encabezado con fondo verde claro
        layout_encabezado = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        

        label_nombre = Label(text='Nombre', size_hint_x=None, width=dp(150), bold=True, font_size='24sp')
        label_apellido = Label(text='Apellido', size_hint_x=None, width=dp(150), bold=True, font_size='24sp')
        label_rango = Label(text='Rango', size_hint_x=None, width=dp(100), bold=True, font_size='24sp')

        layout_encabezado.add_widget(label_nombre)
        layout_encabezado.add_widget(label_apellido)
        layout_encabezado.add_widget(label_rango)

        # Espacio entre el encabezado y el layout de botones
        self.add_widget(BoxLayout(size_hint_y=None, height=dp(10)))  # Espaciador

        self.add_widget(layout_encabezado)

        # ScrollView para la lista de usuarios
        scroll_lista_usuarios = ScrollView(size_hint=(1, 1), bar_width=dp(20))
        self.lista_usuarios_layout = GridLayout(cols=1, size_hint_y=None) 
        self.lista_usuarios_layout.bind(minimum_height=self.lista_usuarios_layout.setter('height'))
        scroll_lista_usuarios.add_widget(self.lista_usuarios_layout)
        self.add_widget(scroll_lista_usuarios)

        # Cargamos los usuarios desde la base de datos
        self.cargar_usuarios()

        # Añadimos el layout completo a la zona de contenido principal
        self.admin_screen_instance.area_principal.add_widget(self)



    def cargar_usuarios(self):
        """Carga los usuarios desde la base de datos y los añade al GridLayout proporcionado."""
        self.lista_usuarios_layout.clear_widgets()
        usuarios = obtener_usuarios_db()
        for id_usuario, nombre, apellido, contrasena, rango in usuarios:

            usuario_layout = GridLayout(cols=3, size_hint_y=None, height=dp(40))

            usuario_nombre = Label(text=nombre, size_hint_x=None, width=dp(150))
            usuario_apellido = Label(text=apellido, size_hint_x=None, width=dp(150))
            usuario_rango = Label(text=rango, size_hint_x=None, width=dp(100))
            usuario_layout.add_widget(usuario_nombre)
            usuario_layout.add_widget(usuario_apellido)
            usuario_layout.add_widget(usuario_rango)

            usuario_layout.bind(on_touch_down=lambda instance, touch, nombre=nombre, apellido=apellido, rango=rango, id_usuario=id_usuario: self.seleccionar_usuario(instance, touch, nombre, apellido, rango, id_usuario))

            self.lista_usuarios_layout.add_widget(usuario_layout)


    def seleccionar_usuario(self, instance, touch, nombre, apellido, rango, id_usuario):
        global usuario_seleccionado
        if instance.collide_point(touch.x, touch.y):
            for label in instance.children:
                label.color = (0, 1, 1, 1)
                label.font_size = '26sp'
            if usuario_seleccionado and usuario_seleccionado['layout'] != instance:
                for label in usuario_seleccionado['layout'].children:
                    label.color = (1, 1, 1, 1)
                    label.font_size = '16sp'
            usuario_seleccionado = {'layout': instance, 'nombre': nombre, 'apellido': apellido, 'rango': rango, 'id': id_usuario}
            #print(f'Se ha seleccionado: {nombre} {apellido} - {rango} (ID: {id_usuario})')





############### agregar usuario ###############
    def abrir_popup_agregar_usuario(self):
        layout_popup = BoxLayout(orientation='vertical', padding=10, spacing=10)

        nombre_input = TextInput(hint_text='Nombre', multiline=False, size_hint_y=None, height=dp(40), background_color=(0.8, 0.8, 0.8, 1))
        apellido_input = TextInput(hint_text='Apellido', multiline=False, size_hint_y=None, height=dp(40), background_color=(0.8, 0.8, 0.8, 1))
        contrasena_input = TextInput(hint_text='Contraseña', multiline=False, password=True, size_hint_y=None, height=dp(40), background_color=(0.8, 0.8, 0.8, 1))
        repetir_contrasena_input = TextInput(hint_text='Repetir Contraseña', multiline=False, password=True, size_hint_y=None, height=dp(40), background_color=(0.8, 0.8, 0.8, 1))

        rango_spinner = Spinner(text='Seleccionar rango', values=('admin', 'user'), size_hint_y=None, height=dp(40), background_color=(0.8, 0.8, 0.8, 1))

        # Label para mostrar mensajes de error
        error_label = Label(text='', color=(1, 0, 0, 1), size_hint_y=None, height=dp(20), font_size='12sp')  # Ajustar tamaño del label y texto

        layout_popup.add_widget(Label(text='Nombre:', bold=True))
        layout_popup.add_widget(nombre_input)
        layout_popup.add_widget(Label(text='Apellido:', bold=True))
        layout_popup.add_widget(apellido_input)
        layout_popup.add_widget(Label(text='Contraseña:', bold=True))
        layout_popup.add_widget(contrasena_input)
        layout_popup.add_widget(Label(text='Repetir Contraseña:', bold=True))
        layout_popup.add_widget(repetir_contrasena_input)
        layout_popup.add_widget(Label(text='Rango:', bold=True))
        layout_popup.add_widget(rango_spinner)

        # Añadir el label de error al layout
        layout_popup.add_widget(error_label)

        btn_cancelar = Button(text='Cancelar', size_hint_y=None, height=dp(40), background_color=(1, 0.647, 0))  # Naranja
        btn_guardar = Button(text='Agregar Usuario', size_hint_y=None, height=dp(40), background_color=(0.678, 0.847, 0.902))  # Celeste

        popup = Popup(title="Agregar Usuario", content=layout_popup, size=(680, 580), size_hint=(None, None), auto_dismiss=False)

        btn_cancelar.bind(on_release=popup.dismiss)

        # Llamar a verificar_campos en el on_release
        btn_guardar.bind(on_release=lambda instance: verificar_campos())

        botones_layout = BoxLayout(orientation='horizontal', spacing=10)
        botones_layout.add_widget(btn_cancelar)
        botones_layout.add_widget(btn_guardar)

        layout_popup.add_widget(botones_layout)

        def verificar_campos():
            if not nombre_input.text or not apellido_input.text or not contrasena_input.text or not repetir_contrasena_input.text:
                error_label.text = "Por favor, complete todos los campos."
                return False

            # Verificar si el spinner tiene la opción 'Seleccionar rango'
            if rango_spinner.text == 'Seleccionar rango':
                error_label.text = "Por favor, elija un rango."
                return False

            if contrasena_input.text != repetir_contrasena_input.text:
                error_label.text = "Las contraseñas no coinciden. Por favor, intente de nuevo."
                return False

            # Si todo está bien, limpiar el mensaje de error y llamar a agregar_usuario
            error_label.text = ""  # Limpiar el mensaje de error
            agregar_usuario()
            popup.dismiss()
            popup.clear_widgets()
            popup.parent.remove_widget(popup)



        def agregar_usuario():
            try:
                conn, cursor = conectar_db_config()
                cursor.execute("INSERT INTO Usuarios (nombre, apellido, contrasena, rango) VALUES (?, ?, ?, ?)", 
                            (nombre_input.text, apellido_input.text, contrasena_input.text, rango_spinner.text))
                conn.commit()
                self.cargar_usuarios()
                print(f'Usuario agregado: {nombre_input.text} {apellido_input.text} - {rango_spinner.text}')
            except sqlite3.Error as e:
                print(f"Error al agregar el usuario a la base de datos: {e}")
            finally:
                if conn:
                    conn.close()

        popup.open()

    def abrir_popup_editar_usuario(self):
        """Abre un popup para editar un usuario seleccionado."""
        global usuario_seleccionado
        if not usuario_seleccionado:
            print("No hay un usuario seleccionado para editar.")
            return

        layout_popup = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Crear campos de entrada y asignar valores iniciales
        nombre_input = TextInput(text=usuario_seleccionado['nombre'], multiline=False, size_hint_y=None, height=dp(40), background_color=(0.8, 0.8, 0.8, 1))
        apellido_input = TextInput(text=usuario_seleccionado['apellido'], multiline=False, size_hint_y=None, height=dp(40), background_color=(0.8, 0.8, 0.8, 1))
        contrasena_input = TextInput(hint_text='Nueva Contraseña', multiline=False, password=True, size_hint_y=None, height=dp(40), background_color=(0.8, 0.8, 0.8, 1))
        repetir_contrasena_input = TextInput(hint_text='Repetir Nueva Contraseña', multiline=False, password=True, size_hint_y=None, height=dp(40), background_color=(0.8, 0.8, 0.8, 1))
        rango_spinner = Spinner(text=usuario_seleccionado['rango'], values=('admin', 'usuario'), size_hint_y=None, height=dp(40), background_color=(0.8, 0.8, 0.8, 1))
        error_label = Label(text='', color=(1, 0, 0, 1), size_hint_y=None, height=dp(20), font_size='12sp')

        # Agregar widgets al layout del popup
        layout_popup.add_widget(Label(text='Nombre:', bold=True))
        layout_popup.add_widget(nombre_input)
        layout_popup.add_widget(Label(text='Apellido:', bold=True))
        layout_popup.add_widget(apellido_input)
        layout_popup.add_widget(Label(text='Nueva Contraseña:', bold=True))
        layout_popup.add_widget(contrasena_input)
        layout_popup.add_widget(Label(text='Repetir Nueva Contraseña:', bold=True))
        layout_popup.add_widget(repetir_contrasena_input)
        layout_popup.add_widget(Label(text='Rango:', bold=True))
        layout_popup.add_widget(rango_spinner)
        layout_popup.add_widget(error_label)

        # Crear botones de cancelar y guardar
        btn_cancelar = Button(text='Cancelar', size_hint_y=None, height=dp(40), background_color=(1, 0.647, 0))
        btn_guardar = Button(text='Guardar Cambios', size_hint_y=None, height=dp(40), background_color=(0.678, 0.847, 0.902))
        popup = Popup(title="Editar Usuario", content=layout_popup, size=(680, 580), size_hint=(None, None), auto_dismiss=False)

        # Vincular eventos a los botones
        btn_cancelar.bind(on_release=popup.dismiss)
        btn_guardar.bind(on_release=lambda instance: verificar_campos())
        botones_layout = BoxLayout(orientation='horizontal', spacing=10)
        botones_layout.add_widget(btn_cancelar)
        botones_layout.add_widget(btn_guardar)
        layout_popup.add_widget(botones_layout)       
        popup.open()

        def verificar_campos():
            global usuario_seleccionado 
            if not nombre_input.text or not apellido_input.text:
                error_label.text = "Por favor, complete todos los campos."
                return False
            if rango_spinner.text == 'Seleccionar rango':
                error_label.text = "Por favor, elija un rango."
                return False
            if contrasena_input.text != repetir_contrasena_input.text:
                error_label.text = "Las contraseñas no coinciden. Por favor, intente de nuevo."
                return False
            error_label.text = ""
            actualizar_usuario(usuario_seleccionado)  # Pasar usuario_seleccionado
            usuario_seleccionado = None
            popup.dismiss()
            popup.clear_widgets()
            popup.parent.remove_widget(popup)
            

        def actualizar_usuario(usuario_seleccionado):
            try:
                conn, cursor = conectar_db_config()
                id_usuario = usuario_seleccionado.get('id')
                if id_usuario is not None:  
                    cursor.execute("UPDATE Usuarios SET nombre = ?, apellido = ?, contrasena = ?, rango = ? WHERE id = ?", 
                                (nombre_input.text, apellido_input.text, contrasena_input.text, rango_spinner.text, id_usuario))
                    conn.commit()
                    self.cargar_usuarios()
            except sqlite3.Error as e:
                agregar_log(f"Error al editar el usuario en la base de datos: {e}")
            finally:
                if conn:
                    conn.close()


    def confirmar_borrar_usuario(self, instance):
        global usuario_seleccionado
        if not usuario_seleccionado:
            return
        if usuario_seleccionado.get('rango') == 'owner':
            return        

        layout_popup = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout_popup.add_widget(Label(text='¿Confirmar borrar usuario?', 
                                    size_hint_y=None, height=dp(40), font_size='18sp'))

        botones_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(40))
        btn_cancelar = Button(text='Cancelar', size_hint_x=1, 
                            background_color=(0, 0.647, 1), font_size='20sp')
        btn_confirmar = Button(text='Confirmar', size_hint_x=1, 
                            background_color=(1, 0, 0), font_size='20sp')
        botones_layout.add_widget(btn_cancelar)
        botones_layout.add_widget(btn_confirmar)

        layout_popup.add_widget(botones_layout)

        popup = Popup(title="Confirmar Borrado", content=layout_popup, size=(400, 200),
                    size_hint=(None, None), auto_dismiss=False)

        btn_cancelar.bind(on_release=popup.dismiss)
        btn_confirmar.bind(on_release=lambda x: borrar_usuario(popup))
        popup.open()



        def borrar_usuario(popup):
            global usuario_seleccionado
            if usuario_seleccionado:  
                id_usuario = usuario_seleccionado.get('id') 
                try:
                    conn, cursor = conectar_db_config() 
                    cursor.execute("DELETE FROM Usuarios WHERE id = ?", (id_usuario,))
                    conn.commit()
                    agregar_log_auditoria(f"Usuario con ID {id_usuario} borrado correctamente.") 
                    self.cargar_usuarios()  
                except sqlite3.Error as e:
                    agregar_log(f"Error al borrar el usuario en la base de datos: {e}")
                finally:
                    if conn:
                        conn.close()            
            popup.dismiss()
            popup.clear_widgets()
            popup.parent.remove_widget(popup)
