import tkinter as tk
from tkinter import PhotoImage, Canvas
import serial
from time import sleep

class ServoControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Servo")
        self.root.geometry("1200x800")

        # Load the background image
        self.background_image = PhotoImage(file='0.png')
        self.canvas = Canvas(self.root, width=1200, height=800)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.background_image, anchor="nw")

        # Frame para los botones, colocado en el lado izquierdo y alineado horizontalmente
        self.button_frame = tk.Frame(self.root, bg="lightblue")
        self.button_frame.place(relx=0.1, rely=0.7, anchor="w")  # Alineado al lado izquierdo

        # Botón para la posición inicial, sin color de fondo
        self.btn_inicio = tk.Button(self.button_frame, text="90 grados", command=self.ir_a_posicion_inicial, width=10, height=5, relief='flat')
        self.btn_inicio.grid(row=0, column=0, padx=40, pady=10)

        # Botón grande para la rutina, sin color de fondo y ubicado en una posición específica
        self.btn_rutina = tk.Button(self.button_frame, text="Rutina", command=self.ejecutar_rutina, width=10, height=5, relief='flat')
        self.btn_rutina.grid(row=1, column=2, padx=10, pady=10)

        # Botón para enviar nueve veces '1' para el ángulo de 90 grados
        self.btn_90_grados = tk.Button(self.button_frame, text="0 Grados", command=lambda: self.enviar_repeticiones('9', 1), width=10, height=5, relief='flat')
        self.btn_90_grados.grid(row=0, column=2, padx=10, pady=10)

        # Botón para enviar trece veces '1' para el ángulo de 130 grados
        self.btn_130_grados = tk.Button(self.button_frame, text="90 Grados", command=lambda: self.enviar_repeticiones('9', 1), width=10, height=5, relief='flat')
        self.btn_130_grados.grid(row=0, column=3, padx=10, pady=10)

        # Botón para enviar trece veces '1' para el ángulo de 130 grados
        self.btn_30_grados = tk.Button(self.button_frame, text="60 Grados", command=lambda: self.enviar_repeticiones('0', 3), width=10, height=5, relief='flat')
        self.btn_30_grados.grid(row=1, column=3, padx=10, pady=10)

        # Inicializar la comunicación serial con Arduino
        try:
            self.arduino = serial.Serial('COM4', 38400, timeout=1)
            sleep(2)  # Esperar a que se establezca la conexión
        except serial.SerialException:
            print("No se pudo conectar con Arduino. Verifica el puerto serial.")

    def enviar_comando(self, comando):
        try:
            self.arduino.write(comando.encode())
        except serial.SerialException:
            print("Error al enviar comando a Arduino.")

    def enviar_repeticiones(self, comando, repeticiones):
        try:
            for _ in range(repeticiones):
                self.arduino.write(comando.encode())
                sleep(0.1)  # Pequeña pausa para no saturar el buffer del Arduino
        except serial.SerialException:
            print("Error al enviar comando repetido a Arduino.")

    def ir_a_posicion_inicial(self):
        print("Moviendo a posición inicial (90 grados)")
        self.enviar_comando('0')

    def ejecutar_rutina(self):
        print("Ejecutando rutina (0 a 180 grados y vuelta)")
        self.enviar_comando('r')
        sleep(1)
        self.enviar_comando('0')

if __name__ == "__main__":
    root = tk.Tk()
    app = ServoControlApp(root)
    root.mainloop()
