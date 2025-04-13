import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QMessageBox, QStatusBar)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon
from database import DatabaseManager
from sync import SyncManager
from financial_reports import FinancialReportsWindow
from accounting import AccountingWindow
from customer_management import CustomerManagementWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FinAsis - Finansal Yönetim Sistemi")
        self.setMinimumSize(800, 600)
        
        # Veritabanı bağlantısı
        self.db = DatabaseManager()
        
        # Senkronizasyon thread'i
        self.sync_thread = None
        self.is_offline_mode = False
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Başlık
        title_label = QLabel("FinAsis")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Alt başlık
        subtitle_label = QLabel("Finansal Yönetim Sistemi")
        subtitle_label.setFont(QFont("Arial", 14))
        subtitle_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle_label)
        
        # Menü butonları
        self.create_menu_buttons(main_layout)
        
        # Durum çubuğu
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Senkronizasyon durumu güncelleme zamanlayıcısı
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.update_sync_status)
        self.sync_timer.start(5000)  # Her 5 saniyede bir güncelle
        
        # İlk senkronizasyon durumu güncellemesi
        self.update_sync_status()
        
        # Stil ayarları
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
            }
            QLabel {
                color: #333333;
            }
            QStatusBar {
                background-color: #FFFFFF;
                color: #333333;
            }
        """)

    def create_menu_buttons(self, layout):
        """Ana menü butonlarını oluşturur"""
        # Buton container
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(20, 20, 20, 20)
        
        # Butonlar
        buttons = [
            ("Finansal Raporlar", self.show_financial_reports),
            ("Muhasebe İşlemleri", self.show_accounting),
            ("Müşteri Yönetimi", self.show_customer_management),
            ("Senkronizasyon", self.manual_sync),
            ("Çevrimdışı Mod", self.toggle_offline_mode)
        ]
        
        for text, slot in buttons:
            button = QPushButton(text)
            button.setFont(QFont("Arial", 12))
            button.setMinimumHeight(50)
            button.clicked.connect(slot)
            
            # Stil ayarları
            button.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
            """)
            
            button_layout.addWidget(button)
        
        # Buton container'ı ana layout'a ekle
        layout.addWidget(button_container)
        layout.addStretch()
    
    def show_financial_reports(self):
        """Finansal raporlar penceresini gösterir"""
        self.financial_reports_window = FinancialReportsWindow(self.db)
        self.financial_reports_window.show()
    
    def show_accounting(self):
        """Muhasebe işlemleri penceresini gösterir"""
        self.accounting_window = AccountingWindow(self.db)
        self.accounting_window.show()
    
    def show_customer_management(self):
        """Müşteri yönetimi penceresini gösterir"""
        self.customer_management_window = CustomerManagementWindow(self.db)
        self.customer_management_window.show()
    
    def update_sync_status(self):
        """Senkronizasyon durumunu günceller"""
        status = self.sync_manager.get_status()
        
        if status["is_syncing"]:
            self.statusBar.showMessage("Senkronizasyon devam ediyor...")
        elif status["offline_mode"]:
            self.statusBar.showMessage("Çevrimdışı mod aktif")
        else:
            last_sync = status["last_sync"]
            if last_sync:
                self.statusBar.showMessage(
                    f"Son senkronizasyon: {last_sync.strftime('%d.%m.%Y %H:%M')} "
                    f"(Başarılı: {status['success_count']}, Hata: {status['error_count']})"
                )
            else:
                self.statusBar.showMessage("Henüz senkronizasyon yapılmadı")
    
    def toggle_offline_mode(self):
        """Çevrimdışı modu açar/kapatır"""
        self.is_offline_mode = not self.is_offline_mode
        self.sync_manager.set_offline_mode(self.is_offline_mode)
        self.update_sync_status()
        
        if self.is_offline_mode:
            QMessageBox.information(self, "Çevrimdışı Mod", 
                                  "Çevrimdışı mod aktif. Veriler yerel veritabanında saklanacak.")
        else:
            QMessageBox.information(self, "Çevrimiçi Mod", 
                                  "Çevrimiçi mod aktif. Veriler sunucu ile senkronize edilecek.")
            self.manual_sync()
    
    def manual_sync(self):
        """Manuel senkronizasyon işlemini başlatır"""
        if self.is_offline_mode:
            QMessageBox.warning(self, "Uyarı", "Çevrimdışı moddayken senkronizasyon yapılamaz!")
            return
            
        self.sync_thread.start()
        self.statusBar().showMessage("Senkronizasyon başlatıldı...")
    
    def closeEvent(self, event):
        """Uygulama kapatılırken yapılacak işlemler"""
        # Senkronizasyon thread'ini durdur
        self.sync_manager.stop()
        # Veritabanı bağlantısını kapat
        self.db.close()
        event.accept()

    def setup_sync(self):
        """Senkronizasyon ayarlarını yapar"""
        self.sync_thread = SyncThread(self.db)
        self.sync_thread.finished.connect(self.on_sync_finished)
        self.sync_thread.error.connect(self.on_sync_error)
        
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.manual_sync)
        self.sync_timer.start(300000)  # 5 dakikada bir
        
    def on_sync_finished(self):
        """Senkronizasyon tamamlandığında çağrılır"""
        self.statusBar().showMessage("Senkronizasyon tamamlandı", 5000)
        
    def on_sync_error(self, error_message):
        """Senkronizasyon hatası olduğunda çağrılır"""
        self.statusBar().showMessage(f"Senkronizasyon hatası: {error_message}", 5000)
        QMessageBox.warning(self, "Senkronizasyon Hatası", error_message)

def main():
    print("Uygulama başlatılıyor...")
    try:
        app = QApplication(sys.argv)
        print("QApplication oluşturuldu")
        window = MainWindow()
        print("Ana pencere oluşturuldu")
        window.show()
        print("Pencere gösteriliyor")
        sys.exit(app.exec())
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        raise

if __name__ == "__main__":
    main() 