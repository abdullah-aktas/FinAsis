# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTableWidget, QTableWidgetItem, QComboBox,
                            QLineEdit, QMessageBox, QDialog, QFormLayout,
                            QTextEdit, QFileDialog, QMenu, QHeaderView, QTabWidget,
                            QMainWindow)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QAction
import csv
import os
from datetime import datetime

class CustomerDialog(QDialog):
    """Müşteri ekleme/düzenleme için dialog penceresi"""
    
    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        self.customer = customer
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Müşteri Ekle" if not self.customer else "Müşteri Düzenle")
        self.setMinimumWidth(500)
        
        layout = QFormLayout()
        
        # Müşteri adı
        self.name_edit = QLineEdit()
        if self.customer:
            self.name_edit.setText(self.customer.name)
        layout.addRow("Müşteri Adı:", self.name_edit)
        
        # E-posta
        self.email_edit = QLineEdit()
        if self.customer:
            self.email_edit.setText(self.customer.email)
        layout.addRow("E-posta:", self.email_edit)
        
        # Telefon
        self.phone_edit = QLineEdit()
        if self.customer:
            self.phone_edit.setText(self.customer.phone)
        layout.addRow("Telefon:", self.phone_edit)
        
        # Adres
        self.address_edit = QTextEdit()
        self.address_edit.setMaximumHeight(100)
        if self.customer:
            self.address_edit.setText(self.customer.address)
        layout.addRow("Adres:", self.address_edit)
        
        # Notlar
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        if self.customer and hasattr(self.customer, 'notes'):
            self.notes_edit.setText(self.customer.notes)
        layout.addRow("Notlar:", self.notes_edit)
        
        # Butonlar
        button_layout = QHBoxLayout()
        save_button = QPushButton("Kaydet")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("İptal")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addRow("", button_layout)
        
        self.setLayout(layout)
    
    def get_customer_data(self):
        """Dialog verilerini döndürür"""
        return {
            "name": self.name_edit.text(),
            "email": self.email_edit.text(),
            "phone": self.phone_edit.text(),
            "address": self.address_edit.toPlainText(),
            "notes": self.notes_edit.toPlainText()
        }

class CustomerTransactionDialog(QDialog):
    """Müşteri işlem detayları için dialog penceresi"""
    
    def __init__(self, parent=None, customer=None, transactions=None):
        super().__init__(parent)
        self.customer = customer
        self.transactions = transactions or []
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle(f"{self.customer.name} - İşlem Geçmişi")
        self.setMinimumSize(800, 500)
        
        layout = QVBoxLayout()
        
        # Müşteri bilgileri
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"Müşteri: {self.customer.name}"))
        info_layout.addWidget(QLabel(f"E-posta: {self.customer.email}"))
        info_layout.addWidget(QLabel(f"Telefon: {self.customer.phone}"))
        layout.addLayout(info_layout)
        
        # İşlem tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Tarih", "Açıklama", "Tür", "Tutar"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Özet bilgiler
        summary_layout = QHBoxLayout()
        self.total_income_label = QLabel("Toplam Gelir: 0 TL")
        self.total_expense_label = QLabel("Toplam Gider: 0 TL")
        self.net_income_label = QLabel("Net Gelir: 0 TL")
        
        summary_layout.addWidget(self.total_income_label)
        summary_layout.addWidget(self.total_expense_label)
        summary_layout.addWidget(self.net_income_label)
        
        layout.addLayout(summary_layout)
        
        # Kapat butonu
        close_button = QPushButton("Kapat")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
        self.load_transactions()
    
    def load_transactions(self):
        """İşlemleri tabloya yükler"""
        self.table.setRowCount(len(self.transactions))
        total_income = 0
        total_expense = 0
        
        for i, trans in enumerate(self.transactions):
            self.table.setItem(i, 0, QTableWidgetItem(str(trans.date)))
            self.table.setItem(i, 1, QTableWidgetItem(trans.description))
            self.table.setItem(i, 2, QTableWidgetItem(trans.type))
            self.table.setItem(i, 3, QTableWidgetItem(f"{trans.amount:.2f} TL"))
            
            if trans.type == "gelir":
                total_income += trans.amount
            else:
                total_expense += trans.amount
        
        # Özet bilgileri güncelle
        self.total_income_label.setText(f"Toplam Gelir: {total_income:.2f} TL")
        self.total_expense_label.setText(f"Toplam Gider: {total_expense:.2f} TL")
        self.net_income_label.setText(f"Net Gelir: {total_income - total_expense:.2f} TL")

class CustomerManagementWindow(QMainWindow):
    """Müşteri yönetimi penceresi"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setWindowTitle("Müşteri Yönetimi")
        self.setGeometry(200, 200, 1200, 700)
        
        # Ana widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.setup_ui(main_widget)
        self.load_customers()
        
    def setup_ui(self, main_widget):
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Başlık
        title = QLabel("Müşteri Yönetimi")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Araç çubuğu
        toolbar = QHBoxLayout()
        
        # Yeni müşteri butonu
        new_button = QPushButton("Yeni Müşteri")
        new_button.clicked.connect(self.add_customer)
        toolbar.addWidget(new_button)
        
        # Düzenle butonu
        edit_button = QPushButton("Düzenle")
        edit_button.clicked.connect(self.edit_customer)
        toolbar.addWidget(edit_button)
        
        # Sil butonu
        delete_button = QPushButton("Sil")
        delete_button.clicked.connect(self.delete_customer)
        toolbar.addWidget(delete_button)
        
        # İşlem geçmişi butonu
        history_button = QPushButton("İşlem Geçmişi")
        history_button.clicked.connect(self.show_customer_history)
        toolbar.addWidget(history_button)
        
        # İçe aktar butonu
        import_button = QPushButton("İçe Aktar")
        import_button.clicked.connect(self.import_customers)
        toolbar.addWidget(import_button)
        
        # Dışa aktar butonu
        export_button = QPushButton("Dışa Aktar")
        export_button.clicked.connect(self.export_customers)
        toolbar.addWidget(export_button)
        
        # Arama
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Müşteri ara...")
        self.search_edit.textChanged.connect(self.filter_customers)
        search_layout.addWidget(self.search_edit)
        
        toolbar.addLayout(search_layout)
        layout.addLayout(toolbar)
        
        # Müşteri tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Müşteri Adı", "E-posta", "Telefon", "Adres", "Notlar"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_customers(self):
        """Müşterileri tabloya yükler"""
        try:
            customers = self.db.session.query(self.db.Customer).all()
            
            # Arama filtresini uygula
            search_text = self.search_edit.text().lower()
            filtered_customers = []
            for customer in customers:
                if (search_text in customer.name.lower() or 
                    search_text in customer.email.lower() or 
                    search_text in customer.phone.lower() or 
                    search_text in customer.address.lower()):
                    filtered_customers.append(customer)
            
            # Tabloyu doldur
            self.table.setRowCount(len(filtered_customers))
            for i, customer in enumerate(filtered_customers):
                self.table.setItem(i, 0, QTableWidgetItem(customer.name))
                self.table.setItem(i, 1, QTableWidgetItem(customer.email))
                self.table.setItem(i, 2, QTableWidgetItem(customer.phone))
                self.table.setItem(i, 3, QTableWidgetItem(customer.address))
                
                notes = ""
                if hasattr(customer, 'notes'):
                    notes = customer.notes
                self.table.setItem(i, 4, QTableWidgetItem(notes))
                
                # Müşteri ID'sini sakla
                for j in range(5):
                    self.table.item(i, j).setData(Qt.ItemDataRole.UserRole, customer.id)
        
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Müşteriler yüklenirken bir hata oluştu: {str(e)}")
    
    def filter_customers(self):
        """Arama filtresini uygular"""
        self.load_customers()
    
    def add_customer(self):
        """Yeni müşteri ekler"""
        dialog = CustomerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_customer_data()
            self.db.add_customer(
                name=data["name"],
                email=data["email"],
                phone=data["phone"],
                address=data["address"]
            )
            self.load_customers()
    
    def edit_customer(self):
        """Seçili müşteriyi düzenler"""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlenecek müşteriyi seçin.")
            return
        
        row = selected_rows[0].row()
        customer_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Müşteriyi bul
        customer = self.db.session.query(self.db.Customer).get(customer_id)
        
        if customer:
            dialog = CustomerDialog(self, customer)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_customer_data()
                # Müşteriyi güncelle
                customer.name = data["name"]
                customer.email = data["email"]
                customer.phone = data["phone"]
                customer.address = data["address"]
                
                # Notları güncelle (eğer notes alanı varsa)
                if hasattr(customer, 'notes'):
                    customer.notes = data["notes"]
                
                self.db.session.commit()
                self.load_customers()
    
    def delete_customer(self):
        """Seçili müşteriyi siler"""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek müşteriyi seçin.")
            return
        
        row = selected_rows[0].row()
        customer_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "Onay", 
            "Bu müşteriyi silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Müşteriyi bul ve sil
            customer = self.db.session.query(self.db.Customer).get(customer_id)
            if customer:
                self.db.session.delete(customer)
                self.db.session.commit()
                self.load_customers()
    
    def show_customer_history(self):
        """Seçili müşterinin işlem geçmişini gösterir"""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir müşteri seçin.")
            return
        
        row = selected_rows[0].row()
        customer_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Müşteriyi bul
        customer = self.db.session.query(self.db.Customer).get(customer_id)
        
        if customer:
            # Müşteriye ait işlemleri bul
            # Not: Bu kısım veritabanı yapısına göre güncellenmelidir
            # Şu anda örnek olarak tüm işlemleri alıyoruz
            transactions = self.db.session.query(self.db.Transaction).all()
            
            dialog = CustomerTransactionDialog(self, customer, transactions)
            dialog.exec()
    
    def import_customers(self):
        """CSV dosyasından müşterileri içe aktarır"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "CSV Dosyası Seç", "", "CSV Dosyaları (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader)  # Başlık satırını atla
                
                for row in reader:
                    if len(row) >= 4:
                        name = row[0]
                        email = row[1]
                        phone = row[2]
                        address = row[3]
                        notes = row[4] if len(row) > 4 else ""
                        
                        self.db.add_customer(
                            name=name,
                            email=email,
                            phone=phone,
                            address=address
                        )
            
            QMessageBox.information(self, "Başarılı", "Müşteriler başarıyla içe aktarıldı.")
            self.load_customers()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"İçe aktarma sırasında bir hata oluştu: {str(e)}")
    
    def export_customers(self):
        """Müşterileri CSV dosyasına dışa aktarır"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "CSV Dosyası Kaydet", "", "CSV Dosyaları (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Müşteri Adı", "E-posta", "Telefon", "Adres", "Notlar"])
                
                for row in range(self.table.rowCount()):
                    name = self.table.item(row, 0).text()
                    email = self.table.item(row, 1).text()
                    phone = self.table.item(row, 2).text()
                    address = self.table.item(row, 3).text()
                    notes = self.table.item(row, 4).text()
                    
                    writer.writerow([name, email, phone, address, notes])
            
            QMessageBox.information(self, "Başarılı", "Müşteriler başarıyla dışa aktarıldı.")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dışa aktarma sırasında bir hata oluştu: {str(e)}")
    
    def show_context_menu(self, position):
        """Sağ tıklama menüsünü gösterir"""
        menu = QMenu()
        
        edit_action = QAction("Düzenle", self)
        edit_action.triggered.connect(self.edit_customer)
        menu.addAction(edit_action)
        
        delete_action = QAction("Sil", self)
        delete_action.triggered.connect(self.delete_customer)
        menu.addAction(delete_action)
        
        history_action = QAction("İşlem Geçmişi", self)
        history_action.triggered.connect(self.show_customer_history)
        menu.addAction(history_action)
        
        menu.exec(self.table.mapToGlobal(position)) 