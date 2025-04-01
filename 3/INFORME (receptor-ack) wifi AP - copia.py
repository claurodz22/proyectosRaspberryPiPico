# lee encabezado del transmisor

from time import sleep
import time
import machine
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import network
import socket
import utime

def get_data(file_name):   
    with open(file_name, 'r') as file:
        data = file.read()        
    return data

def pantalla():
    WIDTH = 128                                              # oled dimensiones
    HEIGHT = 64                                            
    i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=200000)      # pines gpio 21 y 20
    oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
    return oled

def mostrar_oled(oled, message):
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
            sleep(1)     
            oled.fill(0) 
            fila = 0     
            columna = 0  
        oled.text(palabra, columna, fila)
        columna = columna + 7 # --> espacio entre palabras porsia
        columna += ancho_palabra + ancho_caracter  
    oled.show()
    sleep(5)

def recibo_wifi(oled):
    cadena = "RECEPTOR - DISPOSITIVO A CONECTAR"
    mostrar_oled(oled, cadena)
    sleep(3)
    
    file_path = "recibir_wifi.csv"
    file = open(file_path, "w")
    sta = network.WLAN(network.STA_IF)  # crear conexion a wifi disponible
    sta.active(True)  # activar interfaz wifi
    sta.connect("claudia", "12345678")  # conectarse a punto de acceso
    
    while not sta.isconnected():
        print("No conectado")
        cadena = "INTENTANDO CONEXION"
        mostrar_oled(oled, cadena)
        utime.sleep(1)
    
    cadena = "PUNTO DE ACCESO AL QUE SE CONECTO " 
    mostrar_oled(oled, cadena)
    cadena = "NOMBRE:CLAUDIA PASS:12345678"
    mostrar_oled(oled, cadena)
    
    ip = sta.ifconfig()[0]
    print("Conectado con IP:", ip)
    cadena = "Conectado con IP; " + str(ip)
    mostrar_oled(oled, cadena)

    addr = socket.getaddrinfo('192.168.4.1', 80)[0][-1]
    s = socket.socket()
    s.connect(addr)

    while True:
        try:
            s.send(b"GET / HTTP/1.0\r\n\r\n")  # enviar petición
            response = s.recv(1024)  # leer info / almacenar
            file.write(response)  # escribir en archivo
            print("Mensaje recibido: ", response)
            cadena = "INFORMACION RECIBIDA: "
            mostrar_oled(oled, cadena)
            mostrar_oled(oled, response)
            file.flush()
            
            cadena = "Mensaje recibido del transmisor"
            mostrar_oled(oled, cadena)
            
            # Enviar ACK al transmisor
            ack_message = response + " +x2024"
            s.send(ack_message)  # enviar confirmación
            print("ACK enviado al transmisor")
            
            cadena = "Enviando ACK al transmisor" + str(ack_message)
            mostrar_oled(oled, cadena)
            
            s.close()
            break

        except OSError as e:
            s.close()
            print("Conexion cerrada")
            cadena = "Conexion cerrada"
            mostrar_oled(oled, cadena)
        
def main():
    oled = pantalla()
    recibo_wifi(oled)
    
if __name__ == "__main__":
    main()