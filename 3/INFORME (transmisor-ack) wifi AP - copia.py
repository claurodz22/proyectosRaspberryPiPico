# primero ejecuta este, cuando salga que se creo el punto de acceso
# ejecuta el codigo del receptor, especificamente, cuando este entre
# mostrando la clave ESPECIFICAMENTE AHI CONECTALO

from time import sleep
import time
import machine
import uos
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import network
import socket

def pantalla():
    WIDTH = 128                                              
    HEIGHT = 64                                            
    i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)      
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
    
def get_data(file_name): # Function to read data from a file    
    with open(file_name, 'r') as file:
        data = file.read()        
    return data

def envio_wifi(oled):
    cadena = "TRANSMISOR - PUNTO DE ACCESO"
    mostrar_oled(oled, cadena)
    sleep(3)
    
    ap = network.WLAN(network.AP_IF) # crear punto acceso
    ap.config(essid='claudia', password='12345678') # credenciales
    ap.active(True) # prender ap
    
    cadena = "PUNTO DE ACCESO CREADO " 
    mostrar_oled(oled, cadena)
    
    cadena = "NOMBRE:CLAUDIA PASS:12345678"
    mostrar_oled(oled, cadena)
    
    status = ap.ifconfig()
    ip = status[0] # Get the IP address
    print('IP: = ' + ip)

    addr = socket.getaddrinfo(ip, 80)[0][-1] 
    s = socket.socket()
    s.bind(addr)
    s.listen(50) #listen(numero) --> nmro cliente a aceptar
    #print("Escuchando en la direccion: ", addr)
    cadena = "Esperando dispositivos a conectarse"
    mostrar_oled(oled, cadena)

    while True:  # escuchar conexiones
        try:
            conn, addr = s.accept()  # aceptar conexion entrante
            print("Cliente conectado desde la direccion: ", addr)
            
            r = conn.recv(1024)  # recibir peticion de 1024
            
            response = get_data('enviar_wifi.csv')
            cadena = "Mensaje a enviar: "
            mostrar_oled(oled, cadena)
            mostrar_oled(oled, response)
            conn.send(response)
            
            cadena = "Mensaje enviado al dispositivo conectado"
            mostrar_oled(oled, cadena)

            # Esperar por el ACK del receptor
            sleep(8)
            ack = conn.recv(1024)  # esperar el ACK
            if ack:
                ack = str(ack)
                print("ACK recibido del receptor")
                cadena = "Mensaje de confirmacion recibido: " + ack
                print("Mensaje de confirmacion recibido: " , ack)
                mostrar_oled(oled, cadena)
            
            
            break
            
        except OSError as e:
            if ack:
                ack = str(ack)
                print("ACK recibido del receptor")
                cadena = "Mensaje de confirmacion recibido: " + ack
                print("Mensaje de confirmacion recibido: " , ack)
                mostrar_oled(oled, cadena)
                
        print("Conexion cerrada")
        cadena = "Conexion cerrada"
        mostrar_oled(oled, cadena)
        conn.close()  # <-cerrar conexion
            
def main():
    oled = pantalla()
    envio_wifi(oled)
    
if __name__ == "__main__":
    main()