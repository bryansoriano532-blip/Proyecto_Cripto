import time

class MotorPolimorfico:
    """
    Clase que implementa el motor criptográfico basado en el paper.
    Se encarga de la generación dinámica de llaves y el cifrado/descifrado polimórfico.
    """
    def __init__(self, seed, p, q):
        # Seed es la clave inicial para la sincronización.
        self.seed = seed 
        # Los parámetros 'p' y 'q' son números primos usados en el algoritmo de congruencia lineal.
        self.p = p
        self.q = q
        # Estructura que almacenará la sesión actual de llaves para evitar que vuelva a recalcular.
        self.tabla_llaves = []
        # 'N' define el tamaño de la ventana de llaves (16 mensajes antes de rotar o actualizar).
        self.N = 16 

    def fs_scrambled(self, s):
        """
        Función Scrambled (fs): Etapa de pre-procesamiento de seed.
        Utiliza operaciones de Bitwise Shift (desplazamiento) y XOR para aumentar la entropía.
        Esto asegura que los seed pequeñas generen puntos de partida de 64 bits complejos.
        """
        # (s << 13) desplaza bits a la izquierda, (s >> 7) a la derecha. 
        # El & 0xFF... asegura que el resultado se mantenga estrictamente en el rango de 64 bits.
        return (s ^ (s << 13) ^ (s >> 7)) & 0xFFFFFFFFFFFFFFFF

    def fg_generacion(self, val):
        """
        Función de Generación (fg): Crea la llave actual basada en congruencia lineal.
        Genera una secuencia hasta cierto punto aleatoria donde cada llave depende matemáticamente de la anterior.
        """
        return (val * self.p + self.q) & 0xFFFFFFFFFFFFFFFF

    def fm_mutacion(self, llave, index):
        """
        Función de Mutación (fm): El núcleo del polimorfismo.
        Hace que la función de transformación cambie según el índice del paquete (PSN).
        Incluso si dos llaves base fueran similares, la mutación las obliga a ser distintas.
        """
        if index % 2 == 0:
            # Si el índice es par, aplica una máscara fija mediante XOR
            return (llave ^ 0x5555555555555555) & 0xFFFFFFFFFFFFFFFF
        else:
            # Si es impar, aplica una rotación circular de bits
            # Esto redistribuye los bits de la llave de forma no lineal.
            return (llave << 3 | llave >> 61) & 0xFFFFFFFFFFFFFFFF

    def generar_tabla(self):
        """
        Construye la tabla de N llaves (OTP) que se usarán en la sesión de comunicación.
        Este proceso se repite cada vez que se recibe un mensaje de tipo KUM.
        """
        # Se mezcla seed para obtener el valor inicial de la sesión.
        val_actual = self.fs_scrambled(self.seed)
        self.tabla_llaves = []
        
        for i in range(self.N):
            # Generamos la llave para la posición i.
            llave = self.fg_generacion(val_actual)
            self.tabla_llaves.append(llave)
            # Mutamos el valor para que la llave de la posición i+1 sea totalmente diferente.
            val_actual = self.fm_mutacion(llave, i)
            
        return self.tabla_llaves

    def cifrar_payload(self, dato_numerico, psn):
        """
        Cifrado OTP: Aplica la operación XOR entre el dato (telemetría) y la llave de la tabla.
        El PSN actúa como el puntero (Offset) para seleccionar la llave correcta.
        """
        # Extraemos la llave de 64 bits correspondiente al índice actual del paquete.
        llave = self.tabla_llaves[psn]
        # Aplicamos la máscara 0xFFFF para limitar el payload a 16 bits (típico de sensores IoT).
        return dato_numerico ^ (llave & 0xFFFF)

    def descifrar_payload(self, dato_cifrado, psn):
        """
        Descifrado: Al ser una operación XOR, aplicar la misma llave al dato cifrado
        devuelve el valor original del sensor.
        """
        llave = self.tabla_llaves[psn]
        return dato_cifrado ^ (llave & 0xFFFF)
        return dato_cifrado ^ (llave & 0xFFFF)
