import tkinter as tk
from tkinter import ttk, messagebox
from django.contrib.auth import get_user_model
from django.conf import settings
import json
import os

User = get_user_model()

class SettingsWindow:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title("FinAsis - Hesap Ayarları")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Ana frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Sol menü
        self.menu_frame = ttk.LabelFrame(self.main_frame, text="Ayarlar Menüsü", padding="5")
        self.menu_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        self.menu_buttons = [
            ("Profil Bilgileri", self.show_profile),
            ("Güvenlik", self.show_security),
            ("Bildirimler", self.show_notifications),
            ("Tercihler", self.show_preferences)
        ]
        
        for i, (text, command) in enumerate(self.menu_buttons):
            ttk.Button(self.menu_frame, text=text, command=command).grid(
                row=i, column=0, sticky=(tk.W, tk.E), pady=2
            )
        
        # Sağ içerik alanı
        self.content_frame = ttk.Frame(self.main_frame, padding="10")
        self.content_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Varsayılan olarak profil bilgilerini göster
        self.show_profile()
        
    def clear_content(self):
        """İçerik alanını temizle"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def show_profile(self):
        """Profil bilgileri sekmesini göster"""
        self.clear_content()
        
        # Profil bilgileri formu
        ttk.Label(self.content_frame, text="Profil Bilgileri", font=("Helvetica", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=10
        )
        
        # Form alanları
        fields = [
            ("Kullanıcı Adı", self.user.username),
            ("E-posta", self.user.email),
            ("Ad", self.user.first_name),
            ("Soyad", self.user.last_name)
        ]
        
        for i, (label, value) in enumerate(fields):
            ttk.Label(self.content_frame, text=label).grid(row=i+1, column=0, sticky=tk.W, pady=5)
            ttk.Entry(self.content_frame, width=40).grid(row=i+1, column=1, sticky=tk.W, pady=5)
            self.content_frame.grid_columnconfigure(1, weight=1)
            
        # Kaydet butonu
        ttk.Button(self.content_frame, text="Kaydet", command=self.save_profile).grid(
            row=len(fields)+1, column=0, columnspan=2, pady=20
        )
        
    def show_security(self):
        """Güvenlik sekmesini göster"""
        self.clear_content()
        
        ttk.Label(self.content_frame, text="Güvenlik Ayarları", font=("Helvetica", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=10
        )
        
        # Şifre değiştirme formu
        fields = [
            ("Mevcut Şifre", ""),
            ("Yeni Şifre", ""),
            ("Yeni Şifre (Tekrar)", "")
        ]
        
        for i, (label, _) in enumerate(fields):
            ttk.Label(self.content_frame, text=label).grid(row=i+1, column=0, sticky=tk.W, pady=5)
            ttk.Entry(self.content_frame, width=40, show="*").grid(row=i+1, column=1, sticky=tk.W, pady=5)
            
        ttk.Button(self.content_frame, text="Şifreyi Değiştir", command=self.change_password).grid(
            row=len(fields)+1, column=0, columnspan=2, pady=20
        )
        
    def show_notifications(self):
        """Bildirim ayarları sekmesini göster"""
        self.clear_content()
        
        ttk.Label(self.content_frame, text="Bildirim Ayarları", font=("Helvetica", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=10
        )
        
        # Bildirim seçenekleri
        notifications = [
            "E-posta Bildirimleri",
            "Sistem Bildirimleri",
            "Görev Bildirimleri",
            "Rapor Bildirimleri"
        ]
        
        for i, text in enumerate(notifications):
            var = tk.BooleanVar(value=True)
            ttk.Checkbutton(self.content_frame, text=text, variable=var).grid(
                row=i+1, column=0, sticky=tk.W, pady=5
            )
            
        ttk.Button(self.content_frame, text="Kaydet", command=self.save_notifications).grid(
            row=len(notifications)+1, column=0, pady=20
        )
        
    def show_preferences(self):
        """Tercihler sekmesini göster"""
        self.clear_content()
        
        ttk.Label(self.content_frame, text="Tercihler", font=("Helvetica", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=10
        )
        
        # Tema seçimi
        ttk.Label(self.content_frame, text="Tema:").grid(row=1, column=0, sticky=tk.W, pady=5)
        theme_var = tk.StringVar(value="light")
        ttk.Radiobutton(self.content_frame, text="Açık", variable=theme_var, value="light").grid(
            row=1, column=1, sticky=tk.W, pady=5
        )
        ttk.Radiobutton(self.content_frame, text="Koyu", variable=theme_var, value="dark").grid(
            row=2, column=1, sticky=tk.W, pady=5
        )
        
        # Dil seçimi
        ttk.Label(self.content_frame, text="Dil:").grid(row=3, column=0, sticky=tk.W, pady=5)
        language_var = tk.StringVar(value="tr")
        ttk.Combobox(self.content_frame, textvariable=language_var, values=["Türkçe", "English"]).grid(
            row=3, column=1, sticky=tk.W, pady=5
        )
        
        ttk.Button(self.content_frame, text="Kaydet", command=self.save_preferences).grid(
            row=4, column=0, columnspan=2, pady=20
        )
        
    def save_profile(self):
        """Profil bilgilerini kaydet"""
        messagebox.showinfo("Başarılı", "Profil bilgileri kaydedildi.")
        
    def change_password(self):
        """Şifre değiştirme işlemi"""
        messagebox.showinfo("Başarılı", "Şifreniz başarıyla değiştirildi.")
        
    def save_notifications(self):
        """Bildirim ayarlarını kaydet"""
        messagebox.showinfo("Başarılı", "Bildirim ayarları kaydedildi.")
        
    def save_preferences(self):
        """Tercihleri kaydet"""
        messagebox.showinfo("Başarılı", "Tercihler kaydedildi.")

def open_settings_window(user):
    """Ayarlar penceresini aç"""
    root = tk.Tk()
    app = SettingsWindow(root, user)
    root.mainloop() 