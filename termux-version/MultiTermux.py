from yt_dlp import YoutubeDL
import os
import threading
import browser_cookie3 # Puede fallar en Termux, pero la lógica de descarga continuará
import subprocess
import sys
import urllib.request
import random
import time
import tempfile
import json
import requests
import shutil 

# --- CONSTANTES DE COLOR PARA LA TERMINAL ---
HEADER_COLOR = '\033[96m'  # Cyan
OPTION_COLOR = '\033[92m'  # Green
RESET_COLOR = '\033[0m'
ERROR_COLOR = '\033[91m'
INFO_COLOR = '\033[94m'
WARNING_COLOR = '\033[93m' # Yellow

# --- FUNCIONES AUXILIARES (del código original) ---

def get_random_user_agent():
    """Retorna un User-Agent aleatorio de la lista"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
        'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.172 Mobile Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.2 Safari/605.1.15',
    ]
    return random.choice(user_agents)

def get_browser_cookies(url):
    """Obtiene cookies de los navegadores instalados (puede fallar en Termux)"""
    try:
        domain = extract_domain(url)
        browsers = [
            (browser_cookie3.chrome, "Chrome"),
            (browser_cookie3.firefox, "Firefox"),
            (browser_cookie3.edge, "Edge"),
            (browser_cookie3.brave, "Brave")
        ]
        
        for browser_func, browser_name in browsers:
            try:
                cookies = browser_func(domain_name=domain)
                print(f"{INFO_COLOR}Usando cookies de {browser_name} para {domain}{RESET_COLOR}")
                return cookies
            except Exception:
                continue
        
        print(f"{WARNING_COLOR}No se pudieron obtener cookies de ningún navegador para {domain}{RESET_COLOR}")
    except Exception as e:
        print(f"{ERROR_COLOR}Advertencia en cookies: {e}{RESET_COLOR}")
    return None

def extract_domain(url):
    """Extrae el dominio principal de una URL"""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    return '.' + domain 

def get_platform_config(url):
    """Obtiene la configuración específica para cada plataforma (simplificado)"""
    domain = extract_domain(url)[1:]
    
    # Simplemente devuelve una configuración estándar para CLI
    return {
        'format_preference': ['best'],
        'cookies_required': True,
        'user_agent_required': True,
        'proxy_support': True,
    }

def load_proxy_list():
    """Carga la lista de proxies desde un archivo"""
    proxy_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxies.json")
    if os.path.exists(proxy_file):
        try:
            with open(proxy_file, 'r') as f:
                proxies = json.load(f)
                return proxies.get('http', []), proxies.get('socks5', [])
        except:
            pass
    return [], []

def save_proxy_list(http_proxies, socks5_proxies):
    """Guarda la lista de proxies en un archivo"""
    proxy_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxies.json")
    proxy_data = {
        'http': http_proxies,
        'socks5': socks5_proxies
    }
    try:
        with open(proxy_file, 'w') as f:
            json.dump(proxy_data, f, indent=2)
        return True
    except:
        return False

def get_proxies_from_api(proxy_type='http', timeout=10000, country='all', ssl='all', anonymity='all'):
    """Obtiene proxies automáticamente de ProxyScrape API"""
    # ... (lógica de API mantenida) ...
    try:
        params = {
            'request': 'display_proxies',
            'proxy_format': 'protocolipport',
            'format': 'text',
            'timeout': timeout,
            'country': country,
            'ssl': ssl,
            'anonymity': anonymity
        }
        url = "https://api.proxyscrape.com/v4/free-proxy-list/get"
        headers = {'User-Agent': get_random_user_agent()}
        
        print(f"{INFO_COLOR}🔍 Obteniendo proxies de la API...{RESET_COLOR}")
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            proxies_text = response.text.strip()
            if proxies_text:
                proxies = [p.strip() for p in proxies_text.split('\n') if p.strip()]
                print(f"{OPTION_COLOR}✅ Obtenidos {len(proxies)} proxies de la API{RESET_COLOR}")
                return proxies
            else:
                print(f"{WARNING_COLOR}API no devolvió proxies.{RESET_COLOR}")
        else:
            print(f"{ERROR_COLOR}❌ Error en la API: {response.status_code}{RESET_COLOR}")
            
    except requests.RequestException as e:
        print(f"{ERROR_COLOR}❌ Error de conexión con la API: {e}{RESET_COLOR}")
    
    return []

def get_random_proxy(proxy_type='http'):
    """Obtiene un proxy aleatorio de la lista o de la API"""
    http_proxies, socks5_proxies = load_proxy_list()
    
    if proxy_type == 'http' and http_proxies:
        return random.choice(http_proxies)
    elif proxy_type == 'socks5' and socks5_proxies:
        return random.choice(socks5_proxies)
    
    print(f"{WARNING_COLOR}📡 No hay proxies locales, obteniendo de la API...{RESET_COLOR}")
    api_proxies = get_proxies_from_api(proxy_type)
    
    if api_proxies:
        if proxy_type == 'http':
            save_proxy_list(api_proxies, socks5_proxies)
        else:
            save_proxy_list(http_proxies, api_proxies)
        return random.choice(api_proxies)
    
    return None

def test_proxy(proxy, proxy_type='http', test_url='http://httpbin.org/ip'):
    """Testea si un proxy funciona"""
    try:
        proxies = {}
        if proxy_type == 'http':
            proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
        elif proxy_type == 'socks5':
            # Nota: Requests necesita la librería 'requests[socks]' para esto, que ya debería estar en Termux.
            proxies = {'http': f'socks5://{proxy}', 'https': f'socks5://{proxy}'}
        
        response = requests.get(test_url, proxies=proxies, timeout=10)
        return response.status_code == 200
    except:
        return False

def save_cookies_to_file(cookies):
    """Guarda cookies en un archivo temporal para yt-dlp"""
    if not cookies:
        return None
        
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8')
    try:
        temp_file.write("# Netscape HTTP Cookie File\n")
        # Usamos el formato Netscape
        for cookie in cookies:
            # Reconstrucción del formato Netscape
            domain = cookie.domain.lstrip('.')
            secure = "TRUE" if cookie.secure else "FALSE"
            expiration = str(int(cookie.expires)) if cookie.expires else "0"
            temp_file.write(f"{domain}\tTRUE\t{cookie.path}\t{secure}\t{expiration}\t{cookie.name}\t{cookie.value}\n")
        temp_file.close()
        return temp_file.name
    except Exception as e:
        print(f"{ERROR_COLOR}Error guardando cookies: {e}{RESET_COLOR}")
        return None

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# --- CLASE PRINCIPAL CLI ---

class DownloaderCLI:
    def __init__(self):
        self.url = ""
        self.video_resolution = "720p" # Default
        self.video_format = "mp4"      # Default
        self.audio_format = "mp3"      # Default
        # Usar un path amigable para Termux/Linux por defecto
        self.output_path = os.path.expanduser("~/storage/downloads" if os.path.exists(os.path.expanduser("~/storage/downloads")) else os.path.expanduser("~")) 
        self.ffmpeg_custom_path = "ffmpeg" # Suponemos que está en el PATH
        self.use_proxy = False
        self.proxy_type = "http"
        self.auto_retry_proxy = True
        self.auto_fetch_proxies = True
        self.is_downloading = False

    def print_header(self):
        print(HEADER_COLOR)
        print("███ ▄█▄  ▀█▀ █ ▄█   ▄█▄  ▀█▀ █ ▄█")
        print(" █  █ █  █ █ █ █ █  █ █  █ █ █ █ █")
        print(" █  █ █  █ █ █ █ █  █ █  █ █ █ █ █")
        print("Multi Downloader CLI v2.0 - Termux Edition")
        print(RESET_COLOR)
        print("------------------------------------------")

    def print_menu(self):
        clear_screen()
        self.print_header()
        
        url_display = self.url if len(self.url) <= 50 else f"{self.url[:47]}..."
        proxy_status = f"{OPTION_COLOR}SI ({self.proxy_type}){RESET_COLOR}" if self.use_proxy else f"{ERROR_COLOR}NO{RESET_COLOR}"
        
        print(f"  {OPTION_COLOR}1.{RESET_COLOR} [🔗] URL del Video: {INFO_COLOR}{url_display}{RESET_COLOR}")
        print(f"  {OPTION_COLOR}2.{RESET_COLOR} [📁] Carpeta Destino: {INFO_COLOR}{self.output_path}{RESET_COLOR}")
        print(f"  {OPTION_COLOR}3.{RESET_COLOR} [🎬] Configurar Formato de Descarga {WARNING_COLOR}(V:{self.video_format}/{self.video_resolution} | A:{self.audio_format}){RESET_COLOR}")
        print(f"  {OPTION_COLOR}4.{RESET_COLOR} [⚙️] Gestión de Proxies (Actual: {proxy_status}){RESET_COLOR}")
        print("------------------------------------------")
        print(f"  {OPTION_COLOR}D.{RESET_COLOR} [⬇️] Iniciar Descarga (Video + Audio)")
        print(f"  {OPTION_COLOR}A.{RESET_COLOR} [🔊] Iniciar Descarga (Solo Audio)")
        print(f"  {OPTION_COLOR}V.{RESET_COLOR} [🎥] Iniciar Descarga (Solo Video)")
        print(f"  {OPTION_COLOR}Q.{RESET_COLOR} [❌] Salir")
        print("------------------------------------------")

    def input_prompt(self, prompt, default=None):
        """Función helper para obtener entrada del usuario con color"""
        default_display = f" [{default}]" if default else ""
        return input(f"{OPTION_COLOR}>>{RESET_COLOR} {prompt}{default_display}: ") or default

    def handle_menu_choice(self, choice):
        if choice == '1':
            self.url = self.input_prompt("Ingresa la nueva URL del video", self.url)
        elif choice == '2':
            new_path = self.input_prompt("Ingresa la nueva ruta de la carpeta de destino", self.output_path)
            if os.path.isdir(new_path):
                self.output_path = new_path
                print(f"{OPTION_COLOR}Carpeta de destino actualizada a: {self.output_path}{RESET_COLOR}")
            else:
                print(f"{ERROR_COLOR}Error: La ruta '{new_path}' no es válida o no existe.{RESET_COLOR}")
                input("Presiona ENTER para continuar...")
        elif choice == '3':
            self.configure_formats()
        elif choice == '4':
            self.manage_proxies_cli()
        elif choice in ('d', 'D'):
            self.start_download(audio_only=False, video_only=False)
        elif choice in ('a', 'A'):
            self.start_download(audio_only=True, video_only=False)
        elif choice in ('v', 'V'):
            self.start_download(audio_only=False, video_only=True)
        elif choice in ('q', 'Q'):
            sys.exit(0)
        else:
            print(f"{ERROR_COLOR}Opción no válida. Intenta de nuevo.{RESET_COLOR}")
            input("Presiona ENTER para continuar...")

    def configure_formats(self):
        clear_screen()
        self.print_header()
        print("--- CONFIGURACIÓN DE FORMATOS ---")
        
        # Resolución
        resolutions = ["2160p", "1440p", "1080p", "720p", "480p", "360p", "mejor"]
        res_map = {str(i+1): res for i, res in enumerate(resolutions)}
        print("Resoluciones de Video Disponibles:")
        for i, res in enumerate(resolutions):
            print(f"  {i+1}. {res}")
        
        res_choice = self.input_prompt(f"Selecciona resolución (actual: {self.video_resolution})", 
                                       str(resolutions.index(self.video_resolution) + 1) if self.video_resolution in resolutions else "7")
        self.video_resolution = res_map.get(res_choice, "720p")
        
        # Formato de Video
        video_formats = ["mp4", "webm", "mkv"]
        vid_map = {str(i+1): fmt for i, fmt in enumerate(video_formats)}
        print("\nFormatos de Video Disponibles:")
        for i, fmt in enumerate(video_formats):
            print(f"  {i+1}. {fmt}")
        
        vid_choice = self.input_prompt(f"Selecciona formato de video (actual: {self.video_format})", 
                                       str(video_formats.index(self.video_format) + 1) if self.video_format in video_formats else "1")
        self.video_format = vid_map.get(vid_choice, "mp4")

        # Formato de Audio
        audio_formats = ["mp3", "wav", "m4a"]
        aud_map = {str(i+1): fmt for i, fmt in enumerate(audio_formats)}
        print("\nFormatos de Audio Disponibles:")
        for i, fmt in enumerate(audio_formats):
            print(f"  {i+1}. {fmt}")

        aud_choice = self.input_prompt(f"Selecciona formato de audio (actual: {self.audio_format})", 
                                       str(audio_formats.index(self.audio_format) + 1) if self.audio_format in audio_formats else "1")
        self.audio_format = aud_map.get(aud_choice, "mp3")
        
        print(f"{OPTION_COLOR}Configuración de formato guardada.{RESET_COLOR}")
        input("Presiona ENTER para volver al menú...")

    def manage_proxies_cli(self):
        clear_screen()
        self.print_header()
        print("--- GESTIÓN DE PROXIES ---")
        
        # Alternar uso de Proxy
        use_proxy_input = self.input_prompt(f"¿Deseas USAR Proxy? ({'S' if self.use_proxy else 'N'})", 
                                             'S' if self.use_proxy else 'N').upper()
        self.use_proxy = use_proxy_input == 'S'
        
        if self.use_proxy:
            proxy_type_input = self.input_prompt(f"Tipo de Proxy (actual: {self.proxy_type}. Elige HTTP o SOCKS5)", 
                                                 self.proxy_type).lower()
            if proxy_type_input in ('http', 'socks5'):
                self.proxy_type = proxy_type_input
            
            print("\n  Opciones de Proxy Guardado:")
            print(f"  {OPTION_COLOR}1.{RESET_COLOR} Obtener y guardar nuevos proxies de API (Guardarán a archivo)")
            print(f"  {OPTION_COLOR}2.{RESET_COLOR} Ver/Editar proxies guardados (Manual)")
            print(f"  {OPTION_COLOR}3.{RESET_COLOR} Testear proxies guardados")
            print(f"  {OPTION_COLOR}B.{RESET_COLOR} Volver")
            
            proxy_choice = self.input_prompt("Elige una opción").upper()
            if proxy_choice == '1':
                self.fetch_proxies_now()
            elif proxy_choice == '2':
                self.edit_proxies_file()
            elif proxy_choice == '3':
                self.test_proxies()

        input("Presiona ENTER para volver al menú...")

    def edit_proxies_file(self):
        """Permite al usuario editar los proxies directamente en la consola"""
        http_proxies, socks5_proxies = load_proxy_list()
        
        print("\n--- EDICIÓN MANUAL DE PROXIES ---")
        print(f"{WARNING_COLOR}Formato: IP:Puerto (uno por línea). Déjalo vacío para no cambiar.{RESET_COLOR}")
        
        print("\n[Proxies HTTP actuales]:")
        current_http = '\n'.join(http_proxies)
        new_http = input(current_http + "\n> Nuevos HTTP (pega aquí o deja vacío): \n")
        
        print("\n[Proxies SOCKS5 actuales]:")
        current_socks = '\n'.join(socks5_proxies)
        new_socks = input(current_socks + "\n> Nuevos SOCKS5 (pega aquí o deja vacío): \n")
        
        # Procesar entrada
        http_list = [p.strip() for p in new_http.split('\n') if p.strip()] if new_http else http_proxies
        socks_list = [p.strip() for p in new_socks.split('\n') if p.strip()] if new_socks else socks5_proxies

        if save_proxy_list(http_list, socks_list):
            print(f"{OPTION_COLOR}✅ Proxies guardados correctamente.{RESET_COLOR}")
        else:
            print(f"{ERROR_COLOR}❌ Error al guardar proxies.{RESET_COLOR}")

    def fetch_proxies_now(self):
        """Obtiene proxies de la API inmediatamente"""
        http_proxies = get_proxies_from_api('http')
        socks5_proxies = get_proxies_from_api('socks5')
        
        if http_proxies or socks5_proxies:
            save_proxy_list(http_proxies, socks5_proxies)
            total = len(http_proxies) + len(socks5_proxies)
            print(f"{OPTION_COLOR}✅ Obtenidos y guardados {total} proxies de la API.{RESET_COLOR}")
        else:
            print(f"{ERROR_COLOR}❌ No se pudieron obtener proxies de la API.{RESET_COLOR}")
    
    def test_proxies(self):
        """Testea los proxies disponibles"""
        print(f"{INFO_COLOR}Testeando proxies. Esto puede tardar...{RESET_COLOR}")
        http_proxies, socks5_proxies = load_proxy_list()
        working_http = []
        working_socks5 = []
        
        # Testear un subconjunto
        proxies_to_test = http_proxies[:10] + socks5_proxies[:10]
        
        for i, proxy in enumerate(proxies_to_test):
            proxy_type = 'http' if proxy in http_proxies else 'socks5'
            print(f"\r{INFO_COLOR}Testando {i+1}/{len(proxies_to_test)}: {proxy}...{RESET_COLOR}", end='', flush=True)
            if test_proxy(proxy, proxy_type):
                if proxy_type == 'http':
                    working_http.append(proxy)
                else:
                    working_socks5.append(proxy)
        
        save_proxy_list(working_http, working_socks5)
        total_working = len(working_http) + len(working_socks5)
        print(f"\n{OPTION_COLOR}✅ Pruebas finalizadas.{RESET_COLOR}")
        print(f"Proxies funcionando y guardados:\n  HTTP: {len(working_http)}\n  SOCKS5: {len(working_socks5)}")


    # --- LÓGICA DE DESCARGA ---
    
    def progress_hook(self, d):
        """Actualiza el progreso de la descarga en la consola CLI."""
        if d['status'] == 'downloading':
            try:
                percent = float(d.get('_percent_str', '0%').replace('%', ''))
                
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                
                # Barra de progreso ASCII
                bar_length = 30
                filled_length = int(bar_length * percent // 100)
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                
                # Imprimir estado en su lugar usando \r (retorno de carro)
                print(f"\r{INFO_COLOR}[{bar}] {percent:6.1f}% | {speed:10} | ETA: {eta:5} {RESET_COLOR}", end='', flush=True)

            except Exception:
                # Fallback print if calculation or carriage return fails
                print(f"\r{INFO_COLOR}Descargando: {d.get('_percent_str', '...')} | Velocidad: {d.get('_speed_str', 'N/A')}{RESET_COLOR}", end='', flush=True)
                
        elif d['status'] == 'finished':
            print(f"\n{OPTION_COLOR}[✅] Descarga completada. Procesando...{RESET_COLOR}", flush=True)

    def start_download(self, audio_only, video_only):
        if not self.url:
            print(f"{ERROR_COLOR}❌ Error: Por favor, ingresa una URL primero (Opción 1).{RESET_COLOR}")
            input("Presiona ENTER para continuar...")
            return

        if self.is_downloading:
            print(f"{WARNING_COLOR}Ya hay una descarga en curso.{RESET_COLOR}")
            input("Presiona ENTER para continuar...")
            return

        self.is_downloading = True
        print(f"{INFO_COLOR}Iniciando descarga en segundo plano...{RESET_COLOR}")
        
        thread = threading.Thread(
            target=self.download_video,
            args=(
                self.url,
                self.output_path,
                self.video_resolution,
                self.video_format,
                self.audio_format,
                True,  # use_browser_cookies
                audio_only,
                video_only
            )
        )
        thread.daemon = True
        thread.start()
        
        # Dejar que el hilo corra y volver al menú. El progress_hook se encargará de la salida.
        
    def download_video(self, url, output_path, video_resolution, video_format, audio_format, use_browser_cookies, audio_only, video_only):
        max_retries = 5
        current_try = 0
        used_proxies = []
        temp_dir = None
        
        while current_try < max_retries:
            try:
                print(f"\n{HEADER_COLOR}=== INTENTO DE DESCARGA #{current_try + 1} ==={RESET_COLOR}")
                
                # 1. Usar un directorio temporal
                temp_dir = tempfile.mkdtemp()
                final_output_path = os.path.abspath(output_path)
                if not os.path.exists(final_output_path):
                    os.makedirs(final_output_path)

                ffmpeg_path = self.ffmpeg_custom_path
                platform_config = get_platform_config(url)
                cookies = get_browser_cookies(url) if use_browser_cookies and platform_config['cookies_required'] else None
                user_agent = get_random_user_agent() if platform_config['user_agent_required'] else None
                
                ydl_opts = {
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_hook],
                    'noplaylist': True,
                    'ffmpeg_location': ffmpeg_path,
                    'socket_timeout': 30,
                    'retries': 10,
                    'fragment_retries': 10,
                    'nocheckcertificate': True,
                    'ignoreerrors': True,
                    'no_warnings': True,
                    'postprocessors': [], # Inicializar la lista de post-procesadores
                }
                
                # CONFIGURACIÓN DE PROXY
                proxy = None
                if self.use_proxy and platform_config.get('proxy_support', True):
                    proxy = get_random_proxy(self.proxy_type)
                    if proxy:
                        used_proxies.append(proxy)
                        if self.proxy_type == 'http':
                            ydl_opts['proxy'] = f'http://{proxy}' # yt-dlp usa 'proxy' para http, https y socks
                        elif self.proxy_type == 'socks5':
                            ydl_opts['proxy'] = f'socks5://{proxy}'
                        print(f"{INFO_COLOR}🔒 Usando proxy: {proxy}{RESET_COLOR}")

                if user_agent:
                    ydl_opts['http_headers'] = {'User-Agent': user_agent}
                
                if cookies:
                    cookie_file = save_cookies_to_file(cookies)
                    if cookie_file:
                        ydl_opts['cookiefile'] = cookie_file
                
                # CONFIGURACIÓN DE FORMATO
                if audio_only:
                    ydl_opts.update({
                        'format': 'bestaudio/best',
                        'extractaudio': True,
                        'audioformat': audio_format,
                        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': audio_format,'preferredquality': '192',}],
                        'keepvideo': False,
                    })
                elif video_only:
                    # Formato solo video (sin audio)
                    fmt_res = video_resolution.replace('p', '')
                    if fmt_res.isdigit():
                         ydl_opts.update({'format': f'bestvideo[height<={fmt_res}][ext={video_format}]/bestvideo'})
                    else: # 'mejor'
                         ydl_opts.update({'format': f'bestvideo[ext={video_format}]/bestvideo'})
                    
                else: # Video + Audio (Descarga combinada)
                    fmt_res = video_resolution.replace('p', '')
                    
                    # 1. Aplicar el formato de audio estable (+251) y la restricción de resolución/extensión.
                    if fmt_res.isdigit():
                         # Mejor video hasta la resolución + Audio estable (251), luego merge al formato de usuario
                         ydl_opts['format'] = f'bestvideo[height<={fmt_res}][ext={video_format}]+251/best'
                    else: # 'mejor'
                         # Mejor video y audio disponible, pero forzando el audio estable 251.
                         ydl_opts['format'] = f'bestvideo[ext={video_format}]+251/best'
                         
                    # 2. Agregar post-procesador para forzar la fusión (muxing) al formato deseado.
                    ydl_opts['postprocessors'].append({
                        'key': 'FFmpegVideoRemuxer',
                        'preferedformat': video_format # Usa el formato elegido por el usuario (mp4, mkv, webm)
                    })
                    # 3. Eliminar el formato de salida si ya estamos usando FFmpegVideoRemuxer para evitar conflictos.
                    if 'outtmpl' in ydl_opts:
                        # Si usamos remuxer, el archivo final no puede tener extensión en outtmpl.
                        ydl_opts['outtmpl'] = os.path.join(temp_dir, '%(title)s') 
                         
                print(f"{INFO_COLOR}Formato Final Seleccionado: {ydl_opts.get('format')}{RESET_COLOR}")
                print(f"{INFO_COLOR}Formato de Salida para Fusión: {video_format}{RESET_COLOR}")
                
                # EJECUTAR DESCARGA
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # MOVER EL ARCHIVO
                moved_files_count = 0
                for filename in os.listdir(temp_dir):
                    source_path = os.path.join(temp_dir, filename)
                    # Solo mover archivos que NO sean temporales
                    if not os.path.isfile(source_path) or filename.endswith('.tmp') or filename.endswith('.part'):
                        continue
                    
                    # Asegurarse de que el archivo final tiene la extensión correcta (ej: si remuxer se usó correctamente)
                    final_filename = filename
                    if not final_filename.endswith(f'.{video_format}') and not audio_only and not video_only:
                        # Si no es audio ni video_only y no tiene la extensión de fusión, añadirla
                        final_filename = f"{os.path.splitext(filename)[0]}.{video_format}"

                    destination_path = os.path.join(final_output_path, final_filename)
                    shutil.move(source_path, destination_path)
                    moved_files_count += 1
                
                print(f"{OPTION_COLOR}✅ Archivo(s) movido(s) a: {final_output_path}{RESET_COLOR}")

                # LIMPIEZA
                if 'cookiefile' in ydl_opts and os.path.exists(ydl_opts['cookiefile']):
                    os.unlink(ydl_opts['cookiefile'])
                shutil.rmtree(temp_dir)
                
                print(f"{OPTION_COLOR}======================================================={RESET_COLOR}")
                print(f"{OPTION_COLOR}      DESCARGA FINALIZADA CON ÉXITO! 🎉{RESET_COLOR}")
                print(f"{OPTION_COLOR}======================================================={RESET_COLOR}")
                
                self.is_downloading = False
                input("Presiona ENTER para volver al menú principal...")
                return
                
            except Exception as e:
                error_msg = str(e)
                print(f"\n{ERROR_COLOR}❌ Error en intento {current_try + 1}: {error_msg}{RESET_COLOR}")
                
                if temp_dir and os.path.exists(temp_dir):
                    try:
                        shutil.rmtree(temp_dir)
                    except:
                        pass
                
                current_try += 1
                if current_try < max_retries and self.auto_retry_proxy:
                    retry_delay = 2 + (current_try * 2)
                    print(f"{WARNING_COLOR}🔄 Reintentando en {retry_delay} segundos...{RESET_COLOR}")
                    time.sleep(retry_delay)
                else:
                    final_error = f"Error después de {max_retries} intentos. Último error: {error_msg}"
                    print(f"{ERROR_COLOR}❌ {final_error}{RESET_COLOR}")
                    self.is_downloading = False
                    input("Presiona ENTER para volver al menú principal...")
                    return

    def run(self):
        while True:
            self.print_menu()
            choice = self.input_prompt("Selecciona una opción").strip()
            self.handle_menu_choice(choice)

if __name__ == '__main__':
    # No necesitamos ensure_latest_ytdlp aquí, asumimos que el usuario lo tiene.
    app = DownloaderCLI()
    try:
        app.run()
    except KeyboardInterrupt:
        print(f"\n{WARNING_COLOR}¡Adiós!{RESET_COLOR}")
        sys.exit(0)
