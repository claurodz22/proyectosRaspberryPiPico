import serial
import time

    
def get_data(file_name): # Function to read data from a file    
    with open(file_name, 'r') as file:
        data = file.read()        
    return data

# Configura la conexión serial
port = "COM6"  # Ajusta el puerto según tu configuración
baudrate = 115200
serial_connection = serial.Serial(port, baudrate)

# Cadena que deseas enviar
cadena = get_data("C:/Users/Claudia/Desktop/datos_pico.csv")
print("Mensaje a enviar: ", cadena)

cadena = cadena + " *"

# Enviar la cadena a través de la conexión serial

serial_connection.write(cadena.encode())  # Enviar la cadena sin añadir una coma al final
time.sleep(0.01)

time.sleep(10)
serial_connection.close()
