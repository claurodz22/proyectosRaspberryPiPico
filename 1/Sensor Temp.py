from time import sleep
import time
import machine
import sdcard
import uos
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import utime
import network
import socket

def get_data(file_name): #<-- lee desde archivo    
    with open(file_name, 'r') as file:
        data = file.read()        
    return data

def access_point(oled):
    ap = network.WLAN(network.AP_IF) # <-- CREAR punto de acceso
    #CREAR PUNTO DE ACCESO DEL PICO NO CAMBIAR
    ap.config(essid='clau_pico', password='tata4646') #<-- configuracion
    
    ap.active(True) # <--activacion 

    status = ap.ifconfig()
    ip = status[0] # obtener ip
    print('ip = ' + ip)

    addr = socket.getaddrinfo(ip, 80)[0][-1] # servidor http con socket
    s = socket.socket()
    s.bind(addr)
    s.listen(3) #<-esto es para aceptar un solo cliente
    print("Direccion y puerto", addr)
    
    cadena = "ESPERANDO CONEXION DEL CLIENTE"
    mostrar_oled(oled, cadena)
    response = get_data('/sd/lm35.txt') #<--obt txt
    
    while True: #<-escucha conexion
        try:
            conn, addr = s.accept() 
            print("Cliente conectado desde", addr)
            cadena = "CLIENTE CONECTADO DESDE " + str(addr) #  'addr' a una cadena (por si acaso)
            mostrar_oled(oled, cadena) 
            r = conn.recv(1024) #recibe peticion max 2^10
            cadena = "INFORMACION DEL TXT"
            mostrar_oled(oled, cadena)
            response = get_data('/sd/lm35.txt') #<--obt txt
            print(response)
            
            #mostrar_oled(oled, response) #<--mostrar oled
            
            conn.send(response) #<--envia mensaje del txt
            conn.close() #<--cierra conexion
            cadena = "CONEXION CERRADA. CLIENTE RECIBIO RESPUESTA"
            mostrar_oled(oled, cadena)
            break
            
        except OSError as e:
            conn.close()
            print('Conexion cerrada')
            cadena = "CONEXION CERRADA"
            mostrar_oled(oled, cadena)
            
# datos tomados por el ADC0 = GPIO26
# utilice LM35 
def obtener_temperatura():
    sensor_temp = machine.ADC(4)
    conversion_factor = 3.3 / (65535)
    reading = sensor_temp.read_u16() * conversion_factor
    temperature = 27 - (reading - 0.706)/0.001721
    print(temperature)
    temperature = round(temperature,2)
    return temperature

# func para obtener la fecha y hora
# de cuando se toma la muestra
def obtener_fecha_hora_actual():
    current_time = time.time()
    local_time = time.localtime(current_time)

    year = local_time[0]
    month = local_time[1]
    day = local_time[2]
    hour = local_time[3]
    minute = local_time[4]
    second = local_time[5]

    formatted_date = "{:02}/{:02}/{}".format(day, month, year)
    formatted_time = "{:02}:{:02}:{:02}".format(hour, minute, second)

    return formatted_date, formatted_time

# funcion para inicializar la comunicacion entre
# la pantalla oled y el pico, pines gpio21 y gpio20
def pantalla():
    WIDTH = 128                                              # oled dimensiones
    HEIGHT = 64                                            
    i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=200000)      # pines gpio 21 y 20
    #print("I2C Address      : "+hex(i2c.scan()[0]).upper())  # dir oled
    #print("I2C Configuration: "+str(i2c))                   
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
            sleep(5)     
            oled.fill(0) 
            fila = 0     
            columna = 0  

        oled.text(palabra, columna, fila)
        columna = columna + 7 # --> espacio entre palabras porsia
        
        columna += ancho_palabra + ancho_caracter  

    oled.show()
    sleep(5)

# funcion para inicializar la comunicacion spi
# entre el modulo micro sd y pico
def microsd():					# <-inicializacion microsd
    cs = machine.Pin(1, machine.Pin.OUT)
    spi = machine.SPI(0, baudrate=1000000, polarity=0, phase=0, bits=8, firstbit=machine.SPI.MSB, sck=machine.Pin(2), mosi=machine.Pin(3), miso=machine.Pin(4))
    sd = sdcard.SDCard(spi, cs)
    vfs = uos.VfsFat(sd)
    uos.mount(vfs, "/sd")
    return sd				# ret

# funcion para grafico de barras
# parametros, oled y temperaturas
# leidas desde la sd
def graficar(oled, temperaturas):
    oled.fill(0)
    
    # eje 'X' y 'Y'
    space = 40
    space = int(space)
    
    # plano cartesiano, 1er cuadrante
    oled.vline(20,0,55,1) #vertical
    oled.hline(20,55,128,1) #hirzontal
              
    for i in range(len(temperaturas)):
        temperaturas[i] = float(temperaturas[i])
        oled.hline(abs(20 + 10 * i), 55 - (int(temperaturas[i])) , 10, 1) # columna, fila, distan
     
    columna = 20
    space = 15
    
    for i in range(len(temperaturas)):
        oled.vline(columna, 55 - (int(temperaturas[i])), (int(temperaturas[i])) , 1)
        columna = columna + 10
        oled.vline(columna, 55 - (int(temperaturas[i])), (int(temperaturas[i])) , 1)
    
    oled.show() 
    
    return

def main(oled):
    led_onboard = machine.Pin(22, machine.Pin.OUT) 
    led_onboard.value(0) # si el led quedo prendido, se apaga
    oled = pantalla()
    
    muestreo = [] 
    prom_temp = 0
    contador = 1
    
    with open("/sd/lm35.txt", "w") as file:
        file.write("")
        
    with open("/sd/lm35.txt", "r") as file:
        print("Archivo leyendo...")
        print("vacio")
        print(file.read())
        
    while True:
        if contador <= 10:
            tempC = obtener_temperatura()
            fecha, hora = obtener_fecha_hora_actual()
            
            print("Temperatura: ",tempC, "C"," ", fecha, hora)
            
            muestreo.append(float(round(tempC,2)))
            prom_temp = prom_temp + tempC
            
            oled.fill(0)
            oled.text(str(contador) + " Temperatura", 0, 0)
            oled.text(str(tempC), 0, 16)
            oled.text(str(fecha),0,32)
            oled.text(str(hora),0,48)
            oled.show()
            
            time.sleep(1)
            
            with open("/sd/lm35.txt", "a") as file:
                file.write(f'{contador}: {tempC} {fecha} {hora}\n')
                
            time.sleep(1)  # Espera 1 segundo
            contador += 1
        
        else:
            with open("/sd/lm35.txt", "r") as file:
                '''
                print("\n Imprimiendo archivo")
                oled.fill(0)
                oled.text("Imprimiendo", 0, 0)
                oled.text("archivo", 0, 16)
                data = file.read()
                cadena = data.split("\n")
                fila = 0
                numeros_muestra = []
                temperaturas = []

                for i in range(len(cadena) - 1): 
                    if cadena[i] != '':
                        partes = cadena[i].split(' ')
                        if len(partes) >= 3:  
                            contador_temp = partes[0] + ": " + partes[1]  
                            fecha_hora = ' '.join(partes[2:])  
                            
                            fecha, hora = fecha_hora.split(' ')  
                            
                            numero_muestra, temperatura = contador_temp.split(': ')
                            
                            numeros_muestra.append(numero_muestra)
                            temperaturas.append(temperatura)
                            
                            oled.fill(0)
                            oled.text(f'Muestra: {numero_muestra}', 0, 0)  
                            oled.text(f'Temp: {temperatura} C', 0, 16)     
                            oled.text(fecha, 0, 32)                        
                            oled.text(hora, 0, 48)                         
                            oled.show()
                            sleep(1)  
                        
                oled.fill(0)
                prom_temp = round(((prom_temp) / (contador-1)), 2) 
                oled.text("Impresion", 0, 0)
                oled.text("terminada", 0, 16)
                oled.show()
                sleep(2)
                '''
                oled.fill(0)
                oled.text("Promedio de", 0,0)
                oled.text("muestras", 0, 16)
                oled.text(str(prom_temp) + "C", 0, 32)
                oled.show()
                
                sleep(2)  # Mostrar el mensaje durante 2 segundos
                
                # graficar(oled, temperaturas)
                
                break # Salir del bucle while
    
if __name__ == "__main__":
    sd = microsd()
    oled = pantalla()
    main(oled)
    access_point(oled) 