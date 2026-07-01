#!/bin/bash

# 1. Actualizar el sistema e instalar dependencias básicas
sudo apt update && sudo apt upgrade -y
sudo apt install ffmpeg python3-venv python3-pip -y

# 2. Crear el entorno virtual (si no existe ya)
if [ ! -d "env_downloader" ]; then
    echo "Creando entorno virtual de Python..."
    python3 -m venv env_downloader
fi

# 3. Activar el entorno virtual
source env_downloader/bin/activate

# 4. Actualizar pip e instalar librerías
python3 -m pip install --upgrade pip
python3 -m pip install -U --pre "yt-dlp[default]"

if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
else
    echo "Aviso: requirements.txt no encontrado."
fi

# 5. Ejecutar la interfaz gráfica correctamente
echo "Abriendo la interfaz gráfica de MultiDownloaderv4.0.py..."
nohup python3 MultiDownloaderv4.0.py > /dev/null 2>&1 &

# Le damos un segundo para que cargue antes de despedirnos
sleep 1 
echo "¡Listo! Ya puedes cerrar esta terminal si lo deseas."
