import time

class MotorPolimorfico:
    def __init__(self, seed, p, q):
        self.seed = seed
        self.p = p
        self.q = q
        self.tabla_llaves = []
        self.N = 16 

    def fs_scrambled(self, s):
        # Desplazamientos y XOR para mezclar la semilla
        return (s ^ (s << 13) ^ (s >> 7)) & 0xFFFFFFFFFFFFFFFF

    def fg_generacion(self, val):
        # Algoritmo de congruencia lineal para 64 bits
        return (val * self.p + self.q) & 0xFFFFFFFFFFFFFFFF

    def fm_mutacion(self, llave, index):
        # La operación cambia según la posición
        if index % 2 == 0:
            return (llave ^ 0x5555555555555555) & 0xFFFFFFFFFFFFFFFF
        else:
            return (llave << 3 | llave >> 61) & 0xFFFFFFFFFFFFFFFF

    def generar_tabla(self):
        val_actual = self.fs_scrambled(self.seed)
        self.tabla_llaves = []
        for i in range(self.N):
            llave = self.fg_generacion(val_actual)
            self.tabla_llaves.append(llave)
            val_actual = self.fm_mutacion(llave, i)
        return self.tabla_llaves

    def cifrar_payload(self, dato_numerico, psn):
        llave = self.tabla_llaves[psn]
        # Se aplicas XOR entre el dato y la llave (Esto es el OTP)
        return dato_numerico ^ (llave & 0xFFFF) # Usamos 16 bits para el payload

    def descifrar_payload(self, dato_cifrado, psn):
        llave = self.tabla_llaves[psn]
        return dato_cifrado ^ (llave & 0xFFFF)