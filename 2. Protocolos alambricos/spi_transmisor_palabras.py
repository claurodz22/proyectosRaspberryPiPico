import array as arr
from spi_master import SPI_Master
from ssd1306 import SSD1306_I2C
from time import sleep
import utime
from machine import Pin, I2C

def crear_oled():
    i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000) ## <-- pendiente
    oled = SSD1306_I2C(128,64,i2c)
    return oled

def mostrar_oled(oled, message):
    oled.fill(0)
    
    ancho_caracter = 7  # <-- tamaño en pixeles de un caracter
    max_columna = 120   # <-- long max de la pantalla
    fila = 0            # <-- primera linea 

    columna = 0			# <-- primera columna
    palabras = message.split()
    
    for palabra in palabras:
        ancho_palabra = len(palabra) * ancho_caracter
        
        if columna + ancho_palabra > max_columna:
          
            fila += 16  
            columna = 0  
        
        if fila >= 50:
            oled.show()  
            sleep(5)     
            oled.fill(0) 
            fila = 0     
            columna = 0  

        oled.text(palabra, columna, fila)
        columna = columna + 7 # --> espacio entre palabras porsia
        
        columna += ancho_palabra + ancho_caracter  

    oled.show()
    sleep(5)

def transmision(oled):
    SPI_WORDS = 4
    SPI_BYTES = SPI_WORDS * 4
    
    mensaje_a_enviar = "el tren corre por las vias del ferrocarril muy rapido el dia de hoy"
    mensaje_a_enviar = mensaje_a_enviar + "*"
    mostrar_oled(oled, mensaje_a_enviar)
    word_buffer = arr.array("I")
    
    mensaje_bytes = mensaje_a_enviar.encode("utf-8")
    print("Mensaje en bytes:", mensaje_bytes)
   
    for i in range(0, len(mensaje_bytes), SPI_BYTES):
        chunk = mensaje_bytes[i:i+SPI_BYTES]
        if len(chunk) < SPI_BYTES:
            chunk += b"x00" * (SPI_BYTES - len(chunk))  
        word_buffer.extend(arr.array("I", [int.from_bytes(chunk[j:j+4], "big") for j in range(0, SPI_BYTES, 4)]))

    master = SPI_Master(mosi_pin=19, miso_pin=16, sck_pin=18, csel_pin=17, spi_words=SPI_WORDS, F_SPI=1_000_000)

    for i in range(0, len(word_buffer), SPI_WORDS):
        block = word_buffer[i:i+SPI_WORDS]
        master.write(block)
        print("Bloque enviado:", block)
        sleep(1)

    print("Transmision completada")
    cadena = "Transmision completada"


def main():
    oled = crear_oled()
    oled.fill(0)
    oled.show()
    cadena = "MENSAJE A ENVIAR POR SPI"
    mostrar_oled(oled, cadena)
    transmision(oled)
    sleep(1.5)
    cadena = "FIN DEL MENSAJE"
    mostrar_oled(oled, cadena)

if __name__ == "__main__":
    main()