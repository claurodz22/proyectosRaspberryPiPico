from micropython import const
from machine import Pin, SPI, I2C
from ssd1306 import SSD1306_I2C
from sdcard import SDCard
from uos import VfsFat, mount
from os import listdir
from time import localtime
import uasyncio as asyncio
import aioble
import bluetooth
from time import sleep_ms
import random
import struct
import utime
import time

# ---------- FUNCIONES PANTALLA OLED -------------- #
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
            utime.sleep(5)
            oled.fill(0) 
            fila = 0     
            columna = 0  
        oled.text(palabra, columna, fila)
        columna = columna + 7 # --> espacio entre palabras porsia
        columna += ancho_palabra + ancho_caracter  
    oled.show()
    utime.sleep(5)

# ----------- FUNCIONES PARA ESCANEAR, ESCOGER Y ENVIAR MENSAJE
# DEL DISPOSITIVO CENTRAL ---------------------------------
def leer(tope, oled):
    entrada = 0
    primera_vuelta=True
    cadena =  "Seleccione el dispositivo para enviar el mensaje."
    mostrar_oled(oled, cadena)
    while ((not isinstance(entrada, int)) or (not (entrada > 0 and entrada <= tope))):
        if not primera_vuelta:
            print("Ingrese una opción válida")
        try:
            entrada = int(input())
        except Exception:
            print("Ingrese una opción válida")
        primera_vuelta = False
    return entrada

def _encode_datos(dato):
    return struct.pack("<s", dato)

async def enviar(conexion, oled, mensaje):
    _ENV_SENSE_UUID = bluetooth.UUID(0x181A)
    _ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)

    temp_service = aioble.Service(_ENV_SENSE_UUID)
    temp_characteristic = aioble.Characteristic(
        temp_service, _ENV_SENSE_TEMP_UUID, read=True, notify=True
    )
    aioble.register_services(temp_service)
    global Palabras_a_enviar
    sleep_ms(500)
    palabra = mensaje
    tiempo = time.time_ns()
    i = 0
    while True:
        if time.time_ns() - tiempo >= 500_000_000:
            tiempo = time.time_ns()
            if i == len(palabra):
                temp_characteristic.write(_encode_datos("*"))
                break
            elif palabra[i] == " ":
                temp_characteristic.write(_encode_datos("/"))
            else:
                temp_characteristic.write(_encode_datos(palabra[i]))
            i += 1
    cadena = "Mensaje enviado al receptor"
    mostrar_oled(oled, cadena)
    conexion.disconnected()

async def escaner(oled, mensaje):
    lista = []
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if not result in lista:
                if result.name() is not None:
                    lista.append(result)
    
    print("Dispositivos encontrados:")
    cont = 1
    for result in lista:
        print(str(cont) + "- " + result.name())
        cadena = "Dispositivo encontrado: " + str(cont) + "- " + result.name()
        mostrar_oled(oled, cadena)
        cont += 1
    
    opcion = leer(len(lista),oled)
    conexion = await lista[opcion-1].device.connect()
    asyncio.run(enviar(conexion, oled, mensaje))

# ---------- FUNCIONES PARA RECIBIR EL ACK DEL
# DISPOSITIVO RECEPTOR --------------
def _decode_datos(dato):
    return struct.unpack("<s", dato)[0]

async def peripheral_task(oled):
    NOMBRE_DEL_BLUETOOTH = "PICO_CENTRAL"
    _ENV_SENSE_UUID = bluetooth.UUID(0x181A)
    _ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)

    _ADV_INTERVAL_MS = 250_000
    while True:
        async with await aioble.advertise(
            _ADV_INTERVAL_MS,
            name=NOMBRE_DEL_BLUETOOTH,
            services=[_ENV_SENSE_UUID],
        ) as connection:
            async with connection:
                try:
                    temp_service = await connection.service(_ENV_SENSE_UUID)
                    temp_characteristic = await temp_service.characteristic(_ENV_SENSE_TEMP_UUID)
                except asyncio.TimeoutError:
                    return
                datos = []
                tiempo = time.time_ns()
                palabra = ""
                while True:
                    if time.time_ns() - tiempo >= 500_000_000:
                        tiempo = time.time_ns()
                        dato = str(_decode_datos(await temp_characteristic.read()),"utf-8")
                        print(dato, end="")
                        if dato == "/":
                            palabra += " "
                        elif dato == "*":
                            break
                        else:
                            palabra += dato
                print("\n\n", palabra)
                led_onboard = machine.Pin(15, machine.Pin.OUT)
                led_onboard.value(1)
                cadena = "Mensaje ACK: " + str(palabra)
                mostrar_oled(oled, cadena)
                break
            break
    await connection.disconnected()
    return str(palabra)
                
def main():
    oled = pantalla()
    oled.fill(0)
    cadena = "DISPOSITIVO TRANSMISOR"
    mostrar_oled(oled, cadena)
    mensaje = "LUIS RAFAEL RODRIGUEZ DE SIO"
    cadena = "Mensaje a enviar: " + mensaje
    mostrar_oled(oled, cadena)
    asyncio.run(escaner(oled, mensaje))
    asyncio.run(peripheral_task(oled))
    
if __name__ == "__main__":
    main()