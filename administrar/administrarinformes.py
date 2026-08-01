import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.metrics import sp, dp
from kivy.uix.spinner import Spinner
from cargardatos import conectar_db_config
from loggin import configurar_logger, configurar_logger_auditoria
from datos import obtener_ruta_assets
from datetime import datetime, timedelta
from datos import conectar_db


class Informes(BoxLayout):
    def __init__(self, admin_screen_instance, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.admin_screen_instance = admin_screen_instance
        self.ruta_assets = obtener_ruta_assets()
        self.usuarios_icono = os.path.join(self.ruta_assets, 'informes.png')
        self.font_path = os.path.join(self.ruta_assets, 'materialicons-regular.ttf')

        configurar_logger()
        configurar_logger_auditoria()
        self.encabezado_texto = "Informes Ventas Mensual"
        self.selected_tiempo = 'Mensual'  
        self.selected_categoria = 'Ventas'  
        self.setup_layout()

    def setup_layout(self):
        self.admin_screen_instance.area_principal.clear_widgets()
        # Crear la barra de botones con altura fija
        self.add_widget(self.create_button_bar())
        self.add_widget(BoxLayout(size_hint_y=None, height=dp(10)))  # Espaciado fijo entre los botones y el encabezado

        # Crear el encabezado
        self.encabezado_layout = BoxLayout(size_hint=(1, None), height=dp(40)) 
        self.encabezado_label = Label(text=f'[b]Informes Ventas Mensual[/b]', size_hint=(1, 1), font_size=sp(24), markup=True)
        self.encabezado_layout.add_widget(self.encabezado_label)

        self.informes_layout = BoxLayout(orientation='horizontal', size_hint=(1, 1), spacing=dp(10))        
        # Layout para el gráfico
        self.grafico_layout = BoxLayout(orientation='vertical', size_hint=(0.5, 1), padding=dp(10), spacing=dp(10))
        self.grafico_label = Label(text="Gráfico de Ventas", size_hint=(1, None), height=dp(40), bold=True, font_size=sp(18))
        self.grafico_layout.add_widget(self.grafico_label)        
        self.informacion_layout = BoxLayout(orientation='vertical', size_hint=(0.5, 1), padding=dp(10), spacing=dp(10))

  
        self.add_widget(self.encabezado_layout)
        self.informes_layout.add_widget(self.grafico_layout)
        self.informes_layout.add_widget(self.informacion_layout)        
        self.add_widget(self.informes_layout)

        # Cargar los datos
        self.cargar_datos()
        # Añadir el layout completo a la pantalla principal
        self.admin_screen_instance.area_principal.add_widget(self)


    def create_button_bar(self):
        layout_botones = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))

        espacio_logo = Image(source=self.usuarios_icono, size_hint_x=None, size_hint_y=1, width=dp(80))
        espacio_encabezado = Label(text=f'[b]Informes[/b]', size_hint=(1, 1), font_size=sp(18), markup=True, color=(0.7, 0.7, 0.7, 1))

        spinner_tiempo = Spinner(
            text='Mensual',  
            values=('Día', 'Semanal', 'Quincenal' , 'Mensual' , 'Anuales'),
            size_hint=(None, None),
            size=(dp(150), dp(40)),
            background_color=(0.9, 0.9, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        spinner_tiempo.bind(text=self.on_tiempo_select)

        spinner_categoria = Spinner(
            text='Ventas',  
            values=('Ventas', 'Entrada de productos', 'Ganancias'),
            size_hint=(None, None),
            size=(dp(150), dp(40)),
            background_color=(0.9, 0.9, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        spinner_categoria.bind(text=self.on_categoria_select)

        layout_botones.add_widget(espacio_logo)
        layout_botones.add_widget(espacio_encabezado)
        layout_botones.add_widget(spinner_categoria)
        layout_botones.add_widget(spinner_tiempo)
        return layout_botones
    

    def on_tiempo_select(self, spinner, text):
        self.selected_tiempo = text
        self.total_label.text = f"Total Ventas {text}:"     
        self.totalG_label.text = f"Total Ganancia {text}:"        
        self.totalI_label.text = f"Total Invertido {text}:"   
        self.cargar_totales()   
        self.update_encabezado()

    def on_categoria_select(self, spinner, text):
        self.selected_categoria = text

        self.update_encabezado()

    def update_encabezado(self):
        self.encabezado_texto = f"{self.selected_categoria} {self.selected_tiempo}"
        self.encabezado_label.text = f'[b]{self.encabezado_texto}[/b]'



    def cargar_datos(self):
        self.informacion_datos()
        self.cargar_totales()




    def grafica_datos(self):
        pass



    def informacion_datos(self):
        self.informacion_layout.clear_widgets()


        self.total_label = Label(text=f'Total Ventas Mes:', size_hint=(1, None), height=dp(40), bold=True, font_size=sp(18), halign='left')        
        self.detalle_label = Label(text="Información aqui", size_hint=(1, None), height=dp(100), font_size=sp(14), text_size=(self.informacion_layout.width, None), halign='left')



        self.totalG_label = Label(text=f'Total Ganancia Mes:', size_hint=(1, None), height=dp(40), bold=True, font_size=sp(18), halign='left')        
        self.detalleG_label = Label(text="Información aqui", size_hint=(1, None), height=dp(100), font_size=sp(14), text_size=(self.informacion_layout.width, None), halign='left')



        self.totalI_label = Label(text=f'Total Invertido:', size_hint=(1, None), height=dp(40), bold=True, font_size=sp(18), halign='left')        
        self.detalleI_label = Label(text="Información aqui", size_hint=(1, None), height=dp(100), font_size=sp(14), text_size=(self.informacion_layout.width, None), halign='left')

        self.informacion_layout.add_widget(self.total_label)
        self.informacion_layout.add_widget(self.detalle_label)

        self.informacion_layout.add_widget(self.totalG_label)
        self.informacion_layout.add_widget(self.detalleG_label)


        self.informacion_layout.add_widget(self.totalI_label)
        self.informacion_layout.add_widget(self.detalleI_label)     





    def obtener_totales(self, fecha_inicio, fecha_fin):
        print(f"--------------------------------------")
        try:
            conn, cursor = conectar_db()
            cursor.execute('''SELECT fecha, precio_venta, cantidad, ganancia_total FROM salidas''')
            registros_salidas = cursor.fetchall()
            cursor.execute('''SELECT fecha, cantidad, precio_compra FROM entradas''')
            registros_entradas = cursor.fetchall()
            conn.close()

            # Convertir las fechas de inicio y fin a tipo date (sin hora)
            fecha_inicio_dt = datetime.strptime(fecha_inicio, "%d-%m-%Y").date()
            fecha_fin_dt = datetime.strptime(fecha_fin, "%d-%m-%Y").date()

            total_ventas = 0
            total_ganancia = 0
            total_invertido = 0

            for registro in registros_salidas:
                fecha, precio_venta, cantidad, ganancia_total = registro
                fecha_dt = datetime.strptime(fecha, "%d-%m-%Y %H:%M:%S").date()  # Solo fecha, sin hora
                if fecha_inicio_dt <= fecha_dt <= fecha_fin_dt:
                    total_ventas += precio_venta * cantidad
                    total_ganancia += ganancia_total

            for registro in registros_entradas:
                fecha, cantidad, precio_compra = registro
                fecha_dt = datetime.strptime(fecha, "%d-%m-%Y %H:%M:%S").date()  # Solo fecha, sin hora
                if fecha_inicio_dt <= fecha_dt <= fecha_fin_dt:
                    total_invertido += cantidad * precio_compra

            self.total_ventas = total_ventas
            self.total_ganancia = total_ganancia
            self.total_invertido = total_invertido

            print(f"Total Ventas: {self.total_ventas}")
            print(f"Total Ganancia: {self.total_ganancia}")
            print(f"Total Invertido: {self.total_invertido}")
        except Exception as e:
            print(f"Error: {e}")
            self.total_ventas = 0
            self.total_ganancia = 0
            self.total_invertido = 0






    def cargar_totales(self):
        today = datetime.today()

        if self.selected_tiempo == 'Día':
            # Solo la fecha sin hora
            fecha_inicio = today.strftime('%d-%m-%Y')
            fecha_fin = today.strftime('%d-%m-%Y')

        elif self.selected_tiempo == 'Semanal':
            if today.weekday() == 0:
                fecha_inicio = today.strftime('%d-%m-%Y')
                fecha_fin = (today + timedelta(days=6)).strftime('%d-%m-%Y')
            else:
                fecha_inicio = (today - timedelta(days=today.weekday())).strftime('%d-%m-%Y')
                fecha_fin = (datetime.strptime(fecha_inicio, '%d-%m-%Y') + timedelta(days=6)).strftime('%d-%m-%Y')

        elif self.selected_tiempo == 'Mensual':
            fecha_inicio = today.replace(day=1).strftime('%d-%m-%Y')
            if today.month == 12:
                fecha_fin = today.replace(day=31).strftime('%d-%m-%Y')
            else:
                fecha_fin = (today.replace(day=1, month=today.month + 1) - timedelta(days=1)).strftime('%d-%m-%Y')

        elif self.selected_tiempo == 'Quincenal':
            if today.day <= 15:
                fecha_inicio = today.replace(day=1).strftime('%d-%m-%Y')
                fecha_fin = today.replace(day=15).strftime('%d-%m-%Y')
            else:
                fecha_inicio = today.replace(day=16).strftime('%d-%m-%Y')
                if today.month == 12:
                    fecha_fin = today.replace(day=31).strftime('%d-%m-%Y')
                else:
                    siguiente_mes = today.replace(day=1, month=today.month + 1)
                    fecha_fin = (siguiente_mes - timedelta(days=1)).strftime('%d-%m-%Y')

        else:
            fecha_inicio = today.replace(month=1, day=1).strftime('%d-%m-%Y')
            fecha_fin = today.replace(month=12, day=31).strftime('%d-%m-%Y')

        # Llamada a la función de obtener_totales con las fechas modificadas
        self.obtener_totales(fecha_inicio, fecha_fin)

        print(f"---------def cargar_totales-----------")
        print(f"Fecha de inicio: {fecha_inicio}")
        print(f"Fecha de fin: {fecha_fin}")
        print(f"--------------------------------------")

        self.detalle_label.text = f"$ {self.total_ventas}"
        self.detalleG_label.text = f"$  {self.total_ganancia}"
        self.detalleI_label.text = f"$ {self.total_invertido}"




    # def obtener_totales(self, fecha_inicio, fecha_fin):
    #     try:
    #         conn, cursor = conectar_db()

    #         cursor.execute('''SELECT SUM(precio_venta * cantidad) FROM salidas WHERE fecha >= ? AND fecha <= ?''', (fecha_inicio, fecha_fin))
    #         self.total_ventas = (cursor.fetchone()[0] or 0)

    #         cursor.execute('''SELECT SUM(ganancia_total) FROM salidas WHERE fecha >= ? AND fecha <= ?''', (fecha_inicio, fecha_fin))
    #         self.total_ganancia = (cursor.fetchone()[0] or 0)

    #         cursor.execute('''SELECT SUM(cantidad * precio_compra) FROM entradas WHERE fecha >= ? AND fecha <= ?''', (fecha_inicio, fecha_fin))
    #         self.total_invertido = (cursor.fetchone()[0] or 0)

    #         conn.close()

    #         print(f"Total Ventas: {self.total_ventas}")
    #         print(f"Total Ganancia: {self.total_ganancia}")
    #         print(f"Total Invertido: {self.total_invertido}")
            
    #     except Exception as e:
    #         print(f"Error: {e}")
    #         self.total_ventas = self.total_ganancia = self.total_invertido = 0
