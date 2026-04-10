import socket
import json
from colorama import Fore, Style, init
from cripto_core import MotorPolimorfico

init(autoreset=True)

def iniciar_servidor():
    # Configuración de la red local
    HOST = '127.0.0.1'
    PORT = 65432

    # El servidor comienza sin llaves a la espera de el FCM
    motor = None

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"{Fore.YELLOW}[SISTEMA] Servidor iniciado en {HOST}:{PORT}. Esperando al sensor...")

        conn, addr = s.accept()
        with conn:
            while True:
                data = conn.recv(1024)
                if not data: break
                
                msg = json.loads(data.decode())
                m_type = msg['type']
                
                # --- LÓGICA DE TIPOS DE MENSAJE ---
                
                if m_type == "FCM":
                    print(f"{Fore.GREEN}[FCM] Primer contacto recibido de Nodo {msg['id']}")

                    # Se sincronizara con los parámetros recibidos
                    motor = MotorPolimorfico(msg['payload']['seed'], msg['payload']['p'], msg['payload']['q'])
                    motor.generar_tabla()
                    conn.sendall(b"ACK_FCM")

                elif m_type == "RM":
                    psn = msg['psn']
                    dato_cifrado = msg['payload']

                    # Descifrado usando el PSN como puntero 

                    original = motor.descifrar_payload(dato_cifrado, psn)
                    print(f"{Fore.CYAN}[RM] Dato recibido (Cifrado: {hex(dato_cifrado)}) -> "
                          f"{Fore.WHITE}Original: {original}°C (PSN: {psn})")

                elif m_type == "KUM":
                    print(f"{Fore.MAGENTA}[KUM] Actualizando tabla de llaves...")
                    motor.seed += 1 # Mutación para la nueva tabla
                    motor.generar_tabla()
                    print(f"{Fore.MAGENTA}[KUM] Nueva tabla de 64-bits lista.")

                elif m_type == "LCM":
                    print(f"{Fore.RED}[LCM] Conexión cerrada por el sensor. Limpiando memoria...")
                    break

if __name__ == "__main__":
    iniciar_servidor()