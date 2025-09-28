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
            cookies = browser_func(domain_name=domain)
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
                        return False, str(e)
        except Exception as e:
            return False, str(e)
    return True, None

def get_platform_config(url):
    """Obtiene la configuración específica para cada plataforma"""
    domain = extract_domain(url)[1:]  # Eliminar el punto inicial
    
    # Verificar disponibilidad para YouTube
    if 'youtube.com' in domain or 'youtu.be' in domain:
        available, error_msg = check_video_availability(url)
        if not available:
            raise Exception(f"Error de YouTube: {error_msg}")
    
    # Configuraciones específicas por plataforma
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
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            proxies_text = response.text.strip()
            if proxies_text:
                proxies = [p.strip() for p in proxies_text.split('\n') if p.strip()]
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
    
    # Si no hay proxies locales, obtener de la API
    print("📡 No hay proxies locales, obteniendo de la API...")
    api_proxies = get_proxies_from_api(proxy_type)
    
    if api_proxies:
        # Guardar los nuevos proxies para uso futuro
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
            proxies = {'http': f'socks5://{proxy}', 'https': f'socks5://{proxy}'}
        
        response = requests.get(test_url, proxies=proxies, timeout=10)
        return response.status_code == 200
    except:
        return False

class MultiDownloaderGUI:
    def __init__(self, master):
        self.master = master
        master.title("Multi Downloader Pro")
        
        # Configurar ventana principal
        master.geometry("900x800")
        master.configure(bg='#1a1a1a')
        master.resizable(False, False)
        
        # Variables para menús desplegables
        self.video_resolution = StringVar(value="none")
        self.video_format = StringVar(value="none")
        self.audio_format = StringVar(value="none")
        self.output_path = StringVar(value=os.path.expanduser("~/Downloads"))
        # AÑADIDO: Variable para la ruta personalizada de FFmpeg
        self.ffmpeg_custom_path = StringVar(value="")
        self.use_proxy = BooleanVar(value=False)
        self.proxy_type = StringVar(value="http")
        self.auto_retry_proxy = BooleanVar(value=True)
        self.auto_fetch_proxies = BooleanVar(value=True)

        try:
            # Cargar logo
            logo_path = os.path.join(os.path.dirname(__file__), "assets/youtubemp3.png")
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((150, 150), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            
            logo_label = Label(master, image=self.logo_photo, bg='#1a1a1a')
            logo_label.pack(pady=10)
        except Exception as e:
            print(f"Error al cargar el logo: {e}")

        # Marco principal
        main_frame = Frame(master, bg='#2d2d2d')
        main_frame.pack(padx=20, pady=10, fill=BOTH, expand=True)

        # URL Entry
        Label(main_frame, text="URL del Video:", bg='#2d2d2d', fg='white', 
              font=('Segoe UI', 12)).pack(pady=5)
        self.url_entry = Entry(main_frame, width=50, font=('Segoe UI', 10))
        self.url_entry.pack(pady=5)

        # Directorio de salida
        dir_frame = Frame(main_frame, bg='#2d2d2d')
        dir_frame.pack(pady=10)
        Label(dir_frame, text="Carpeta de Destino:", bg='#2d2d2d', fg='white', 
              font=('Segoe UI', 10)).pack(side=LEFT)
        Entry(dir_frame, textvariable=self.output_path, width=40).pack(side=LEFT, padx=5)
        Button(dir_frame, text="Examinar", command=self.browse_directory).pack(side=LEFT)
        
        # AÑADIDO: Ruta FFmpeg (Opcional)
        ffmpeg_frame = Frame(main_frame, bg='#2d2d2d')
        ffmpeg_frame.pack(pady=5)
        Label(ffmpeg_frame, text="Ruta FFmpeg (Opcional):", bg='#2d2d2d', fg='white', 
              font=('Segoe UI', 10)).pack(side=LEFT)
        Entry(ffmpeg_frame, textvariable=self.ffmpeg_custom_path, width=40, state='readonly').pack(side=LEFT, padx=5)
        Button(ffmpeg_frame, text="Seleccionar .exe", command=self.browse_ffmpeg_path).pack(side=LEFT)

        # Configuración de Proxy
        proxy_frame = Frame(main_frame, bg='#2d2d2d')
        proxy_frame.pack(pady=10)
        
        Label(proxy_frame, text="Configuración Proxy:", bg='#2d2d2d', fg='white', 
              font=('Segoe UI', 10)).grid(row=0, column=0, sticky=W, pady=5)
        
        Checkbutton(proxy_frame, text="Usar Proxy", variable=self.use_proxy, 
                   bg='#2d2d2d', fg='white', selectcolor='#1a1a1a').grid(row=0, column=1, padx=10)
        
        Label(proxy_frame, text="Tipo:", bg='#2d2d2d', fg='white').grid(row=1, column=0, sticky=W)
        proxy_types = ["http", "socks5"]
        OptionMenu(proxy_frame, self.proxy_type, *proxy_types).grid(row=1, column=1, padx=5)
        
        Checkbutton(proxy_frame, text="Auto-reintento", variable=self.auto_retry_proxy,
                   bg='#2d2d2d', fg='white', selectcolor='#1a1a1a').grid(row=1, column=2, padx=10)
        
        Checkbutton(proxy_frame, text="Auto-obtener proxies", variable=self.auto_fetch_proxies,
                   bg='#2d2d2d', fg='white', selectcolor='#1a1a1a').grid(row=1, column=3, padx=10)
        
        Button(proxy_frame, text="Obtener Proxies Ahora", command=self.fetch_proxies_now).grid(row=2, column=0, padx=5, pady=5)
        Button(proxy_frame, text="Gestionar Proxies", command=self.manage_proxies).grid(row=2, column=1, padx=5, pady=5)
        Button(proxy_frame, text="Testear Proxies", command=self.test_proxies).grid(row=2, column=2, padx=5, pady=5)

        # Menús desplegables
        options_frame = Frame(main_frame, bg='#2d2d2d')
        options_frame.pack(pady=10)

        # Resolución
        resolution_frame = Frame(options_frame, bg='#2d2d2d')
        resolution_frame.pack(side=LEFT, padx=10)
        Label(resolution_frame, text="Resolución", bg='#2d2d2d', fg='white').pack()
        resolutions = ["none", "mejor", "2160p", "1440p", "1080p", "720p", "480p", "360p"]
        OptionMenu(resolution_frame, self.video_resolution, *resolutions).pack()

        # Formato de video
        video_format_frame = Frame(options_frame, bg='#2d2d2d')
        video_format_frame.pack(side=LEFT, padx=10)
        Label(video_format_frame, text="Formato Video", bg='#2d2d2d', fg='white').pack()
        video_formats = ["none", "mp4", "webm", "mkv"]
        OptionMenu(video_format_frame, self.video_format, *video_formats).pack()

        # Formato de audio
        audio_format_frame = Frame(options_frame, bg='#2d2d2d')
        audio_format_frame.pack(side=LEFT, padx=10)
        Label(audio_format_frame, text="Formato Audio", bg='#2d2d2d', fg='white').pack()
        audio_formats = ["none", "mp3", "wav", "m4a"]
        OptionMenu(audio_format_frame, self.audio_format, *audio_formats).pack()

        # Botones
        buttons_frame = Frame(main_frame, bg='#2d2d2d')
        buttons_frame.pack(pady=20)

        self.download_button = Button(buttons_frame, text="Descargar", command=self.start_download)
        self.download_button.pack(side=LEFT, padx=5)
        Button(buttons_frame, text="Solo Audio", command=self.download_audio_only).pack(side=LEFT, padx=5)
        Button(buttons_frame, text="Solo Video", command=self.download_video_only).pack(side=LEFT, padx=5)

        # Barra de progreso
        self.progress_bar = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.progress_bar.pack(pady=10)

        # Etiqueta de estado
        self.status_label = Label(main_frame, text="Listo para descargar", bg='#2d2d2d', fg='white')
        self.status_label.pack()

        # Crear menú
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
            self.status_label.config(text="Obteniendo proxies de la API...")
            http_proxies = get_proxies_from_api('http')
            socks5_proxies = get_proxies_from_api('socks5')
            
            if http_proxies or socks5_proxies:
                save_proxy_list(http_proxies, socks5_proxies)
                total = len(http_proxies) + len(socks5_proxies)
                self.status_label.config(text=f"✅ Obtenidos {total} proxies")
                MessageBox.showinfo("Éxito", f"Se obtuvieron {total} proxies de la API")
            else:
                self.status_label.config(text="❌ Error obteniendo proxies")
                MessageBox.showerror("Error", "No se pudieron obtener proxies de la API")
        
        threading.Thread(target=fetch_thread, daemon=True).start()

    def test_proxies(self):
        """Testea los proxies disponibles"""
        def test_thread():
            self.status_label.config(text="Testeando proxies...")
            http_proxies, socks5_proxies = load_proxy_list()
            working_http = []
            working_socks5 = []
            
            # Testear proxies HTTP
            for proxy in http_proxies[:10]:  # Testear solo los primeros 10
                if test_proxy(proxy, 'http'):
                    working_http.append(proxy)
            
            # Testear proxies SOCKS5
            for proxy in socks5_proxies[:10]:
                if test_proxy(proxy, 'socks5'):
                    working_socks5.append(proxy)
            
            save_proxy_list(working_http, working_socks5)
            total_working = len(working_http) + len(working_socks5)
            self.status_label.config(text=f"✅ {total_working} proxies funcionando")
            MessageBox.showinfo("Resultados", 
                              f"Proxies funcionando:\nHTTP: {len(working_http)}\nSOCKS5: {len(working_socks5)}")
        
        threading.Thread(target=test_thread, daemon=True).start()

    def manage_proxies(self):
        """Abre el diálogo para gestionar proxies"""
        proxy_window = Toplevel(self.master)
        proxy_window.title("Gestión de Proxies")
        proxy_window.geometry("500x400")
        proxy_window.configure(bg='#2d2d2d')
        
        Label(proxy_window, text="Configuración de Proxies", bg='#2d2d2d', fg='white', 
              font=('Segoe UI', 14)).pack(pady=10)
        
        # Frame para proxies HTTP
        http_frame = Frame(proxy_window, bg='#2d2d2d')
        http_frame.pack(fill=X, padx=20, pady=5)
        Label(http_frame, text="Proxies HTTP (uno por línea):", bg='#2d2d2d', fg='white').pack(anchor=W)
        http_text = Text(http_frame, height=4, width=50)
        http_text.pack(fill=X, pady=5)
        
        # Frame para proxies SOCKS5
        socks_frame = Frame(proxy_window, bg='#2d2d2d')
        socks_frame.pack(fill=X, padx=20, pady=5)
        Label(socks_frame, text="Proxies SOCKS5 (uno por línea):", bg='#2d2d2d', fg='white').pack(anchor=W)
        socks_text = Text(socks_frame, height=4, width=50)
        socks_text.pack(fill=X, pady=5)
        
        # Cargar proxies existentes
        http_proxies, socks5_proxies = load_proxy_list()
        http_text.insert('1.0', '\n'.join(http_proxies))
        socks_text.insert('1.0', '\n'.join(socks5_proxies))
        
        def save_proxies():
            http_list = [p.strip() for p in http_text.get('1.0', END).split('\n') if p.strip()]
            socks_list = [p.strip() for p in socks_text.get('1.0', END).split('\n') if p.strip()]
            
            if save_proxy_list(http_list, socks_list):
                MessageBox.showinfo("Éxito", "Proxies guardados correctamente")
                proxy_window.destroy()
            else:
                MessageBox.showerror("Error", "No se pudieron guardar los proxies")
        
        Button(proxy_window, text="Guardar", command=save_proxies).pack(pady=10)
        Button(proxy_window, text="Cancelar", command=proxy_window.destroy).pack()

    def progress_hook(self, d):
        """Actualiza la barra de progreso durante la descarga"""
        if d['status'] == 'downloading':
            try:
                percent = d['_percent_str']
                percent = float(percent.replace('%', ''))
                self.progress_bar["value"] = percent
                self.status_label.config(text=f"Descargando: {percent:.1f}%")
            except:
                pass
        elif d['status'] == 'finished':
            self.status_label.config(text="Descarga completada. Procesando...")

    def start_download(self):
        """Inicia el proceso de descarga"""
        if not self.url_entry.get():
            MessageBox.showerror("Error", "Por favor ingresa una URL")
            return

        # Desactivar botón durante la descarga
        self.download_button.config(state='disabled')
        
        # Reiniciar barra de progreso
        self.progress_bar["value"] = 0
        self.status_label.config(text="Iniciando descarga...")
        
        # Verificar si es solo audio
        is_audio_only = self.video_format.get() == "none" and self.audio_format.get() != "none"
        
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
                is_audio_only,  # audio_only
                False   # video_only
            )
        )
        thread.daemon = True
        thread.start()

    def download_audio_only(self):
        """Descarga solo el audio"""
        self.download_button.config(state='disabled')
        url = self.url_entry.get()
        if not url:
            MessageBox.showerror("Error", "Por favor ingresa una URL")
            return
        
        thread = threading.Thread(
            target=self.download_video,
            args=(
                url,
                self.output_path.get(),
                "none",
                "none",
                self.audio_format.get(),
                True,  # use_browser_cookies
                True,  # audio_only
                False  # video_only
            )
        )
        thread.daemon = True
        thread.start()

    def download_video_only(self):
        """Descarga solo el video"""
        self.download_button.config(state='disabled')
        url = self.url_entry.get()
        if not url:
            MessageBox.showerror("Error", "Por favor ingresa una URL")
            return
        
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
        
        # 1. Prioridad: Ruta personalizada por el usuario (la que seleccionó en la GUI)
        custom_path = self.ffmpeg_custom_path.get()
        if custom_path and os.path.exists(custom_path):
            print(f"✅ FFmpeg encontrado en la ruta personalizada: {custom_path}")
            return custom_path
        
        # 2. Segundo intento: Verificar si ffmpeg está en el PATH del entorno de ejecución
        try:
            # Usar 'check=True' para lanzar un FileNotFoundError o CalledProcessError si el comando falla
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True)
            if result.returncode == 0:
                print("✅ FFmpeg encontrado en el sistema PATH.")
                return 'ffmpeg'  # Usar desde PATH
        except subprocess.CalledProcessError:
            # Comando encontrado, pero falló (ej. error interno). Continuar búsqueda.
            print("⚠ 'ffmpeg -version' encontró un error, buscando ruta absoluta.")
            pass
        except FileNotFoundError:
            # Comando no encontrado en el PATH. Continuar búsqueda.
            print("❌ 'ffmpeg' no encontrado en el PATH del entorno, buscando en rutas comunes.")
            pass

        # 3. Rutas comunes en Windows (incluye la portable y Winget en AppData)
        local_appdata_path = os.path.expandvars('%LOCALAPPDATA%')
        
        common_paths = [
            # Instalación portable junto al script (Máxima portabilidad)
            os.path.join(os.path.dirname(__file__), "ffmpeg", "bin", "ffmpeg.exe"),
            # Rutas típicas de desarrollador y Winget en AppData
            os.path.join(local_appdata_path, 'Programs', 'ffmpeg', 'bin', 'ffmpeg.exe'),
            # Rutas de instalación tradicionales
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe", 
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        ]
        
        # Búsqueda simple de las rutas definidas
        for path in common_paths:
            if os.path.exists(path):
                print(f"✅ FFmpeg encontrado en ruta común: {path}")
                return path

        # 4. Fallo total: Mostrar el error y pedir la ruta manual
        self.master.after(0, lambda: MessageBox.showerror("Error FFmpeg", 
            "ERROR: FFmpeg no se encontró en el sistema. Es necesario para conversiones.\n\n"
            "Por favor, instálalo o usa el botón 'Seleccionar .exe' para localizar tu 'ffmpeg.exe'."
        ))
        raise FileNotFoundError("FFmpeg no encontrado. Es necesario para conversiones de audio.")

    def save_cookies_to_file(self, cookies):
        """Guarda cookies en un archivo temporal para yt-dlp"""
        if not cookies:
            return None
            
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8')
        try:
            # Formato Netscape para cookies
            temp_file.write("# Netscape HTTP Cookie File\n")
            for cookie in cookies:
                # Dominio, flag, path, secure, expiration, name, value
                domain = cookie.domain.lstrip('.')
                secure = "TRUE" if cookie.secure else "FALSE"
                expiration = str(int(cookie.expires)) if cookie.expires else "0"
                temp_file.write(f"{domain}\tTRUE\t{cookie.path}\t{secure}\t{expiration}\t{cookie.name}\t{cookie.value}\n")
            temp_file.close()
            return temp_file.name
        except Exception as e:
            print(f"Error guardando cookies: {e}")
            return None

    def download_video(self, url, output_path, video_resolution, video_format, audio_format, use_browser_cookies, audio_only, video_only):
        max_retries = 5
        current_try = 0
        used_proxies = []
        
        while current_try < max_retries:
            try:
                print(f"\n=== INTENTO DE DESCARGA #{current_try + 1} ===")
                
                # Sanitizar ruta de salida
                output_path = os.path.abspath(output_path)
                if not os.path.exists(output_path):
                    os.makedirs(output_path)

                # Obtener ruta de ffmpeg
                ffmpeg_path = self.get_ffmpeg_path()
                
                # Obtener configuración de plataforma
                platform_config = get_platform_config(url)
                print(f"Plataforma detectada: {extract_domain(url)[1:]}")
                
                # Obtener cookies y user agent
                cookies = get_browser_cookies(url) if use_browser_cookies and platform_config['cookies_required'] else None
                user_agent = get_random_user_agent() if platform_config['user_agent_required'] else None
                
                # CONFIGURACIÓN BASE
                ydl_opts = {
                    'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_hook],
                    'noplaylist': True,
                    # Usa la ruta de FFmpeg encontrada
                    'ffmpeg_location': ffmpeg_path,
                    'socket_timeout': 30,
                    'retries': 10,
                    'fragment_retries': 10,
                    'nocheckcertificate': True,
                    'ignoreerrors': True,
                    'no_warnings': True,
                }
                
                # CONFIGURAR PROXY SI ESTÁ HABILITADO
                proxy = None
                if self.use_proxy.get() and platform_config.get('proxy_support', True):
                    proxy_type = self.proxy_type.get()
                    proxy = get_random_proxy(proxy_type)
                    
                    if proxy:
                        # Evitar usar el mismo proxy dos veces
                        if proxy in used_proxies:
                            available_proxies = []
                            for _ in range(5):
                                new_proxy = get_random_proxy(proxy_type)
                                if new_proxy and new_proxy not in used_proxies:
                                    proxy = new_proxy
                                    break
                        
                        if proxy:
                            used_proxies.append(proxy)
                            if proxy_type == 'http':
                                ydl_opts['http_proxy'] = proxy
                            elif proxy_type == 'socks5':
                                ydl_opts['socks_proxy'] = proxy
                            print(f"🔒 Usando proxy: {proxy}")
                
                # Configurar headers
                if user_agent:
                    ydl_opts['http_headers'] = {'User-Agent': user_agent}
                
                # Configurar cookies
                if cookies:
                    cookie_file = self.save_cookies_to_file(cookies)
                    if cookie_file:
                        ydl_opts['cookiefile'] = cookie_file
                
                # CONFIGURACIÓN DE FORMATO
                if audio_only:
                    print("=== MODO: SOLO AUDIO ===")
                    ydl_opts.update({
                        'format': 'bestaudio/best',
                        'extractaudio': True,
                        'audioformat': audio_format if audio_format != "none" else 'mp3',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': audio_format if audio_format != "none" else 'mp3',
                            'preferredquality': '192',
                        }],
                        'keepvideo': False,
                    })
                    
                elif video_only:
                    print("=== MODO: SOLO VIDEO ===")
                    ydl_opts.update({
                        'format': 'bestvideo/best',
                    })
                    
                else:
                    print("=== MODO: VIDEO + AUDIO ===")
                    ydl_opts.update({
                        'format': 'best[height<=1080]/best[height<=720]/best',
                    })
                
                print(f"Configuración: {ydl_opts.get('format')}")
                if proxy:
                    print(f"Proxy: {proxy}")
                
                # EJECUTAR DESCARGA
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # Éxito
                if 'cookiefile' in ydl_opts and os.path.exists(ydl_opts['cookiefile']):
                    try:
                        os.unlink(ydl_opts['cookiefile'])
                    except:
                        pass
                
                self.master.after(0, lambda: self.status_label.config(text=f"✓ Descarga completada"))
                self.master.after(0, lambda: self.progress_bar.config(value=100))
                self.master.after(0, lambda: self.download_button.config(state='normal'))
                return
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Error en intento {current_try + 1}: {error_msg}")
                
                # Estrategia de recuperación inteligente
                if "not available" in error_msg.lower() or "region" in error_msg.lower():
                    print("⚠ Video no disponible en la región. Activando proxy...")
                    self.use_proxy.set(True)
                    
                elif "proxy" in error_msg.lower():
                    print("⚠ Error de proxy. Intentando sin proxy...")
                    self.use_proxy.set(False)
                    used_proxies = []
                
                current_try += 1
                if current_try < max_retries:
                    retry_delay = 2 + (current_try * 2)
                    print(f"🔄 Reintentando en {retry_delay} segundos...")
                    time.sleep(retry_delay)
                else:
                    final_error = f"Error después de {max_retries} intentos"
                    if "not available" in error_msg.lower():
                        final_error += "\nEl video no está disponible en tu región."
                    
                    self.master.after(0, lambda: self.status_label.config(text=f"❌ Error: {final_error}"))
                    self.master.after(0, lambda: MessageBox.showerror("Error", final_error))
                    self.master.after(0, lambda: self.download_button.config(state='normal'))

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
        if os.path.exists(ytdlp_path):
            try:
                result = subprocess.run([ytdlp_path, '--version'], capture_output=True, text=True, check=True)
                current_version = result.stdout.strip()
                print(f"Versión actual: {current_version}")
                
                update_result = subprocess.run([ytdlp_path, '-U'], capture_output=True, text=True)
                
                if "yt-dlp is up to date" in update_result.stdout:
                    needs_update = False
                    print("yt-dlp está actualizado")
            except Exception as e:
                print(f"Error verificando versión: {e}")
        
        if needs_update:
            print("Descargando última versión de yt-dlp...")
            user_agents = [get_random_user_agent() for _ in range(3)]
            success = False
            
            for user_agent in user_agents:
                try:
                    headers = {'User-Agent': user_agent}
                    req = urllib.request.Request(ytdlp_url, headers=headers)
                    with urllib.request.urlopen(req) as response, open(ytdlp_path, 'wb') as out_file:
                        out_file.write(response.read())
                    success = True
                    print("yt-dlp actualizado correctamente")
                    break
                except Exception as e:
                    print(f"Intento fallido con User-Agent: {str(e)}")
                    continue
            
            if not success:
                raise Exception("No se pudo actualizar yt-dlp después de múltiples intentos")
        
        subprocess.run([ytdlp_path, '--version'], check=True, capture_output=True)
        
    except Exception as e:
        print(f"Error en la actualización de yt-dlp: {e}")
        print("Continuando con la versión existente...")
        
    config_path = os.path.join(os.path.expanduser("~"), "yt-dlp.conf")
    if not os.path.exists(config_path):
        try:
            with open(config_path, 'w') as f:
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

if __name__ == '__main__':
    ensure_latest_ytdlp()
    root = Tk()
    app = MultiDownloaderGUI(root)
    root.mainloop()