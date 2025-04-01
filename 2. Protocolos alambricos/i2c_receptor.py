from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from time import sleep
from i2cSlave import i2c_slave

def i2c_transmision_pin():
    i2c_trans = machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0), freq=1000000)
    return i2c_trans

def i2c_pin_recepcion():
    s_i2c = i2c_slave(0,sda=0,scl=1,slaveAddress=0x41)
    return s_i2c

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
    palabras = message.split() # <-- string a lista
    
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

def recepcion_i2c(s_i2c):
    message = ""
    terminado = False
    while not terminado:
        data = s_i2c.get()
        char = chr(int(hex(data), 16))
        message += char
        if char == "*":
            terminado = True
            #print("Mensaje recibido:", message[:-1]) # Imprime el mensaje completo sin el '*'
            message = message.rstrip(" *")
            break # Sale del bucle
    return message

def envio_i2c(message, i2c_trans):
    device_address = 0x41 # <-- dir esclavo
    message = message + " *" #<-- caracter delimitador
    # <-- por seguridad, envia el mensaje por partes
    message_parts = [message[i:i+10] for i in range(0, len(message), 10)]
    for part in message_parts:
        message_bytes = bytearray(part, "utf-8")
        i2c_trans.writeto(device_address, message_bytes)
        sleep(0.05) #<-- obligatorio delay pq si no no envia bien

def main():
    oled = crear_oled()	# <-- objeto para oled
    oled.fill(0)
    s_i2c = i2c_pin_recepcion()
    mensaje = recepcion_i2c(s_i2c)
    print("MENSAJE I2C A RECIBIR: ")
    print(mensaje)
    print("Recibido")
    
    oled.fill(0)
    oled.show()
    cadena = "MENSAJE I2C A RECIBIR: "
    mostrar_oled(oled, cadena)
    mostrar_oled(oled, mensaje)
    cadena = "MENSAJE RECIBIDO POR I2C"
    mostrar_oled(oled, cadena)
    
    # add añade al inicio de la cadena 
    add = "123-56+"
    mensaje = str(mensaje)
    mensaje = add + mensaje 
    
    cadena = "MENSAJE RECIBIDO POR EL RECEPTOR. GRACIAS "
    mostrar_oled(oled, cadena)  
    
    i2c_respuesta = i2c_transmision_pin()
    
    envio_i2c(mensaje, i2c_respuesta)
    
    cadena = "FINALIZADO"
    
    mostrar_oled(oled, cadena)
            
    
if __name__ == "__main__":
    main()
