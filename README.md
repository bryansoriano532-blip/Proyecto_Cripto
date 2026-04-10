# 🔒 Proyecto Cripto - 
> **Descripción:** Implementación de un algoritmo de cifrado polimórfico para nodos IoT.

---

## 🚀 Guía de Ejecución

Siga estos pasos para poner en marcha la simulación del sistema criptográfico:

### 1️⃣ Requisitos Previos
Es necesario tener instalado **Python 3.x** y la librería `colorama`. 
Instálela ejecutando el siguiente comando:

```bash
pip install colorama
```

### 2️⃣ Archivos del Proyecto
Verifique que los siguientes archivos estén en la misma carpeta raíz:

cripto_core.py (Motor de cifrado)

nodo_servidor.py (Receptor/Gateway)

nodo_sensor.py (Emisor/IoT)

### 3️⃣ 🛠️ Instrucciones de Uso

Paso A: Iniciar el Servidor
Ejecute en una terminal:

```bash
python nodo_servidor.py
```

Paso B: Iniciar el Sensor
Ejecute en una segunda terminal:

```bash
python nodo_sensor.py
```

### 4️⃣ 📊 Resultados Esperados

Al ejecutar el sistema, observará el flujo de datos:

🔵 Nodo Sensor: Muestra temperatura original y cifrada.

🟣 KUM: Al mensaje #8, la tabla de llaves mutará.

🔴 LCM: Cierre seguro de la conexión.




