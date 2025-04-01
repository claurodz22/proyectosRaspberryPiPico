# DE PICO A COMPUTADORA

import machine
import time
from machine import Pin, UART, I2C
import uos
from ssd1306 import SSD1306_I2C
from time import sleep
import utime

import sdcard
import uos

def microsd():					# <-inicializacion microsd
    cs = machine.Pin(1, machine.Pin.OUT)
    spi = machine.SPI(0, baudrate=1000000, polarity=0, phase=0, bits=8, firstbit=machine.SPI.MSB, sck=machine.Pin(2), mosi=machine.Pin(3), miso=machine.Pin(4))
    sd = sdcard.SDCard(spi, cs)
    vfs = uos.VfsFat(sd)
    uos.mount(vfs, "/sd")
    return sd

def pantalla():
    WIDTH = 128                                              
    HEIGHT = 64                                            
    i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=200000)      
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

def enviar_info_pico(oled, sd):
    cadena = "TRANSMISION DE PICO A PC"
    mostrar_oled(oled, cadena)
    # Configura el UART
    uart = machine.UART(0, baudrate=115200)
    uart.init(115200, bits=8, parity=None, stop=1, tx=Pin(0), rx=Pin(1))
    uos.dupterm(uart)
        
    # Frase a enviar
    frase = get_data("picoapc.csv")
    cadena = "Mensaje a enviar: " + str(frase)
    mostrar_oled(oled, cadena)
    
    frase = frase + "*"

    enviado = False
    while not enviado:
        uart.write(frase)  # Envía la frase a través del UART
        print(frase.strip())  # Imprime la frase en la consola
        enviado = True
        break
    
    cadena = "Mensaje enviado a PC"
    mostrar_oled(oled, cadena)

def get_data(file_name): # Function to read data from a file    
    with open(file_name, 'r') as file:
        data = file.read()        
    return data

def main():
    sd = microsd()
    oled = pantalla()
    enviar_info_pico(oled, sd)
    
if __name__ == "__main__":
    main()