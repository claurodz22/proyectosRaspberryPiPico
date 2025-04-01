import time
from sys import stdin
import uselect

from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from time import sleep
import utime

csv_filename = "data.csv"

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

def save_to_csv(data):
    with open(csv_filename, "w") as f:
        f.write(data + "\n")

def main():
    oled = pantalla()
    mostrar_oled(oled, "mensaje recibido")
    listo = False
    while not listo:
        select_result = uselect.select([stdin], [], [], 0)
        buffer = ''
        
        while select_result[0]:
            input_character = stdin.read(1)

            # Verificar si el carácter es un asterisco
            if input_character == '*':
                # Si encontramos un asterisco, guardamos los datos y salimos
                if buffer:  # Solo guardar si hay datos en el buffer
                    save_to_csv(buffer)
                    mostrar_oled(oled, buffer)
                    listo = True
                #buffer = ''  # Limpiar el buffer
                break  # Salimos del bucle al encontrar el asterisco

            # Agregar cualquier carácter al buffer, incluidas las comas
            buffer += input_character
            
            select_result = uselect.select([stdin], [], [], 0)
    
    mostrar_oled(oled, "listo")
    

if __name__ == "__main__":
    main()

