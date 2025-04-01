import array as arr
from spi_slave import SPI_Slave
from ssd1306 import SSD1306_I2C
from time import sleep
import utime
from machine import Pin, I2C

def crear_oled():
    i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000) ## <-- pendiente
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

def spi_pin():
    SPI_WORDS = 4
    slave = SPI_Slave(csel=28, mosi=26, sck=27, miso=22, spi_words=SPI_WORDS, F_PIO=10_000_000)
    return slave

def user_func(slave):
    read = slave.rx_words()
    write = slave.tx_words()
    
    data_bytes = bytearray()
    for word in read:
        data_bytes.extend(word.to_bytes(4, "big"))
    
    data = data_bytes.decode("utf-8")  
    for i, word in enumerate(read):
        write[i] = word
    slave.put_words()
    
    return data

def main():
    oled = crear_oled()
    oled.fill(0)
    oled.show()
    cadena = "MENSAJE A RECIBIR POR SPI"
    mostrar_oled(oled, cadena)
    slave = spi_pin()
    continuar = True
    mensaje_recibido = ""
    while continuar:
        if slave.received():
            mensaje_recibido += user_func(slave)  
            if "*" in mensaje_recibido:  
                continuar = False
    mensaje_recibido = mensaje_recibido.split('*')[0]
    print("Mensaje recibido: ", mensaje_recibido)
    mostrar_oled(oled, mensaje_recibido)
    sleep(1.5)
    cadena = "FIN DEL MENSAJE"
    mostrar_oled(oled, cadena)

if __name__ == "__main__":
    main()