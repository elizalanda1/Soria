import tkinter as tk
import serial
from time import sleep
from tkinter import Scale, Button
class ServoControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Servo")

        # Frame para los botones
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(padx=20, pady=20)

        # Botón para la posición inicial
        self.btn_inicio = tk.Button(self.button_frame, text="Inicio", command=self.ir_a_posicion_inicial)
        self.btn_inicio.grid(row=0, column=0, padx=10, pady=10)

        # Botón para la rutina
        self.btn_rutina = tk.Button(self.button_frame, text="Rutina", command=self.ejecutar_rutina)
        self.btn_rutina.grid(row=1, column=1, padx=10, pady=10)

        # Inicializar la comunicación serial con Arduino
        try:
            self.arduino = serial.Serial('COM3', 9600, timeout=1)  # Cambia 'COM3' por tu puerto serial
            sleep(2)  # Esperar a que se establezca la conexión
        except serial.SerialException:
            print("No se pudo conectar con Arduino. Verifica el puerto serial.")

    def enviar_comando(self, comando):
        try:
            self.arduino.write(comando.encode())  # Enviar el comando como byte
        except serial.SerialException:
            print("Error al enviar comando a Arduino.")

    def ir_a_posicion_inicial(self):
        # Mover el servo a posición inicial (0 grados)
        print("Moviendo a posición inicial (0 grados)")
        self.enviar_comando('0')

# Slider para seleccionar la posición del servo
      
    def enviar_posicion(self):
        # Enviar la posición seleccionada por el slider al servo
        posicion = self.slider.get()
        print(f"Enviando posición {posicion} grados")
        self.enviar_comando(str(posicion))

    def ejecutar_rutina(self):
        # Ejecutar la rutina (0 a 180 grados y de vuelta a 0 grados)
        print("Ejecutando rutina (0 a 180 grados y vuelta)")
        self.enviar_comando('r')
        sleep(1)  # Pausa de 1 segundo
        self.enviar_comando('0')  # Volver a posición inicial (0 grados)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServoControlApp(root)
    root.mainloop()
