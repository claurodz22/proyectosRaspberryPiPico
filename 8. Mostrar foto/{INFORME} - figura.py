' ejecutar en el pico ' 

import framebuf
import ssd1306
import os
import sdcard
import machine

# config modulo sd
cs = machine.Pin(1, machine.Pin.OUT)
spi = machine.SPI(0, baudrate=1000000, polarity=0, phase=0, bits=8, firstbit=machine.SPI.MSB, sck=machine.Pin(2), mosi=machine.Pin(3), miso=machine.Pin(4))
sd = sdcard.SDCard(spi, cs)
vfs = os.VfsFat(sd)
os.mount(vfs, "/sd")

# instanciar ssd1306
i2c = machine.I2C(0, scl=machine.Pin(17), sda=machine.Pin(16), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# leer la foto desde la sd
def read_bmp(filename):
    # abre el archivo bmp en modo lectura binaria
    with open(filename, "rb") as f:
        bmp = f.read()  # lee todo el contenido del archivo
    
    # obtiene la posicion en la que comienzan los datos de la imagen
    data_offset = int.from_bytes(bmp[10:14], "little")  # posicion donde empiezan los datos
    
    # obtiene el ancho de la imagen a partir del archivo bmp
    width = int.from_bytes(bmp[18:22], "little")        # ancho de la imagen
    
    # obtiene el alto de la imagen a partir del archivo bmp
    height = int.from_bytes(bmp[22:26], "little")       # alto de la imagen
    
    # obtiene los bits por pixel (bpp) a partir del archivo bmp
    bpp = int.from_bytes(bmp[28:30], "little")          # bits por pixel
    
    # inicializa un arreglo para almacenar los datos de la imagen
    img_data = bytearray()
    
    # calcula el tamaño de cada fila en bytes (cada fila es un conjunto de pixeles)
    row_size = (width + 7) // 8  # bytes x fila
    
    for y in range(height):
        # calcula la posicion inicial de la fila (el bmp almacena las filas de abajo hacia arriba)
        row_start = data_offset + (height - 1 - y) * row_size  # bmp almacena de abajo hacia arriba
        
        # extrae la fila de datos y la agrega a img_data
        img_data.extend(bmp[row_start:row_start + row_size])
    return img_data

img_data = read_bmp("/sd/imagen_convertida.bmp")

# crea un frame buffer con los datos de la imagen
fb = framebuf.FrameBuffer(img_data, 128, 64, framebuf.MONO_HLSB)
oled.fill(0) 
oled.blit(fb, 0, 0)  
oled.show() 
print("imagen cargada desde bmp y mostrada en la oled.")