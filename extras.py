# administrar_editar_agregar_eliminar.py
import os
import sys
import calendar
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from datetime import datetime


from loggin import configurar_logger, agregar_log
from configs import obtener_imprimir_ticket
from datos import obtener_ruta_assets

# funciones:
# imprimir
# Calendario PopUp
# log
# extra.py


def opcion_imprimir_tickets_dispositivo(factura_texto):
    configurar_logger()
    if sys.platform.startswith('win'):  # Comprueba si es Windows
        imprimir_tickets_windows(factura_texto)
    else:
        imprimir_android()



def imprimir_tickets_windows(factura_texto):
    if sys.platform.startswith('win'):
        print('def imprimir_tickets_windows: Imprimiendo. . .')
        import win32print
        import win32api        
       # ruta_assets = obtener_ruta_assets()
        #logobmp_assets = os.path.join(ruta_assets, 'logo.bmp')
    try:
        printer_name = obtener_imprimir_ticket()
        raw_data = factura_texto

        # Abre una conexión con la impresora
        hPrinter = win32print.OpenPrinter(printer_name)
        try:

            job = win32print.StartDocPrinter(hPrinter, 1, ("Test", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                win32print.WritePrinter(hPrinter, raw_data.encode())
                win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)

    except Exception as e:
        agregar_log(f"Error al imprimir: {e}")     






# extra.py
def imprimir_android():
    pass 



def opcion_imprimir_Factura_dispositivo(contenido_factura):
    if sys.platform.startswith('win'):  # Comprueba si es Windows
        imprimir_factura_windows(contenido_factura)
    else:
        imprimir_android()


def imprimir_factura_windows(contenido_factura):
    try:
        import win32ui
        import win32print
        import win32con
        
        # Obtener la impresora predeterminada
        impresora = win32print.GetDefaultPrinter()

        # Configurar el dispositivo de impresión
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(impresora)
        hDC.StartDoc("Factura POS")
        hDC.StartPage()

        # Configurar fuente y tamaño de texto
        hDC.SetMapMode(win32con.MM_TWIPS)  # Configura la escala de impresión (1/1440 de pulgada)
        hDC.SetTextAlign(win32con.TA_LEFT)

        # Definir posición inicial para el texto
        y_position = -100  # Posición inicial en la página

        # Escribir cada línea de la factura en la posición actual
        for line in contenido_factura.splitlines():
            hDC.TextOut(100, y_position, line)
            y_position -= 200  # Espacio entre líneas

        # Finalizar la impresión
        hDC.EndPage()
        hDC.EndDoc()
        
        print("Factura enviada a la impresora.")

    except Exception as e:
        print(f"Error al imprimir la factura en Windows: {e}")
 








































#administrar_editar_agregar_eliminar.py
MESES_ES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
class CalendarPopup(Popup):
    def __init__(self, parent=None, **kwargs):
        super().__init__(**kwargs)
        self.title = "Seleccionar Fecha"
        self.size_hint = (0.8, 0.8)
        self.parent_popup = parent
        self.size = (400, 300) 
        self.size_hint = None, None          
        # Obtener el año y mes actual
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month

        # Layout principal vertical
        layout = BoxLayout(orientation='vertical')

        # Crear el spinner para seleccionar el mes y año
        header_layout = BoxLayout(size_hint=(1, 0.2))

        # Botón para mes anterior
        self.btn_prev_month = Button(text="<", size_hint=(0.1, 1), background_color=(0.2, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        self.btn_prev_month.bind(on_release=self.change_month_prev)

        # Spinner para el mes en español
        self.spinner_month = Spinner(
            text=MESES_ES[self.current_month - 1], values=MESES_ES, size_hint=(0.5, 1), background_color=(0.2, 0.2, 0.2, 1), color=(1, 1, 1, 1)  )
        self.spinner_month.bind(text=self.update_month)

        # Spinner para el año (de 2020 a 2040)
        self.spinner_year = Spinner(
            text=str(self.current_year), values=[str(year) for year in range(2020, 2041)], size_hint=(0.5, 1),
            background_color=(0.2, 0.2, 0.2, 1),  color=(1, 1, 1, 1))
        self.spinner_year.bind(text=self.update_calendar)

        # Botón para mes siguiente
        self.btn_next_month = Button(text=">", size_hint=(0.1, 1), background_color=(0.2, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        self.btn_next_month.bind(on_release=self.change_month_next)

        header_layout.add_widget(self.btn_prev_month)
        header_layout.add_widget(self.spinner_month)
        header_layout.add_widget(self.spinner_year)
        header_layout.add_widget(self.btn_next_month)

        # Layout del calendario
        self.calendar_layout = GridLayout(cols=7)
        self.create_calendar(self.current_year, self.current_month)

        layout.add_widget(header_layout)
        layout.add_widget(self.calendar_layout)

        self.content = layout

        # Aplicar estilo de texto en negrita a los botones
        for btn in [self.btn_prev_month, self.btn_next_month]:
            btn.font_size = '20sp'  # Ajustar el tamaño de la fuente
            btn.bold = True  # Hacer el texto en negrita

    # Crear el calendario para un mes y año determinados
    def create_calendar(self, year, month):
        # Limpiar el calendario actual
        self.calendar_layout.clear_widgets()

        # Agregar etiquetas de los días de la semana
        dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        for dia in dias_semana:
            self.calendar_layout.add_widget(Label(text=dia))

        # Obtener la matriz de días para el mes y año dados
        month_days = calendar.monthcalendar(year, month)

        # Agregar los días al calendario
        for week in month_days:
            for day in week:
                if day == 0:
                    self.calendar_layout.add_widget(Label(text=""))  # Espacio vacío para días fuera del mes
                else:
                    btn = Button(text=str(day), background_color=(0.2, 0.2, 0.2, 1), color=(1, 1, 1, 1))
                    btn.font_size = '20sp'  # Ajustar el tamaño de la fuente
                    btn.bold = True  # Hacer el texto en negrita

                    # Asociar la función para imprimir la fecha al botón
                    btn.bind(on_release=lambda instance, d=day: self.enviar_fecha(d))

                    self.calendar_layout.add_widget(btn)



    # Actualizar el calendario cuando se cambie el año
    def update_calendar(self, *args):
        selected_year = int(self.spinner_year.text)
        self.create_calendar(selected_year, self.current_month)

    # Actualizar el calendario cuando se cambie el mes desde el spinner
    def update_month(self, spinner, selected_month):
        month_index = MESES_ES.index(selected_month) + 1  # Convertir el mes a índice
        self.current_month = month_index
        self.create_calendar(self.current_year, self.current_month)

    # Cambiar al mes anterior
    def change_month_prev(self, instance):
        self.current_month -= 1
        if self.current_month == 0:
            self.current_month = 12
            self.current_year -= 1
            self.spinner_year.text = str(self.current_year)
        self.spinner_month.text = MESES_ES[self.current_month - 1]
        self.create_calendar(self.current_year, self.current_month)

    # Cambiar al mes siguiente
    def change_month_next(self, instance):
        self.current_month += 1
        if self.current_month == 13:
            self.current_month = 1
            self.current_year += 1
            self.spinner_year.text = str(self.current_year)
        self.spinner_month.text = MESES_ES[self.current_month - 1]
        self.create_calendar(self.current_year, self.current_month)


    def enviar_fecha(self, day): 
        self.dismiss()  # Cerrar el popup
        fecha_texto = f"{day}-{self.current_month}-{self.current_year}"
        
        # Comprobar si la fecha ya existe antes de enviarla
        if self.parent_popup.fecha_seleccionada is not None: 
            self.parent_popup.fecha_seleccionada(fecha_texto)
        else:
            print("def fecha seleccionada, no existe.")


    def on_dismiss(self):
        super().on_dismiss()  # Llamar al método de la clase base










