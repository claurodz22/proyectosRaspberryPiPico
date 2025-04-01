# publicador led blanco
# suscriptor led azul

import network
import time
from machine import Pin, I2C
from umqtt.simple import MQTTClient
from time import sleep
from ssd1306 import SSD1306_I2C

# -- crear objeto para manejar la pantalla oled -- #
def crear_oled():
    i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)
    oled = SSD1306_I2C(128,64,i2c)
    return oled

# -- funcion para mostrar mensajes en la pantalla OLED -- # 
def mostrar_oled(oled, message, n):
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
            sleep(n)     
            oled.fill(0) 
            fila = 0     
            columna = 0  
        oled.text(palabra, columna, fila)
        columna = columna + 7 # --> espacio entre palabras porsia
        columna += ancho_palabra + ancho_caracter  
    oled.show()
    sleep(n)
    
# -- conectar a wifi, modificar dependiendo de la locacion -- #
def conectar_wifi(oled):
    wifi_ssid = "clau-moto"
    wifi_password = "tata4646"
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_ssid, wifi_password)
    while wlan.isconnected() == False:
        cadena = 'Esperando por conexion...'
        print(cadena)
        mostrar_oled(oled, cadena, 1)
        time.sleep(1)
    print(f"Conectado a wifi: {wifi_ssid}")
    cadena = f"Conectado a wifi: {wifi_ssid}"
    mostrar_oled(oled, cadena, 3)
    
def publicador(oled):
    led = Pin(14, Pin.OUT)
    led.value(0)
    
    """ DETALLES PARA AUTENTICACION REVISAR """
    # host
    mqtt_host = "io.adafruit.com"
    
    # mi nombre de usuario
    mqtt_username = "claurodz23"  
    
    # key en adafruit (es en la llave que esta en la página de inicio
    mqtt_password = "aio_AZhi42pzoZw5F1UkQD1SJ4DDJKjW"  
    
    # nombre del feed de mensaje publicador --> suscriptor
    mqtt_publish_topic = "claurodz23/feeds/prueba-pico"  
    
    # nombre del feed para enviar ack de suscriptor --> publicador
    mqtt_ack_topic = "claurodz23/feeds/prueba-pico2"  

    # id unico para hacer la comunicacion
    mqtt_client_id = "claudiaelenarodriguezdesio27943668"

    # inicializacion mqtt
    mqtt_client = MQTTClient(
            client_id=mqtt_client_id,
            server=mqtt_host,
            user=mqtt_username,
            password=mqtt_password)

    mqtt_client.connect()

    # -- funcion de callback para manejar el mensaje ACK -- #
    def ack_callback(topic, message):
        ack_message = message.decode('utf-8')
        sleep(4)
        led.value(1)
        print(f"ACK recibido: {ack_message}")
        mostrar_oled(oled, f"ACK recibido: {ack_message}", 3)
        led.value(0)

    # -- callback para recibir el ACK -- #
    mqtt_client.set_callback(ack_callback)

    # -- publicar frase publicador --> tema / prueba_pico2
    try:
        while True:
            led.value(1) # <-- indicador de poder escribir la frase
            cadena = "Ingrese una frase: "
            print(cadena)
            mostrar_oled(oled, cadena, 2)
            frase = input()
            cadena = f"Frase ingresada: {frase}"
            mostrar_oled(oled, cadena, 2.5)
            cadena = f'Frase publicada: {frase}'
            led.value(0)  # <--- indicador que ya se publico 
            print(cadena)
            mostrar_oled(oled, cadena, 2)
            mqtt_client.publish(mqtt_publish_topic, str(frase))
            mostrar_oled(oled, "Esperando ACK del suscriptor..", 3)
            if frase == "fin":
                cadena = "Cerrando comunicacion MQTT"
                print(cadena)
                mostrar_oled(oled, cadena, 3)
                mqtt_client.disconnect()
                break
            
            # esperando ack del topic prueba pico2
            print(f"Esperando ACK para: {frase}")
            mqtt_client.subscribe(mqtt_ack_topic)  # suscripcion 
            mqtt_client.wait_msg()

            led.value(0)
            time.sleep(3)

    except Exception as e:
        print(f'Error al publicar el mensaje: {e}')
        mostrar_oled(oled, "Error al publicar mensaje", 3)
    
    finally:
        mqtt_client.disconnect()


if __name__ == "__main__":
    oled = crear_oled()
    oled.fill(0)
    led = Pin(14, Pin.OUT)
    led.value(0)
    oled.show()
    cadena = "MQTT PUBLICADOR"
    print(cadena)
    mostrar_oled(oled, cadena, 3)
    conectar_wifi(oled)
    sleep(10)
    publicador(oled)
