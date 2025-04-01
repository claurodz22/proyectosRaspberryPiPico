import network
import time
from machine import Pin, I2C, ADC
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
        mensaje = "Esperando por conexion..."
        print(mensaje)
        mostrar_oled(oled, mensaje, 1)
        time.sleep(1)
    mensaje = f"Conectado a WiFi: {wifi_ssid}"
    print(mensaje)
    mostrar_oled(oled, mensaje, 3)

# -- Leer el sensor de temperatura -- #
def leer_sensor():
    sensor_temp = ADC(4)
    conversion_factor = 3.3 / 65535
    lectura = sensor_temp.read_u16() * conversion_factor
    temperatura = 27 - (lectura - 0.706) / 0.001721
    temperatura = round(temperatura, 2)
    print(f"Temperatura: {temperatura} grados centigrados")
    return temperatura

# -- Publicar datos a MQTT -- #
def publicador(oled):
    led = Pin(14, Pin.OUT)
    led.value(0)

    # Detalles de autenticación de Adafruit IO
    mqtt_host = "io.adafruit.com"
    mqtt_username = "claurodz23"
    mqtt_password = "aio_AZhi42pzoZw5F1UkQD1SJ4DDJKjW"
    mqtt_publish_topic = "claurodz23/feeds/prueba-pico"
    mqtt_ack_topic = "claurodz23/feeds/prueba-pico2"

    # ID único para el cliente MQTT
    mqtt_client_id = "claudiaelenarodriguezdesio27943668"

    # Inicializa el cliente MQTT y conéctate al servidor MQTT
    mqtt_client = MQTTClient(
        client_id=mqtt_client_id,
        server=mqtt_host,
        user=mqtt_username,
        password=mqtt_password
    )

    mqtt_client.connect()

    # Función de callback para manejar el mensaje ACK
    def ack_callback(topic, message):
        ack_message = message.decode('utf-8')
        led.value(1)
        print(f"ACK recibido: {ack_message}")
        mostrar_oled(oled, f"ACK recibido: {ack_message}", 3)
        led.value(0)
        cadena = "Monitoreando siguiente temperatura..."
        print(cadena)
        mostrar_oled(oled, cadena, 3)

    # Asignar el callback para recibir el ACK
    mqtt_client.set_callback(ack_callback)

    try:
        while True:
            # Leer la temperatura del sensor
            temperatura = leer_sensor()
            mensaje = f"Temperatura monitoreada: {temperatura} grados centigrados"
            print(mensaje)
            led.value(1)
            mostrar_oled(oled, mensaje, 2.5)
            led.value(0)
            mostrar_oled(oled, "Esperando ACK", 2.5)

            # Publicar la temperatura al tema MQTT
            mqtt_client.publish(mqtt_publish_topic, str(temperatura))
            print(f"Esperando ACK para: {temperatura} grados centigrados")

            # Suscribirse al tema de ACK y esperar mensaje
            mqtt_client.subscribe(mqtt_ack_topic)
            mqtt_client.wait_msg()  # Esperar mensaje de ACK

            # Control del LED para indicar actividad
            led.value(0)
            time.sleep(5)

    except Exception as e:
        print(f"Error al publicar el mensaje: {e}")
        mostrar_oled(oled, "Error al publicar mensaje", 3)

    finally:
        mqtt_client.disconnect()

if __name__ == "__main__":
    led = Pin(14, Pin.OUT)
    led.value(0)
    oled = crear_oled()
    oled.fill(0)
    oled.show()
    mensaje_inicial = "MQTT PUBLICADOR"
    print(mensaje_inicial)
    mostrar_oled(oled, mensaje_inicial, 3)
    conectar_wifi(oled)
    sleep(5)
    publicador(oled)
