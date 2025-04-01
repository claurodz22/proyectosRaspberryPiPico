from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from time import sleep

def uart_pin():
    uart = machine.UART(0, baudrate=9600, tx=machine.Pin(12), rx=machine.Pin(13))
    return uart

def crear_oled():
    i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000) ## <-- pendiente
    oled = SSD1306_I2C(128,64,i2c)
    return oled

def enviar_archivo(uart, oled):
    file_path = "enviar_uart.csv"
    file = open(file_path, "r") # data.csv archivo
    file_content = file.read()  # almacena
    file.close()				# cierro
    for line in file_content.split("\n"):
        uart.write(line + "\n")
        if line != "*":
            print("Mensaje enviado: ", line)
            mostrar_oled(oled, line)
        sleep(2.5)
    print("listo")
    
def mostrar_oled(oled, message):
    asterisco = False
    #print(message)
    if message == "*":
        asterisco = True
        oled.fill(0)
        oled.show()
        cadena = "FIN DEL MENSAJE"
        mostrar_oled(oled, cadena)
    
    while not asterisco:
        oled.fill(0)
        
        ancho_caracter = 7  # <-- tamaño en pixeles de un caracter
        max_columna = 120   # <-- long max de la pantalla
        fila = 0            # <-- primera linea 

        columna = 0			# <-- primera columna

        # metodo split para convertir un string
        # en una lista
        palabras = message.split()
        
        for palabra in palabras:
            ancho_palabra = len(palabra) * ancho_caracter
            '''
            este if es para verificar si en la columna que esta mas
            el ancho de la palabra no pasa los 120 pixeles
            '''
            if columna + ancho_palabra > max_columna:
                '''
                si se excede, entonces se salta de fila, y se
                inicia desde la columna 0
                '''
                fila += 16  
                columna = 0  
            
            '''
            ya esto es por si la cadena a enviar es muuy larga
            entonces en caso de que exceda, borra lo que esta en la panntalla
            y sigue escribiendo
            '''
            if fila >= 50:
                oled.show()  
                sleep(5)     
                oled.fill(0) 
                fila = 0     
                columna = 0  

            oled.text(palabra, columna, fila)
            columna = columna + 7 # --> espacio entre palabras porsia
            
            columna += ancho_palabra + ancho_caracter  
        asterisco = True
        oled.show()
        sleep(5)
    
def main():
    uart = uart_pin()
    cadena = "El siguiente texto fue enviado por el transmisor"
    oled = crear_oled()
    mostrar_oled(oled, cadena)
    enviar_archivo(uart, oled)
    sleep(0.5)
    cadena = "El mensaje fue recibido por el receptor. "
    mostrar_oled(oled, cadena)
    cadena = "FINALIZADO"
    mostrar_oled(oled, cadena)
    
if __name__ == "__main__":
    main()
