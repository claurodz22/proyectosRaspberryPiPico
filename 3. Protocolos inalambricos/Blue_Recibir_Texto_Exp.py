import sys
import machine
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from time import localtime
import uos
from micropython import const
import uasyncio as asyncio
import aioble
import bluetooth
from time import sleep_ms
import time
import random
import struct
import utime

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

# ---------- FUNCIONES RECIBIR DEL DISPOSITIVO CENTRAL -------------- #
def _decode_datos(dato):
    return struct.unpack("<s", dato)[0]

def avisar():
    led_onboard = machine.Pin(15, machine.Pin.OUT)
    while True:
        led_onboard.toggle()
        utime.sleep(0.5)

async def peripheral_task(oled):
    cadena = "Esperando mensaje del PICO CENTRAL"
    mostrar_oled(oled, cadena)
    NOMBRE_DEL_BLUETOOTH = "claudia-receptor-picow"
    _ENV_SENSE_UUID = bluetooth.UUID(0x181A)
    _ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
    _ADV_INTERVAL_MS = 250_000
    while True:
        async with await aioble.advertise(
            _ADV_INTERVAL_MS,
            name=NOMBRE_DEL_BLUETOOTH,
            services=[_ENV_SENSE_UUID],
        ) as connection:
            print("Connection from", connection.device)
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
                cadena = "Mensaje recibido: " + str(palabra) + " FIN DEL MENSAJE"
                mostrar_oled(oled, cadena)
                break
            break
    await connection.disconnected()
    return str(palabra)

# -------------- FUNCIONES PARA ENVIAR AL DISPOSITIVO CENTRAL ACK ----------------

def _encode_datos(dato):
    return struct.pack("<s", dato)

async def enviar(conexion, oled, mensaje):
    _ENV_SENSE_UUID = bluetooth.UUID(0x181A)
    _ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
    temp_service = aioble.Service(_ENV_SENSE_UUID)
    temp_characteristic = aioble.Characteristic(temp_service, _ENV_SENSE_TEMP_UUID, read=True, notify=True)
    aioble.register_services(temp_service)
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
    cadena = "Mensaje enviado al transmisor"
    mostrar_oled(oled, cadena)
    conexion.disconnected()

async def escaner(oled, mensaje):
    lista = []
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if result not in lista:
                if result.name() is not None:
                    lista.append(result)
    cont = 1
    for result in lista:
        cont += 1
    
    pico_central_index = None
    for i, result in enumerate(lista):
        if result.name() == "PICO_CENTRAL":
            pico_central_index = i
            break

    if pico_central_index is not None:
        conexion = await lista[pico_central_index].device.connect()
        await enviar(conexion, oled, mensaje)
    else:
        print("ERROR: PICO_CENTRAL SE DESCONECTO.")

# ------ FUNCION MAIN -------
def main():
    led_onboard = machine.Pin(15, machine.Pin.OUT)
    led_onboard.value(0)
    oled = pantalla()
    oled.fill(0)
    cadena = "DISPOSITIVO RECEPTOR"
    mostrar_oled(oled, cadena)
    mensaje_recibido = asyncio.run(peripheral_task(oled))
    mensaje_recibido = mensaje_recibido + " 123456"
    cadena = "ENVIANDO ACK AL DISPOSITIVO CENTRAL"
    mostrar_oled(oled, cadena)
    asyncio.run(escaner(oled, mensaje_recibido))
    
if __name__ == "__main__":
    main()