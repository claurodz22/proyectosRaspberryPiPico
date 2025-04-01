from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import utime
import math
from time import sleep

# --- definicion de parametros para el uso del keypad matricial --- #
TECLA_ARRIBA  = 0
TECLA_ABAJO = 1

teclas = [['1', '2', '3', 'A'], ['4', '5', '6', 'B'], ['7', '8', '9', 'C'], ['*', '0', '#', 'D']]

filas = [2,3,4,5]
columnas = [6,7,8,9]

fila_pines = [Pin(nombre_pin, mode=Pin.OUT) for nombre_pin in filas]
columna_pines = [Pin(nombre_pin, mode=Pin.IN, pull=Pin.PULL_DOWN) for nombre_pin in columnas]

# --- inicializacion del keypad --- # 
def init_keypad():
    for fila in fila_pines:
        fila.low()

# --- funcion para determinar si la tecla esta siendo presionada --- #
# --- esta se invoca en la funcion obtener_valor --- #
def scan_keypad():
    for fila in range(4):
        fila_pines[fila].high()
        for columna in range(4):
            if columna_pines[columna].value() == TECLA_ABAJO:
                utime.sleep(0.3) 
                fila_pines[fila].low()
                return teclas[fila][columna]
        fila_pines[fila].low()
    return None

# --- funcion para determinar ancho y alto ingresado por keypad --- #
# --- se utiliza la tecla asterisco del keypad para finalizar la entrada --- #
def obtener_valor(mensaje, min_val, max_val, oled):
    valor = ""
    print(mensaje)
    while True:
        tecla = scan_keypad()
        if tecla:
            if tecla == '*':
                if valor and min_val <= int(valor) <= max_val:
                    return int(valor)
                else:
                    mensaje = "Valor fuera de rango. Intente nuevamente."
                    print(mensaje)
                    mostrar_oled(oled, mensaje, 3)
                    valor = ""
            elif tecla.isdigit():
                valor += tecla
                cadena = f"Ingresado: {valor}"
                print(cadena)
                mostrar_oled(oled, cadena, 0.5)

# --- creacion de la instancia oled --- #
def crear_oled():
    i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)
    return SSD1306_I2C(128, 64, i2c)

# -- funcion para mostrar mensajes en la pantalla OLED -- #
def mostrar_oled(oled, message, n):
    oled.fill(0)
    ancho_caracter = 7 # <-- tamaño en pixeles de un caracter
    max_columna = 120   # <-- long max de la pantalla
    fila = 0            # <-- primera linea
    columna = 0      # <-- primera columna
    palabras = message.split() # <-- string a lista
    for palabra in palabras:
        ancho_palabra = len(palabra) * ancho_caracter
        if columna + ancho_palabra > max_columna:
            fila += 16
            columna = 0
        if fila >= 50:
            oled.show()
            sleep(n)
            oled.fill(0)
            fila = 0
            columna = 0
        oled.text(palabra, columna, fila)
        columna = columna + 7 # --> espacio entre palabras porsia
        columna += ancho_palabra + ancho_caracter
    oled.show()
    sleep(n)

# --- funcion para dibujar corazon, param: oled, ancho y alto
def dibujar_corazon(oled, tam_ancho, tam_alto):
    centro_x = 64
    centro_y = 37
    oled.fill(0)
    tam_ancho = tam_ancho 
    # dibujar cora punto x punto
    for pos_x in range(128):
        if pos_x < centro_x:
            continue
        if pos_x - centro_x - 1 > tam_ancho:
            continue
        # modifcar el ,1 es que es un parametro 
        pos_y = int(abs((pow((pos_x - centro_x) / tam_ancho, 0.35) + pow(-pow((pos_x - centro_x) / tam_ancho, 2) + 1, 1 / 2)) * -1 * tam_alto + centro_y))
        oled.pixel(pos_x, pos_y, 1)
        oled.pixel(pos_x - (pos_x - centro_x) * 2, pos_y, 1)

        pos_y = int(abs((pow((pos_x - centro_x) / tam_ancho, 0.35) - pow(-pow((pos_x - centro_x) / tam_ancho, 2) + 1, 1 / 2)) * -1 * tam_alto + centro_y))
        oled.pixel(pos_x, pos_y, 1)
        oled.pixel(pos_x - (pos_x - centro_x) * 2, pos_y, 1)
        oled.show()
    
    # plano cartesiano 
    oled.hline(0, 37, 128, 1)
    oled.vline(64, 0, 64, 1)
    oled.show()

'''
30 x 23
20 x 18
27 x 19
'''
if __name__ == "__main__":
    init_keypad()
    led = Pin(14, Pin.OUT)
    led.value(0)
    
    oled = crear_oled()
    oled.fill(0)
    oled.show()
    mostrar_oled(oled, "GRAFICADORA DE CORAZON", 3)
    
    while True:
        # llamar para mostrar pantalla oled la cadena
        led.value(1)
        mostrar_oled(oled, "Ingrese ancho (18-30) y presione * para confirmar:", 2)
        led.value(0)
        # invocar funcion para solicitar parametros, (cadena, valor min, valor max, instancia oled)
        ancho = 30
        alto = 23
        
        #ancho = obtener_valor("Ingrese ancho (18-30) y presione * para confirmar:", 18, 30, oled)
        
        led.value(1)
        # llamar para mostrar pantalla oled la cadena
        mostrar_oled(oled, "Ingrese alto (11-23) y presione * para confirmar:", 2)
        led.value(0)
        
        # invocar funcion para solicitar parametros, (cadena, valor min, valor max, instancia oled)
        #alto = obtener_valor("Ingrese alto (11-23) y presione * para confirmar:", 11, 23, oled)
        
        # dibujar con los datos capturados
        led.value(1)
        dibujar_corazon(oled, ancho, alto)
        
        # tiempo de espera para no borrar tan rapido el cora
        sleep(10)
        led.value(0)
        mostrar_oled(oled, "Reiniciando para graficar con otros datos...", 3)
        
        
'''
prueba 1: 23 x 20

'''