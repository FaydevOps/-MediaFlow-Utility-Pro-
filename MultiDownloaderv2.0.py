from yt_dlp import YoutubeDL
from tkinter import *
from tkinter import messagebox as MessageBox
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk 
import os
import threading
import browser_cookie3
import subprocess
import sys
import urllib.request
import random
import time
import tempfile
import json
import requests
import shutil 
import customtkinter as ctk 

# Configuración inicial de CustomTkinter
ctk.set_appearance_mode("Dark")  # Modo Oscuro
ctk.set_default_color_theme("blue") # Tema principal azul/primary blue

# Definición de funciones auxiliares
def get_random_user_agent():
    """Retorna un User-Agent aleatorio de la lista"""
    user_agents = [
        # Chrome
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        # Firefox
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0',
        # Edge
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/116.0.1938.69',
        # Safari
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.2 Safari/605.1.15',
        # Mobile User Agents
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.2 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.172 Mobile Safari/537.36'
    ]
    return random.choice(user_agents)

def get_browser_cookies(url):
    """Obtiene cookies de los navegadores instalados basado en la URL"""
    cookies = None
    domain = extract_domain(url)
    browsers = [
        (browser_cookie3.chrome, "Chrome"),
        (browser_cookie3.firefox, "Firefox"),
        (browser_cookie3.edge, "Edge"),
        (browser_cookie3.opera, "Opera"),
        (browser_cookie3.brave, "Brave")
    ]
    
    for browser_func, browser_name in browsers:
        try:
            # Intentar obtener las cookies, usando domain_name=None para obtener todas
            # y luego filtrar si es necesario (browser_cookie3 ya filtra por dominio)
            cookies = browser_func(domain_name=domain)
            # Asegurarse de que el objeto de cookies no esté vacío antes de retornar
            if list(cookies):
                print(f"Usando cookies de {browser_name} para {domain}")
                return cookies
        except Exception as e:
            continue
    
    print(f"No se pudieron obtener cookies de ningún navegador para {domain}")
    return None

def extract_domain(url):
    """Extrae el dominio principal de una URL"""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    # Eliminar subdominio www si existe
    if domain.startswith('www.'):
        domain = domain[4:]
    return '.' + domain  # Agregar punto para coincidir con el formato de dominio de cookies

def check_video_availability(url):
    """Verifica si un video de YouTube está disponible"""
    if 'youtube.com' in url or 'youtu.be' in url:
        try:
            # Configuración mínima para verificar disponibilidad
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                try:
                    result = ydl.extract_info(url, download=False)
                    if result:
                        return True, None
                except Exception as e:
                    if 'Private video' in str(e):
                        return False, "Video privado"
                    elif 'This video is unavailable' in str(e):
                        return False, "Video no disponible"
                    elif 'Video unavailable' in str(e):
                        return False, "Video no disponible"
                    else:
                        # Para errores genéricos de yt-dlp, es mejor elevar la excepción
                        raise
        except Exception as e:
            return False, str(e)
    return True, None

def get_platform_config(url):
    """Obtiene la configuración específica para cada plataforma"""
    domain = extract_domain(url)[1:]  # Eliminar el punto inicial
    
    # Verificar disponibilidad para YouTube (solo si es YouTube)
    if 'youtube.com' in domain or 'youtu.be' in domain:
        try:
            available, error_msg = check_video_availability(url)
            if not available:
                # Elevar la excepción para que sea capturada en download_video
                raise Exception(f"Error de YouTube: {error_msg}")
        except Exception as e:
             # Si check_video_availability eleva una excepción (como 'Video privado'), la volvemos a elevar
             raise e
    
    # Configuraciones específicas por plataforma
    platform_configs = {
        'youtube.com': {
            # Se usa 'best' como base, pero la lógica de formato en download_video lo refinará
            'format_preference': ['bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'],
            'cookies_required': True,
            'user_agent_required': True,
            'proxy_support': True,
        },
        'vimeo.com': {
            'format_preference': ['best'],
            'cookies_required': False,
            'user_agent_required': True,
            'proxy_support': True,
        },
        'dailymotion.com': {
            'format_preference': ['bestvideo+bestaudio/best'],
            'cookies_required': False,
            'user_agent_required': True,
            'proxy_support': True,
        },
        'twitter.com': {
            'format_preference': ['best'],
            'cookies_required': True,
            'user_agent_required': True,
            'proxy_support': True,
        },
        'facebook.com': {
            'format_preference': ['best'],
            'cookies_required': True,
            'user_agent_required': True,
            'proxy_support': True,
        },
        'instagram.com': {
            'format_preference': ['best'],
            'cookies_required': True,
            'user_agent_required': True,
            'proxy_support': True,
        },
        'tiktok.com': {
            'format_preference': ['best'],
            'cookies_required': False,
            'user_agent_required': True,
            'proxy_support': True,
        },
        'twitch.tv': {
            'format_preference': ['best'],
            'cookies_required': False,
            'user_agent_required': True,
            'proxy_support': True,
        }
    }
    
    # Configuración por defecto si la plataforma no está en la lista
    default_config = {
        'format_preference': ['best'],
        'cookies_required': False,
        'user_agent_required': True,
        'proxy_support': True,
    }
    
    # Buscar configuración para el dominio o cualquier subdominio
    for platform_domain, config in platform_configs.items():
        if platform_domain in domain or domain in platform_domain:
            return config
    
    return default_config

def load_proxy_list():
    """Carga la lista de proxies desde un archivo"""
    proxy_file = os.path.join(os.path.dirname(__file__), "proxies.json")
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
    proxy_file = os.path.join(os.path.dirname(__file__), "proxies.json")
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
    try:
        # Parámetros para la API
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
        
        # Headers para evitar bloqueos
        headers = {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        print(f"🔍 Obteniendo proxies de la API...")
        # Usamos timeout: 30 segundos
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            proxies_text = response.text.strip()
            if proxies_text:
                proxies = [p.strip() for p in proxies_text.split('\n') if p.strip()]
                # Filtrar solo por el tipo solicitado si la API lo permite, o simplemente devolver la lista
                print(f"✅ Obtenidos {len(proxies)} proxies de la API")
                return proxies
            else:
                print("❌ La API no devolvió proxies")
        else:
            print(f"❌ Error en la API: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Error de conexión con la API: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    return []

def get_random_proxy(proxy_type='http'):
    """Obtiene un proxy aleatorio de la lista o de la API"""
    # Primero intentar con proxies locales
    http_proxies, socks5_proxies = load_proxy_list()
    
    if proxy_type == 'http' and http_proxies:
        return random.choice(http_proxies)
    elif proxy_type == 'socks5' and socks5_proxies:
        return random.choice(socks5_proxies)
    
    # Si no hay proxies locales, retornamos None. La lógica de auto-fetch se maneja en el GUI
    return None

def test_proxy(proxy, proxy_type='http', test_url='http://httpbin.org/ip'):
    """Testea si un proxy funciona"""
    try:
        proxies = {}
        if proxy_type == 'http':
            proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
        elif proxy_type == 'socks5':
            # Nota: Requests requiere la librería PySocks para SOCKS5
            proxies = {'http': f'socks5://{proxy}', 'https': f'socks5://{proxy}'}
        
        # Timeout más corto para pruebas
        response = requests.get(test_url, proxies=proxies, timeout=8)
        return response.status_code == 200
    except:
        return False

class MultiDownloaderGUI:
    def __init__(self, master):
        self.master = master
        master.title("Multi Downloader Pro")
        
        # --- COLORES DEL TEMA CTk (Ajustados al logo) ---
        PRIMARY_BLUE = "#4AB8FF"
        ACCENT_GREEN = "#4CAF50"
        
        # La ventana principal ahora se configura como ctk.CTk
        master.geometry("900x800")
        master.resizable(False, False)
        
        # FIX para asegurar que el fondo de la ventana principal combine con el modo oscuro
        self.master.configure(fg_color="#212121") 
        
        # Variables para menús desplegables
        self.video_resolution = StringVar(value="none")
        self.video_format = StringVar(value="none")
        self.audio_format = StringVar(value="none")
        self.output_path = StringVar(value=os.path.expanduser("~/Downloads"))
        self.ffmpeg_custom_path = StringVar(value="") 
        self.use_proxy = BooleanVar(value=False)
        self.proxy_type = StringVar(value="http")
        self.auto_retry_proxy = BooleanVar(value=True)
        self.auto_fetch_proxies = BooleanVar(value=True)

        try:
            # Cargar logo (usando PIL y CTk)
            logo_path = os.path.join(os.path.dirname(__file__), "assets/youtubemp3.png")
            
            if not os.path.exists(logo_path):
                logo_label = ctk.CTkLabel(master, text="Multi Downloader Pro", font=ctk.CTkFont(size=20, weight="bold"))
                logo_label.pack(pady=10)
            else:
                logo_image = Image.open(logo_path)
                
                # FIX para el UserWarning: Usar ctk.CTkImage en lugar de ImageTk.PhotoImage
                self.logo_image_ctk = ctk.CTkImage(
                    dark_image=logo_image,
                    light_image=logo_image,
                    size=(150, 150)
                )
                
                # Usamos CTkLabel con el objeto CTkImage
                logo_label = ctk.CTkLabel(master, image=self.logo_image_ctk, text="")
                logo_label.pack(pady=10)

        except Exception as e:
            print(f"Error al cargar el logo: {e}")
            logo_label = ctk.CTkLabel(master, text="Multi Downloader Pro", font=ctk.CTkFont(size=20, weight="bold"))
            logo_label.pack(pady=10)


        # Marco principal (usando ctk.CTkFrame con esquinas redondeadas)
        # El color de este frame es ligeramente diferente al del fondo principal, lo que crea un bonito contraste.
        main_frame = ctk.CTkFrame(master, corner_radius=10)
        main_frame.pack(padx=20, pady=10, fill=BOTH, expand=True)

        # URL Entry
        ctk.CTkLabel(main_frame, text="URL del Video:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5)
        # ctk.CTkEntry reemplaza ttk.Entry con bordes redondeados (corner_radius)
        self.url_entry = ctk.CTkEntry(main_frame, width=400, font=('Segoe UI', 12), corner_radius=8, border_width=1)
        self.url_entry.pack(pady=5)

        # --- SECCIÓN DE RUTAS ---
        # Directorio de salida
        dir_frame = ctk.CTkFrame(main_frame, fg_color="transparent") # Transparente para usar el fondo del frame principal
        dir_frame.pack(pady=10)
        ctk.CTkLabel(dir_frame, text="Carpeta de Destino:").pack(side=LEFT)
        ctk.CTkEntry(dir_frame, textvariable=self.output_path, width=280, corner_radius=8, state='readonly').pack(side=LEFT, padx=5)
        # Botón con acento verde
        ctk.CTkButton(dir_frame, text="Examinar", command=self.browse_directory, corner_radius=8, fg_color=ACCENT_GREEN, hover_color="#388e3c", text_color="black").pack(side=LEFT)
        
        # Ruta FFmpeg
        ffmpeg_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        ffmpeg_frame.pack(pady=5)
        ctk.CTkLabel(ffmpeg_frame, text="Ruta FFmpeg (Opcional):").pack(side=LEFT)
        ctk.CTkEntry(ffmpeg_frame, textvariable=self.ffmpeg_custom_path, width=280, corner_radius=8, state='readonly').pack(side=LEFT, padx=5)
        ctk.CTkButton(ffmpeg_frame, text="Seleccionar .exe", command=self.browse_ffmpeg_path, corner_radius=8, fg_color=ACCENT_GREEN, hover_color="#388e3c", text_color="black").pack(side=LEFT)

        # --- SECCIÓN DE PROXY ---
        # Usamos CTkFrame con un ligero color de fondo para distinguirla
        proxy_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=("#333333"))
        proxy_frame.pack(pady=10, padx=20, ipadx=10, ipady=10)
        
        ctk.CTkLabel(proxy_frame, text="Configuración Proxy:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky=W, pady=5, columnspan=4)
        
        # ctk.CTkCheckBox reemplaza ttk.Checkbutton
        ctk.CTkCheckBox(proxy_frame, text="Usar Proxy", variable=self.use_proxy).grid(row=1, column=0, padx=10, pady=5, sticky=W)
        
        ctk.CTkLabel(proxy_frame, text="Tipo:").grid(row=1, column=1, sticky=W)
        proxy_types = ["http", "socks5"]
        # ctk.CTkOptionMenu reemplaza OptionMenu con diseño moderno
        ctk.CTkOptionMenu(proxy_frame, variable=self.proxy_type, values=proxy_types, corner_radius=8).grid(row=1, column=2, padx=5, sticky=W)
        
        ctk.CTkCheckBox(proxy_frame, text="Auto-reintento", variable=self.auto_retry_proxy).grid(row=2, column=0, padx=10, pady=5, sticky=W)
        ctk.CTkCheckBox(proxy_frame, text="Auto-obtener proxies", variable=self.auto_fetch_proxies).grid(row=2, column=1, padx=10, pady=5, columnspan=2, sticky=W)
        
        # Botones de gestión de Proxy (Color de acento verde)
        ctk.CTkButton(proxy_frame, text="Obtener Proxies", command=self.fetch_proxies_now, corner_radius=8, fg_color=ACCENT_GREEN, hover_color="#388e3c", text_color="black").grid(row=3, column=0, padx=5, pady=5)
        ctk.CTkButton(proxy_frame, text="Gestionar Proxies", command=self.manage_proxies, corner_radius=8, fg_color=ACCENT_GREEN, hover_color="#388e3c", text_color="black").grid(row=3, column=1, padx=5, pady=5)
        ctk.CTkButton(proxy_frame, text="Testear Proxies", command=self.test_proxies, corner_radius=8, fg_color=ACCENT_GREEN, hover_color="#388e3c", text_color="black").grid(row=3, column=2, padx=5, pady=5)


        # --- SECCIÓN DE FORMATO ---
        options_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        options_frame.pack(pady=10)

        # Resolución
        resolution_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        resolution_frame.pack(side=LEFT, padx=10)
        ctk.CTkLabel(resolution_frame, text="Resolución").pack()
        resolutions = ["none", "mejor", "2160p", "1440p", "1080p", "720p", "480p", "360p"]
        ctk.CTkOptionMenu(resolution_frame, variable=self.video_resolution, values=resolutions, corner_radius=8).pack()

        # Formato de video
        video_format_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        video_format_frame.pack(side=LEFT, padx=10)
        ctk.CTkLabel(video_format_frame, text="Formato Video").pack()
        video_formats = ["none", "mp4", "webm", "mkv"]
        ctk.CTkOptionMenu(video_format_frame, variable=self.video_format, values=video_formats, corner_radius=8).pack()

        # Formato de audio
        audio_format_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        audio_format_frame.pack(side=LEFT, padx=10)
        ctk.CTkLabel(audio_format_frame, text="Formato Audio").pack()
        audio_formats = ["none", "mp3", "wav", "m4a"]
        ctk.CTkOptionMenu(audio_format_frame, variable=self.audio_format, values=audio_formats, corner_radius=8).pack()

        # --- SECCIÓN DE BOTONES DE ACCIÓN ---
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=20)

        # Botón principal con el color del logo (PRIMARY_BLUE)
        self.download_button = ctk.CTkButton(buttons_frame, text="DESCARGAR", command=self.start_download, 
                                             corner_radius=10, fg_color=PRIMARY_BLUE, hover_color="#00a2e8", 
                                             text_color="white", font=ctk.CTkFont(size=14, weight="bold"))
        self.download_button.pack(side=LEFT, padx=15, ipady=5)
        
        # Botones secundarios con el color de acento (ACCENT_GREEN)
        ctk.CTkButton(buttons_frame, text="Solo Audio", command=self.download_audio_only, 
                      corner_radius=8, fg_color=ACCENT_GREEN, hover_color="#388e3c", text_color="black").pack(side=LEFT, padx=5)
        ctk.CTkButton(buttons_frame, text="Solo Video", command=self.download_video_only, 
                      corner_radius=8, fg_color=ACCENT_GREEN, hover_color="#388e3c", text_color="black").pack(side=LEFT, padx=5)

        # Barra de progreso (ttk.Progressbar es simple y funcional)
        self.progress_bar = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.progress_bar.pack(pady=10)
        
        # Etiqueta de estado
        self.status_label = ctk.CTkLabel(main_frame, text="Listo para descargar", font=('Segoe UI', 10, 'italic'))
        self.status_label.pack()

        # Crear menú (el menú principal de Tkinter no se ve afectado por CTk, así que queda igual)
        self.create_menu()

    def browse_directory(self):
        """Abre el diálogo para seleccionar carpeta de destino"""
        directory = filedialog.askdirectory()
        if directory:
            self.output_path.set(directory)

    def browse_ffmpeg_path(self): 
        """Abre el diálogo para seleccionar el ejecutable de ffmpeg"""
        filepath = filedialog.askopenfilename(
            defaultextension=".exe",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")],
            title="Seleccionar ffmpeg.exe"
        )
        if filepath:
            self.ffmpeg_custom_path.set(filepath)
            MessageBox.showinfo("Ruta Guardada", f"Ruta FFmpeg establecida:\n{filepath}")

    def fetch_proxies_now(self):
        """Obtiene proxies de la API inmediatamente"""
        def fetch_thread():
            self.status_label.configure(text="Obteniendo proxies de la API...") # Usar configure en CTkLabel
            http_proxies = get_proxies_from_api('http')
            socks5_proxies = get_proxies_from_api('socks5')
            
            if http_proxies or socks5_proxies:
                save_proxy_list(http_proxies, socks5_proxies)
                total = len(http_proxies) + len(socks5_proxies)
                self.status_label.configure(text=f"✅ Obtenidos {total} proxies")
                MessageBox.showinfo("Éxito", f"Se obtuvieron {total} proxies de la API")
            else:
                self.status_label.configure(text="❌ Error obteniendo proxies")
                MessageBox.showerror("Error", "No se pudieron obtener proxies de la API")
        
        threading.Thread(target=fetch_thread, daemon=True).start()

    def test_proxies(self):
        """Testea los proxies disponibles"""
        def test_thread():
            self.status_label.configure(text="Testeando proxies...")
            http_proxies, socks5_proxies = load_proxy_list()
            working_http = []
            working_socks5 = []
            
            # Testear solo los primeros 10 para no tardar mucho
            proxies_to_test = http_proxies[:10] + socks5_proxies[:10]
            
            for proxy in proxies_to_test:  
                proxy_type = 'http' if proxy in http_proxies else 'socks5'
                if test_proxy(proxy, proxy_type):
                    if proxy_type == 'http':
                        working_http.append(proxy)
                    else:
                        working_socks5.append(proxy)
            
            save_proxy_list(working_http, working_socks5)
            total_working = len(working_http) + len(working_socks5)
            self.status_label.configure(text=f"✅ {total_working} proxies funcionando")
            MessageBox.showinfo("Resultados", 
                              f"Proxies funcionando:\nHTTP: {len(working_http)}\nSOCKS5: {len(working_socks5)}")
        
        threading.Thread(target=test_thread, daemon=True).start()

    def manage_proxies(self):
        """Abre el diálogo para gestionar proxies con interfaz CTk"""
        # Usamos ctk.CTkToplevel para heredar el estilo moderno y oscuro de CTk
        proxy_window = ctk.CTkToplevel(self.master)
        proxy_window.title("Gestión de Proxies")
        proxy_window.geometry("500x450")
        
        # Etiqueta de título CTk
        ctk.CTkLabel(proxy_window, text="Configuración de Proxies", 
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        
        # Frame para proxies HTTP
        http_frame = ctk.CTkFrame(proxy_window, corner_radius=10)
        http_frame.pack(fill=X, padx=20, pady=5)
        ctk.CTkLabel(http_frame, text="Proxies HTTP (uno por línea):").pack(padx=10, pady=5, anchor=W)
        # Usamos ctk.CTkTextbox, que tiene bordes redondeados y estilo oscuro
        http_text = ctk.CTkTextbox(http_frame, height=80, corner_radius=8) 
        http_text.pack(fill=X, padx=10, pady=(0, 10))
        
        # Frame para proxies SOCKS5
        socks_frame = ctk.CTkFrame(proxy_window, corner_radius=10)
        socks_frame.pack(fill=X, padx=20, pady=5)
        ctk.CTkLabel(socks_frame, text="Proxies SOCKS5 (uno por línea):").pack(padx=10, pady=5, anchor=W)
        socks_text = ctk.CTkTextbox(socks_frame, height=80, corner_radius=8)
        socks_text.pack(fill=X, padx=10, pady=(0, 10))
        
        # Cargar proxies existentes
        http_proxies, socks5_proxies = load_proxy_list()
        http_text.insert('0.0', '\n'.join(http_proxies)) 
        socks_text.insert('0.0', '\n'.join(socks5_proxies))
        
        def save_proxies():
            # Obtenemos el contenido de CTkTextbox. 'end-1c' evita el caracter de nueva línea final.
            http_list = [p.strip() for p in http_text.get('0.0', 'end-1c').split('\n') if p.strip()] 
            socks_list = [p.strip() for p in socks_text.get('0.0', 'end-1c').split('\n') if p.strip()]
            
            if save_proxy_list(http_list, socks_list):
                MessageBox.showinfo("Éxito", "Proxies guardados correctamente")
                proxy_window.destroy()
            else:
                MessageBox.showerror("Error", "No se pudieron guardar los proxies")
        
        # Contenedor para botones (transparente)
        button_container = ctk.CTkFrame(proxy_window, fg_color="transparent")
        button_container.pack(pady=15)
        
        # Botones CTk con estilo moderno
        ctk.CTkButton(button_container, text="Guardar", command=save_proxies, corner_radius=8, 
                      fg_color="#4AB8FF", hover_color="#00a2e8").pack(side=LEFT, padx=10)
        ctk.CTkButton(button_container, text="Cancelar", command=proxy_window.destroy, corner_radius=8,
                      fg_color=("gray70", "gray30")).pack(side=LEFT, padx=10)

    def progress_hook(self, d):
        """Actualiza la barra de progreso durante la descarga"""
        if d['status'] == 'downloading':
            try:
                # yt-dlp proporciona un diccionario d con el progreso
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded_bytes = d.get('downloaded_bytes')
                
                if total_bytes and downloaded_bytes:
                    percent = (downloaded_bytes / total_bytes) * 100
                    self.progress_bar["value"] = percent
                    # También podemos usar la cadena de progreso de yt-dlp si está disponible
                    speed = d.get('_speed_str', '')
                    eta = d.get('_eta_str', '')
                    self.status_label.configure(text=f"Descargando: {percent:.1f}% @ {speed} ETA: {eta}")
                elif '_percent_str' in d:
                    # Fallback si las métricas de bytes no están disponibles (p.e. antes de empezar)
                    percent_str = d['_percent_str'].replace('%', '')
                    percent = float(percent_str) if percent_str.replace('.', '', 1).isdigit() else 0
                    self.progress_bar["value"] = percent
                    self.status_label.configure(text=f"Descargando: {d['_percent_str']}")

            except Exception as e:
                # Evitar que errores de parseo detengan el progreso
                pass

        elif d['status'] == 'finished':
            self.status_label.configure(text="Descarga completada. Procesando...")

    def start_download(self):
        """Inicia el proceso de descarga"""
        if not self.url_entry.get():
            MessageBox.showerror("Error", "Por favor ingresa una URL")
            return

        # Desactivar botón durante la descarga
        self.download_button.configure(state='disabled') # Usamos configure con CTkButton
        
        # Reiniciar barra de progreso
        self.progress_bar["value"] = 0
        self.status_label.configure(text="Iniciando descarga...")
        
        # Iniciar descarga en un hilo separado
        thread = threading.Thread(
            target=self.download_video,
            args=(
                self.url_entry.get(),
                self.output_path.get(),
                self.video_resolution.get(),
                self.video_format.get(),
                self.audio_format.get(),
                True,  # use_browser_cookies
                False,  # audio_only
                False   # video_only
            )
        )
        thread.daemon = True
        thread.start()

    def download_audio_only(self):
        """Descarga solo el audio"""
        url = self.url_entry.get()
        if not url:
            MessageBox.showerror("Error", "Por favor ingresa una URL")
            return
            
        self.download_button.configure(state='disabled')
        self.progress_bar["value"] = 0
        self.status_label.configure(text="Iniciando descarga de solo audio...")
        
        thread = threading.Thread(
            target=self.download_video,
            args=(
                url,
                self.output_path.get(),
                "none",
                "none",
                self.audio_format.get(), # Usar el formato de audio seleccionado
                True,  # use_browser_cookies
                True,  # audio_only
                False  # video_only
            )
        )
        thread.daemon = True
        thread.start()

    def download_video_only(self):
        """Descarga solo el video"""
        url = self.url_entry.get()
        if not url:
            MessageBox.showerror("Error", "Por favor ingresa una URL")
            return

        self.download_button.configure(state='disabled')
        self.progress_bar["value"] = 0
        self.status_label.configure(text="Iniciando descarga de solo video...")
        
        thread = threading.Thread(
            target=self.download_video,
            args=(
                url,
                self.output_path.get(),
                self.video_resolution.get(),
                self.video_format.get(),
                "none",
                True,  # use_browser_cookies
                False,  # audio_only
                True   # video_only
            )
        )
        thread.daemon = True
        thread.start()

    def create_menu(self):
        menubar = Menu(self.master)
        self.master.config(menu=menubar)
        
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de", command=self.popup_author)
        help_menu.add_command(label="Donar", command=self.popup_donate)

    def popup_author(self):
        MessageBox.showinfo("Acerca de", "Multi Downloader Pro\nCreado por FayDev\nVersión 2.0")

    def popup_donate(self):
        """Muestra el diálogo de donación con el enlace de PayPal"""
        donate_text = """¡Gracias por usar YouTube Multi Downloader Pro!

      Si te gusta esta aplicación, considera hacer una donación:

      PayPal: https://www.paypal.me/faycraxE

      Tu apoyo ayuda a mantener y mejorar el proyecto."""
        
        MessageBox.showinfo("Donar", donate_text)

    def get_ffmpeg_path(self): 
        """Busca la ruta de ffmpeg en el sistema de forma inteligente, priorizando la ruta manual."""
        
        # 1. Prioridad: Ruta personalizada por el usuario
        custom_path = self.ffmpeg_custom_path.get()
        if custom_path and os.path.exists(custom_path):
            print(f"✅ FFmpeg encontrado en la ruta personalizada: {custom_path}")
            return custom_path
        
        # 2. Segundo intento: Verificar si ffmpeg está en el PATH
        try:
            # Usar 'where ffmpeg' en Windows o 'which ffmpeg' en Linux/macOS
            if sys.platform.startswith('win'):
                cmd = ['where', 'ffmpeg']
            else:
                cmd = ['which', 'ffmpeg']
                
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            path_from_path = result.stdout.strip().split('\n')[0] # Usar solo el primer resultado
            if os.path.exists(path_from_path):
                 print(f"✅ FFmpeg encontrado en el sistema PATH: {path_from_path}")
                 return path_from_path
        except subprocess.CalledProcessError:
             print("❌ 'ffmpeg' no encontrado en el PATH del entorno.")
             pass
        except FileNotFoundError:
             # Esto debería ser raro si se usa 'which' o 'where' correctamente, pero por seguridad
             print("❌ Comando de búsqueda de ruta (where/which) no encontrado.")
             pass

        # 3. Rutas comunes
        local_appdata_path = os.path.expandvars('%LOCALAPPDATA%')
        
        common_paths = [
            os.path.join(os.path.dirname(__file__), "ffmpeg", "bin", "ffmpeg.exe"),
            os.path.join(local_appdata_path, 'Programs', 'ffmpeg', 'bin', 'ffmpeg.exe'),
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                print(f"✅ FFmpeg encontrado en ruta común: {path}")
                return path

        # 4. Fallo total
        self.master.after(0, lambda: MessageBox.showerror("Error FFmpeg", 
            "ERROR: FFmpeg no se encontró en el sistema. Es necesario para conversiones.\n\n"
            "Por favor, instálalo o usa el botón 'Seleccionar .exe' para localizar tu 'ffmpeg.exe'."
        ))
        # Generar un error para detener la descarga si es necesaria la conversión
        raise FileNotFoundError("FFmpeg no encontrado. Es necesario para conversiones de audio/video.")


    def save_cookies_to_file(self, cookies):
        """Guarda cookies en un archivo temporal en formato Netscape para yt-dlp"""
        if not cookies:
            return None
            
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8')
        try:
            # Formato Netscape para cookies
            temp_file.write("# Netscape HTTP Cookie File\n")
            # Usar iter(cookies) para asegurar que funciona con el objeto CookieJar
            for cookie in iter(cookies): 
                # Dominio, flag, path, secure, expiration, name, value
                # La bandera es TRUE si el dominio comienza con '.', FALSE si no. yt-dlp/curl requiere esto.
                domain = cookie.domain
                domain_prefix = 'TRUE' if domain.startswith('.') else 'FALSE' 
                secure = "TRUE" if cookie.secure else "FALSE"
                expiration = str(int(cookie.expires)) if cookie.expires else "0"
                
                temp_file.write(f"{domain}\t{domain_prefix}\t{cookie.path}\t{secure}\t{expiration}\t{cookie.name}\t{cookie.value}\n")
                
            temp_file.close()
            return temp_file.name
        except Exception as e:
            print(f"Error guardando cookies: {e}")
            # Si falla, asegurarse de eliminar el archivo incompleto
            if os.path.exists(temp_file.name):
                 os.unlink(temp_file.name)
            return None

    def download_video(self, url, output_path, video_resolution, video_format, audio_format, use_browser_cookies, audio_only, video_only):
        # Lógica de descarga segura en carpeta temporal (Mantiene la corrección de Windows Defender)
        max_retries = 5
        current_try = 0
        used_proxies = []
        
        # Obtener ruta de ffmpeg primero. Eleva FileNotFoundError si es necesario para conversión
        try:
            ffmpeg_path = self.get_ffmpeg_path()
        except FileNotFoundError:
            # Si no se encuentra FFmpeg y es el primer intento, el error de MessageBox ya se mostró.
            self.master.after(0, lambda: self.download_button.configure(state='normal'))
            return

        while current_try < max_retries:
            temp_dir = None
            cookie_file = None
            try:
                print(f"\n=== INTENTO DE DESCARGA #{current_try + 1} ===")
                
                # 1. Usar un directorio temporal para el proceso de descarga y conversión
                temp_dir = tempfile.mkdtemp()
                
                # 2. Sanitizar ruta de salida final
                final_output_path = os.path.abspath(output_path)
                if not os.path.exists(final_output_path):
                    os.makedirs(final_output_path)

                # Obtener configuración de plataforma
                platform_config = get_platform_config(url)
                
                # Obtener cookies y user agent
                cookies = get_browser_cookies(url) if use_browser_cookies and platform_config.get('cookies_required', False) else None
                user_agent = get_random_user_agent() if platform_config.get('user_agent_required', False) else None
                
                # CONFIGURACIÓN BASE
                ydl_opts = {
                    # 3. La descarga se hace en el directorio temporal
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_hook],
                    'noplaylist': True,
                    'ffmpeg_location': ffmpeg_path,
                    'socket_timeout': 30,
                    'retries': 10,
                    'fragment_retries': 10,
                    'nocheckcertificate': True,
                    'ignoreerrors': False, # Cambiado a False para obtener errores detallados
                    'no_warnings': True,
                }
                
                # ... (CONFIGURACIÓN DE PROXY, HEADERS, COOKIES) ...
                proxy = None
                if self.use_proxy.get() and platform_config.get('proxy_support', True):
                    proxy_type = self.proxy_type.get()
                    # Si auto-fetch está activo Y no hay proxies locales, obtener de la API
                    if self.auto_fetch_proxies.get() and not load_proxy_list()[0] and not load_proxy_list()[1]:
                        api_proxies = get_proxies_from_api(proxy_type)
                        if api_proxies:
                            save_proxy_list(api_proxies, load_proxy_list()[1] if proxy_type == 'http' else api_proxies)
                    
                    proxy = get_random_proxy(proxy_type)
                    
                    if proxy:
                        if proxy in used_proxies and len(used_proxies) < 10: # Límite de 10 reintentos de proxy
                            available_proxies = load_proxy_list()[0] if proxy_type == 'http' else load_proxy_list()[1]
                            
                            # Buscar un proxy no usado
                            new_proxy = None
                            for p in available_proxies:
                                if p not in used_proxies:
                                    new_proxy = p
                                    break
                            
                            proxy = new_proxy if new_proxy else proxy # Si no hay nuevo, usar el último
                        
                        if proxy:
                            used_proxies.append(proxy)
                            # Formato de proxy para yt-dlp
                            proxy_url = f"{proxy_type}://{proxy}"
                            ydl_opts['proxy'] = proxy_url
                            print(f"🔒 Usando proxy: {proxy_url}")
                
                if user_agent:
                    ydl_opts['http_headers'] = {'User-Agent': user_agent}
                
                if cookies:
                    cookie_file = self.save_cookies_to_file(cookies)
                    if cookie_file:
                        ydl_opts['cookiefile'] = cookie_file
                
                
                # --- Lógica de CONFIGURACIÓN DE FORMATO CORREGIDA (Fix para FFmpegVideoConvertorPP) ---
                
                if audio_only:
                    # Sobrescribir para solo audio si se seleccionó esa opción
                    audio_codec = audio_format if audio_format != "none" else 'mp3'
                    ydl_opts.update({
                        'format': 'bestaudio/best', # Asegura la mejor calidad de audio
                        'extractaudio': True,
                        'audioformat': audio_codec,
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': audio_codec,
                            'preferredquality': '192', # Calidad estándar alta
                        }],
                        'keepvideo': False,
                        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    })
                    
                elif video_only:
                    # Sobrescribir para solo video si se seleccionó esa opción
                    video_codec = video_format if video_format != "none" else 'mp4'
                    
                    # Formato de video con resolución preferida
                    res_pref = ""
                    if video_resolution != "none" and video_resolution != "mejor":
                        res_val = video_resolution.replace('p', '')
                        res_pref = f"[height<={res_val}]"
                        
                    format_string = f"bestvideo{res_pref}/bestvideo"
                    
                    # Solo forzamos el remux si el usuario seleccionó un formato específico (no 'none' o 'mp4')
                    postprocessors = []
                    if video_codec != 'none' and video_codec != 'mp4':
                        postprocessors.append({'key': 'FFmpegVideoRemuxer', 'preferredformat': video_codec})
                    
                    ydl_opts.update({
                        'format': format_string,
                        'keepvideo': False,
                        'postprocessors': postprocessors,
                        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    })
                    
                else: # Modo combinado (Video + Audio)
                    # 1. Resolución
                    res_pref = ""
                    if video_resolution != "none" and video_resolution != "mejor":
                        res_val = video_resolution.replace('p', '')
                        res_pref = f"[height<={res_val}]"
                    
                    # 2. Formato de Contenedor (ext)
                    container_format = video_format if video_format != "none" else 'mp4'
                    
                    # 3. Construir la cadena de formato
                    format_string = f"bestvideo{res_pref}+bestaudio/bestvideo{res_pref}/best"
                    
                    # 4. Post-procesador para muxear (unir) y remuxear.
                    postprocessors = []
                    
                    # Si el formato es diferente a los formatos más comunes de muxing (none, mp4), 
                    # forzamos el remux. Si es "mp4" o "none", yt-dlp muxea automáticamente.
                    if container_format != 'none' and container_format != 'mp4':
                         postprocessors.append({
                            'key': 'FFmpegVideoRemuxer', 
                            'preferredformat': container_format
                         })
                    
                    ydl_opts.update({
                        'format': format_string,
                        'postprocessors': postprocessors,
                        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    })
                
                print(f"Configuración final de 'format': {ydl_opts.get('format')}")
                
                # EJECUTAR DESCARGA
                self.master.after(0, lambda: self.status_label.configure(text="Conectando y obteniendo información..."))
                with YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(url, download=True)
                
                # --- Lógica: MOVER EL ARCHIVO ---
                # 4. Encontrar el archivo final (puede haber sido remuxeado)
                moved_files_count = 0
                final_filename = None
                
                # 4a. Buscar el archivo con la extensión correcta en el directorio temporal
                # Determinar la extensión final esperada
                expected_ext = ""
                if audio_only:
                    expected_ext = audio_format if audio_format != "none" else 'mp3'
                elif video_only:
                    expected_ext = video_format if video_format != "none" else 'mp4'
                else:
                    expected_ext = video_format if video_format != "none" else 'mp4'

                for filename in os.listdir(temp_dir):
                    if filename.endswith(f".{expected_ext}") and os.path.isfile(os.path.join(temp_dir, filename)):
                         final_filename = filename
                         break
                
                # 4b. Mover el archivo (o todos si no se encontró un solo archivo principal)
                if final_filename:
                    source_path = os.path.join(temp_dir, final_filename)
                    destination_path = os.path.join(final_output_path, final_filename)
                    shutil.move(source_path, destination_path)
                    moved_files_count = 1
                else:
                    # Fallback: mover todos los archivos generados si no se pudo identificar uno
                    for filename in os.listdir(temp_dir):
                        source_path = os.path.join(temp_dir, filename)
                        if os.path.isfile(source_path):
                            destination_path = os.path.join(final_output_path, filename)
                            shutil.move(source_path, destination_path)
                            moved_files_count += 1
                
                print(f"✅ Se movieron {moved_files_count} archivos de {temp_dir} a {final_output_path}")

                # Éxito y limpieza
                if cookie_file and os.path.exists(cookie_file):
                    try:
                        os.unlink(cookie_file)
                    except:
                        pass
                
                # 6. Eliminar la carpeta temporal
                shutil.rmtree(temp_dir)
                temp_dir = None
                
                self.master.after(0, lambda: self.status_label.configure(text=f"✓ Descarga completada"))
                self.master.after(0, lambda: self.progress_bar.config(value=100))
                self.master.after(0, lambda: self.download_button.configure(state='normal'))
                return
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Error en intento {current_try + 1}: {error_msg}")
                
                # Limpiar recursos en caso de error
                if cookie_file and os.path.exists(cookie_file):
                    try: os.unlink(cookie_file)
                    except: pass
                if temp_dir and os.path.exists(temp_dir):
                    try: shutil.rmtree(temp_dir)
                    except: pass
                
                # Estrategia de recuperación inteligente si está activada
                if self.auto_retry_proxy.get():
                    if "not available" in error_msg.lower() or "region" in error_msg.lower() or "geo-restricted" in error_msg.lower():
                        print("⚠ Video no disponible. Activando proxy para reintentar...")
                        self.use_proxy.set(True)
                    elif ("proxy" in error_msg.lower() or "failed to send request" in error_msg.lower()) and self.use_proxy.get():
                        print("⚠ Error de proxy. Desactivando proxy y reintentando...")
                        self.use_proxy.set(False)
                        used_proxies = [] # Resetear proxies usados
                
                current_try += 1
                if current_try < max_retries:
                    retry_delay = 2 + (current_try * 2)
                    self.master.after(0, lambda: self.status_label.configure(text=f"Error. Reintentando en {retry_delay}s..."))
                    print(f"🔄 Reintentando en {retry_delay} segundos...")
                    time.sleep(retry_delay)
                else:
                    final_error = f"Error después de {max_retries} intentos. Último error: {error_msg}"
                    self.master.after(0, lambda: self.status_label.configure(text=f"❌ Error fatal"))
                    self.master.after(0, lambda: MessageBox.showerror("Error", final_error))
                    self.master.after(0, lambda: self.download_button.configure(state='normal'))
                    # Salir del bucle
                    break

def verify_youtube_url(url):
    """Verifica y limpia una URL de YouTube"""
    from urllib.parse import parse_qs, urlparse
    
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]+)',
        r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]+)'
    ]
    
    import re
    video_id = None
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            break
    
    if not video_id:
        parsed_url = urlparse(url)
        if 'youtube.com' in parsed_url.netloc:
            query_params = parse_qs(parsed_url.query)
            video_id = query_params.get('v', [None])[0]
    
    if video_id:
        return f'https://www.youtube.com/watch?v={video_id}'
    return url

def ensure_latest_ytdlp():
    """Asegura que yt-dlp esté actualizado y configurado correctamente"""
    ytdlp_path = os.path.join(os.getcwd(), "yt-dlp.exe")
    ytdlp_url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
    
    try:
        print("Verificando instalación de yt-dlp...")
        
        needs_update = True
        # Usar la versión de la librería si no se encuentra el binario externo, aunque
        # la intención parece ser usar el binario externo para mejor rendimiento
        if os.path.exists(ytdlp_path):
            try:
                # Comprobar la versión instalada y actualizar
                result = subprocess.run([ytdlp_path, '--version'], capture_output=True, text=True, check=True)
                current_version = result.stdout.strip()
                print(f"Versión actual: {current_version}")
                
                update_result = subprocess.run([ytdlp_path, '-U'], capture_output=True, text=True)
                
                if "yt-dlp is up to date" in update_result.stdout:
                    needs_update = False
                    print("yt-dlp está actualizado")
                else:
                    print("yt-dlp actualizado a la última versión.")
            except Exception as e:
                print(f"Error verificando o actualizando versión de yt-dlp: {e}")
        
        if needs_update:
            print("Descargando última versión de yt-dlp...")
            user_agents = [get_random_user_agent() for _ in range(3)]
            success = False
            
            for user_agent in user_agents:
                try:
                    headers = {'User-Agent': user_agent}
                    req = urllib.request.Request(ytdlp_url, headers=headers)
                    with urllib.request.urlopen(req) as response, open(ytdlp_path, 'wb') as out_file:
                        # Descarga segura
                        shutil.copyfileobj(response, out_file)
                    success = True
                    print("yt-dlp actualizado/descargado correctamente")
                    break
                except Exception as e:
                    print(f"Intento fallido con User-Agent: {str(e)}")
                    continue
            
            if not success:
                # Si falla, advertir pero permitir que el programa continúe usando la librería instalada
                print("ADVERTENCIA: No se pudo descargar el binario de yt-dlp. Se usará la versión de Python.")

        # La configuración global se deja como está, ya que la lógica en download_video la ignora/sobrescribe
        config_path = os.path.join(os.path.expanduser("~"), "yt-dlp.conf")
        if not os.path.exists(config_path):
             try:
                 with open(config_path, 'w') as f:
                     # Esta configuración es principalmente para el uso de línea de comandos, 
                     # pero no molesta si existe.
                     f.write("""# Configuración global de yt-dlp
--force-ipv4
--no-check-certificates
--prefer-ffmpeg
--extract-audio
--audio-quality 0
--format bestvideo+bestaudio/best
--concurrent-fragments 3
--retry-sleep 5
--buffer-size 16K
--no-warnings
""")
                 print("Archivo de configuración de yt-dlp creado")
             except Exception as e:
                 print(f"Error creando archivo de configuración: {e}")

    except Exception as e:
        print(f"Error general en la inicialización de yt-dlp: {e}")
        print("Continuando con la versión existente/instalada...")

if __name__ == '__main__':
    # Ejecutar la verificación en un hilo para no bloquear el GUI al inicio
    threading.Thread(target=ensure_latest_ytdlp, daemon=True).start()
    
    # Usamos la clase principal de CustomTkinter para la ventana
    root = ctk.CTk()
    app = MultiDownloaderGUI(root)
    root.mainloop()
