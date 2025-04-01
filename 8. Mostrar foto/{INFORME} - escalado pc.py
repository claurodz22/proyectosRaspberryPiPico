'''
ejecutar en la PC
'''

from PIL import Image, ImageOps, ImageEnhance  
import os  

# -- convertir_a_bmp: funcion que convierte la imagen a BMP -- #
def convertir_a_bmp(imagen_entrada, imagen_salida):
    
    # abre la imagen y la instancia
    img = Image.open(imagen_entrada)  
    
    # toma ancho y alto de la foto
    ancho, alto = img.size
    
    print(f"Tamaño original de la imagen: {ancho}x{alto}") 
    
    # pedir datos para hacer zoom
    print("Por favor, ingresa las coordenadas para la region que deseas ampliar.")
    print(f"Las dimensiones de la imagen son {ancho}x{alto}.") 
    
    '''OJO POR ACA'''
    zoom_x = int(input("Coordenada X inicial (0 a {0}): ".format(ancho - 1))) # coordenada X inicial --> va desde 0 hasta el ancho-1 
    zoom_y = int(input("Coordenada Y inicial (0 a {0}): ".format(alto - 1)))  # coordenada Y inicial --> va desde 0 hasta el alto-1
    
    zoom_w = int(input("Ancho de la region (1 a {0}): ".format(ancho - zoom_x))) # ancho p/ampliar --> va desde 1-ancho_restante
    zoom_h = int(input("Alto de la region (1 a {0}): ".format(alto - zoom_y)))   # alto p/ampliar  --> va desde 1-alto_restante
    
    region = img.crop((zoom_x, zoom_y, zoom_x + zoom_w, zoom_y + zoom_h)) # corta la region con los parametros anteriores
    
    # aumentar contraste para mayor nitidez, osea, que haya mas pixeles negros
    region = ImageEnhance.Contrast(region).enhance(2.0)  
    
    # redimensiona
    ratio = min(128 / zoom_w, 64 / zoom_h)  
    nuevo_ancho = int(zoom_w * ratio)  
    nuevo_alto = int(zoom_h * ratio)  
    
    region = region.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)  
    
    # esta es la imagen que se va a guardar, y lo que queda vacio se rellena con 1 --> blanco
    lienzo = Image.new("1", (128, 64), 1)  
    
    # calcular la posicion para centrar la imagen redimensionada (opcional, pero se ve mejor centrada)
    pos_x = (128 - nuevo_ancho) // 2
    pos_y = (64 - nuevo_alto) // 2
    
    # pega la imagen redimensionada en el lienzo en blanco, centrada
    lienzo.paste(region.convert("1"), (pos_x, pos_y))
    
    # guarda la imagen final en el formato deseado
    lienzo.save(imagen_salida)
    print(f"Imagen {imagen_entrada} convertida, redimensionada y guardada como {imagen_salida}") 

# -- procesar_imagen: verifica la extension de la foto (png/jpeg/jpg) -- #
def procesar_imagen(imagen_entrada):  
    extension = os.path.splitext(imagen_entrada)[1].lower()  
    if extension in [".png", ".jpg", ".jpeg"]:
        imagen_salida = "imagen_convertida.bmp" 
        convertir_a_bmp(imagen_entrada, imagen_salida)  
    else:
        print("El formato de la imagen no es compatible. Usa PNG o JPEG/JPG.")  

procesar_imagen("2.JPG")  
