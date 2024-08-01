import serial
import time

# Configuración de la conexión serial
ser = serial.Serial(
    port='COM11',
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE
)

# Función para calcular CRC16
def calculate_crc16(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if (crc & 1) != 0:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

# Función para enviar comando y recibir respuesta
def send_command(command, motor_id):
    frame_header = 0x3E
    length = len(command)
    message = [frame_header, motor_id, length] + command
    crc = calculate_crc16(bytearray(message))
    message += [crc & 0xFF, (crc >> 8) & 0xFF]
    ser.write(bytearray(message))
    response = ser.read(13)  # Leer 13 bytes de respuesta (ajustar según sea necesario)
    return response

# Función para el comando de control de posición absoluta cerrada (A4)
def absolute_position_control_command(motor_id, angle, max_speed):
    angle_control_value = int(angle * 100)
    max_speed_value = int(5 * 6)  # Convertir RPM a unidad del motor (DPS)
    command = [
        0xA4, 0x00,
        max_speed_value & 0xFF, (max_speed_value >> 8) & 0xFF,
        angle_control_value & 0xFF, (angle_control_value >> 8) & 0xFF,
        (angle_control_value >> 16) & 0xFF, (angle_control_value >> 24) & 0xFF
    ]
    response = send_command(command, motor_id)
    print(f"Respuesta del comando A4: {response}")

# Función para leer la posición actual del motor (usando el comando 0x92)
def read_current_position(motor_id):
    command = [0x92, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    response = send_command(command, motor_id)
    print("Respuesta del motor:", response)  # Imprimir la respuesta completa

    if response[0] == 0x3E and response[1] == motor_id:
        # Imprimir los bytes individuales de la posición
        position_bytes = response[4:8]
        print(f"Bytes de la posición: {position_bytes}")

        # Extraer y combinar los bytes de la posición
        position = int.from_bytes(position_bytes, byteorder='little', signed=True)
        position = position / 100.0  # Convertir a grados
        return position
    else:
        print("Error en la lectura de posición")
        return None

# ID del motor
motor_id = 1

# Enviar comando de posición (por ejemplo, 1 grado)
absolute_position_control_command(motor_id, 1, 5)

# Esperar un momento para que el motor se mueva
time.sleep(2)

# Leer y mostrar la posición actual del motor
current_position = read_current_position(motor_id)
print(f"Posición actual del motor: {current_position}°")

# Cerrar la conexión serial
ser.close()
