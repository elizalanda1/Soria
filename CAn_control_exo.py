import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import serial
import can

ser = None
can_bus = None
communication_protocol = 'RS485'  # Valor predeterminado

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

# Función para enviar comando y recibir respuesta a través de RS485
def send_command_rs485(command, motor_id):
    frame_header = 0x3E
    length = 8
    message = [frame_header, motor_id, length] + command
    crc = calculate_crc16(bytearray(message))
    message += [crc & 0xFF, (crc >> 8) & 0xFF]
    ser.write(bytearray(message))
    response = ser.read(13)
    return response

# Función para enviar comando y recibir respuesta a través de CAN
def send_command_can(command, motor_id):
    msg = can.Message(arbitration_id=motor_id, data=command, is_extended_id=False)
    can_bus.send(msg)
    response = can_bus.recv(1.0)  # Esperar 1 segundo por la respuesta
    if response:
        return response.data
    return None

# Función para enviar comando y recibir respuesta
def send_command(command, motor_id):
    if communication_protocol == 'RS485':
        return send_command_rs485(command, motor_id)
    elif communication_protocol == 'CAN':
        return send_command_can(command, motor_id)

# Función para el comando de control de posición absoluta cerrada (A4)
def absolute_position_control_command(motor_id, angle, max_speed):
    angle_control_value = int(angle * 100)
    max_speed_value = int(max_speed * 6)
    command = [
        0xA4, 0x00,
        max_speed_value & 0xFF, (max_speed_value >> 8) & 0xFF,
        angle_control_value & 0xFF, (angle_control_value >> 8) & 0xFF,
        (angle_control_value >> 16) & 0xFF, (angle_control_value >> 24) & 0xFF
    ]
    response = send_command(command, motor_id)
    if response and response[0] == 0x3E and response[1] == motor_id:
        print(f"Comando de posición absoluta enviado al motor {motor_id}")
    else:
        print("Error en la respuesta")

# Función para leer la posición actual del motor
def read_current_position(motor_id):
    command = [0x92, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    response = send_command(command, motor_id)
    if response and response[0] == 0x3E and response[1] == motor_id:
        position = response[4] + (response[5] << 8) + (response[6] << 16) + (response[7] << 24)
        position /= 100  # Convertir a grados
        return position
    else:
        print("Error en la lectura de posición")
        return None

# Función para inicializar el motor
def init_motor(motor_id):
    command = [0x88, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    send_command(command, motor_id)

# Función para abrir la conexión serial y enviar el comando de inicialización
def connect_motor():
    global ser, can_bus
    if communication_protocol == 'RS485':
        if ser is None or not ser.is_open:
            port = port_var.get()
            baudrate = int(baudrate_var.get())
            motor_id = int(motor_id_var.get())

            ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )

            init_motor(motor_id)
            connection_status.set("Conectado")
            update_connection_indicator("green")
            connect_button.config(text="Desconectar")
            print("Motor inicializado y conexión establecida")

            if messagebox.askyesno("Posición Inicial", "¿Desea mover el exoesqueleto a la posición inicial?"):
                move_to_initial_position()
            
            current_position = read_current_position(motor_id)
            if current_position is not None:
                position_var.set(f"Posición Actual: {current_position:.2f}°")
        else:
            ser.close()
            connection_status.set("Desconectado")
            update_connection_indicator("red")
            connect_button.config(text="Conectar")
            print("Conexión cerrada")
    elif communication_protocol == 'CAN':
        if can_bus is None:
            can_interface = 'can0'  # Ajustar según el nombre de la interfaz CAN
            can_bus = can.interface.Bus(can_interface, bustype='socketcan')

            motor_id = int(motor_id_var.get())
            init_motor(motor_id)
            connection_status.set("Conectado")
            update_connection_indicator("green")
            connect_button.config(text="Desconectar")
            print("Motor inicializado y conexión establecida")

            if messagebox.askyesno("Posición Inicial", "¿Desea mover el exoesqueleto a la posición inicial?"):
                move_to_initial_position()

            current_position = read_current_position(motor_id)
            if current_position is not None:
                position_var.set(f"Posición Actual: {current_position:.2f}°")
        else:
            can_bus.shutdown()
            can_bus = None
            connection_status.set("Desconectado")
            update_connection_indicator("red")
            connect_button.config(text="Conectar")
            print("Conexión cerrada")

# Función para enviar el comando de posición y velocidad
def send_motor_command():
    motor_id = int(motor_id_var.get())
    angle = float(angle_var.get())
    speed = float(speed_var.get())
    absolute_position_control_command(motor_id, angle, speed)
    
    current_position = read_current_position(motor_id)
    if current_position is not None:
        position_var.set(f"Posición Actual: {current_position:.2f}°")

# Funciones para mover el exoesqueleto a posiciones predefinidas
def move_to_initial_position():
    absolute_position_control_command(int(motor_id_var.get()), 0, 5)
    position_var.set("Posición Actual: 0.00°")

def move_to_extension_position():
    absolute_position_control_command(int(motor_id_var.get()), 180, 5)
    position_var.set("Posición Actual: 180.00°")

def move_to_flexion_position():
    absolute_position_control_command(int(motor_id_var.get()), 90, 5)
    position_var.set("Posición Actual: 90.00°")

# Función para cerrar la aplicación al presionar ESC
def on_esc(event):
    root.destroy()

# Función para actualizar el indicador de conexión
def update_connection_indicator(color):
    connection_canvas.delete("all")
    connection_canvas.create_oval(5, 5, 25, 25, fill=color, outline="")

# Función para actualizar el protocolo de comunicación
def update_communication_protocol(event):
    global communication_protocol
    communication_protocol = protocol_var.get()
    print(f"Protocolo de comunicación seleccionado: {communication_protocol}")

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Control de Exoesqueleto")
root.geometry("1792x1024")

# Asociar la tecla ESC para cerrar la aplicación
root.bind("<Escape>", on_esc)

# Cargar la imagen de fondo
bg_image = Image.open("fondo.png")
bg_photo = ImageTk.PhotoImage(bg_image)

# Canvas para mostrar la imagen de fondo
canvas = tk.Canvas(root, width=1792, height=1024)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_photo, anchor="nw")

# Frame principal posicionado en el área específica
mainframe = ttk.Frame(root, padding="10 10 10 10")
canvas.create_window(497.7 + 948.8/2, 108 + 839.8/2, window=mainframe, width=948.8, height=839.8)

# Configurar el grid para expandirse
for i in range(1, 11):  # Incrementar las filas para acomodar los nuevos botones
    mainframe.rowconfigure(i, weight=1)
for i in range(1, 4):
    mainframe.columnconfigure(i, weight=1)

# Variables de entrada
port_var = tk.StringVar(value="COM11")
baudrate_var = tk.StringVar(value="115200")
motor_id_var = tk.StringVar(value="1")
angle_var = tk.StringVar(value="0.0")
speed_var = tk.StringVar(value="0.0")
connection_status = tk.StringVar(value="Desconectado")
position_var = tk.StringVar(value="Posición Actual: --°")
protocol_var = tk.StringVar(value="RS485")

# Estilo para los widgets
style = ttk.Style()
style.configure("TLabel", font=("Helvetica", 14))
style.configure("TEntry", font=("Helvetica", 14), padding=10)
style.configure("TButton", font=("Helvetica", 12), padding=5)

# Color de fondo del recuadro (ajusta según el color exacto)
background_color = "#2c3e50"

# Distribuir los elementos de manera uniforme
ttk.Label(mainframe, text="Puerto COM:").grid(column=1, row=1, sticky=tk.EW, padx=10, pady=10)
ttk.Entry(mainframe, textvariable=port_var).grid(column=2, row=1, sticky=(tk.EW), padx=10, pady=10)

ttk.Label(mainframe, text="Baudrate:").grid(column=1, row=2, sticky=tk.EW, padx=10, pady=10)
ttk.Entry(mainframe, textvariable=baudrate_var).grid(column=2, row=2, sticky=(tk.EW), padx=10, pady=10)

ttk.Label(mainframe, text="Estado de Conexión:").grid(column=1, row=3, sticky=tk.EW, padx=10, pady=10)

connection_frame = ttk.Frame(mainframe)
connection_frame.grid(column=2, row=3, sticky=tk.W, padx=10, pady=10)

ttk.Label(connection_frame, textvariable=connection_status).pack(side=tk.LEFT)
connection_canvas = tk.Canvas(connection_frame, width=30, height=30, bg=background_color)
connection_canvas.pack(side=tk.LEFT)
update_connection_indicator("red")

connect_button = ttk.Button(mainframe, text="Conectar", command=connect_motor, width=15)
connect_button.grid(column=3, row=3, sticky=tk.EW, padx=10, pady=10)

# Selección del protocolo de comunicación
ttk.Label(mainframe, text="Protocolo de Comunicación:").grid(column=1, row=4, sticky=tk.EW, padx=10, pady=10)
protocol_combobox = ttk.Combobox(mainframe, textvariable=protocol_var, values=["RS485", "CAN"], state="readonly")
protocol_combobox.grid(column=2, row=4, sticky=(tk.EW), padx=10, pady=10)
protocol_combobox.bind("<<ComboboxSelected>>", update_communication_protocol)

ttk.Label(mainframe, text="ID del Motor:").grid(column=1, row=5, sticky=tk.EW, padx=10, pady=10)
ttk.Entry(mainframe, textvariable=motor_id_var).grid(column=2, row=5, sticky=(tk.EW), padx=10, pady=10)

ttk.Label(mainframe, text="Posición Objetivo (grados):").grid(column=1, row=6, sticky=tk.EW, padx=10, pady=10)
ttk.Entry(mainframe, textvariable=angle_var).grid(column=2, row=6, sticky=(tk.EW), padx=10, pady=10)

ttk.Label(mainframe, text="Velocidad Máxima (RPM):").grid(column=1, row=7, sticky=tk.EW, padx=10, pady=10)
ttk.Entry(mainframe, textvariable=speed_var).grid(column=2, row=7, sticky=(tk.EW), padx=10, pady=10)

ttk.Button(mainframe, text="Enviar Comando", command=send_motor_command, width=15).grid(column=3, row=7, sticky=tk.EW, padx=10, pady=10)

# Botones adicionales para control de posición predefinida
ttk.Button(mainframe, text="Posición Inicial", command=move_to_initial_position, width=15).grid(column=1, row=8, sticky=tk.EW, padx=10, pady=10)
ttk.Button(mainframe, text="Extensión", command=move_to_extension_position, width=15).grid(column=2, row=8, sticky=tk.EW, padx=10, pady=10)
ttk.Button(mainframe, text="Flexión", command=move_to_flexion_position, width=15).grid(column=3, row=8, sticky=tk.EW, padx=10, pady=10)

# Indicador de posición actual
ttk.Label(mainframe, textvariable=position_var).grid(column=1, row=9, columnspan=3, sticky=tk.EW, padx=10, pady=10)

root.mainloop()
