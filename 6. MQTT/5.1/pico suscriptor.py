"""
Pico suscriptor, lee el mensaje que publica el pico publicador
y controla un LED basado en la temperatura recibida.
Si la temperatura es igual o mayor a 25, el LED se enciende.
Si no, el LED permanece apagado.
"""

import time
import network
from machine import Pin, I2C
from umqtt.simple import MQTTClient
from time import sleep
from ssd1306 import SSD1306_I2C

# -- Crear objeto para manejar la pantalla OLED -- #
def crear_oled():
    i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)
    oled = SSD1306_I2C(128, 64, i2c)
    return oled

# -- Función para mostrar mensajes en la pantalla OLED -- #
def mostrar_oled(oled, message, n):
    oled.fill(0)
    ancho_caracter = 7 # <-- tamaño en pixeles de un caracter
    max_columna = 120   # <-- long max de la pantalla
    fila = 0            # <-- primera linea
    columna = 0      # <-- primera columna
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

# -- Conectar a WiFi -- #
def conectar_wifi(oled):
    wifi_ssid = "CARPINCHO_CERVEZERO"
    wifi_password = "cartman123*"
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_ssid, wifi_password)
    while not wlan.isconnected():
        cadena = 'Esperando por conexion...'
        print(cadena)
        mostrar_oled(oled, cadena, 1)
        time.sleep(1)
    cadena = f"Conectado a WiFi: {wifi_ssid}"
    print(cadena)
    mostrar_oled(oled, cadena, 3)

# -- Función principal del suscriptor MQTT -- #
def suscriptor(oled):
    led = Pin(14, Pin.OUT)
    led.value(0)

    # Detalles del servidor MQTT
    mqtt_host = "io.adafruit.com"
    mqtt_username = "claurodz23"  # Nombre de usuario de Adafruit IO
    mqtt_password = "aio_AZhi42pzoZw5F1UkQD1SJ4DDJKjW"  # Clave de Adafruit IO
    mqtt_receive_topic = "claurodz23/feeds/prueba-pico"  # Tema para recibir mensajes
    mqtt_ack_topic = "claurodz23/feeds/prueba-pico2"  # Tema para enviar ACKs

    mqtt_client_id = "claudiaelenarodriguezdesio_subscriber_led_control"

    mqtt_client = MQTTClient(
        client_id=mqtt_client_id,
        server=mqtt_host,
        user=mqtt_username,
        password=mqtt_password
    )

    # Callback para manejar mensajes recibidos
    def mqtt_subscription_callback(topic, message):
        decoded_message = message.decode('utf-8')  # Decodificar mensaje
        cadena = f"Temperatura recibida {decoded_message} grados centigrados"
        print(cadena)
        mostrar_oled(oled, cadena, 2)

        try:
            temperatura = float(decoded_message)
            if temperatura >= 30:
                led.value(1)
                mostrar_oled(oled, "ALERTA: TEMPERATURA ALTA.", 3)
            else:
                led.value(0)
                mostrar_oled(oled, "ESTADO: TEMPERATURA NORMAL.", 3)
        except ValueError:
            mostrar_oled(oled, "Mensaje no valido.", 3)
            print("Mensaje recibido no es una temperatura válida.")
        
        led.value(0)
        ack_message = "TEMPERATURA RECIBIDA"
        try:
            mqtt_client.publish(mqtt_ack_topic, ack_message)
            cadena = "TEMPERATURA RECIBIDA"
            print(f"{cadena}")
            mostrar_oled(oled, f"{cadena}", 3)
            mostrar_oled(oled, "Esperando siguiente muestra...", 3)
        except Exception as e_ack:
            print(f"Error al enviar ACK: {e_ack}")
            mostrar_oled(oled, "Error al enviar ACK.", 3)
    
    mqtt_client.set_callback(mqtt_subscription_callback)

    try:
        mqtt_client.connect()
        mqtt_client.subscribe(mqtt_receive_topic)
        print(f"Conectado al MQTT y suscrito al tema {mqtt_receive_topic}")
        mostrar_oled(oled, "Conectado y suscrito.", 3)

        while True:
            mqtt_client.check_msg()  # Revisar mensajes entrantes
            time.sleep(1)  # Reducir uso de CPU

    except Exception as e:
        print(f"Error en el suscriptor MQTT: {e}")
        mostrar_oled(oled, "Error en suscripción.", 3)
    finally:
        mqtt_client.disconnect()
        print("Desconectado de MQTT")
        mostrar_oled(oled, "Desconectado de MQTT.", 3)


if __name__ == "__main__":
    led = Pin(14, Pin.OUT)
    led.value(0)
    oled = crear_oled()
    oled.fill(0)
    oled.show()

    cadena = "MQTT SUSCRIPTOR"
    print(cadena)
    mostrar_oled(oled, cadena, 3)

    conectar_wifi(oled)
    suscriptor(oled)

    print("Fin del programa suscriptor")
    mostrar_oled(oled, "Fin del programa.", 3)
