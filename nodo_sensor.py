import socket
import json
import time
import random
from colorama import Fore, init
from cripto_core import MotorPolimorfico

init(autoreset=True)

def iniciar_sensor():
    # Parámetros iniciales para el algoritmo [cite: 362]
    SEED, P, Q = 54321, 997, 883
    motor = MotorPolimorfico(SEED, P, Q)
    motor.generar_tabla()
    
    HOST, PORT = '127.0.0.1', 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        
        # 1. ENVIO DEL FCM
        fcm = {"id": 1, "type": "FCM", "payload": {"seed": SEED, "p": P, "q": Q}, "psn": 0}
        s.sendall(json.dumps(fcm).encode())
        time.sleep(1)

        # 2. ENVIAR RM (Simulando 10 lecturas)
        for i in range(10):
            psn = i % 16
            # En caso de llegar al final de la tabla se envia el KUM [cite: 330]
            if i == 8:
                kum = {"id": 1, "type": "KUM", "payload": "Update", "psn": psn}
                s.sendall(json.dumps(kum).encode())
                motor.seed += 1
                motor.generar_tabla()
                time.sleep(1)

            temp = random.randint(20, 30) # Dato original
            cifrado = motor.cifrar_payload(temp, psn)
            
            rm = {"id": 1, "type": "RM", "payload": cifrado, "psn": psn}
            s.sendall(json.dumps(rm).encode())
            print(f"{Fore.BLUE}[INFO] Enviando Temp: {temp}°C (Cifrado: {hex(cifrado)})")
            time.sleep(1)

        # 3. ENVIO DE LCM [cite: 331]
        lcm = {"id": 1, "type": "LCM", "payload": "Bye", "psn": 0}
        s.sendall(json.dumps(lcm).encode())

if __name__ == "__main__":
    iniciar_sensor()