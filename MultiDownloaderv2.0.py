from yt_dlp import YoutubeDL
from tkinter import *
from tkinter import messagebox as MessageBox
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk 
import os
import threading
import subprocess
import sys
import urllib.request
import random
import time
import tempfile
import json
import shutil 
import customtkinter as ctk 

# Configuración inicial de CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ========== FUNCIONES AUXILIARES ==========

def get_base_path():
    """Retorna la ruta base de los archivos de configuración"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(__file__)

def get_random_user_agent():
    """Retorna un User-Agent aleatorio de la lista"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
    ]
    return random.choice(user_agents)

def detect_installed_browsers():
    """Detecta qué navegadores están instalados en el sistema"""
    browsers = []
    
    # Rutas comunes de navegadores en Windows
    browser_paths = {
        'chrome': [
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data'),
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
        ],
        'firefox': [
            os.path.join(os.environ.get('APPDATA', ''), 'Mozilla', 'Firefox', 'Profiles'),
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'Mozilla Firefox', 'firefox.exe'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Mozilla Firefox', 'firefox.exe'),
        ],
        'edge': [
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
        ],
        'opera': [
            os.path.join(os.environ.get('APPDATA', ''), 'Opera Software', 'Opera Stable'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Opera'),
        ],
        'brave': [
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'BraveSoftware', 'Brave-Browser', 'User Data'),
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'BraveSoftware', 'Brave-Browser', 'Application', 'brave.exe'),
        ],
    }
    
    # Rutas para Linux/Mac
    if sys.platform != 'win32':
        if sys.platform == 'darwin':  # macOS
            browser_paths['chrome'].extend([
                os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'Google', 'Chrome'),
            ])
            browser_paths['firefox'].extend([
                os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'Firefox', 'Profiles'),
            ])
            browser_paths['safari'] = [
                os.path.join(os.path.expanduser('~'), 'Library', 'Safari'),
            ]
        else:  # Linux
            browser_paths['chrome'].extend([
                os.path.join(os.path.expanduser('~'), '.config', 'google-chrome'),
            ])
            browser_paths['firefox'].extend([
                os.path.join(os.path.expanduser('~'), '.mozilla', 'firefox'),
            ])
    
    # Verificar qué navegadores existen
    for browser, paths in browser_paths.items():
        for path in paths:
            if os.path.exists(path):
                if browser not in browsers:
                    browsers.append(browser)
                break
    
    return browsers

def extract_domain(url):
    """Extrae el dominio principal de una URL"""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain

def check_video_availability(url):
    """Verifica si un video de YouTube está disponible"""
    if 'youtube.com' in url or 'youtu.be' in url:
        try:
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
                    error_str = str(e)
                    if 'Private video' in error_str:
                        return False, "Video privado"
                    elif 'unavailable' in error_str.lower():
                        return False, "Video no disponible"
                    else:
                        raise
        except Exception as e:
            return False, str(e)
    return True, None

def get_platform_config(url):
    """Obtiene la configuración específica para cada plataforma"""
    domain = extract_domain(url)
    
    if 'youtube.com' in domain or 'youtu.be' in domain:
        try:
            available, error_msg = check_video_availability(url)
            if not available:
                raise Exception(f"Error de YouTube: {error_msg}")
        except Exception as e:
            raise e
    
    platform_configs = {
        'youtube.com': {
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
        'tiktok.com': {
            'format_preference': ['best'],
            'cookies_required': False,
            'user_agent_required': True,
            'proxy_support': True,
        },
    }
    
    default_config = {
        'format_preference': ['best'],
        'cookies_required': False,
        'user_agent_required': True,
        'proxy_support': True,
    }
    
    for platform_domain, config in platform_configs.items():
        if platform_domain in domain or domain in platform_domain:
            return config
    
    return default_config

def load_proxy_list():
    """Carga la lista de proxies desde un archivo"""
    proxy_file = os.path.join(get_base_path(), "proxies.json")
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
    proxy_file = os.path.join(get_base_path(), "proxies.json")
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

def get_proxies_from_api(proxy_type='http', timeout=10000):
    """Obtiene proxies automáticamente de una API pública"""
    try:
        if proxy_type == 'http':
            url = "https://www.proxy-list.download/api/v1/get?type=http"
        else:
            url = "https://www.proxy-list.download/api/v1/get?type=socks5"
        
        headers = {
            'User-Agent': get_random_user_agent(),
        }
        
        print(f"🔍 Obteniendo proxies de la API...")
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            proxies_text = response.read().decode('utf-8').strip()
            
        if proxies_text:
            proxies = [p.strip() for p in proxies_text.split('\n') if p.strip()]
            print(f"✅ Obtenidos {len(proxies)} proxies de la API")
            return proxies
        else:
            print("❌ La API no devolvió proxies")
            
    except Exception as e:
        print(f"❌ Error obteniendo proxies: {e}")
    
    return []

def get_random_proxy(proxy_type='http'):
    """Obtiene un proxy aleatorio de la lista"""
    http_proxies, socks5_proxies = load_proxy_list()
    
    if proxy_type == 'http' and http_proxies:
        return random.choice(http_proxies)
    elif proxy_type == 'socks5' and socks5_proxies:
        return random.choice(socks5_proxies)
    
    return None

def test_proxy(proxy, proxy_type='http'):
    """Testea si un proxy funciona usando urllib"""
    try:
        if proxy_type == 'http':
            proxy_handler = urllib.request.ProxyHandler({'http': f'http://{proxy}', 'https': f'http://{proxy}'})
        else:
            proxy_handler = urllib.request.ProxyHandler({'http': f'socks5://{proxy}', 'https': f'socks5://{proxy}'})
        
        opener = urllib.request.build_opener(proxy_handler)
        opener.addheaders = [('User-Agent', get_random_user_agent())]
        
        response = opener.open('http://httpbin.org/ip', timeout=8)
        return response.getcode() == 200
    except:
        return False

class MultiDownloaderGUI:
    def __init__(self, master):
        self.master = master
        master.title("Multi Downloader Pro v3.1")
        
        PRIMARY_BLUE = "#4AB8FF"
        ACCENT_GREEN = "#4CAF50"
        
        # Hacer la ventana redimensionable
        master.geometry("900x950")
        master.minsize(800, 850)  # Tamaño mínimo
        master.resizable(True, True)  # Permitir redimensionar
        self.master.configure(fg_color="#212121") 
        
        # Variables
        self.video_resolution = StringVar(value="none")
        self.video_format = StringVar(value="none")
        self.audio_format = StringVar(value="none")
        self.output_path = StringVar(value=os.path.expanduser("~/Downloads"))
        self.ffmpeg_custom_path = StringVar(value="") 
        self.use_proxy = BooleanVar(value=False)
        self.proxy_type = StringVar(value="http")
        self.auto_retry_proxy = BooleanVar(value=True)
        self.auto_fetch_proxies = BooleanVar(value=True)
        self.use_browser_cookies = BooleanVar(value=False)
        
        # Detectar navegadores instalados
        self.installed_browsers = detect_installed_browsers()
        if self.installed_browsers:
            self.selected_browser = StringVar(value=self.installed_browsers[0])
        else:
            self.selected_browser = StringVar(value="ninguno")

        # Logo
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "assets/youtubemp3.png")
            
            if not os.path.exists(logo_path):
                logo_label = ctk.CTkLabel(master, text="Multi Downloader Pro", font=ctk.CTkFont(size=20, weight="bold"))
                logo_label.pack(pady=10)
            else:
                logo_image = Image.open(logo_path)
                self.logo_image_ctk = ctk.CTkImage(
                    dark_image=logo_image,
                    light_image=logo_image,
                    size=(150, 150)
                )
                logo_label = ctk.CTkLabel(master, image=self.logo_image_ctk, text="")
                logo_label.pack(pady=10)

        except Exception as e:
            print(f"Error al cargar el logo: {e}")
            logo_label = ctk.CTkLabel(master, text="Multi Downloader Pro", font=ctk.CTkFont(size=20, weight="bold"))
            logo_label.pack(pady=10)

        # Marco principal con scrollbar
        # Crear un canvas con scrollbar para contenido scrolleable
        canvas_frame = ctk.CTkFrame(master, corner_radius=0, fg_color="#212121")
        canvas_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # Canvas
        self.canvas = ctk.CTkCanvas(canvas_frame, bg="#212121", highlightthickness=0)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ctk.CTkScrollbar(canvas_frame, command=self.canvas.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame principal dentro del canvas
        main_frame = ctk.CTkFrame(self.canvas, corner_radius=10)
        self.canvas_window = self.canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        # Configurar el scroll
        def configure_scroll(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            # Ajustar el ancho del frame al canvas
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        main_frame.bind("<Configure>", configure_scroll)
        self.canvas.bind("<Configure>", configure_scroll)
        
        # Habilitar scroll con la rueda del mouse
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # URL Entry
        ctk.CTkLabel(main_frame, text="URL del Video:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5, padx=10)
        self.url_entry = ctk.CTkEntry(main_frame, font=('Segoe UI', 12), corner_radius=8, border_width=1)
        self.url_entry.pack(pady=5, padx=20, fill=X)

        # Directorio de salida
        dir_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        dir_frame.pack(pady=10, padx=20, fill=X)
        ctk.CTkLabel(dir_frame, text="Carpeta de Destino:").pack(side=LEFT, padx=5)
        ctk.CTkEntry(dir_frame, textvariable=self.output_path, corner_radius=8, state='readonly').pack(side=LEFT, padx=5, fill=X, expand=True)
        ctk.CTkButton(dir_frame, text="Examinar", command=self.browse_directory, corner_radius=8, fg_color=ACCENT_GREEN, hover_color="#388e3c", text_color="black", width=100).pack(side=LEFT, padx=5)
        
        # Ruta FFmpeg
        ffmpeg_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        ffmpeg_frame.pack(pady=5, padx=20, fill=X)
        ctk.CTkLabel(ffmpeg_frame, text="Ruta FFmpeg (Opcional):").pack(side=LEFT, padx=5)
        ctk.CTkEntry(ffmpeg_frame, textvariable=self.ffmpeg_custom_path, corner_radius=8, state='readonly').pack(side=LEFT, padx=5, fill=X, expand=True)
        ctk.CTkButton(ffmpeg_frame, text="Seleccionar .exe", command=self.browse_ffmpeg_path, corner_radius=8, fg_color=ACCENT_GREEN, hover_color="#388e3c", text_color="black", width=120).pack(side=LEFT, padx=5)

        # SECCIÓN MEJORADA: Cookies del navegador (MÁS COMPACTA)
        cookies_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=("#333333"))
        cookies_frame.pack(pady=8, padx=20, ipadx=10, ipady=8, fill=X)
        
        ctk.CTkLabel(cookies_frame, text="🍪 Cookies del Navegador:", 
                     font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky=W, pady=3, columnspan=3)
        
        # Checkbox principal
        ctk.CTkCheckBox(cookies_frame, text="Usar cookies", 
                       variable=self.use_browser_cookies, 
                       command=self.on_cookie_toggle).grid(row=1, column=0, padx=10, pady=3, sticky=W)
        
        # Selector de navegador
        ctk.CTkLabel(cookies_frame, text="Navegador:").grid(row=1, column=1, sticky=W, padx=5)
        
        if self.installed_browsers:
            self.browser_menu = ctk.CTkOptionMenu(cookies_frame, variable=self.selected_browser, 
                                                   values=self.installed_browsers, corner_radius=8, width=100)
            self.browser_menu.grid(row=1, column=2, padx=5, sticky=W)
            
            # Botón de detección más pequeño
            ctk.CTkButton(cookies_frame, text="🔄 Detectar", 
                         command=self.refresh_browsers, corner_radius=8, 
                         fg_color=ACCENT_GREEN, hover_color="#388e3c", 
                         text_color="black", width=100, height=28).grid(row=2, column=0, padx=10, pady=3, sticky=W)
            
            # Status de navegadores más compacto
            browser_status = f"✅ {', '.join([b.title() for b in self.installed_browsers])}"
            ctk.CTkLabel(cookies_frame, text=browser_status, 
                        font=ctk.CTkFont(size=8), text_color="#4CAF50").grid(row=2, column=1, padx=5, pady=2, sticky=W, columnspan=2)
        else:
            ctk.CTkLabel(cookies_frame, text="❌ Sin navegadores", 
                        text_color="red", font=ctk.CTkFont(size=9)).grid(row=1, column=1, padx=5, columnspan=2, sticky=W)
            ctk.CTkButton(cookies_frame, text="🔄 Buscar", 
                         command=self.refresh_browsers, corner_radius=8,
                         fg_color=ACCENT_GREEN, hover_color="#388e3c", 
                         text_color="black", width=100, height=28).grid(row=2, column=0, padx=10, pady=3, sticky=W)
        
        # Nota más pequeña
        ctk.CTkLabel(cookies_frame, text="⚠️ Cierra el navegador antes de descargar", 
                    font=ctk.CTkFont(size=8), text_color="yellow").grid(row=3, column=0, padx=10, pady=2, sticky=W, columnspan=3)

        # Sección de Proxy (MÁS COMPACTA)
        proxy_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=("#333333"))
        proxy_frame.pack(pady=8, padx=20, ipadx=10, ipady=8)
        
        ctk.CTkLabel(proxy_frame, text="🔒 Configuración Proxy:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky=W, pady=3, columnspan=4)
        
        ctk.CTkCheckBox(proxy_frame, text="Usar Proxy", variable=self.use_proxy).grid(row=1, column=0, padx=10, pady=3, sticky=W)
        
        ctk.CTkLabel(proxy_frame, text="Tipo:").grid(row=1, column=1, sticky=W)
        proxy_types = ["http", "socks5"]
        ctk.CTkOptionMenu(proxy_frame, variable=self.proxy_type, values=proxy_types, corner_radius=8, width=90).grid(row=1, column=2, padx=5, sticky=W)
        
        ctk.CTkCheckBox(proxy_frame, text="Auto-reintento", variable=self.auto_retry_proxy).grid(row=2, column=0, padx=10, pady=3, sticky=W)
        ctk.CTkCheckBox(proxy_frame, text="Auto-obtener", variable=self.auto_fetch_proxies).grid(row=2, column=1, padx=10, pady=3, columnspan=2, sticky=W)
        
        ctk.CTkButton(proxy_frame, text="Obtener", command=self.fetch_proxies_now, corner_radius=8, fg_color=ACCENT_GREEN, hover_color="#388e3c", text_color="black", width=90, height=28).grid(row=3, column=0, padx=5, pady=3)
        ctk.CTkButton(proxy_frame, text="Gestionar", command=self.manage_proxies, corner_radius=8, fg_color=ACCENT_GREEN, hover_color="#388e3c", text_color="black", width=90, height=28).grid(row=3, column=1, padx=5, pady=3)
        ctk.CTkButton(proxy_frame, text="Testear", command=self.test_proxies, corner_radius=8, fg_color=ACCENT_GREEN, hover_color="#388e3c", text_color="black", width=90, height=28).grid(row=3, column=2, padx=5, pady=3)

        # Sección de Formato
        options_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        options_frame.pack(pady=10, padx=20, fill=X)
        
        # Usar grid para mejor distribución
        options_frame.grid_columnconfigure(0, weight=1)
        options_frame.grid_columnconfigure(1, weight=1)
        options_frame.grid_columnconfigure(2, weight=1)

        # Resolución
        resolution_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        resolution_frame.grid(row=0, column=0, padx=10, sticky="ew")
        ctk.CTkLabel(resolution_frame, text="Resolución").pack()
        resolutions = ["none", "mejor", "2160p", "1440p", "1080p", "720p", "480p", "360p"]
        ctk.CTkOptionMenu(resolution_frame, variable=self.video_resolution, values=resolutions, corner_radius=8).pack(fill=X, padx=5)

        # Formato de video
        video_format_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        video_format_frame.grid(row=0, column=1, padx=10, sticky="ew")
        ctk.CTkLabel(video_format_frame, text="Formato Video").pack()
        video_formats = ["none", "mp4", "webm", "mkv"]
        ctk.CTkOptionMenu(video_format_frame, variable=self.video_format, values=video_formats, corner_radius=8).pack(fill=X, padx=5)

        # Formato de audio
        audio_format_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        audio_format_frame.grid(row=0, column=2, padx=10, sticky="ew")
        ctk.CTkLabel(audio_format_frame, text="Formato Audio").pack()
        audio_formats = ["none", "mp3", "wav", "m4a"]
        ctk.CTkOptionMenu(audio_format_frame, variable=self.audio_format, values=audio_formats, corner_radius=8).pack(fill=X, padx=5)

        # Botones de Acción
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=20, padx=20, fill=X)
        
        # Centrar botones usando grid
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=0)
        buttons_frame.grid_columnconfigure(2, weight=0)
        buttons_frame.grid_columnconfigure(3, weight=0)
        buttons_frame.grid_columnconfigure(4, weight=1)

        self.download_button = ctk.CTkButton(buttons_frame, text="⬇️ DESCARGAR", 
                                             command=self.start_download, 
                                             corner_radius=10, 
                                             fg_color=PRIMARY_BLUE, 
                                             hover_color="#00a2e8", 
                                             text_color="white", 
                                             font=ctk.CTkFont(size=14, weight="bold"),
                                             width=180, 
                                             height=40)
        self.download_button.grid(row=0, column=1, padx=10, pady=5)
        
        ctk.CTkButton(buttons_frame, text="🎵 Solo Audio", 
                      command=self.download_audio_only, 
                      corner_radius=8, 
                      fg_color=ACCENT_GREEN, 
                      hover_color="#388e3c", 
                      text_color="black", 
                      width=130, 
                      height=40).grid(row=0, column=2, padx=5, pady=5)
        
        ctk.CTkButton(buttons_frame, text="🎬 Solo Video", 
                      command=self.download_video_only, 
                      corner_radius=8, 
                      fg_color=ACCENT_GREEN, 
                      hover_color="#388e3c", 
                      text_color="black", 
                      width=130, 
                      height=40).grid(row=0, column=3, padx=5, pady=5)

        # Barra de progreso
        self.progress_bar = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.progress_bar.pack(pady=10, padx=20, fill=X)
        
        # Etiqueta de estado
        self.status_label = ctk.CTkLabel(main_frame, text="Listo para descargar", font=('Segoe UI', 10, 'italic'))
        self.status_label.pack(pady=5)

        self.create_menu()

    def on_cookie_toggle(self):
        """Callback cuando se activa/desactiva el uso de cookies"""
        if self.use_browser_cookies.get() and not self.installed_browsers:
            MessageBox.showwarning("Sin navegadores", 
                                  "No se detectaron navegadores instalados.\n\n"
                                  "Presiona 'Buscar navegadores' para intentar detectarlos nuevamente.")
            self.use_browser_cookies.set(False)

    def refresh_browsers(self):
        """Detecta nuevamente los navegadores instalados"""
        self.status_label.configure(text="🔍 Buscando navegadores instalados...")
        self.installed_browsers = detect_installed_browsers()
        
        if self.installed_browsers:
            self.selected_browser.set(self.installed_browsers[0])
            browsers_found = ', '.join([b.title() for b in self.installed_browsers])
            MessageBox.showinfo("Navegadores detectados", 
                               f"Se encontraron los siguientes navegadores:\n\n{browsers_found}")
            self.status_label.configure(text=f"✅ {len(self.installed_browsers)} navegador(es) detectado(s)")
            
            # Recrear el frame de cookies para actualizar la UI
            # (Esto requeriría rediseñar la UI, por ahora solo mostramos el mensaje)
        else:
            MessageBox.showwarning("Sin navegadores", 
                                  "No se detectaron navegadores instalados en tu sistema.\n\n"
                                  "Navegadores compatibles:\n"
                                  "• Google Chrome\n"
                                  "• Mozilla Firefox\n"
                                  "• Microsoft Edge\n"
                                  "• Opera\n"
                                  "• Brave")
            self.status_label.configure(text="❌ No se detectaron navegadores")

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_path.set(directory)

    def browse_ffmpeg_path(self): 
        filepath = filedialog.askopenfilename(
            defaultextension=".exe",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")],
            title="Seleccionar ffmpeg.exe"
        )
        if filepath:
            self.ffmpeg_custom_path.set(filepath)
            MessageBox.showinfo("Ruta Guardada", f"Ruta FFmpeg establecida:\n{filepath}")

    def fetch_proxies_now(self):
        def fetch_thread():
            self.status_label.configure(text="Obteniendo proxies de la API...")
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
        def test_thread():
            self.status_label.configure(text="Testeando proxies...")
            http_proxies, socks5_proxies = load_proxy_list()
            working_http = []
            working_socks5 = []
            
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
        proxy_window = ctk.CTkToplevel(self.master)
        proxy_window.title("Gestión de Proxies")
        proxy_window.geometry("500x450")
        
        ctk.CTkLabel(proxy_window, text="Configuración de Proxies", 
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        
        http_frame = ctk.CTkFrame(proxy_window, corner_radius=10)
        http_frame.pack(fill=X, padx=20, pady=5)
        ctk.CTkLabel(http_frame, text="Proxies HTTP (uno por línea):").pack(padx=10, pady=5, anchor=W)
        http_text = ctk.CTkTextbox(http_frame, height=80, corner_radius=8) 
        http_text.pack(fill=X, padx=10, pady=(0, 10))
        
        socks_frame = ctk.CTkFrame(proxy_window, corner_radius=10)
        socks_frame.pack(fill=X, padx=20, pady=5)
        ctk.CTkLabel(socks_frame, text="Proxies SOCKS5 (uno por línea):").pack(padx=10, pady=5, anchor=W)
        socks_text = ctk.CTkTextbox(socks_frame, height=80, corner_radius=8)
        socks_text.pack(fill=X, padx=10, pady=(0, 10))
        
        http_proxies, socks5_proxies = load_proxy_list()
        http_text.insert('0.0', '\n'.join(http_proxies)) 
        socks_text.insert('0.0', '\n'.join(socks5_proxies))
        
        def save_proxies():
            http_list = [p.strip() for p in http_text.get('0.0', 'end-1c').split('\n') if p.strip()] 
            socks_list = [p.strip() for p in socks_text.get('0.0', 'end-1c').split('\n') if p.strip()]
            
            if save_proxy_list(http_list, socks_list):
                MessageBox.showinfo("Éxito", "Proxies guardados correctamente")
                proxy_window.destroy()
            else:
                MessageBox.showerror("Error", "No se pudieron guardar los proxies")
        
        button_container = ctk.CTkFrame(proxy_window, fg_color="transparent")
        button_container.pack(pady=15)
        
        ctk.CTkButton(button_container, text="Guardar", command=save_proxies, corner_radius=8, 
                      fg_color="#4AB8FF", hover_color="#00a2e8").pack(side=LEFT, padx=10)
        ctk.CTkButton(button_container, text="Cancelar", command=proxy_window.destroy, corner_radius=8,
                      fg_color=("gray70", "gray30")).pack(side=LEFT, padx=10)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded_bytes = d.get('downloaded_bytes')
                
                if total_bytes and downloaded_bytes:
                    percent = (downloaded_bytes / total_bytes) * 100
                    self.progress_bar["value"] = percent
                    speed = d.get('_speed_str', '')
                    eta = d.get('_eta_str', '')
                    self.status_label.configure(text=f"Descargando: {percent:.1f}% @ {speed} ETA: {eta}")
                elif '_percent_str' in d:
                    percent_str = d['_percent_str'].replace('%', '')
                    percent = float(percent_str) if percent_str.replace('.', '', 1).isdigit() else 0
                    self.progress_bar["value"] = percent
                    self.status_label.configure(text=f"Descargando: {d['_percent_str']}")

            except Exception as e:
                pass

        elif d['status'] == 'finished':
            self.status_label.configure(text="Descarga completada. Procesando...")

    def start_download(self):
        if not self.url_entry.get():
            MessageBox.showerror("Error", "Por favor ingresa una URL")
            return

        self.download_button.configure(state='disabled')
        self.progress_bar["value"] = 0
        self.status_label.configure(text="Iniciando descarga...")
        
        thread = threading.Thread(
            target=self.download_video,
            args=(
                self.url_entry.get(),
                self.output_path.get(),
                self.video_resolution.get(),
                self.video_format.get(),
                self.audio_format.get(),
                self.use_browser_cookies.get(),
                self.selected_browser.get() if self.use_browser_cookies.get() else None,
                False,
                False
            )
        )
        thread.daemon = True
        thread.start()

    def download_audio_only(self):
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
                self.audio_format.get(),
                self.use_browser_cookies.get(),
                self.selected_browser.get() if self.use_browser_cookies.get() else None,
                True,
                False
            )
        )
        thread.daemon = True
        thread.start()

    def download_video_only(self):
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
                self.use_browser_cookies.get(),
                self.selected_browser.get() if self.use_browser_cookies.get() else None,
                False,
                True
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
        MessageBox.showinfo("Acerca de", "Multi Downloader Pro\nCreado por FayDev\nVersión 3.1 - Multi-Browser")

    def popup_donate(self):
        donate_text = """¡Gracias por usar YouTube Multi Downloader Pro!

Si te gusta esta aplicación, considera hacer una donación:

PayPal: https://www.paypal.me/faycraxE

Tu apoyo ayuda a mantener y mejorar el proyecto."""
        
        MessageBox.showinfo("Donar", donate_text)

    def get_ffmpeg_path(self): 
        custom_path = self.ffmpeg_custom_path.get()
        if custom_path and os.path.exists(custom_path):
            print(f"✅ FFmpeg encontrado en la ruta personalizada: {custom_path}")
            return custom_path
        
        try:
            if sys.platform.startswith('win'):
                cmd = ['where', 'ffmpeg']
            else:
                cmd = ['which', 'ffmpeg']
                
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            path_from_path = result.stdout.strip().split('\n')[0]
            if os.path.exists(path_from_path):
                 print(f"✅ FFmpeg encontrado en el sistema PATH: {path_from_path}")
                 return path_from_path
        except:
            pass

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

        self.master.after(0, lambda: MessageBox.showerror("Error FFmpeg", 
            "ERROR: FFmpeg no se encontró en el sistema. Es necesario para conversiones.\n\n"
            "Por favor, instálalo o usa el botón 'Seleccionar .exe' para localizar tu 'ffmpeg.exe'."
        ))
        raise FileNotFoundError("FFmpeg no encontrado. Es necesario para conversiones de audio/video.")

    def download_video(self, url, output_path, video_resolution, video_format, audio_format, use_browser_cookies, selected_browser, audio_only, video_only):
        max_retries = 5
        current_try = 0
        used_proxies = []
        
        try:
            ffmpeg_path = self.get_ffmpeg_path()
        except FileNotFoundError:
            self.master.after(0, lambda: self.download_button.configure(state='normal'))
            return

        while current_try < max_retries:
            temp_dir = None
            try:
                print(f"\n=== INTENTO DE DESCARGA #{current_try + 1} ===")
                
                temp_dir = tempfile.mkdtemp()
                final_output_path = os.path.abspath(output_path)
                if not os.path.exists(final_output_path):
                    os.makedirs(final_output_path)

                platform_config = get_platform_config(url)
                user_agent = get_random_user_agent() if platform_config.get('user_agent_required', False) else None
                
                ydl_opts = {
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_hook],
                    'noplaylist': True,
                    'ffmpeg_location': ffmpeg_path,
                    'socket_timeout': 30,
                    'retries': 10,
                    'fragment_retries': 10,
                    'nocheckcertificate': True,
                    'ignoreerrors': False,
                    'no_warnings': True,
                }
                
                # COOKIES - MEJORADO PARA MÚLTIPLES NAVEGADORES
                if use_browser_cookies and selected_browser and selected_browser != "ninguno":
                    try:
                        print(f"🍪 Intentando usar cookies de {selected_browser.title()}...")
                        ydl_opts['cookiesfrombrowser'] = (selected_browser,)
                        print(f"✅ Configuración de cookies establecida para {selected_browser.title()}")
                    except Exception as cookie_error:
                        print(f"⚠️ No se pudieron configurar cookies de {selected_browser.title()}: {cookie_error}")
                        print("⚠️ Continuando sin cookies...")
                        if 'cookiesfrombrowser' in ydl_opts:
                            del ydl_opts['cookiesfrombrowser']
                
                # PROXY
                proxy = None
                if self.use_proxy.get() and platform_config.get('proxy_support', True):
                    proxy_type = self.proxy_type.get()
                    if self.auto_fetch_proxies.get() and not load_proxy_list()[0] and not load_proxy_list()[1]:
                        api_proxies = get_proxies_from_api(proxy_type)
                        if api_proxies:
                            if proxy_type == 'http':
                                save_proxy_list(api_proxies, load_proxy_list()[1])
                            else:
                                save_proxy_list(load_proxy_list()[0], api_proxies)
                    
                    proxy = get_random_proxy(proxy_type)
                    
                    if proxy:
                        if proxy in used_proxies and len(used_proxies) < 10:
                            available_proxies = load_proxy_list()[0] if proxy_type == 'http' else load_proxy_list()[1]
                            
                            new_proxy = None
                            for p in available_proxies:
                                if p not in used_proxies:
                                    new_proxy = p
                                    break
                            
                            proxy = new_proxy if new_proxy else proxy
                        
                        if proxy:
                            used_proxies.append(proxy)
                            proxy_url = f"{proxy_type}://{proxy}"
                            ydl_opts['proxy'] = proxy_url
                            print(f"🔒 Usando proxy: {proxy_url}")
                
                if user_agent:
                    ydl_opts['http_headers'] = {'User-Agent': user_agent}
                
                # CONFIGURACIÓN DE FORMATO
                if audio_only:
                    audio_codec = audio_format if audio_format != "none" else 'mp3'
                    ydl_opts.update({
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': audio_codec,
                            'preferredquality': '192',
                        }],
                    })
                    
                elif video_only:
                    video_codec = video_format if video_format != "none" else 'mp4'
                    
                    res_pref = ""
                    if video_resolution != "none" and video_resolution != "mejor":
                        res_val = video_resolution.replace('p', '')
                        res_pref = f"[height<={res_val}]"
                        
                    format_string = f"bestvideo{res_pref}/bestvideo"
                    
                    postprocessors = []
                    if video_codec != 'none' and video_codec != 'mp4':
                        postprocessors.append({'key': 'FFmpegVideoRemuxer', 'preferredformat': video_codec})
                    
                    ydl_opts.update({
                        'format': format_string,
                        'postprocessors': postprocessors,
                    })
                    
                else:
                    res_pref = ""
                    if video_resolution != "none" and video_resolution != "mejor":
                        res_val = video_resolution.replace('p', '')
                        res_pref = f"[height<={res_val}]"
                    
                    container_format = video_format if video_format != "none" else 'mp4'
                    format_string = f"bestvideo{res_pref}+bestaudio/bestvideo{res_pref}/best"
                    
                    postprocessors = []
                    if container_format != 'none' and container_format != 'mp4':
                         postprocessors.append({
                            'key': 'FFmpegVideoRemuxer', 
                            'preferredformat': container_format
                         })
                    
                    ydl_opts.update({
                        'format': format_string,
                        'postprocessors': postprocessors,
                    })
                
                print(f"Configuración final de 'format': {ydl_opts.get('format')}")
                
                # EJECUTAR DESCARGA
                self.master.after(0, lambda: self.status_label.configure(text="Conectando y obteniendo información..."))
                with YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(url, download=True)
                
                # MOVER ARCHIVOS
                moved_files_count = 0
                final_filename = None
                
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
                
                if final_filename:
                    source_path = os.path.join(temp_dir, final_filename)
                    destination_path = os.path.join(final_output_path, final_filename)
                    shutil.move(source_path, destination_path)
                    moved_files_count = 1
                else:
                    for filename in os.listdir(temp_dir):
                        source_path = os.path.join(temp_dir, filename)
                        if os.path.isfile(source_path):
                            destination_path = os.path.join(final_output_path, filename)
                            shutil.move(source_path, destination_path)
                            moved_files_count += 1
                
                print(f"✅ Se movieron {moved_files_count} archivos de {temp_dir} a {final_output_path}")

                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                
                self.master.after(0, lambda: self.status_label.configure(text=f"✓ Descarga completada"))
                self.master.after(0, lambda: self.progress_bar.config(value=100))
                self.master.after(0, lambda: self.download_button.configure(state='normal'))
                return
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Error en intento {current_try + 1}: {error_msg}")
                
                if temp_dir and os.path.exists(temp_dir):
                    try: shutil.rmtree(temp_dir)
                    except: pass
                
                # Si el error es de cookies, desactivar cookies y reintentar
                if "cookies" in error_msg.lower() or "database" in error_msg.lower():
                    print(f"⚠️ Error de cookies detectado con {selected_browser}. Desactivando cookies para próximo intento...")
                    self.use_browser_cookies.set(False)
                
                if self.auto_retry_proxy.get():
                    if "not available" in error_msg.lower() or "region" in error_msg.lower() or "geo-restricted" in error_msg.lower():
                        print("⚠️ Video no disponible. Activando proxy para reintentar...")
                        self.use_proxy.set(True)
                    elif ("proxy" in error_msg.lower() or "failed to send request" in error_msg.lower()) and self.use_proxy.get():
                        print("⚠️ Error de proxy. Desactivando proxy y reintentando...")
                        self.use_proxy.set(False)
                        used_proxies = []
                
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
                    break

def update_ytdlp():
    """Actualiza yt-dlp usando pip"""
    try:
        print("🔍 Verificando actualizaciones de yt-dlp...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], 
                      capture_output=True, check=True)
        print("✅ yt-dlp actualizado correctamente")
    except Exception as e:
        print(f"⚠️ No se pudo actualizar yt-dlp: {e}")

if __name__ == '__main__':
    threading.Thread(target=update_ytdlp, daemon=True).start()
    
    root = ctk.CTk()
    app = MultiDownloaderGUI(root)
    root.mainloop()