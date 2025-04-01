# COM6 --> CLIENTE
# si le funciona el sensor
import usocket as socket
import network
import time
import re
from ssd1306 import SSD1306_I2C
from machine import Pin, I2C
import utime
from time import sleep

# -- crear objeto para manejar la pantalla oled -- #
def crear_oled():
    i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000) ## <-- pendiente
    oled = SSD1306_I2C(128,64,i2c)
    return oled

# -- funcion para mostrar mensajes en la pantalla OLED -- # 
def mostrar_oled(oled, message, n):
    oled.fill(0)
    ancho_caracter = 7  # <-- tamaño en pixeles de un caracter
    max_columna = 120   # <-- long max de la pantalla
    fila = 0            # <-- primera linea 
    columna = 0			# <-- primera columna
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

# -- funcion para conectar a wifi ---
def conectar_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        time.sleep(1)
    print("Conectado a WiFi")
    return wlan.ifconfig()[0]

# -- leer sensor de temperatura del PICO W -- #
def leer_sensor():
    sensor_temp = machine.ADC(4)
    conversion_factor = 3.3 / (65535)
    reading = sensor_temp.read_u16() * conversion_factor
    temperature = 27 - (reading - 0.706)/0.001721
    print(temperature)
    temperature = round(temperature,2)
    return temperature

# -- funcion para enviar datos al servidor -- #
def enviar_datos_servidor(ip_servidor, puerto=80, temperatura=0):
    try:
        s = socket.socket()
        s.connect((ip_servidor, puerto))
        mensaje = f"TEMPERATURA={temperatura}"
        s.send(f"POST / HTTP/1.1\r\nHost: {ip_servidor}\r\nContent-Type: text/plain\r\nContent-Length: {len(mensaje)}\r\n\r\n{mensaje}")
        s.close()
        print("Datos enviados al servidor")
    except OSError as e:
        print(f"Error al conectar con el servidor: {e}")

# -- main -- #
def cliente():
    '''MODIFICAR DE ACUERDO SI ESTAS
    EN CASA O EN LA CLASE'''
    azul = Pin(14, Pin.OUT)
    azul.value(0)
    oled = crear_oled()
    oled.fill(0)
    oled.show()
    sleep(2)
    mostrar_oled(oled, "CLIENTE: MONITOREO DE TEMPERATURA", 3)
    ssid = 'clau-moto'
    password = 'tata4646'
    mostrar_oled(oled, f"SSID A CONECTAR: {ssid}", 4)
    ip_servidor = '192.168.219.74'
    conectar_wifi(ssid, password)
    azul = Pin(14, Pin.OUT)
    ejecutar = True
    while ejecutar:
        temperatura = leer_sensor()
        azul.value(1)
        cadena = f"Temperatura medida: {temperatura}  grados centigrados"
        print(cadena)
        mostrar_oled(oled, cadena, 1)
        azul.value(0)
        enviar_datos_servidor(ip_servidor, temperatura=temperatura)
        mostrar_oled(oled, "Esperando nueva muestra a tomar (cliente)", 1)
        time.sleep(5)  # espera 5 seg mas antes de tomar nueva muestra

if __name__ == "__main__":
    cliente()