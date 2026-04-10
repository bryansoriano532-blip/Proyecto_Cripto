import socket
import json
from colorama import Fore, Style, init
from cripto_core import MotorPolimorfico


init(autoreset=True)

def iniciar_servidor():
    """
    Implementa el Nodo Receptor (Servidor). Su función es gestionar el ciclo de vida
    de la comunicación, descifrar los payloads recibidos y administrar las tablas
    de llaves polimórficas.
    """
    
    # --- CONFIGURACIÓN DE RED ---
    # HOST '127.0.0.1' permite la comunicación entre procesos en la misma máquina.
    HOST = '127.0.0.1'
    PORT = 65432

    # El objeto 'motor' se inicializa vacío. El servidor es "agnóstico" a la llave hasta que el sensor le entrega los parámetros de sincronización en el FCM.
    motor = None

    # Creación del socket bajo el protocolo TCP para asegurar que ningún paquete se pierda o llegue en orden incorrecto
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Vinculación del socket al puerto y escucha de conexiones entrantes.
        s.bind((HOST, PORT))
        s.listen()
        print(f"{Fore.YELLOW}[SISTEMA] Servidor iniciado en {HOST}:{PORT}. Esperando al sensor...")

        # El servidor se bloquea aquí hasta que un sensor intenta conectar.
        conn, addr = s.accept()
        with conn:
            print(f"{Fore.GREEN}[SISTEMA] Conexión establecida con: {addr}")
            
            while True:
                # Se recibe el flujo de datos.
                data = conn.recv(1024)
                if not data: 
                    break # Si no hay datos, se asume desconexión.
                
                # Deserialización del objeto JSON recibido para procesar los campos.
                msg = json.loads(data.decode())
                m_type = msg['type']
                
                # --- LÓGICA DE PROCESAMIENTO SEGÚN EL TIPO DE MENSAJE ---
                
                if m_type == "FCM":
                    # Fasw de sicronizacion: 
                    # El servidor extrae seed y los primos para replicar el motor criptográfico.
                    print(f"{Fore.GREEN}[FCM] Primer contacto recibido de Nodo {msg['id']}")

                    # Instanciación del motor con los parámetros del sensor.
                    motor = MotorPolimorfico(msg['payload']['seed'], msg['payload']['p'], msg['payload']['q'])
                    # Generación de la tabla espejo de 64 bits.
                    motor.generar_tabla()
                    
                    # Confirmación de recepción (Acknowledge) para avanzar en la comunicación.
                    conn.sendall(b"ACK_FCM")

                elif m_type == "RM":
                    # Fase de Produccion (Regular Message):
                    # Se extrae el PSN (Packet Sequence Number) para saber qué llave usar de la tabla.
                    psn = msg['psn']
                    dato_cifrado = msg['payload']

                    # Descifrado: Aplicamos la función inversa usando el PSN como puntero de memoria.
                    original = motor.descifrar_payload(dato_cifrado, psn)
                    
                    # Log de auditoría que muestra el valor cifrado vs el recuperado.
                    print(f"{Fore.CYAN}[RM] Dato recibido (Cifrado: {hex(dato_cifrado)}) -> "
                          f"{Fore.WHITE}Original: {original}°C (PSN: {psn})")

                elif m_type == "KUM":
                    # Fase de mantenimiento (Key Update Message):
                    # El servidor detecta la solicitud de rotación de llaves del sensor.
                    print(f"{Fore.MAGENTA}[KUM] Umbral alcanzado. Actualizando tabla de llaves...")
                    
                    # Aplicamos la misma mutación de seed que el sensor (+1) para mantener simetría.
                    motor.seed += 1 
                    motor.generar_tabla()
                    print(f"{Fore.MAGENTA}[KUM] Nueva tabla de 64-bits lista para los siguientes mensajes.")

                elif m_type == "LCM":
                    # El Fase de cierre (Last Contact Message):
                    # Se realiza un cierre ordenado de la sesión.
                    print(f"{Fore.RED}[LCM] Conexión cerrada por el sensor. Limpiando variables de sesión...")
                    break

if __name__ == "__main__":
    iniciar_servidor()
