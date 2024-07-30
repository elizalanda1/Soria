import tkinter as tk
from tkinter import PhotoImage, Canvas
import serial
from time import sleep
import threading

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
        self.button_frame.place(relx=0.05, rely=0.75, anchor="w")  # Alineado al lado izquierdo

        # Frame para los nuevos botones, colocado a la derecha del primer frame
        self.new_button_frame = tk.Frame(self.root, bg="lightgreen")
        self.new_button_frame.place(relx=0.27, rely=0.75, anchor="w")  # Alineado al lado derecho

        # Botón para la posición inicial, sin color de fondo
        self.btn_inicio = tk.Button(self.button_frame, text="inicio(90grd)", command=self.ir_a_posicion_inicial, width=10, height=5, relief='flat')
        self.btn_inicio.grid(row=0, column=0, padx=40, pady=10)

        # Botón para enviar nueve veces '1' para el ángulo de 90 grados
        self.btn_0_grados = tk.Button(self.button_frame, text="0 Grados", command=self.ir_a_posicion_final, width=10, height=5, relief='flat')
        self.btn_0_grados.grid(row=0, column=2, padx=10, pady=10)

        # Botón de incremento
        self.btn_incremento = tk.Button(self.button_frame, text="Incremento ", command=self.incrementar_angulo, width=10, height=5, relief='flat')
        self.btn_incremento.grid(row=2, column=0, padx=10, pady=10)

        # Botón de decremento
        self.btn_decremento = tk.Button(self.button_frame, text="Decremento ", command=self.decrementar_angulo, width=10, height=5, relief='flat')
        self.btn_decremento.grid(row=2, column=2, padx=10, pady=10)

        # Botón para guardar el valor de contador_decremento
        self.btn_guardar_decremento = tk.Button(self.new_button_frame, text="Guardar Decremento", command=self.guardar_decremento, width=15, height=5, relief='flat')
        self.btn_guardar_decremento.grid(row=0, column=0, padx=10, pady=10)

        # Botón para iniciar la rutina
        self.btn_iniciar_rutina = tk.Button(self.new_button_frame, text="Iniciar Rutina", command=self.iniciar_rutina, width=15, height=5, relief='flat')
        self.btn_iniciar_rutina.grid(row=1, column=0, padx=10, pady=10)

        # Botón para detener la rutina
        self.btn_detener_rutina = tk.Button(self.new_button_frame, text="Detener Rutina", command=self.detener_rutina, width=15, height=5, relief='flat')
        self.btn_detener_rutina.grid(row=2, column=0, padx=10, pady=10)

        # Etiqueta para mensajes de estado
        self.label_estado = tk.Label(self.button_frame, text="", bg="lightblue", fg="red")
        self.label_estado.grid(row=3, column=0, columnspan=3, pady=10)

        # Inicializar la comunicación serial con Arduino
        try:
            self.arduino = serial.Serial('COM10', 38400, timeout=1)
            sleep(2)  # Esperar a que se establezca la conexión
        except serial.SerialException:
            print("No se pudo conectar con Arduino. Verifica el puerto serial.")

        # Contadores para incrementos y decrementos
        self.contador_incremento = 0
        self.contador_decremento = 0
        self.max_incremento = 9
        self.max_decremento = 9

        # Variable para verificar el último comando
        self.ultimo_comando = ""

        # Variable para almacenar el valor de contador_decremento
        self.valor_guardado_decremento = 0

        # Variable para controlar el bucle de la rutina
        self.ejecutando_rutina = False

    def enviar_comando(self, comando):
        try:
            self.arduino.write(comando.encode())
        except serial.SerialException:
            print("Error al enviar comando a Arduino.")

    def enviar_repeticiones(self, comando, repeticiones):
        try:
            for _ in range(repeticiones):
                self.arduino.write(comando.encode())
                print("Moviendo")
                sleep(1)  # Pequeña pausa para no saturar el buffer del Arduino
        except serial.SerialException:
            print("Error al enviar comando repetido a Arduino.")

    def ir_a_posicion_inicial(self):
        print("Moviendo a posición inicial (90 grados)")
        self.enviar_comando('0')
        self.reset_contadores()
        self.ultimo_comando = '0'
        self.label_estado.config(text="")

    def ir_a_posicion_final(self):
        print("Moviendo a posición final (0 grados)")
        self.enviar_comando('9')
        self.reset_contadores()
        self.ultimo_comando = '9'
        self.label_estado.config(text="")

    def incrementar_angulo(self):
        if self.ultimo_comando == '0':
            self.label_estado.config(text="Límite mecánico alcanzado")
        elif self.contador_incremento < self.max_incremento:
            print("Incrementando ángulo")
            self.enviar_comando('2')
            self.contador_incremento += 1
            if self.contador_decremento > 0:
                self.contador_decremento -= 1
            self.ultimo_comando = '2'
            self.label_estado.config(text="")
        else:
            print("Límite de incrementos alcanzado")

    def decrementar_angulo(self):
        if self.ultimo_comando == '9':
            self.label_estado.config(text="Límite mecánico alcanzado")
        elif self.contador_decremento < self.max_decremento:
            print("Decrementando ángulo")
            self.enviar_comando('1')
            self.contador_decremento += 1
            if self.contador_incremento > 0:
                self.contador_incremento -= 1
            self.ultimo_comando = '1'
            self.label_estado.config(text="")
        else:
            print("Límite de decrementos alcanzado")

    def guardar_decremento(self):
        self.valor_guardado_decremento = self.contador_decremento
        print(f"Valor guardado de contador_decremento: {self.valor_guardado_decremento}")

    def iniciar_rutina(self):
        self.ejecutando_rutina = True
        self.rutina_thread = threading.Thread(target=self.rutina)
        self.rutina_thread.start()

    def detener_rutina(self):
        self.ejecutando_rutina = False
        self.ir_a_posicion_inicial()

    def rutina(self):
        while self.ejecutando_rutina:
            self.enviar_repeticiones('2', self.valor_guardado_decremento)
            self.enviar_repeticiones('1', self.valor_guardado_decremento)

    def reset_contadores(self):
        self.contador_incremento = 0
        self.contador_decremento = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = ServoControlApp(root)
    root.mainloop()
