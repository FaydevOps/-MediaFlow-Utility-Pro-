## **🛡️ MediaFlow Utility Pro (Advanced Media Stream Manager)**

## **Una aplicación de escritorio (GUI) desarrollada en Python (CustomTkinter) diseñada para gestionar, personalizar y adquirir flujos de medios utilizando la potencia del motor de código abierto yt-dlp.**

## **Este proyecto es Open Source. El código fuente completo se proporciona en el repositorio. La distribución de binarios compilados es por conveniencia del usuario final y protección de la propiedad intelectual del desarrollador.**

## **🛑 ⚠️ Descargo de Responsabilidad Legal CRUCIAL ⚠️ 🛑**

## **El propósito de MediaFlow Utility Pro es exclusivamente facilitar la gestión y descarga de contenido al que el usuario ya tiene derecho de acceso legal o que se encuentra bajo licencias de dominio público/Creative Commons.**

* ## **Responsabilidad del Usuario: El usuario es enteramente responsable de asegurar que el uso de este software cumpla con todas las leyes locales, las leyes de derechos de autor y los términos de servicio de cualquier plataforma de donde se obtenga el contenido.**

* ## **Uso No Promovido: Los desarrolladores NO avalan ni promueven el uso de esta herramienta para infringir las leyes de propiedad intelectual.**

* ## **Cualquier uso indebido es responsabilidad exclusiva y única del usuario final.**

## **✨ Características Principales**

* ## **GUI Intuitiva: Interfaz gráfica moderna con CustomTkinter.**

* ## **Gestión Avanzada: Utiliza yt-dlp para descargas de alta calidad, formatos personalizados, y gestión de contenido de listas de reproducción.**

* ## **Soporte de Autenticación: Integra browser-cookie3 para cargar las *cookies* de sesión, permitiendo el acceso a contenido de plataformas que requieren una cuenta (solo para usuarios legítimamente suscritos).**

## **🚀 Requisitos y Despliegue**

## **La herramienta requiere obligatoriamente FFmpeg para procesar audio y video.**

## **1\. Instalación de FFmpeg (Obligatorio)**

## **FFmpeg debe estar instalado y disponible en el PATH del sistema.**

| Sistema | Instrucción de Instalación |
| :---- | :---- |
| **Windows** | **1\. Descargue los binarios estáticos desde el sitio web oficial de [FFmpeg](https://ffmpeg.org/download.html). 2\. Descomprima el archivo y mueva la carpeta a una ubicación fácil (ej: C:\\ffmpeg). 3\. Crucial: Añada la carpeta bin (C:\\ffmpeg\\bin) a la variable de entorno PATH de Windows.** |
| **Termux (Android)** | **Instale directamente con el gestor de paquetes: pkg update && pkg install ffmpeg** |
| **Linux (Ej: Ubuntu)** | **Instale con el gestor de paquetes: sudo apt install ffmpeg** |

## **2\. Ejecución de la Aplicación**

## **Opción A: Ejecutable (Recomendado para Windows/Usuarios Finales)**

1. ## **Diríjase a la [Sección de Releases de GitHub](https://www.google.com/search?q=https://github.com/TuUsuario/MediaFlow-Utility/releases).**

2. ## **Descargue el archivo binario más reciente (MultiDownloaderPro.exe).**

3. ## **Asegúrese de que FFmpeg está configurado (Paso 1).**

4. ## **Ejecute haciendo doble clic en MultiDownloaderPro.exe.**

## **Opción B: Código Fuente (Para Termux, Desarrolladores y Linux Desktop)**

1. ## **Clonar e Instalar Dependencias:**    **git clone \[https://github.com/TuUsuario/MediaFlow-Utility.git\](https://github.com/TuUsuario/MediaFlow-Utility.git) cd MediaFlow-Utility \# Instalar librerías de Python (del requirements.txt) pip install \-r requirements.txt**

2. ## **Ejecución:**

   * ## **Windows/Linux Desktop (GUI): python MultiDowloaderv2.0.py**

   * ## **Termux (CLI \- Modo Consola): El script detecta la falta de entorno gráfico y entra automáticamente en modo CLI. python MultiTermux.py**

## **📘 Tutorial de Uso (GUI)**

## **El flujo de trabajo es simple y se maneja enteramente desde la interfaz gráfica:**

1. ## **Ingresar URL: Pegue la URL del video o de la lista de reproducción en el campo principal.**

2. ## **Opciones de Autenticación (Opcional): Si el contenido es privado (ej. videos de un canal al que está suscrito), haga clic en la opción de cookies. La aplicación intentará leer automáticamente las cookies de sesión desde su navegador (Chrome, Firefox, Edge, etc.) usando browser-cookie3.**

3. ## **Seleccionar Formato:**

   * ## **Video: Seleccione la resolución y el contenedor (MP4, MKV, etc.).**

   * ## **Audio: Elija un formato de audio (MP3, WAV, etc.) si solo desea extraer el sonido.**

4. ## **Iniciar: Haga clic en el botón de descarga. La aplicación mostrará el progreso y utilizará FFmpeg en segundo plano para procesar la salida.**

## **💻 Notas para el Desarrollador (Compilación)**

## **Si desea replicar el ejecutable de Windows y mantener el código fuente protegido, siga estos pasos:**

1. ## **Generar Módulo Binario (.pyd):**    **python setup.py build\_ext \--inplace**

2. ## **Empaquetar con PyInstaller:**    **pyinstaller MultiDownloaderPro.spec**

## **🚨 Nota sobre Falsos Positivos de Antivirus**

## **Esta aplicación no contiene malware. Si el antivirus marca el ejecutable, esto es un Falso Positivo debido a que la herramienta lee cookies y maneja procesos de red avanzados (como la descarga de yt-dlp y la lectura de cookies con browser-cookie3).**

* ## **Solución: Reporte el archivo como seguro a su proveedor de antivirus y añada el ejecutable a la lista de excepciones.**