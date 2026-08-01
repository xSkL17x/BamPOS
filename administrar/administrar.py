#administrar.py
import os


from kivy.uix.image import Image

from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

from kivy.graphics import Color, Line, Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.textinput import TextInput

from kivy.uix.recycleview import RecycleView
from kivy.properties import StringProperty, BooleanProperty
from kivy.metrics import dp, sp
from kivy.uix.image import Image
# En administrar.py
from administrar.administrarproducto import AddCategoryPopup,  ProductosOcultos, EditCategoryPopup, DeleteCategoryPopup
from administrar.administrar_editar_agregar_eliminar import crearpopupproductos, ConfirmDeletePopup
from administrar.administrar_entradas_salidas import Agregar_Entradas, ConfirmDeleteEntradaPopup, ConfirmDeleteSalidasPopup
from administrar.administrarusuarios import ListaUsuarios
from administrar.administrarnegociowindows import ConfigNegocio, Configwindows

from administrar.administrarinformes import Informes



from cargardatos import cargar_productos_administrar, cargar_categorias_db, cargar_entradas_administrar, cargar_salidas_administrar, cargar_productos_administrar_lat_entradas
from datos import obtener_ruta_assets
from loggin import configurar_logger, agregar_log

Builder.load_file('administrar/administrar.kv')
# En administrar.py  




class AdminScreen(Screen):
    ruta_assets = obtener_ruta_assets()
    obtener_logo = os.path.join(ruta_assets, 'logo.png')
    font_path = os.path.join(ruta_assets, 'materialicons-regular.ttf')


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mostrar_texto = False  # Inicialmente sin mostrar texto
        self.retraso_busqueda_evento = None
        self.selected_category = None
        ##### categorias y tablas ########
        self.datos_en_boxlayoutP_izquierda = None     
        self.estado_boxlayoutproductos = None
        self.tabla_actual = None    #'tabla_productos',   'tabla_entradas'    
        self.boton_lateral_actual = None  
        ####### Productos seleccionados ########
        self.producto_seleccionado = None
        self.nombre_producto_seleccionado = None
        self.categoria_producto_seleccionado = None
        self.precio_compra_producto_seleccionado = None
        self.precio_venta_producto_seleccionado = None   

        configurar_logger()

        self.canvas_screen()
        
        self.layout_principal = BoxLayout(orientation='horizontal')  # Layout principal abarca toda el app  
        self.layout_barra_lateral = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(50))  # Configuramos la barra lateral
        
        self.button_toggle_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(50))  # BoxLayout para el botón toggle
        self.layout_barra_lateral.add_widget(self.button_toggle_layout) 
        
        self.action_buttons_layout = BoxLayout(orientation='vertical', size_hint_x= 1, width=dp(50), spacing=2)# Layout botones laterales
        self.layout_barra_lateral.add_widget(self.action_buttons_layout)  # Agrega el layout de acción a la barra lateral

        # Área principal con contenido
        self.area_principal = BoxLayout(orientation='vertical', size_hint_x=1, padding=(dp(5), 0, 0, 0))  #loyaud derecha al lado de
        self.layout_principal.add_widget(self.layout_barra_lateral)  # Agrega la barra lateral al layout principal
        self.layout_principal.add_widget(self.area_principal)
        self.add_widget(self.layout_principal)

        self.barra_lateral()  # Asegúrate de llamar aquí después de haber definido el action_buttons_layout

        self.canvas_botones_laterales()
        
        # Contenido que ira en el área principal
        self.cargar_imagen()

    def cargar_imagen(self):
        self.estado_boxlayoutproductos = None

        # Ruta de la imagen del icono
        ruta_imagen = os.path.join(self.ruta_assets, 'icono.png')
        self.area_principal.clear_widgets()
        # Crear un widget de imagen y cargar la imagen
        if os.path.exists(ruta_imagen):
            # Crear un widget de imagen y cargar la imagen
            imagen = Image(source=ruta_imagen, size_hint=(1, 1))
            self.area_principal.add_widget(imagen)
        else:
            print(f"La imagen {ruta_imagen} no existe. No se cargará.")

        ##################### Botones laterales ###############################
    def barra_lateral(self):
        # Botón de toggle
        self.boton_togle = Button(text='arrow_forward', size_hint_y=None, height=dp(50), size_hint_x=1, font_name=self.font_path)
        self.boton_togle.bind(on_press=self.toggle_botones)

        # Agregar el botón toggle a button_toggle_layout
        self.button_toggle_layout.add_widget(self.boton_togle)

        # Crear botones con size_hint_x=1 para que se ajusten
        self.boton6 = Button(text='bar_chart', size_hint_y=None, height=dp(50), size_hint_x=1, font_size=sp(16), font_name=self.font_path, on_press=self.botonlateral_informes)
        self.boton5 = Button(text='computer', size_hint_y=None, height=dp(50), size_hint_x=1, font_size=sp(16), font_name=self.font_path, on_press=self.botonlateral_opciones_windows)
        self.boton4 = Button(text='group', size_hint_y=None, height=dp(50), size_hint_x=1, font_size=sp(16), font_name=self.font_path, on_press=self.botonlateral_usuarios)
        self.boton3 = Button(text='business', size_hint_y=None, height=dp(50), size_hint_x=1, font_size=sp(16), font_name=self.font_path, on_press=self.botonlateral_datos_negocio)
        self.boton2 = Button(text='inventory', size_hint_y=None, height=dp(50), size_hint_x=1, font_size=sp(16), font_name=self.font_path, on_press=self.botonlateral_entradas_salidas)
        self.boton1 = Button(text='store', size_hint_y=None, height=dp(50), size_hint_x=1, font_size=sp(16), font_name=self.font_path, on_press=self.botonlateral_productos)
        self.ir_pos = Button(text='arrow_back', size_hint_y=None, height=dp(50), size_hint_x=1, font_name=self.font_path , on_press=self.back_to_pos, font_size=sp(16))

        # Agrega los botones al action_buttons_layout
        self.action_buttons_layout.add_widget(self.boton6)
        self.action_buttons_layout.add_widget(self.boton5)
        self.action_buttons_layout.add_widget(self.boton4)
        self.action_buttons_layout.add_widget(self.boton3)
        self.action_buttons_layout.add_widget(self.boton2)
        self.action_buttons_layout.add_widget(self.boton1)
        self.action_buttons_layout.add_widget(self.ir_pos)

    def toggle_botones(self, instance):
        if self.layout_barra_lateral.width != dp(50):
            self.layout_barra_lateral.width = dp(50)
            self.boton_togle.text = 'arrow_forward'
            self.boton6.text = 'bar_chart'            
            self.boton5.text = 'computer'
            self.boton4.text = 'group'
            self.boton3.text = 'business'
            self.boton2.text = 'inventory'
            self.boton1.text = 'store'
            self.ir_pos.text = 'arrow_back'
            
            # Cambiar la fuente de todos los botones a la fuente personalizada
            for button in [self.boton1, self.boton2, self.boton3, self.boton4, self.boton5, self.boton6, self.ir_pos]:
                button.font_name = self.font_path
        else:
            self.layout_barra_lateral.width = dp(150)
            self.boton_togle.text = 'arrow_back'
            
            # Cambiar los textos de los botones para que se ajusten al nuevo ancho
            self.boton6.text = 'Informes'                    
            self.boton5.text = 'Windows'
            self.boton4.text = 'Usuarios'
            self.boton3.text = 'Negocio'
            self.boton2.text = 'Entradas y Salidas'
            self.boton1.text = 'Productos'
            self.ir_pos.text = '<- Atras'
            
            # Cambiar la fuente de todos los botones a Roboto
            for button in [self.boton1, self.boton2, self.boton3, self.boton4, self.boton5, self.boton6, self.ir_pos]:
                button.font_name = 'Roboto-Bold'


            


    def funcion_dobleclick(self, instance):
        if self.tabla_actual == 'tabla_productos':  
            if self.boton_lateral_actual == 'lateral_productos':
                self.editar_productos(None)
            elif self.boton_lateral_actual == 'lateral_entradas_salidas':
                self.entrada_producto(None)



###########################    def botones principal        ############################################################### self.productos_boxLayout()
##########'lateral_entradas_salidas', 'lateral_productos', 'datos_negocio', 'lateral_opciones_windows'

    def botonlateral_informes(self, instance):
        if self.boton_lateral_actual == 'lateral_informes': #no hacer nada si ya estamos en este boton lateral
            return
        self.boton_lateral_actual = 'lateral_informes'
        self.tabla_actual = None
        self.estado_boxlayoutproductos = None
        Informes(self)

        self.reset_buttons()             
        self.boton6.disabled = True
        self.boton6.background_color = (0.5, 0.7, 1, 1)



    def botonlateral_opciones_windows(self, instance):
        if self.boton_lateral_actual == 'lateral_opciones_windows': #no hacer nada si ya estamos en este boton lateral
            return
        self.boton_lateral_actual = 'lateral_opciones_windows'
        self.tabla_actual = None
        self.estado_boxlayoutproductos = None
        Configwindows(self)

        self.reset_buttons()  
           
        self.boton5.disabled = True
        self.boton5.background_color = (0.5, 0.7, 1, 1)





    def botonlateral_usuarios(self, instance):        
        self.reset_buttons()
        if self.boton_lateral_actual == 'lateral_usuarios':
            return
        self.boton_lateral_actual = 'lateral_usuarios'
        self.tabla_actual = None
        self.estado_boxlayoutproductos = None
        ListaUsuarios(self)

        self.reset_buttons()        
        self.boton4.background_color = (0.1176, 0.5137, 0.8078, 1) 
        self.boton4.disabled = True


        # print('boton lateral actual:')
        # print({self.boton_lateral_actual})              




        

    def botonlateral_datos_negocio(self, instance):
        self.reset_buttons()
        if self.boton_lateral_actual == 'lateral_datos_negocio':  # no hacer nada si ya estamos en este boton lateral
            return
        self.boton_lateral_actual = 'lateral_datos_negocio'
        self.tabla_actual = None
        self.estado_boxlayoutproductos = None

        ConfigNegocio(self)


        self.reset_buttons()     

        self.boton3.background_color = (0.5, 0.7, 1, 1)
        self.boton3.disabled = True
        # print('boton lateral actual:')
        # print({self.boton_lateral_actual})



    def botonlateral_entradas_salidas(self, instance):
        self.reset_buttons()        
        if self.boton_lateral_actual == 'lateral_entradas_salidas': #no hacer nada si ya estamos en este boton lateral 
            return      
        self.boton_lateral_actual = 'lateral_entradas_salidas'

        if self.estado_boxlayoutproductos is None: # Llama a productos_boxLayout si es None
            self.productos_boxLayout() 
            self.botones_entradas_salidas_productos()    

        else:
            if self.boton_lateral_actual == 'lateral_entradas_salidas':
                self.botones_entradas_salidas_productos()    
                

        self.cargar_productos_entradas_salidas()
        self.reset_buttons()     

        self.boton2.background_color = (0.5, 0.7, 1, 1)
        self.boton2.disabled = True

        # print('boton lateral actual:')
        # print({self.boton_lateral_actual})    






    def botonlateral_productos(self, instance): #100%
        self.reset_buttons()      
        if self.boton_lateral_actual == 'lateral_productos': #no hacer nada si ya estamos en lateral productos
            return
        self.boton_lateral_actual = 'lateral_productos'

        if self.estado_boxlayoutproductos is None: # Llama a productos_boxLayout si no existe
            self.productos_boxLayout()  
            self.botones_productos_add() 
        else:
            if self.boton_lateral_actual == 'lateral_productos':  #  si existe solo crea botones de productos
                self.botones_productos_add() 
            if self.Datos_en_boxlayoutP_izquierda != 'categorias': 
                self.tabla_categoria()                
            if self.tabla_actual != 'tabla_productos':  
                self.encabezado_productos()  
                
                
        self.cargar_productos_en_tabla()
        self.reset_buttons()     

        self.boton1.background_color = (0.5, 0.7, 1, 1)
        self.boton1.disabled = True

        # print('boton lateral actual:')
        # print({self.boton_lateral_actual})    


    def reset_buttons(self,):

        # Activar todos los botones
        self.boton6.disabled = False
        self.boton5.disabled = False
        self.boton4.disabled = False
        self.boton3.disabled = False
        self.boton2.disabled = False
        self.boton1.disabled = False

        # Restaurar el color de fondo a blanco        
        self.boton6.background_color = (1, 1, 1, 1)
        self.boton5.background_color = (1, 1, 1, 1)
        self.boton4.background_color = (1, 1, 1, 1)
        self.boton3.background_color = (1, 1, 1, 1)
        self.boton2.background_color = (1, 1, 1, 1)
        self.boton1.background_color = (1, 1, 1, 1)




###########################    Boxloyaut de las productos         ###############################################################

    def productos_boxLayout(self):
        self.area_principal.clear_widgets()
        self.estado_boxlayoutproductos = 'Creado'
        self.layout_productos = BoxLayout(orientation='vertical')  # Principal, abarca el área derecha pegada a los botones laterales.

        # BoxLayout superior con altura fija <Botones y barra de búsqueda>
        self.superior = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))  # Usamos dp para la altura.
        self.contenedor_botones = BoxLayout(orientation='horizontal', spacing=dp(10))  # Usamos dp para el espaciado de botones.
        self.superior.add_widget(self.contenedor_botones)

        self.barra_busqueda()  # Llamamos a la función barra_busqueda aquí.

        # Creamos el BoxLayout inferior con disposición horizontal
        self.inferior = BoxLayout(orientation='horizontal', size_hint_y=1) 

        # Añadimos los BoxLayout de izquierda y derecha a la parte inferior
        self.boxlayoutP_izquierda = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(200))  
        self.boxlayoutP_derecha = BoxLayout(orientation='vertical', size_hint_x=1) 

        # Añadimos los BoxLayout izquierda y derecha al inferior
        self.inferior.add_widget(self.boxlayoutP_izquierda)
        self.inferior.add_widget(self.boxlayoutP_derecha)

        # Añadimos el layout de productos al área principal
        self.layout_productos.add_widget(self.superior)
        self.layout_productos.add_widget(self.inferior)
        self.area_principal.add_widget(self.layout_productos)
        self.canvas_productos()


        #self.botones_productos_add()  # borrar segun tabla principal  

        # Cargar tablas al iniciar
        self.tabla_categoria()    
        self.encabezado_y_tabla_productos()



##################################### tablas de los productos ######################


    def tabla_categoria(self):
        # Botones para agregar, editar y borrar categorías 
        self.boxlayoutP_izquierda.clear_widgets()
        self.Datos_en_boxlayoutP_izquierda = 'categorias'


        self.botones_categoria()
        # Crear el encabezado de la tabla de categorías
        categories_header = BoxLayout(size_hint_y=None, height=30)
        category_label = Label(text='Categorías', font_size=sp(18), bold=True, size_hint_y=None, height=30)
        categories_header.add_widget(category_label)

        # Agregar el encabezado al BoxLayout principal
        self.boxlayoutP_izquierda.add_widget(categories_header)

        # ScrollView para las categorías
        self.categories_list_scroll = ScrollView()
        self.categories_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.categories_list.bind(minimum_height=self.categories_list.setter('height'))
        
        self.canvas_categorias()

        # Añadir lista de categorías al ScrollView
        self.categories_list_scroll.add_widget(self.categories_list)
        self.boxlayoutP_izquierda.add_widget(self.categories_list_scroll)

        self.cargar_categorias()




    def cargar_categorias(self):
        categorias = [("Todas",), *cargar_categorias_db(), ("Sin categoría",)]
        self.categories_list.clear_widgets()

        self.selected_category = "Todas"
        self.categories_list.spacing = 8
        for categoria in categorias:
            if categoria[0] == "Todas":
                categoria_label = Label(text=categoria[0], size_hint_y=None, height=30, padding=(0, 10), color=(1, 1, 0, 1), bold=True, font_size='18sp')
            else:
                categoria_label = Label(text=categoria[0], size_hint_y=None, height=30, padding=(0, 10), color=(1, 1, 1, 1), bold=False, font_size='16sp')
            self.categories_list.add_widget(categoria_label)
            categoria_label.bind(on_touch_down=self.on_category_select)

        

    def botones_categoria(self):
        self.category_buttons = BoxLayout(size_hint_y=None, height=dp(50), orientation='horizontal', spacing=8, padding=[5, 5])
        
        # Crear botones de categoría      
        self.add_category_button = Button(text='add_circle', size_hint_x=1, width=dp(40), font_size=sp(16), background_color=(0, 0, 0, 0), color=(1, 1, 1, 1), font_name=self.font_path)
        self.add_category_button.bind(on_press=self.show_new_category_popup)

        self.edit_category_button = Button(text='edit', size_hint_x=1, width=dp(40), font_size=sp(16), background_color=(0, 0, 0, 0), color=(1, 1, 1, 1), font_name=self.font_path)
        self.edit_category_button.bind(on_press=self.editar_categoria)

        self.delete_category_button = Button(text='delete', size_hint_x=1, width=dp(40), font_size=sp(16), background_color=(0, 0, 0, 0), color=(1, 1, 1, 1), font_name=self.font_path)
        self.delete_category_button.bind(on_press=self.borrar_categoria)

        # Agregar los botones al contenedor
        self.category_buttons.add_widget(self.add_category_button)
        self.category_buttons.add_widget(self.edit_category_button)
        self.category_buttons.add_widget(self.delete_category_button)

        # Agregar los botones de categoría a la parte izquierda
        self.boxlayoutP_izquierda.add_widget(self.category_buttons)

        

    def encabezado_y_tabla_productos(self):
        # Crear un BoxLayout para el encabezado y productos
        self.encabezado_box_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        self.tabla_producto_box_layout = BoxLayout(orientation='vertical', size_hint_y=1)
        self.boxlayoutP_derecha.add_widget(self.encabezado_box_layout)
        self.boxlayoutP_derecha.add_widget(self.tabla_producto_box_layout)

        self.encabezado_productos()
        self.crear_loyaut_tabla_productos()
     

    def encabezado_productos(self, headers=None):
        self.encabezado_box_layout.clear_widgets()
        if headers is None:
            headers = ['', 'ID', 'Nombre', 'Categoría', 'Precio\nCompra', 'Precio\nVenta', 'Stock\nActual']
        proportions = [0.1, 0.1, 0.2, 0.2, 0.15, 0.15, 0.2] 

        for header, proportion in zip(headers, proportions):
            label = Label(text=header, bold=True, font_size=sp(16), size_hint_x=proportion, halign='center', valign='middle')
            label.bind(size=label.setter('text_size'))  # Permite que el texto se ajuste dentro del Label
            self.encabezado_box_layout.add_widget(label)



    def crear_loyaut_tabla_productos(self):
        self.tabla_productos = TablaProductos()  
        self.tabla_producto_box_layout.add_widget(self.tabla_productos)
        #self.cargar_productos_en_tabla()  # Cargar los productos en la tabla



    def cargar_productos_en_tabla(self):
        if hasattr(self, 'tabla_productos') and self.tabla_productos:
            self.tabla_productos.data = []  # Limpiar los datos actuales
            productos = cargar_productos_administrar() 
            self.tabla_productos.cargar_productos(productos)  
            self.id_transaccion_seleccionada = None
            self.producto_seleccionado = None    
            self.tabla_actual = 'tabla_productos'   
            self.search_input.text = ''    

            self.selected_category = "Todas" if self.selected_category != "Todas" else self.selected_category
            for category_label in self.categories_list.children:
                if category_label.text == "Todas":
                    self.cambiar_color_categoria(category_label)
                    break                         
        else:
            agregar_log("Error: 'productos_recycle_view' no está disponible.")        




    def cargar_productos_entradas_salidas(self):
        if hasattr(self, 'tabla_productos') and self.tabla_productos:
            self.tabla_productos.data = []  # Limpiar los datos actuales
            productos = cargar_productos_administrar_lat_entradas()
            self.tabla_productos.cargar_productos(productos)  
            self.id_transaccion_seleccionada = None
            self.producto_seleccionado = None    
            self.tabla_actual = 'tabla_productos'
            self.search_input.text = ''


            self.selected_category = "Todas" if self.selected_category != "Todas" else self.selected_category
            for category_label in self.categories_list.children:
                if category_label.text == "Todas":
                    self.cambiar_color_categoria(category_label)
                    break            
        else:
            agregar_log("Error: 'productos_recycle_view' no está disponible.")               


    def recargarproductos_en_tabla(self):
        if hasattr(self, 'tabla_productos') and self.tabla_productos:
            self.tabla_productos.data = []
        productos = cargar_productos_administrar()
        self.tabla_productos.cargar_productos(productos)
        self.filtrar_por_categoria()
        if self.search_input.text:
            self.ejecutar_filtro(self.search_input.text)

##########################  🔎🔎🔎🔎  Barra de busqueda    🔎🔎🔎🔎   #################################        


    def barra_busqueda(self):
        self.search_input = TextInput(hint_text="Buscar por ID, Nombre o Nota", size_hint_y=None, height=dp(40), background_color=(0.2, 0.2, 0.2, 1), hint_text_color=(0.5, 0.5, 0.5, 1), foreground_color=(1, 1, 1, 1), multiline=False)
        self.search_input.bind(text=self.buscar_productos)
        self.superior.add_widget(self.search_input)  # Agregamos el TextInput al superior



##########################  🏷️🏷️🏷️🏷️  Barra de busqueda    🏷️🏷️🏷️🏷️   #################################   



    def botones_productos_add(self):
        self.contenedor_botones.clear_widgets() #borrar widgets antes de cargar


        espacio_logo = Image(source=self.obtener_logo, size_hint_x=None, size_hint_y=1, width=dp(100))  # El alto se ajustará al contenedor

        
        self.add_product_button = Button(text='Agregar', size_hint_x=None, width=dp(100), background_color=(0, 0, 1, 1), font_size=sp(16), on_press=self.abrir_popup_nuevo_producto)
        self.edit_button = Button(text='Editar', size_hint_x=None, width=dp(100), font_size=sp(16), on_press=self.editar_productos)
        self.delete_button = Button(text='Eliminar', size_hint_x=None, width=dp(100), font_size=sp(16), on_press=self.borrar_productos)
        self.productos_ocultos = Button(text='Productos\n    Ocultos', size_hint_x=None, width=dp(80), background_color=(0, 0.4, 0, 1), font_size=sp(12), on_press=self.ProductosOcultos_popup)

        self.contenedor_botones.add_widget(espacio_logo)
        self.contenedor_botones.add_widget(self.add_product_button)
        self.contenedor_botones.add_widget(self.edit_button)
        self.contenedor_botones.add_widget(self.delete_button)
        self.contenedor_botones.add_widget(self.productos_ocultos)




    ############ Botones Productos DEF #####################    
    def ProductosOcultos_popup(self, instance):
        self.productos_ocultos_popup = ProductosOcultos(parent=self)
        self.productos_ocultos_popup.open()


    def editar_productos(self, instance):
        if self.producto_seleccionado:
            editando = True
            popup = crearpopupproductos(parent=self, editando=editando, admin_screen=self, codigo=self.producto_seleccionado)
            popup.open()  # Abrir el popup
        else:
            pass


    def abrir_popup_nuevo_producto(self, instance):
        editando = False
        popup = crearpopupproductos(parent=self, editando=editando, admin_screen=self, codigo=None)
        popup.open()


    def borrar_productos(self, instance):
        if self.producto_seleccionado:       
            popup = ConfirmDeletePopup(parent=self, admin_screen=self, codigo=self.producto_seleccionado)
            popup.open()  # Abrir el popup
        else:
            pass





    ###############   📦 📦 📦 📦 📦 Botones mas Entradas y Salidas productos 📦 📦 📦 📦 📦 📦 📦   ############

    def encabezado_entradas(self):
        self.encabezado_box_layout.clear_widgets()
        headers = ['', 'ID', 'Nombre', 'Categoría', 'Precio\nCompra', ' Cantidad', 'Fecha']
        #headers = ['', 'ID', 'Nombre', 'Categoría', 'Precio\nCompra', 'Precio\nVenta', 'Stock\nActual']
        
        proportions = [0.1, 0.1, 0.2, 0.2, 0.15, 0.15, 0.2]  # Ajusta estos valores según sea necesario

        for header, proportion in zip(headers, proportions):
            label = Label(text=header, bold=True, font_size=sp(16), size_hint_x=proportion, halign='center', valign='middle')
            label.bind(size=label.setter('text_size'))  # Permite que el texto se ajuste dentro del Label
            self.encabezado_box_layout.add_widget(label)

    def botones_entradas_salidas_productos(self):        
        self.contenedor_botones.clear_widgets()

        #espacio_logo = Image(source=self.obtener_logo, size_hint_x=None, size_hint_y=1, width=dp(100))
        label_texto_ventana = Label(text='[b]Entradas y Salidas[/b]', size_hint_x=None, width=dp(150), size_hint_y=1, font_size=sp(16), markup=True)

        self.add_entrada_product_button = Button(text='[b]Agregar\n   Entradas[/b]', size_hint_x=None, width=100, background_color=(0, 0, 1, 1), font_size=sp(16), markup=True, on_press=self.entrada_producto)        
        self.ver_entradas = Button(text='Entradas\n Productos', size_hint_x=None, width=100, font_size=sp(16), background_color=(1, 1, 0, 1), on_press=self.ver_entradas_def)
        self.ver_salidas = Button(text='Salidas\n Producto', size_hint_x=None, width=100, font_size=sp(16), background_color=(1, 1, 0, 1), on_press=self.ver_salidas_def)

        #self.contenedor_botones.add_widget(espacio_logo)
        self.contenedor_botones.add_widget(label_texto_ventana)  # Agrega el label después del logo
        self.contenedor_botones.add_widget(self.ver_entradas) 
        self.contenedor_botones.add_widget(self.ver_salidas)
        self.contenedor_botones.add_widget(self.add_entrada_product_button)        


            # BOTONES EDITAR ENTRADAS #
    def cambiar_botones_entradas_salidas_productos(self, tipo):
        self.contenedor_botones.clear_widgets()  # Limpiar el layout antes de cargar los nuevos botones

        # Determinar el texto y las funciones on_press según el tipo
        if tipo == "entradas":
            label_texto = 'Entradas Productos'

            ocultar_texto = 'Ocultar\n entradas'
            borrar_texto = 'Eliminar\n entrada'

            ocultar_func = self.ocultar_dt_entradas_salidas
            borrar_func = self.borrar_entrada

        elif tipo == "salidas":
            label_texto = 'Salidas Productos'

            ocultar_texto = 'Ocultar\n Salidas'
            borrar_texto = 'Eliminar\n Salidas'

            ocultar_func = self.ocultar_dt_entradas_salidas
            borrar_func = self.borrar_salidas

        label_texto_ventana = Label(text=f'[b]{label_texto}[/b]', size_hint_x=None, width=dp(150), size_hint_y=1, font_size=sp(16), markup=True)

        
        # Añadir el botón de eliminar antes que el de ocultar en salidas
        self.borrar_button = Button(text=borrar_texto, size_hint_x=None, width=90, background_color=(1, 0, 0, 1), font_size=12, on_press=borrar_func)
        self.ocultar_entradas = Button(text=ocultar_texto, size_hint_x=None, width=100, background_color=(1, 1, 0, 1), font_size=16, on_press=ocultar_func)     
        
        # Añadir widgets al contenedor en el orden deseado
        self.contenedor_botones.add_widget(label_texto_ventana)
        
        # Primero añadir el botón de borrar y luego el de ocultar
        if tipo == "salidas":
            self.contenedor_botones.add_widget(self.borrar_button)
            self.contenedor_botones.add_widget(self.ocultar_entradas)
        else:
            self.contenedor_botones.add_widget(self.ocultar_entradas)
            self.contenedor_botones.add_widget(self.borrar_button)



   ###############                   Datos en tabla que sean de entradas               ############


    def cargar_entradas_en_tabla(self):    #usar para recargar tabla si estas en entradas
        if hasattr(self, 'tabla_productos') and self.tabla_productos:
            self.tabla_productos.data = []  
            entradas = cargar_entradas_administrar()
            self.id_transaccion_seleccionada = None
            self.producto_seleccionado = None              
            self.tabla_productos.cargar_entradas(entradas)  
            self.tabla_actual = 'tabla_entradas' 




   ###############    Def mas Entradas y salidas principal   ############

    def ver_entradas_def(self, instance):    
        if hasattr(self, 'tabla_productos') and self.tabla_productos:
            self.boxlayoutP_izquierda.clear_widgets() #mover al crear filtro por fecha
            self.Datos_en_boxlayoutP_izquierda = 'filtro_fechas'    #mover al crear filtros         
           # self.encabezado_entradas()
            self.cargar_entradas_en_tabla()
            self.cambiar_botones_entradas_salidas_productos("entradas")
            self.encabezado_productos(headers=['', 'ID', 'Nombre', 'Categoría', 'Precio\nCompra', 'Cantidad', 'Fecha'])     

                                
    def entrada_producto(self, instance):
        if self.producto_seleccionado:    
            popup = Agregar_Entradas(admin_screen=self, codigo=self.producto_seleccionado, nombre=self.nombre_producto_seleccionado,
                                     categoria=self.categoria_producto_seleccionado, precio_compra=self.precio_compra_producto_seleccionado,
                                     precio_venta=self.precio_venta_producto_seleccionado)           
            popup.open()  
        else:
            print("No hay ningún producto seleccionado.")

  ###############                   Datos en tabla que sean de salidas              ############
    def cargar_salidas_en_tabla(self):    #usar para recargar tabla si estas en entradas
        if hasattr(self, 'tabla_productos') and self.tabla_productos:
            self.tabla_productos.data = []  
            salidas = cargar_salidas_administrar()
            self.tabla_productos.cargar_salidas(salidas)             
            self.id_transaccion_seleccionada = None
            self.producto_seleccionado = None              
            self.tabla_actual = 'tabla_salidas' 
             #para crear fechas en la boxloyaus izquierda
            #self.botones_entradas_productos() 




    def ver_salidas_def(self, instance):    
        if hasattr(self, 'tabla_productos') and self.tabla_productos:
            self.boxlayoutP_izquierda.clear_widgets() #mover al def que creara las fechas
            self.Datos_en_boxlayoutP_izquierda = 'filtro_fechas'    #mover al crear filtros         
            #self.encabezado_entradas()
            self.cargar_salidas_en_tabla()
            self.cambiar_botones_entradas_salidas_productos("salidas")                
            self.encabezado_productos(headers=['', 'ID', 'Nombre', 'Categoría', 'Precio\nVenta', 'Cantidad', 'Fecha'])          











###############   📦 📦 📦 📦 📦 Def mas Entradas y Salidas productos 📦 📦 📦 📦 📦 📦 📦   ############

    def ocultar_dt_entradas_salidas(self, instance):
        self.tabla_actual = 'tabla_productos'  
        self.tabla_categoria()
        self.botones_entradas_salidas_productos()
        self.cargar_productos_en_tabla()
        self.tabla_categoria() 
        self.encabezado_productos()
      





    def borrar_entrada(self, instance):
        # Verificar que hay un producto seleccionado y que id_transaccion_seleccionada no es None o una cadena vacía
        if self.producto_seleccionado and self.id_transaccion_seleccionada not in (None, ''):       
            popup = ConfirmDeleteEntradaPopup(parent=self, admin_screen=self, id_transaccion=self.id_transaccion_seleccionada, codigo=self.producto_seleccionado)
            popup.open()

        else: #borrar print solo porrar desde else
            print("No hay entrada seleccionada o el ID de entrada no es válido.")  # Mensaje opcional



    def borrar_salidas(self, instance):
        # Verificar que hay un producto seleccionado y que id_transaccion_seleccionada no es None o una cadena vacía
        if self.producto_seleccionado and self.id_transaccion_seleccionada not in (None, ''):       
            popup = ConfirmDeleteSalidasPopup(parent=self, admin_screen=self, id_transaccion=self.id_transaccion_seleccionada, codigo=self.producto_seleccionado)
            popup.open()

        else: #borrar print solo porrar desde else
            print("No hay entrada seleccionada o el ID de entrada no es válido.")  # Mensaje opcional





############################################# Barra de busqueda y busqueda por categoria #####################      []                              ###############################

    def buscar_productos(self, instance, value):
        # Si no hay texto en el campo de búsqueda, no ejecutar el filtro
        if not value:
            return
        if self.selected_category != "Todas":
            for category_label in self.categories_list.children:
                if category_label.text == "Todas":
                    self.cambiar_color_categoria(category_label)  # Cambiar el color de "Todas"
                    break  # Ya encontramos el label, no necesitamos seguir buscando
        if self.retraso_busqueda_evento is not None:
            self.retraso_busqueda_evento.cancel()

        self.retraso_busqueda_evento = Clock.schedule_once(lambda dt: self.ejecutar_filtro(value), 0.2)



    def ejecutar_filtro(self, value):
        query = value.lower()
        
        if self.tabla_actual == 'tabla_productos':
            productos = cargar_productos_administrar_lat_entradas() if self.boton_lateral_actual == 'lateral_entradas_salidas' else cargar_productos_administrar()  # Cargar todos los productos
            if query:
                productos_filtrados = [
                    prod for prod in productos
                    if query in prod[0].lower() or query in prod[1].lower() or query in (prod[6] or '').lower()
                ]
            else:
                productos_filtrados = productos
            self.tabla_productos.cargar_productos(productos_filtrados)

        elif self.tabla_actual == 'tabla_entradas':
            entradas = cargar_entradas_administrar()  # Cargar todas las entradas
            if query:
                entradas_filtradas = [
                    entrada for entrada in entradas
                    if query in entrada[1].lower() or query in entrada[2].lower()  # Filtrar por código (índice 1) y nombre (índice 2)
                ]
            else:
                entradas_filtradas = entradas
            self.tabla_productos.cargar_entradas(entradas_filtradas)

        elif self.tabla_actual == 'tabla_salidas':
            salidas = cargar_salidas_administrar()  # Cargar todas las salidas
            if query:
                salidas_filtradas = [
                    salida for salida in salidas
                    if query in salida[1].lower() or query in salida[2].lower()  # Filtrar por código (índice 1) y nombre (índice 2)
                ]
            else:
                salidas_filtradas = salidas
            self.tabla_productos.cargar_salidas(salidas_filtradas)





    def filtrar_por_categoria(self):
        productos = cargar_productos_administrar()
        
        if self.selected_category == "Todas":
            productos_filtrados = productos
        elif self.selected_category == "Sin categoria":
            productos_filtrados = [
                prod for prod in productos
                if not prod[2]
            ]
        elif self.selected_category:
            productos_filtrados = [
                prod for prod in productos
                if prod[2].lower() == self.selected_category.lower()
            ]
        else:
            productos_filtrados = productos

        self.tabla_productos.cargar_productos(productos_filtrados)


    def on_category_select(self, instance, touch):
        if self.tabla_actual != 'tabla_productos':  # Comprobar si la tabla actual no es 'tabla_productos'
            return      
        if instance.collide_point(*touch.pos):
            self.selected_category = instance.text  # Obtener el texto directamente del Label
            if self.search_input.text:
                self.search_input.text = ''

            self.cambiar_color_categoria(instance)
            self.filtrar_por_categoria()


    def cambiar_color_categoria(self, selected_instance):
        # Cambiar el color y tamaño de fuente de todos los labels en la lista de categorías
        for category_label in self.categories_list.children:
            category_label.color = (1, 1, 1, 1)  # Color blanco
            category_label.bold = False
            category_label.font_size = '14sp'  # Tamaño de fuente predeterminado
        selected_instance.color = (1, 1, 0, 1)  # Color amarillo
        selected_instance.bold = True
        selected_instance.font_size = '18sp'  # Tamaño de fuente aumentado para el label seleccionado




############################################ Mouse y color, y barra lateral ############################










################################ opciones categoria ###################
    def show_new_category_popup(self, instance):
        popup = AddCategoryPopup(admin_screen=self)        
        popup.open()


    def editar_categoria(self, instance):
        if self.selected_category:
            if self.selected_category.lower() in ['todas', 'sin categoría']:  # Verifica si la categoría es "todas" o "sin categoría"
                print(f"La categoría '{self.selected_category}' no se puede editar.")  # Mensaje informativo
            else:
                popup = EditCategoryPopup(admin_screen=self, selected_category=self.selected_category)
                popup.open()
        else:
            print("Por favor, selecciona una categoría para editar.")


    def borrar_categoria(self, instance):
        if self.selected_category:
            if self.selected_category.lower() in ['todas', 'sin categoría']:  # Verifica si la categoría es "todas" o "sin categoría"
                print(f"La categoría '{self.selected_category}' no se puede borrar.")  # Mensaje informativo
            else:
                popup = DeleteCategoryPopup(admin_screen=self, selected_category=self.selected_category)
                popup.open()
        else:
            # Opcional: mostrar un mensaje si no hay categoría seleccionada
            print("Por favor, selecciona una categoría para borrar.")

############################ Canvas de Tabla #########################        
    def canvas_screen(self):
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 1)  # Color gris oscuro
            self.rect_fondo = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=lambda instance, value: self.update_rect(self.rect_fondo, instance), 
                    pos=lambda instance, value: self.update_rect(self.rect_fondo, instance))

    def canvas_botones_laterales(self):
        with self.layout_barra_lateral.canvas.before:
            Color(0.3, 0.3, 0.3, 1)  # Color gris claro
            self.rect_lateral = Rectangle(size=self.layout_barra_lateral.size, pos=self.layout_barra_lateral.pos)
            self.layout_barra_lateral.bind(size=lambda instance, value: self.update_rect(self.rect_lateral, instance), 
                                            pos=lambda instance, value: self.update_rect(self.rect_lateral, instance))

    def canvas_productos(self):
        with self.inferior.canvas.before:
            Color(0.051, 0.051, 0.051, 1)  # Color negro
            self.rect = Rectangle(size=self.inferior.size, pos=self.inferior.pos)
        self.inferior.bind(size=lambda instance, value: self.update_rect(self.rect, instance), 
                        pos=lambda instance, value: self.update_rect(self.rect, instance))

    def canvas_categorias(self):
        with self.boxlayoutP_izquierda.canvas.before:
            Color(0.105, 0.105, 0.105, 1)  # Gris muy oscuro
            self.rect_categories = Rectangle(size=self.boxlayoutP_izquierda.size, pos=self.boxlayoutP_izquierda.pos)
        self.boxlayoutP_izquierda.bind(size=lambda instance, value: self.update_rect(self.rect_categories, instance), 
                                        pos=lambda instance, value: self.update_rect(self.rect_categories, instance))

    def update_rect(self, rect, instance):
        # Actualizar el tamaño y posición del rectángulo
        rect.pos = instance.pos
        rect.size = instance.size




##################### Regresar al Pos ########################################
    def back_to_pos(self, instance):
        products_screen = self.manager.get_screen('products')
        if hasattr(products_screen, 'productos_tabla_pos'):
            print('#actualizar_productos_pos(products_screen.productos_tabla_pos')
            #actualizar_productos_pos(products_screen.productos_tabla_pos)        
        self.manager.current = 'products'        
        self.manager.remove_widget(self)      



























#################################### Tablas ####################################################################
class ProductoRow(BoxLayout):
    id_transaccion = StringProperty('')
    codigo = StringProperty('')
    nombre = StringProperty('')
    categoria = StringProperty('')
    precio_compra = StringProperty('')
    precio_venta = StringProperty('')
    stock_actual = StringProperty('')
    ruta_imagen = StringProperty('')
    selected = BooleanProperty(False) 


    def reset_selection(self):
        self.selected = False  # Reinicia la selección al reutilizar la fila


    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos) or super(ProductoRow, self).on_touch_down(touch):
            return False

        if hasattr(self, 'last_touch_time') and Clock.get_time() - self.last_touch_time < 0.2:
            self.call_funcion_dobleclick_tabla()
        else:
            self.last_touch_time = Clock.get_time()
            self.parent.parent.update_selection(self)
        return True



    def call_funcion_dobleclick_tabla(self):
        app = App.get_running_app()
        admin_screen = app.root.get_screen('admin')
        admin_screen.funcion_dobleclick(self)  # Llama al método editar_productos con la instancia seleccionada


    def on_selected(self, instance, value):
        self.canvas.before.clear()  # Limpia el lienzo anterior
        with self.canvas.before:
            Color(0, 0.6, 1, 1) if value else Color(0.051, 0.051, 0.051, 1)  # Celeste si seleccionado, blanco si no
            self.rect = Rectangle(size=self.size, pos=self.pos)  # Crea el rectángulo
        self.bind(size=self._update_rect, pos=self._update_rect)  # Vínculo para actualizar el rectángulo al cambiar tamaño o posición

    def _update_rect(self, instance, value):
        self.rect.pos = self.pos  # Actualiza la posición del rectángulo


class TablaProductos(RecycleView):
    def __init__(self, **kwargs):
        super(TablaProductos, self).__init__(**kwargs)
        self.data = []  # Inicializa una lista vacía para los datos
        self.viewclass = ProductoRow  # Establecer viewclass aquí
        self.selected_row = None  # Propiedad para almacenar la fila seleccionada
    

    def cargar_productos(self, productos):
        self.data.clear()
        self.data.extend([{
            'codigo': f'{prod[0]}',           
            'nombre': f'{prod[1]}',        
            'categoria': f'{prod[2]}',       
            'precio_compra': f'{prod[3]}',    
            'precio_venta': f'{prod[4]}',     
            'stock_actual': f'{int(prod[5]) if prod[5].is_integer() else prod[5]}',    
            'ruta_imagen': self.verificar_imagen(prod[7]),
            'selected': False  # Inicializar aquí
        } for prod in productos])

        self.refresh_from_data()  # Actualizar la vista con los nuevos datos

    def verificar_imagen(self, ruta_imagen):
        """Verifica si la imagen existe. Si no, retorna una cadena vacía."""
        if ruta_imagen and os.path.exists(ruta_imagen):
            return ruta_imagen
        return ''  # Retorna una cadena vacía si la imagen no existe o si es None



    def update_selection(self, selected_row):
        """Actualiza la selección de filas."""
        # Reiniciar la selección anterior si existe y es diferente a la nueva
        if self.selected_row and self.selected_row != selected_row:
            self.selected_row.reset_selection()        
        
        # Actualizar la fila seleccionada y marcar como seleccionada
        self.selected_row = selected_row
        selected_row.selected = True
        
        # Guardar los datos seleccionados
        seleccionID = {
            'producto_seleccionado': selected_row.codigo,
            'id_transaccion_seleccionada': selected_row.id_transaccion
        }
        
        seleccion_completa = {
            'producto_seleccionado': selected_row.codigo,
            'nombre_producto_seleccionado': selected_row.nombre,
            'categoria_producto_seleccionado': selected_row.categoria,
            'precio_compra_producto_seleccionado': selected_row.precio_compra,
            'precio_venta_producto_seleccionado': selected_row.precio_venta,
        }        


        app = App.get_running_app()
        admin_screen = app.root.get_screen('admin')
        
        for key, value in seleccionID.items():
            setattr(admin_screen, key, value)
        
        # Actualizar los atributos en admin_screen con seleccion_completa
        for key, value in seleccion_completa.items():
            setattr(admin_screen, key, value)
        pass
        #print(f"Producto seleccionado: {self.selected_row.codigo}, {self.selected_row.nombre}, {self.selected_row.categoria}, {self.selected_row.precio_compra}, {self.selected_row.precio_venta}, {self.selected_row.id_transaccion}")



################### Cargar Entradas  ##################

    def cargar_entradas(self, productos):
        self.data.clear()        
        self.data.extend([{             
            'id_transaccion': f'{prod[0]}',   
            'stock_actual': f'{prod[6]}',      
            'codigo': f'{prod[1]}',       
            'nombre': f'{prod[2]}',   
            'categoria': f'{prod[3]}',
            'precio_compra': f'{prod[5]}',               
            'precio_venta': f'{prod[4]}',             
            'ruta_imagen': '',  
            'selected': False  # Inicializar aquí
        } for prod in productos])
        
        self.refresh_from_data()




    def cargar_salidas(self, productos):
        self.data.clear()        
        self.data.extend([{             
            'id_transaccion': f'{prod[0]}', 
            'stock_actual': f'{prod[6]}',      
            'codigo': f'{prod[1]}',       
            'nombre': f'{prod[2]}',   
            'categoria': f'{prod[3]}',
            'precio_compra': f'{prod[5]}',               
            'precio_venta': f'{prod[4]}',             
            'ruta_imagen': '',  
            'selected': False  # Inicializar aquí
        } for prod in productos])
        
        self.refresh_from_data()


################### Cargar Entradas  ##################





def reset_seleccion(self):
    """Restablece los datos seleccionados a None."""
    self.selected_row = None  # Reiniciar la fila seleccionada
    app = App.get_running_app()
    admin_screen = app.root.get_screen('admin')

    # Establecer todos los atributos de selección en None
    atributos_a_resetear = [
        'producto_seleccionado',
        'nombre_producto_seleccionado',
        'categoria_producto_seleccionado',
        'precio_compra_producto_seleccionado',
        'id_transaccion_seleccionada'
    ]
    
    for attr in atributos_a_resetear:
        setattr(admin_screen, attr, None)

    print("Datos seleccionados restablecidos a None.")







class AdminApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(AdminScreen(name='admin'))

        return sm

if __name__ == '__main__':
    AdminApp().run()
