import os
import sys
import webbrowser
import threading
import subprocess
import time
import ctypes
import platform
from http.client import HTTPConnection
import socket
import signal
import tkinter as tk
from tkinter import ttk, messagebox

class FinasisDesktopApp:
    def __init__(self, root):
        self.root = root
        self.server_process = None
        self.server_url = "http://127.0.0.1:8000"
        self.is_server_running = False
        
        # Window setup
        self.root.title("FinAsis - Finansal Yönetim Sistemi")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        self.setup_ui()
        
        # Check if the server is already running
        self.check_server()
        
    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo and title
        logo_frame = ttk.Frame(main_frame)
        logo_frame.pack(pady=20)
        
        title_label = ttk.Label(logo_frame, text="FinAsis", font=("Arial", 24, "bold"))
        title_label.pack()
        
        subtitle_label = ttk.Label(logo_frame, text="Finansal Yönetim Sistemi", font=("Arial", 14))
        subtitle_label.pack()
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Sunucu Durumu", padding="10")
        status_frame.pack(fill=tk.X, pady=20)
        
        self.status_label = ttk.Label(status_frame, text="Kontrol ediliyor...", font=("Arial", 12))
        self.status_label.pack(pady=10)
        
        self.progress = ttk.Progressbar(status_frame, orient=tk.HORIZONTAL, length=300, mode='indeterminate')
        self.progress.pack(pady=10)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        # Start server button
        self.start_button = ttk.Button(buttons_frame, text="Sunucuyu Başlat", command=self.start_server)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)
        
        # Stop server button
        self.stop_button = ttk.Button(buttons_frame, text="Sunucuyu Durdur", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)
        
        # Open browser button
        self.browser_button = ttk.Button(buttons_frame, text="Tarayıcıda Aç", command=self.open_browser, state=tk.DISABLED)
        self.browser_button.grid(row=0, column=2, padx=10, pady=10)
        
        # Footer
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        version_label = ttk.Label(footer_frame, text="Versiyon 1.0.0")
        version_label.pack(side=tk.LEFT)
        
        copyright_label = ttk.Label(footer_frame, text="© 2023-2025 FinAsis")
        copyright_label.pack(side=tk.RIGHT)
        
    def check_server(self):
        """Check if Django server is already running"""
        self.progress.start()
        self.status_label.config(text="Sunucu durumu kontrol ediliyor...")
        
        # Run in a separate thread to avoid blocking the UI
        threading.Thread(target=self._check_server_thread, daemon=True).start()
    
    def _check_server_thread(self):
        """Thread function to check server status"""
        try:
            conn = HTTPConnection("127.0.0.1", 8000, timeout=1)
            conn.request("HEAD", "/")
            response = conn.getresponse()
            
            if response.status < 400:
                self.is_server_running = True
                self.update_ui_server_running()
            else:
                self.is_server_running = False
                self.update_ui_server_stopped()
                
        except (socket.error, socket.timeout) as e:
            self.is_server_running = False
            self.update_ui_server_stopped()
        finally:
            self.progress.stop()
    
    def update_ui_server_running(self):
        """Update UI when server is running"""
        self.root.after(0, lambda: self.status_label.config(text="Sunucu çalışıyor"))
        self.root.after(0, lambda: self.start_button.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.stop_button.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.browser_button.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.progress.stop())
    
    def update_ui_server_stopped(self):
        """Update UI when server is stopped"""
        self.root.after(0, lambda: self.status_label.config(text="Sunucu çalışmıyor"))
        self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.browser_button.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.progress.stop())
    
    def start_server(self):
        """Start the Django development server"""
        if self.is_server_running:
            messagebox.showinfo("Sunucu Durumu", "Sunucu zaten çalışıyor.")
            return
        
        self.progress.start()
        self.status_label.config(text="Sunucu başlatılıyor...")
        
        # Create a function to run the server in a separate thread
        def run_server():
            try:
                # For Windows, create a new process group
                if platform.system() == "Windows":
                    self.server_process = subprocess.Popen(
                        ["python", "manage.py", "runserver"],
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True,
                    )
                else:  # For Unix-like systems
                    self.server_process = subprocess.Popen(
                        ["python", "manage.py", "runserver"],
                        preexec_fn=os.setsid,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True,
                    )
                
                # Wait for the server to start
                for i in range(30):  # Try for 30 seconds
                    time.sleep(1)
                    try:
                        conn = HTTPConnection("127.0.0.1", 8000, timeout=1)
                        conn.request("HEAD", "/")
                        response = conn.getresponse()
                        
                        if response.status < 400:
                            self.is_server_running = True
                            self.update_ui_server_running()
                            return
                    except (socket.error, socket.timeout):
                        pass
                
                # If we get here, the server didn't start
                self.is_server_running = False
                self.update_ui_server_stopped()
                messagebox.showerror("Hata", "Sunucu başlatılamadı.")
                
            except Exception as e:
                self.is_server_running = False
                self.update_ui_server_stopped()
                messagebox.showerror("Hata", f"Sunucu başlatılırken hata oluştu: {str(e)}")
        
        # Start the server in a separate thread
        threading.Thread(target=run_server, daemon=True).start()
    
    def stop_server(self):
        """Stop the Django development server"""
        if not self.is_server_running:
            messagebox.showinfo("Sunucu Durumu", "Sunucu zaten çalışmıyor.")
            return
        
        self.progress.start()
        self.status_label.config(text="Sunucu durduruluyor...")
        
        try:
            if self.server_process:
                # Send signal to terminate the process
                if platform.system() == "Windows":
                    # On Windows, use CTRL+C signal
                    self.server_process.send_signal(signal.CTRL_C_EVENT)
                else:
                    # On Unix-like systems, use SIGTERM
                    os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
                
                # Wait for process to terminate
                self.server_process.wait(timeout=5)
                self.server_process = None
            
            # Additional check to verify server is stopped
            try:
                conn = HTTPConnection("127.0.0.1", 8000, timeout=1)
                conn.request("HEAD", "/")
                response = conn.getresponse()
                
                # If we can still connect, the server is still running
                self.is_server_running = True
                messagebox.showerror("Hata", "Sunucu durdurulamadı.")
            except (socket.error, socket.timeout):
                self.is_server_running = False
                self.update_ui_server_stopped()
                
        except Exception as e:
            messagebox.showerror("Hata", f"Sunucu durdurulurken hata oluştu: {str(e)}")
        
        self.progress.stop()
    
    def open_browser(self):
        """Open web browser to access the application"""
        if not self.is_server_running:
            messagebox.showinfo("Sunucu Durumu", "Önce sunucuyu başlatmalısınız.")
            return
        
        webbrowser.open(self.server_url)
        
    def on_closing(self):
        """Handle window closing event"""
        if self.is_server_running and messagebox.askyesno("Çıkış", "Sunucu çalışıyor. Çıkmadan önce sunucuyu durdurmak ister misiniz?"):
            self.stop_server()
        
        self.root.destroy()

def set_app_id():
    """Set application ID for Windows taskbar"""
    if platform.system() == "Windows":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.finasis.desktop")

if __name__ == "__main__":
    set_app_id()
    root = tk.Tk()
    
    # Set application icon (replace with actual icon path if available)
    if platform.system() == "Windows":
        try:
            root.iconbitmap("static/img/favicon.ico")
        except:
            pass
    
    app = FinasisDesktopApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop() 