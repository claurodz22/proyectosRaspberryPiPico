# DE PICO A COMPUTADORA

import serial

def get_data(file_name): # Function to read data from a file    
    with open(file_name, 'r') as file:
        data = file.read()        
    return data

def recibir_info_pc():
    print("TRANSFERENCIA PICO A PC")
    port = "COM6" 			# configuracion puerto COM
    baudrate = 115200		# velocidad
    serial_connection = serial.Serial(port, baudrate) # crear objeto
    print(f"Configurando parametros..Puerto:{port}   Velocidad: {baudrate}")
    recibido = False		# bandera para detener bucle while
    while not recibido:
        data = serial_connection.read(128)
        if data == b"EOF":
            break
        #print(data)
        recibido = True
    
    # recibir info y dividir la parte que nos importa
    data = data.decode('utf-8')
    pos = data.find('*')
    if pos != -1:
        parte_filtrada = data[:pos]
    else:
        parte_filtrada = data  # Si no hay asterisco, mantener la cadena original
    partes = data.split('*')
    data = partes[0]
    print("Mensaje recibido del pico: ", data)

    with open("C:/Users/Claudia/Desktop/datos_pico.csv", "wb") as destination_file:
        destination_file.write(partes[0].encode())
       
    serial_connection.close()

def main():
    recibir_info_pc()
        
if __name__ == "__main__":
    main()