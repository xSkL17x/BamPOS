from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.core.window import Window
from pos.pos import ProductsScreen  # Importa la pantalla de productos
from administrar.administrar import AdminScreen  # Importa la pantalla de administración
from loggin import configurar_logger, agregar_log  # Importa las funciones de logging
from datos import verificar_instancia, eliminar_pid  # Importa la función para verificar carpetas y archivos
from cargardatos import set_products_screen  # Importa la función para establecer products_screen
from inicio_sesion import LoginScreen
from kivy.clock import Clock
from configs import imprimir_datos_configuracion
# Establecemos los límites mínimos de las ventanas
Window.minimum_width = 900  # Mínimo ancho
Window.minimum_height = 600  # Mínimo alto






class MainApp(App):
    def build(self):
        #import os ######borrar
       # os.system('cls')#######borrar al compilar


        verificar_instancia()
        configurar_logger()
        agregar_log("Iniciando la aplicación POS.")


        self.title = "POS By SKL"    
        self.sm = ScreenManager(transition=NoTransition())
        
        # Agregar la pantalla de inicio de sesión
        self.sm.add_widget(LoginScreen(name='login'))          
        
        # Agregar la pantalla de productos después de un retraso
        Clock.schedule_once(self.add_products_screen, 0.5)
        return self.sm

    def add_products_screen(self, dt):
        self.products_screen = ProductsScreen(name='products')
        self.sm.add_widget(self.products_screen)
        agregar_log("Pantalla de Principal de POS añadida al ScreenManager.")

    def on_stop(self):
        eliminar_pid()
        agregar_log("cerrando App")         

if __name__ == "__main__":
    MainApp().run()
