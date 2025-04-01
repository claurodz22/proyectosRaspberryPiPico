# COM7 --> SERVER_SENSOR
# es porque el cliente si le funciona el sensor

import socket
import network
from machine import Pin, I2C
from time import sleep
import time
from ssd1306 import SSD1306_I2C
import utime
import requests

# -- funcion para crear el objeto OLED -- #
def crear_oled():
    i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000) ## <-- pendiente
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

# -- conectarse al wifi -- #
def conectar_wifi(ssid, password):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(ssid, password)
    while not station.isconnected():
        time.sleep(1)
    print("Conexion a WiFi exitosa")
    print(station.ifconfig())
    print("CONECTARSE EN EL SERVER A LA PRIMERA\nDIRECCION QUE IMPRIME")

# -- obtener fecha/hora actual -- #
def obtener_fecha_hora_actual():
    current_time = time.time()
    local_time = time.localtime(current_time)
    year = local_time[0]
    month = local_time[1]
    day = local_time[2]
    hour = local_time[3]
    minute = local_time[4]
    second = local_time[5]
    fecha = "{:02}/{:02}/{}".format(day, month, year)
    hora = "{:02}:{:02}:{:02}".format(hour, minute, second)
    return fecha, hora

# -- servidor (que es el main) -- #
def servidor():
    blanco = Pin(14, Pin.OUT)
    blanco.value(0)
    oled = crear_oled()
    oled.fill(0)
    oled.show()
    sleep(2)
    mostrar_oled(oled, "SERVIDOR: PROVEEDOR DE PAGINA WEB", 3)
    ultima_temperatura = "vacio"
    ssid = 'clau-moto'
    password = 'tata4646'
    mostrar_oled(oled, f"SSID A CONECTAR: {ssid}", 4)
    conectar_wifi(ssid, password)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    cadena = "Esperando conexiones de posibles clientes.."
    mostrar_oled(oled, cadena, 4)
    print(cadena)
    ejecutar = True
    while ejecutar:
        mostrar_oled(oled, "Esperando informacion del cliente..  (servidor)", 3)
        conn, addr = s.accept()
        print(f"Conexion desde: {addr}")
        print(f"Cliente detectado")
        request = conn.recv(1024).decode('utf-8')
        
        # solicitud POST
        if "POST" in request:
            contenido_inicio = request.find("\r\n\r\n") + 4
            datos = request[contenido_inicio:]
            if "TEMPERATURA=" in datos:
                ultima_temperatura = datos.split("=")[1].strip()
                blanco.value(1)
                cadena = f"Temperatura recibida: {ultima_temperatura} grados centigrados"
                mostrar_oled(oled, cadena, 2)
                blanco.value(0)
                mostrar_oled(oled, "Esperando nueva muestra (servidor)", 1)
                print(cadena)
        
        # obtener datos de la pagina
        api_data = obtener_datos_clima()
        # enviar los dos parametros con la info de la temp y de la api
        respuesta = pagina_web(ultima_temperatura, api_data)
        conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n" + respuesta)
        # finaliza la comunicacion
        conn.close()

# -- funcion para obtener datos del clima de la api -- #
def obtener_datos_clima():
    api_key = '2d5f2c6bf4d14d6c84d123921252201' # esta api-key es de mi perfil creado
    location = 'VENEZUELA' # puse venezuela porque no tomaba anzoategui
    url = f'https://api.weatherapi.com/v1/current.json?q={location}&key={api_key}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            weather = response.json() # obtiene el json de lagpina
            return {
                'weather_description': weather['current']['condition']['text'],
                'temperature_c': weather['current']['temp_c'],
                'humidity': weather['current']['humidity'],
                'precipitation': weather['current']['precip_mm'],
                'wind_speed': weather['current']['wind_kph']
            }
        else:
            return {'error': 'Unable to fetch data from API'}
    except Exception as e:
        return {'error': str(e)}

# -- funcion para crear pagina web -- #
def pagina_web(ultima_temperatura, api_data):
    api_info = """<p>Error obteniendo datos de la API.</p>"""
    if 'error' not in api_data:
        api_info = f"""
        <p>Clima actual en API:</p>
        <ul>
            <li>Descripcion: {api_data['weather_description']}</li>
            <li>Temperatura: {api_data['temperature_c']} °C</li>
            <li>Humedad: {api_data['humidity']}%</li>
            <li>Precipitacion: {api_data['precipitation']} mm</li>
            <li>Velocidad del viento: {api_data['wind_speed']} kph</li>
        </ul>
        """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Servidor y Clima</title>
    </head>
    <body>
        <h1>Datos recibidos</h1>
        <p>Temperatura ultima recibida del cliente: {ultima_temperatura} °C</p>
        {api_info}
    </body>
    </html>
    """
    return html

# -- main -- #
if __name__ == "__main__":
    servidor()