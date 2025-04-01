import time
import network
from machine import Pin, I2C
from umqtt.simple import MQTTClient
from time import sleep
from ssd1306 import SSD1306_I2C

# -- crear objeto para manejar la pantalla oled -- #
def crear_oled():
    i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000) ## <-- pendiente
    oled = SSD1306_I2C(128,64,i2c)
    return oled

# -- funcion para mostrar mensajes en la pantalla OLED -- #
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

def suscriptor(oled):
    led = Pin(14, Pin.OUT)
    led.value(0)

    """ DETALLES PARA AUTENTICACION REVISAR """
    # host 
    mqtt_host = "io.adafruit.com"
    
    # mi nombre/usuario en adafruit
    mqtt_username = "claurodz23"
    
    # mi llave de adafruit (que es la llave que esta en la esquina de mi main page)
    mqtt_password = "aio_AZhi42pzoZw5F1UkQD1SJ4DDJKjW"
    
    # topic para que el suscriptor lea los mensajes del publicador
    mqtt_receive_topic = "claurodz23/feeds/prueba-pico"
    
    # topic para que el suscriptor "publique" el ack 
    mqtt_ack_topic = "claurodz23/feeds/prueba-pico2" 

    # recuerda que esta tiene que ser super super super unica
    mqtt_client_id = "claudiaelenarodriguezdesio28686549"
    
    # inicializacion
    mqtt_client = MQTTClient(
            client_id=mqtt_client_id,
            server=mqtt_host,
            user=mqtt_username,
            password=mqtt_password)

    # funcion callback de la suscripcion
    def mqtt_subscription_callback(topic, message):
        led.value(1)
        decoded_message = message.decode('utf-8') 
        cadena = f'Mensaje recibido: {decoded_message}'
        print (cadena) 
        mostrar_oled(oled, cadena, 2)
        led.value(0)
        
        # agregado de por si quieres finalizar la comunicacion de
        # manera adecuada
        if decoded_message == "fin":
            cadena_fin = "Recibido 'fin', desconectando MQTT"
            print(cadena_fin)
            mostrar_oled(oled, cadena_fin, 3)
            mqtt_client.disconnect()
            return # salida del callback

        # envio del ack, osea, mensaje original y le añadi el 123
        ack_message =  decoded_message + " 123"
        
        try:
            mqtt_client.publish(mqtt_ack_topic, ack_message)
            print(f"ACK enviado al topic: {mqtt_ack_topic}")
            print(f"ACK enviado: {ack_message}")
            cadena = "ACK ENVIADO: " + ack_message
            mostrar_oled(oled, cadena, 3)
            cadena = "Esperando siguiente mensaje"
            print(cadena)
            mostrar_oled(oled, cadena, 3)
        except Exception as e_ack:
            print(f"Error al enviar ACK: {e_ack}")

    # antes de conectarse, le tiene que avisar al cliente para usar el callback
    mqtt_client.set_callback(mqtt_subscription_callback)
    try:
        mqtt_client.connect()

        # una vez conectado, se suscribe al tema de prueba pico2
        mqtt_client.subscribe(mqtt_receive_topic)
        cadena = "Conectado y suscrito"
        print(cadena)
        mostrar_oled(oled, cadena, 2)

        # esto para asegurar que el led este apagado
        led.value(0)
        mqtt_client.publish(mqtt_receive_topic, "INICIAR") # limpieza del tema

        while True:
            # revisar si existen mensajes
            mqtt_client.check_msg()
            time.sleep(1) # deja ese tiempo por si acaso

    except Exception as e:
        cadena = f'Falla en el suscriptor MQTT: {e}'
        print(cadena)
        mostrar_oled(oled, cadena, 5)
    finally:
        mqtt_client.disconnect()
        cadena_desconectado = "Desconectado de MQTT"
        print(cadena_desconectado)
        mostrar_oled(oled, cadena_desconectado, 3)


if __name__ == "__main__":
    oled = crear_oled()
    oled.fill(0)
    oled.show()
    led = Pin(14, Pin.OUT)
    led.value(0)
    
    cadena = "MQTT SUSCRIPTOR"
    print(cadena)
    mostrar_oled(oled, cadena, 3)
    
    conectar_wifi(oled)
    suscriptor(oled)
    
    cadena_fin_programa = "Fin del programa suscriptor"
    print(cadena_fin_programa)
    mostrar_oled(oled, cadena_fin_programa, 3)