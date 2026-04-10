import socket
import json
import time
import random
from colorama import Fore, init
from cripto_core import MotorPolimorfico
init(autoreset=True)

def iniciar_sensor():
    """
    Simula un dispositivo IoT (Nodo Sensor) que captura datos de temperatura
    y los envía de forma segura al servidor usando cifrado polimórfico.
    """
    
    # --- PARÁMETROS DE CONFIGURACIÓN ---
    # SEED, P y Q son los secretos compartidos iniciales. 
    SEED, P, Q = 54321, 997, 883
    
    # Se genera el motor criptográfico y generamos la primera tabla de 16 llaves.
    motor = MotorPolimorfico(SEED, P, Q)
    motor.generar_tabla()
    
    # Configuración de red: IP local y puerto de escucha del servidor.
    HOST, PORT = '127.0.0.1', 65432

    # Establecemos una conexión TCP con el servidor.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            
            # --------FCM (First Contact Message) ---
            # El sensor envía sus parámetros para que el servidor pueda replicar exactamente la misma tabla de llaves.
            fcm = {
                "id": 1,           # Identificador del dispositivo
                "type": "FCM",     # Tipo de mensaje: Primer contacto
                "payload": {"seed": SEED, "p": P, "q": Q}, 
                "psn": 0           # Packet Sequence Number inicial
            }
            s.sendall(json.dumps(fcm).encode())
            print(f"{Fore.GREEN}[SISTEMA] Conexión establecida. Sincronizando tablas...")
            time.sleep(1) # Pausa  para permitir el procesamiento en el servidor

            # --- RM (Regular Message) ----
            # Simulamos un bucle de captura de datos (10 lecturas de temperatura).
            for i in range(10):
                # El PSN (Puntero) rota del 0 al 15 según el tamaño de la tabla (N=16).
                psn = i % 16
                
                # --- KUM (Key Update Message) ---
                # Si el puntero llega a un límite (ej. mensaje 8),  se solicita actualizar las llaves para evitar que un atacante analice patrones.
                if i == 8:
                    print(f"{Fore.MAGENTA}[KUM] Umbral alcanzado. Solicitando actualización de llaves...")
                    kum = {"id": 1, "type": "KUM", "payload": "Update", "psn": psn}
                    s.sendall(json.dumps(kum).encode())
                    
                    # Se actualiza seed localmente para que la siguiente tabla sea distinta.
                    motor.seed += 1
                    motor.generar_tabla()
                    time.sleep(1)

                # Simulación de telemetría (Captura de temperatura ambiente)
                temp = random.randint(20, 30) 
                
                # El valor numérico se mezcla con la llave polimórfica actual (OTP).
                cifrado = motor.cifrar_payload(temp, psn)
                
                # Construcción del mensaje RM con el payload oculto.
                rm = {"id": 1, "type": "RM", "payload": cifrado, "psn": psn}
                s.sendall(json.dumps(rm).encode())
                
                print(f"{Fore.BLUE}[INFO] Enviando Temp: {temp}°C -> "
                      f"{Fore.YELLOW}Cifrado en Red: {hex(cifrado)} (PSN: {psn})")
                time.sleep(1)

            # --- LCM (Last Contact Message) ---
            # Informa al servidor que la sesión ha terminado para que pueda liberar recursos y borrar las llaves de la memoria RAM
            # cumpliendo con la seguridad post-comunicación.
            lcm = {"id": 1, "type": "LCM", "payload": "Bye", "psn": 0}
            s.sendall(json.dumps(lcm).encode())
            print(f"{Fore.RED}[SISTEMA] Cerrando sesión de forma segura.")

        except ConnectionRefusedError:
            print(f"{Fore.RED}[ERROR] No se pudo conectar. ¿Iniciaste primero el 'nodo_servidor.py'?")

if __name__ == "__main__":
    iniciar_sensor()
