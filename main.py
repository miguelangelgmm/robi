import tkinter as tk
from tkinter import ttk
import serial
import time
import threading

# Inherit from tkinter.Tk
class ServoControllerApp(tk.Tk):
    def __init__(self, port):
        super().__init__()  # Call the constructor of the parent class
        self.title("Robi")

        # Serial port configuration
        self.bluetooth = serial.Serial(port, 115200)
        self.last_command_time = time.time()

        self.scale_update_delay = 0.2  # Delay in seconds to update the servo after moving the scale
        self.scale_update_timer = None

        # Method to create the interface elements
        self.create_widgets()

    def create_widgets(self):
        # Speed
        velocidad_label = ttk.Label(self, text="velocidad:")
        velocidad_label.grid(row=0, column=0, padx=10, pady=10)

        velocidad_buttons = []
        for i in range(6):
            if i == 0:
                button_text = "velocidad"
                label = ttk.Label(self, text=button_text)
                label.grid(row=0, column=i, padx=5, pady=5)
            else:
                button_text = "velocidad {}".format(i)
                button = ttk.Button(self, text=button_text, command=lambda i=i: self.set_speed(i))
                button.grid(row=0, column=i, padx=5, pady=5)
                velocidad_buttons.append(button)

        # Servos
        servo_label = ttk.Label(self, text="Servos:")
        servo_label.grid(row=1, column=0, padx=10, pady=10)

        self.servo_scales = []
        self.servo_labels = []

        for i in range(2, 6):
            servo_value = tk.StringVar()
            servo_scale = ttk.Scale(self, from_=0, to=180, command=lambda value, i=i: self.on_scale_change(i, value),
                                    variable=servo_value)
            servo_scale.set(90)  # Initial value
            servo_scale.grid(row=i, column=1, padx=5, pady=5)  # ajustamos el espacio vertical y horizontal de la fila
            self.servo_scales.append(servo_scale)

            servo_label = ttk.Label(self, text="Servo {}: {:.2f}°".format(i, float(servo_value.get())))
            servo_label.grid(row=i, column=2, padx=5)  # ajustamos la fila
            self.servo_labels.append(servo_label)

        # Open and close
        abrir_button = ttk.Button(self, text="Abrir", command=self.open)
        abrir_button.grid(row=6, column=0, padx=5, pady=10)  # Adjust the row

        cerrar_button = ttk.Button(self, text="Cerrar", command=self.close)
        cerrar_button.grid(row=6, column=1, padx=5, pady=10)  # Adjust the row

        finalizar_button = ttk.Button(self, text="Finalizar", command=self.finish)
        finalizar_button.grid(row=6, column=2, padx=5, pady=10)  # Adjust the row

    def send_command(self, command):
        current_time = time.time()
        if current_time - self.last_command_time >= self.scale_update_delay:  # Control the update frequency
            try:
                self.bluetooth.write(command.encode())
                self.bluetooth.readline()  # Wait for confirmation from Arduino
                self.last_command_time = current_time
            except Exception as e:
                print("Error:", str(e))

    def set_speed(self, speed):
        self.send_command("V{}".format(speed))

    def on_scale_change(self, servo_num, value):
        if self.scale_update_timer:
            self.after_cancel(self.scale_update_timer)  # Cancel the existing timer

        # Set a new timer to send the command after a delay
        self.scale_update_timer = self.after(int(self.scale_update_delay * 1000), self.update_servo, servo_num, value)

    def update_servo(self, servo_num, value):
        command = "{}:{}".format(servo_num, int(float(value)))
        self.send_command(command)
        self.update_servo_labels()

    def update_servo_labels(self):
        for i, servo_label in enumerate(self.servo_labels):
            value = float(self.servo_scales[i].get())
            servo_label.configure(text="Servo {}: {:.2f}°".format(i + 2, value))

    def open(self):
        self.send_command("open")

    def close(self):
        self.send_command("close")

    def finish(self):
        self.bluetooth.close()
        self.destroy()

    def close_serial(self):
        self.bluetooth.close()
        self.destroy()

class CommunicationThread(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

if __name__ == "__main__":
    port = "COM8"  # Puerto
    app = ServoControllerApp(port)

    # Creamos y ejecutamos el hilo de la comunicación
    communication_thread = CommunicationThread(app)
    communication_thread.start()

    app.protocol("WM_DELETE_WINDOW", app.close_serial)
    app.mainloop()  # Continuamos corriendo la interfaz

    # denetemos la aplicación cuando cerramos la interfaz
    communication_thread.stop()
    communication_thread.join()
