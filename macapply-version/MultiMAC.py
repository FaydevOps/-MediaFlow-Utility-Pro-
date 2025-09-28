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
from yt_dlp.utils import DownloadError

class MultiDownloaderGUI:
    def __init__(self, master):
        self.master = master
        master.title("Multi Downloader Pro")
        
        # Configurar ventana principal
        master.geometry("900x750")
        master.configure(bg='#1a1a1a')
        master.resizable(False, False)
        
        # Variables para menús desplegables
        self.video_resolution = StringVar(value="mejor")
        self.video_format = StringVar(value="mp4")
        self.audio_format = StringVar(value="mp3")
        self.output_path = StringVar(value=os.path.expanduser("~/Downloads"))

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

        # Menús desplegables
        options_frame = Frame(main_frame, bg='#2d2d2d')
        options_frame.pack(pady=10)

        # Resolución
        resolution_frame = Frame(options_frame, bg='#2d2d2d')
        resolution_frame.pack(side=LEFT, padx=10)
        Label(resolution_frame, text="Resolución", bg='#2d2d2d', fg='white').pack()
        resolutions = ["mejor", "2160p", "1440p", "1080p", "720p", "480p", "360p"]
        OptionMenu(resolution_frame, self.video_resolution, *resolutions).pack()

        # Formato de video
        video_format_frame = Frame(options_frame, bg='#2d2d2d')
        video_format_frame.pack(side=LEFT, padx=10)
        Label(video_format_frame, text="Formato Video", bg='#2d2d2d', fg='white').pack()
        video_formats = ["mp4", "webm", "mkv", "best"]
        OptionMenu(video_format_frame, self.video_format, *video_formats).pack()

        # Formato de audio
        audio_format_frame = Frame(options_frame, bg='#2d2d2d')
        audio_format_frame.pack(side=LEFT, padx=10)
        Label(audio_format_frame, text="Formato Audio", bg='#2d2d2d', fg='white').pack()
        audio_formats = ["mp3", "wav", "m4a", "best"]
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
        input_file = self.url_entry.get()
        output_dir = self.output_path.get()
        selected_resolution = self.video_resolution.get()
        selected_video_format = self.video_format.get()
        selected_audio_format = self.audio_format.get()

        if not input_file:
            MessageBox.showerror("Error", "Por favor ingresa una URL")
            return

        # Desactivar botón durante la descarga
        self.download_button.config(state='disabled')
        
        # Reiniciar barra de progreso
        self.progress_bar["value"] = 0
        self.status_label.config(text="Iniciando descarga...")
        
        # Iniciar descarga en un hilo separado
        thread = threading.Thread(
            target=self.download_video,
            args=(
                input_file,
                output_dir,
                selected_resolution,
                selected_video_format,
                selected_audio_format,
                False,  # audio_only
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
                True,   # audio_only
                False   # video_only
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
                False,  # audio_only
                True    # video_only
            )
        )
        thread.daemon = True
        thread.start()

    def get_ffmpeg_path(self):
        """Busca la ruta de ffmpeg en el sistema"""
        try:
            # Intenta encontrar ffmpeg en PATH
            if sys.platform == "win32":
                result = subprocess.run(['where', 'ffmpeg'], 
                                      capture_output=True, 
                                      text=True, 
                                      check=True)
            else:
                result = subprocess.run(['which', 'ffmpeg'], 
                                      capture_output=True, 
                                      text=True, 
                                      check=True)
            return result.stdout.strip().split('\n')[0]
        except:
            # Rutas comunes donde podría estar ffmpeg
            username = os.getenv('USERNAME') or os.getenv('USER')
            common_paths = [
                r"C:\ffmpeg\bin\ffmpeg.exe",
                r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
                r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
                os.path.join(os.getenv('LOCALAPPDATA', ''), 'Programs', 'ffmpeg', 'bin', 'ffmpeg.exe'),
                f"C:\\Users\\{username}\\AppData\\Local\\Programs\\ffmpeg\\bin\\ffmpeg.exe"
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    return path
                    
            # Si no se encuentra, usar el del sistema PATH
            return "ffmpeg"

    def download_video(self, url, output_path, video_resolution, video_format, audio_format, audio_only, video_only):
        try:
            # Sanitize output path
            output_path = os.path.abspath(output_path)
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            # Obtener ruta de ffmpeg
            ffmpeg_path = self.get_ffmpeg_path()
            
            # CONFIGURACIÓN MÁS SIMPLE Y ROBUSTA
            ydl_opts = {
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'ffmpeg_location': ffmpeg_path,
                'format': 'best'  # Formato más simple y compatible
            }

            # Configuración específica para audio
            if audio_only:
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': audio_format if audio_format != 'best' else 'mp3',
                    }],
                })
            # Para video, mantener la configuración simple

            # Primero verificar que el video existe
            try:
                with YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    video_title = info.get('title', 'video')
                    # CORRECCIÓN: Usar método seguro para actualizar la UI
                    self.master.after(0, self.update_status, f"Encontrado: {video_title}")
            except Exception as info_error:
                # CORRECCIÓN: Pasar el error como argumento
                self.master.after(0, self.show_error, f"No se pudo obtener información del video: {str(info_error)}")
                return

            # Intentar descarga con configuración simple
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                self.master.after(0, self.update_status, "Descarga completada correctamente")
                self.master.after(0, self.update_progress, 100)
                
            except DownloadError as e:
                error_msg = str(e)
                if "Requested format is not available" in error_msg:
                    # Intentar con formato ultra simple
                    try:
                        self.master.after(0, self.update_status, "Intentando formato ultra simple...")
                        
                        simple_ydl_opts = {
                            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                            'progress_hooks': [self.progress_hook],
                            'format': 'best[height<=720]'  # Limitar a 720p para mayor compatibilidad
                        }
                        
                        if audio_only:
                            simple_ydl_opts['format'] = 'bestaudio/best'
                            simple_ydl_opts['postprocessors'] = [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                            }]
                        
                        with YoutubeDL(simple_ydl_opts) as ydl:
                            ydl.download([url])
                        
                        self.master.after(0, self.update_status, "Descarga completada con formato simple")
                        
                    except Exception as retry_error:
                        self.master.after(0, self.show_error, f"No se pudo descargar el video: {str(retry_error)}")
                else:
                    self.master.after(0, self.show_error, f"Error al descargar: {error_msg}")
        
        except Exception as error:
            error_msg = str(error)
            self.master.after(0, self.show_error, error_msg)
        
        finally:
            self.master.after(0, self.enable_download_button)

    # NUEVOS MÉTODOS PARA MANEJAR LA UI DE FORMA SEGURA
    def update_status(self, message):
        """Actualiza el estado de forma segura"""
        self.status_label.config(text=message)

    def update_progress(self, value):
        """Actualiza la barra de progreso de forma segura"""
        self.progress_bar["value"] = value

    def show_error(self, error_message):
        """Muestra error de forma segura"""
        self.status_label.config(text=f"Error: {error_message}")
        MessageBox.showerror("Error", error_message)

    def enable_download_button(self):
        """Habilita el botón de descarga de forma segura"""
        self.download_button.config(state='normal')

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
        donate_text = """¡Gracias por usar YouTube Multi Downloader Pro!

      Si te gusta esta aplicación, considera hacer una donación:

      PayPal: https://www.paypal.me/faycraxE

      Tu apoyo ayuda a mantener y mejorar el proyecto."""
        
        MessageBox.showinfo("Donar", donate_text)

def ensure_latest_ytdlp():
    """Actualiza yt-dlp si es necesario"""
    try:
        # Para Windows
        if sys.platform == "win32":
            ytdlp_path = os.path.join(os.getcwd(), "yt-dlp.exe")
            ytdlp_url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
        else:
            # Para Linux/Mac
            ytdlp_path = os.path.join(os.getcwd(), "yt-dlp")
            ytdlp_url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
        
        print("Verificando yt-dlp...")
        # Solo descargar si no existe
        if not os.path.exists(ytdlp_path):
            print("Descargando yt-dlp...")
            urllib.request.urlretrieve(ytdlp_url, ytdlp_path)
            if sys.platform != "win32":
                os.chmod(ytdlp_path, 0o755)  # Dar permisos de ejecución
            print("yt-dlp descargado correctamente")
        else:
            print("yt-dlp ya existe, omitiendo descarga")
    except Exception as e:
        print(f"Error actualizando yt-dlp: {e}")

if __name__ == '__main__':
    ensure_latest_ytdlp()
    root = Tk()
    app = MultiDownloaderGUI(root)
    root.mainloop()