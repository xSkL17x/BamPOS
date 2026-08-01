import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.metrics import dp, sp 
from kivy.clock import Clock
import time
from datos import verificar_carpeta_y_archivo, obtener_ruta_assets, crear_y_verificar_configuraciones,conectar_db_config
from configs import cargar_todas_configuraciones, obtener_autologin, obtener_autologin_usuario, obtener_remember_user, obtener_remember_user_usuario
from loggin import agregar_log, configurar_logger
import sqlite3
from kivy.core.window import Window
from kivy.uix.checkbox import CheckBox
Window.size = (900, 600)  # Ancho y alto iniciales



ruta_assets = obtener_ruta_assets() 
obtener_logo = os.path.join(ruta_assets, 'logo.png')


usuario_actual = {"usuario": None, "rango": None}


def obtener_usuario_actual():
    return usuario_actual["usuario"], usuario_actual["rango"]



class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.Estado_Pos = ""
        self.Estado_Inicialicaciones = ""
        self.usuarios = ""
        self.estado_autologin = ""
        self.estado_remember_user = ""
        self.remember_usuario= ""

        

        self.areaprincipal_boxlayout = BoxLayout(orientation='vertical')

        with self.areaprincipal_boxlayout.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

        self.bampos_layout = FloatLayout(size_hint_y=None, height=dp(200))
        self.setup_bampos_layout()

        self.inicio_sesion_layout = FloatLayout(size_hint_y=1)
        self.setup_inicio_sesion_layout()

        self.areaprincipal_boxlayout.add_widget(self.bampos_layout)
        self.areaprincipal_boxlayout.add_widget(self.inicio_sesion_layout)

        self.add_widget(self.areaprincipal_boxlayout)
        Clock.schedule_once(self.Inicialisaciones, 1)


        
    def setup_bampos_layout(self):
        self.bampos_layout.add_widget(Image(source=obtener_logo, size_hint=(1, None), height=dp(150), pos_hint={'center_x': 0.5, 'top': 0.9}))  # top - baja + sube

    def setup_inicio_sesion_layout(self):
        inputs_layout = BoxLayout(orientation='vertical', size_hint=(None, None), size=(dp(400), dp(250)), spacing=dp(10))
        inputs_layout.bind(size=self._update_rect)

        inicio_sesion_label = Label(text='Inicio de Sesión', size_hint=(1, None), height=dp(60), font_size=sp(24), bold=True)

        username_label = Label(text='Usuario:', size_hint=(None, None), size=(dp(400), dp(40)))
        self.username_input = TextInput(hint_text='Ingrese su usuario', halign='center', font_size='20sp', multiline=False, size_hint=(None, None), on_text_validate=self.login, size=(dp(400), dp(40)))
        
        password_label = Label(text='Contraseña:', size_hint=(None, None), size=(dp(400), dp(40)))
        self.password_input = TextInput(hint_text='Ingrese su contraseña', password=True, multiline=False, on_text_validate=self.login, size_hint=(None, None), size=(dp(400), dp(40)))

        checkboxes_layout = BoxLayout(orientation='horizontal', size_hint=(None, None), size=(dp(400), dp(40)), spacing=dp(10), padding=dp(5))

        self.autologin_checkbox = CheckBox(size_hint=(None, None), size=(dp(30), dp(30)))
        autologin_label = Label(text='Autologin', size_hint=(None, None), size=(dp(50), dp(30)), halign='left', valign='middle')

        self.recordar_usuario_checkbox = CheckBox(size_hint=(None, None), size=(dp(30), dp(30)))
        recordar_usuario_label = Label(text='Recordar Usuario', size_hint=(None, None), size=(dp(100), dp(30)), halign='right', valign='middle')

        checkboxes_layout.add_widget(self.autologin_checkbox)
        checkboxes_layout.add_widget(autologin_label)
        checkboxes_layout.add_widget(Label(size_hint_x=None, width=dp(120)))
        checkboxes_layout.add_widget(self.recordar_usuario_checkbox)
        checkboxes_layout.add_widget(recordar_usuario_label)

        login_button = Button(text='Iniciar Sesión', size_hint=(None, None), size=(dp(120), dp(40)), on_release=self.login, pos_hint={'center_x': 0.5})

        self.error_label = Label(text='Cargando Base de Datos', size_hint=(None, None), size=(dp(400), dp(40)), bold=True, color=(0, 0, 0.545, 1), font_size=sp(16))

        inputs_layout.add_widget(inicio_sesion_label)
        inputs_layout.add_widget(username_label)
        inputs_layout.add_widget(self.username_input)
        inputs_layout.add_widget(password_label)
        inputs_layout.add_widget(self.password_input)

        inputs_layout.add_widget(checkboxes_layout)
        inputs_layout.add_widget(login_button)
        inputs_layout.add_widget(self.error_label)

        self.inicio_sesion_layout.add_widget(inputs_layout)

        inputs_layout.pos_hint = {'center_x': 0.5, 'top': 0.65}

    def on_key_down(self, window, key, *args):
        if key == 13 and self.username_input.focus:  # Solo actúa si el foco está en el TextInput
            self.login(None)


    def login(self, instance):
        username = self.username_input.text.upper()
        password = self.password_input.text

        if username not in self.usuarios:
            self.error_label.text = f"Error: El usuario '{username}' no existe."
            self.error_label.color = (1, 0, 0, 1)
            Clock.schedule_once(self.limpiar_mensaje_error, 2)
            return

        if self.usuarios[username]["contrasena"] != password:
            self.error_label.text = "Error: Contraseña incorrecta."
            self.error_label.color = (1, 0, 0, 1)
            Clock.schedule_once(self.limpiar_mensaje_error, 2)
            return

        # Actualizar el diccionario global de usuario
        usuario_actual["usuario"] = username
        usuario_actual["rango"] = self.usuarios[username]["rango"]

        self.entrar_Pos()
        self.checkbox_estados()


###########################  #########################################


    def entrar_Pos(self):    
        if self.Estado_Inicialicaciones == 'listo' and self.manager.has_screen('products'):


            self.manager.current = 'products'
            Window.maximize()
            products_screen = self.manager.get_screen('products')
            products_screen.cargar_productos()  
            products_screen.usuario_actual()  
            self.manager.remove_widget(self)  # Esto elimina la instancia actual de LoginScreen
            
            self.error_label.text = "Pos y Base de Datos Listos" 
            self.error_label.color = (0, 0, 0.545, 1)  
        else: 
            self.error_label.text = "Cargando Pos y Base de Datos"  
            self.error_label.color = (0, 0, 0.545, 1)  
            Clock.schedule_once(self.limpiar_mensaje_error, 2)

                

    def limpiar_mensaje_error(self, dt):
        self.error_label.text = ""  # Limpiar el mensaje de error  

    def verificar_credenciales(self, username, password):
        if username not in self.usuarios:
            print(f"Error: El usuario '{username}' no existe.")
            return False  # O puedes devolver None, dependiendo de lo que prefieras
        if self.usuarios[username]["contrasena"] != password:
            print(f"Error: La contraseña para el usuario '{username}' es incorrecta.")
            return False

        return True  # Si el usuario y la contraseña son correctos
    



    def _update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size



##############################################################################



    def Inicialisaciones(self, *args): 
        configurar_logger()
        if crear_y_verificar_configuraciones() == "db_Configuraciones_lista":
            self.usuarios = self.obtener_usuarios()                 

        if verificar_carpeta_y_archivo() == "verificacion_hecha":
            self.cargar_configs = cargar_todas_configuraciones()  

            if self.cargar_configs == "configuraciones_cargadas":  
                self.error_label.color = (0, 0, 0.5, 1)                
                self.error_label.text = "Base de Datos Lista\nConfiguraciones listas"  
                Clock.schedule_once(self.limpiar_mensaje_error, 3)  
                self.Estado_Inicialicaciones = 'listo'
                Clock.schedule_once(lambda dt: self.autologins(), 0.3)
            else:
                Clock.schedule_once(lambda dt: self.cargar_configs, 2)
        else:
            Clock.schedule_once(lambda dt: self.Inicialisaciones(), 2)




#autologins self se establese al iniciar el app

    def autologins(self):
        if usuario_actual != {"usuario": None, "rango": None}:
            return
        else:
            if obtener_autologin() == "si":
                self.estado_autologin = "si"
                autologin_usuario = obtener_autologin_usuario()
                usuario, _, rango = autologin_usuario
                usuario_actual["usuario"] = usuario
                usuario_actual["rango"] = rango           
                self.autologin_checkbox.active = True
                self.recordar_usuario_checkbox.active = False
                self.entrar_Pos()
            elif obtener_remember_user() == "si":
                self.estado_remember_user = "si"
                self.remember_usuario = obtener_remember_user_usuario()  
                self.username_input.text = self.remember_usuario
                self.recordar_usuario_checkbox.active = True             



    def checkbox_estados(self):
        usuario_actual_c = usuario_actual["usuario"]
        # Manejo del checkbox de autologin
        if self.autologin_checkbox.active:
            if usuario_actual_c != self.username_input.text and self.estado_autologin == "":
                self.actualizar_autologin_en_db(self.username_input.text)
                self.estado_autologin = "si"  # Actualiza el estado para reflejar que se ha establecido el autologin
        elif self.recordar_usuario_checkbox.active:
            # Verificar si el usuario ingresado es diferente al recordado
            if self.username_input.text != self.remember_usuario:
                self.actualizar_remember_en_db(self.username_input.text)
                self.estado_remember_user = "si"  # Actualiza el estado para reflejar que se ha establecido el recordar usuario
        else:
            self.limpiar_db_checks()




    def actualizar_autologin_en_db(self, nuevo_usuario):
        conn, cursor = conectar_db_config()
        try:
            rango_actual_c = usuario_actual["rango"]
            cursor.execute("""UPDATE configuraciones SET valor1 = 'si', valor2 = ?, valor4 = ? WHERE accion = 'autologin'""", (nuevo_usuario, rango_actual_c))
            cursor.execute("""UPDATE configuraciones SET valor1 = 'no', valor2 = '', valor3 = '', valor4 = '', valor5 = '' WHERE accion = 'remember user'""")
            conn.commit()
        except sqlite3.Error as e:
            agregar_log(f"Error al actualizar autologin: {e}")
        finally:
            if conn:
                conn.close()


    def actualizar_remember_en_db(self, nuevo_usuario):
        conn, cursor = conectar_db_config()
        try:
            cursor.execute("""UPDATE configuraciones SET valor1 = 'si', valor2 = ? WHERE accion = 'remember user'""", (nuevo_usuario,))
            cursor.execute("""UPDATE configuraciones SET valor1 = 'no', valor2 = '', valor3 = '', valor4 = '', valor5 = '' WHERE accion = 'autologin'""")
            conn.commit()
        except sqlite3.Error as e:
            agregar_log(f"Error al actualizar recordar usuario: {e}")
        finally:
            if conn:
                conn.close()





    def limpiar_db_checks(self):
        conn, cursor = conectar_db_config()
        try:
            # Verificar el estado actual
            cursor.execute("SELECT valor1 FROM configuraciones WHERE accion = 'remember user'")
            remember_user_status = cursor.fetchone()
            
            cursor.execute("SELECT valor1 FROM configuraciones WHERE accion = 'autologin'")
            autologin_status = cursor.fetchone()

            # Comprobar si ambos están en 'no'
            if remember_user_status and remember_user_status[0] == 'no' and autologin_status and autologin_status[0] == 'no':
                return 

            # Si se necesita actualizar, proceder con la actualización
            cursor.execute("""UPDATE configuraciones SET valor1 = 'no', valor2 = '', valor3 = '', valor4 = '', valor5 = '' WHERE accion = 'remember user'""")
            cursor.execute("""UPDATE configuraciones SET valor1 = 'no', valor2 = '', valor3 = '', valor4 = '', valor5 = '' WHERE accion = 'autologin'""")
            conn.commit()

        except sqlite3.Error as e:
            agregar_log(f"Error al actualizar recordar usuario: {e}")
        finally:
            if conn:
                conn.close()








    def obtener_usuarios(self):
        usuarios = {}
        try:
            conn, cursor = conectar_db_config() 
            cursor.execute("SELECT UPPER(nombre), contrasena, rango FROM Usuarios")
            filas = cursor.fetchall()

            for fila in filas:
                nombre, contrasena, rango = fila
                usuarios[nombre] = {"contrasena": contrasena, "rango": rango}
            conn.close()
            return usuarios

        except sqlite3.Error as e:
            agregar_log(f"Error al obtener los usuarios: {e}")
            return usuarios

