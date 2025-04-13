from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTableWidget, QTableWidgetItem, QComboBox,
                            QDateEdit, QMessageBox, QDialog, QLineEdit, QFormLayout,
                            QDoubleSpinBox, QFileDialog, QMenu, QHeaderView, QMainWindow)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QAction
import csv
import os
from datetime import datetime

class TransactionDialog(QDialog):
    """İşlem ekleme/düzenleme için dialog penceresi"""
    
    def __init__(self, parent=None, transaction=None, categories=None):
        super().__init__(parent)
        self.transaction = transaction
        self.categories = categories or []
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("İşlem Ekle" if not self.transaction else "İşlem Düzenle")
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        # Tarih
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        if self.transaction:
            self.date_edit.setDate(QDate.fromString(str(self.transaction.date), "yyyy-MM-dd"))
        layout.addRow("Tarih:", self.date_edit)
        
        # Açıklama
        self.description_edit = QLineEdit()
        if self.transaction:
            self.description_edit.setText(self.transaction.description)
        layout.addRow("Açıklama:", self.description_edit)
        
        # Tutar
        self.amount_edit = QDoubleSpinBox()
        self.amount_edit.setRange(0, 1000000)
        self.amount_edit.setDecimals(2)
        self.amount_edit.setSingleStep(10)
        if self.transaction:
            self.amount_edit.setValue(self.transaction.amount)
        layout.addRow("Tutar:", self.amount_edit)
        
        # Tür
        self.type_combo = QComboBox()
        self.type_combo.addItems(["gelir", "gider"])
        if self.transaction:
            self.type_combo.setCurrentText(self.transaction.type)
        layout.addRow("Tür:", self.type_combo)
        
        # Kategori
        self.category_combo = QComboBox()
        self.category_combo.addItems(self.categories)
        if self.transaction:
            self.category_combo.setCurrentText(self.transaction.category)
        layout.addRow("Kategori:", self.category_combo)
        
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
    
    def get_transaction_data(self):
        """Dialog verilerini döndürür"""
        return {
            "date": self.date_edit.date().toPyDate(),
            "description": self.description_edit.text(),
            "amount": self.amount_edit.value(),
            "type": self.type_combo.currentText(),
            "category": self.category_combo.currentText()
        }

class AccountingWindow(QMainWindow):
    """Muhasebe işlemleri penceresi"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setWindowTitle("Muhasebe İşlemleri")
        self.setGeometry(200, 200, 1200, 700)
        
        # Ana widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.setup_ui(main_widget)
        self.load_transactions()
        
    def setup_ui(self, main_widget):
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Başlık
        title = QLabel("Muhasebe İşlemleri")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Araç çubuğu
        toolbar = QHBoxLayout()
        
        # Yeni işlem butonu
        new_button = QPushButton("Yeni İşlem")
        new_button.clicked.connect(self.add_transaction)
        toolbar.addWidget(new_button)
        
        # Düzenle butonu
        edit_button = QPushButton("Düzenle")
        edit_button.clicked.connect(self.edit_transaction)
        toolbar.addWidget(edit_button)
        
        # Sil butonu
        delete_button = QPushButton("Sil")
        delete_button.clicked.connect(self.delete_transaction)
        toolbar.addWidget(delete_button)
        
        # İçe aktar butonu
        import_button = QPushButton("İçe Aktar")
        import_button.clicked.connect(self.import_transactions)
        toolbar.addWidget(import_button)
        
        # Dışa aktar butonu
        export_button = QPushButton("Dışa Aktar")
        export_button.clicked.connect(self.export_transactions)
        toolbar.addWidget(export_button)
        
        # Filtreler
        filter_layout = QHBoxLayout()
        
        # Tarih aralığı
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        
        filter_layout.addWidget(QLabel("Başlangıç:"))
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(QLabel("Bitiş:"))
        filter_layout.addWidget(self.end_date)
        
        # Tür filtresi
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Tümü", "gelir", "gider"])
        filter_layout.addWidget(QLabel("Tür:"))
        filter_layout.addWidget(self.type_filter)
        
        # Kategori filtresi
        self.category_filter = QComboBox()
        self.category_filter.addItem("Tümü")
        self.update_category_filter()
        filter_layout.addWidget(QLabel("Kategori:"))
        filter_layout.addWidget(self.category_filter)
        
        # Filtreleme butonu
        filter_button = QPushButton("Filtrele")
        filter_button.clicked.connect(self.apply_filters)
        filter_layout.addWidget(filter_button)
        
        toolbar.addLayout(filter_layout)
        layout.addLayout(toolbar)
        
        # İşlem tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Tarih", "Açıklama", "Tür", "Kategori", "Tutar"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
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
        
        self.setLayout(layout)
    
    def update_category_filter(self):
        """Kategori filtresini günceller"""
        current_text = self.category_filter.currentText()
        self.category_filter.clear()
        self.category_filter.addItem("Tümü")
        
        # Veritabanından kategorileri al
        categories = set()
        transactions = self.db.get_transactions_by_date_range(
            self.start_date.date().toPyDate(),
            self.end_date.date().toPyDate()
        )
        for trans in transactions:
            categories.add(trans.category)
        
        self.category_filter.addItems(sorted(categories))
        
        # Önceki seçimi koru
        index = self.category_filter.findText(current_text)
        if index >= 0:
            self.category_filter.setCurrentIndex(index)
    
    def load_transactions(self):
        """İşlemleri tabloya yükler"""
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        
        transactions = self.db.get_transactions_by_date_range(start_date, end_date)
        
        # Filtreleri uygula
        type_filter = self.type_filter.currentText()
        category_filter = self.category_filter.currentText()
        
        filtered_transactions = []
        for trans in transactions:
            if type_filter != "Tümü" and trans.type != type_filter:
                continue
            if category_filter != "Tümü" and trans.category != category_filter:
                continue
            filtered_transactions.append(trans)
        
        # Tabloyu doldur
        self.table.setRowCount(len(filtered_transactions))
        total_income = 0
        total_expense = 0
        
        for i, trans in enumerate(filtered_transactions):
            self.table.setItem(i, 0, QTableWidgetItem(str(trans.date)))
            self.table.setItem(i, 1, QTableWidgetItem(trans.description))
            self.table.setItem(i, 2, QTableWidgetItem(trans.type))
            self.table.setItem(i, 3, QTableWidgetItem(trans.category))
            self.table.setItem(i, 4, QTableWidgetItem(f"{trans.amount:.2f} TL"))
            
            if trans.type == "gelir":
                total_income += trans.amount
            else:
                total_expense += trans.amount
        
        # Özet bilgileri güncelle
        self.total_income_label.setText(f"Toplam Gelir: {total_income:.2f} TL")
        self.total_expense_label.setText(f"Toplam Gider: {total_expense:.2f} TL")
        self.net_income_label.setText(f"Net Gelir: {total_income - total_expense:.2f} TL")
    
    def apply_filters(self):
        """Filtreleri uygular ve tabloyu günceller"""
        self.load_transactions()
    
    def add_transaction(self):
        """Yeni işlem ekler"""
        # Kategorileri al
        categories = set()
        transactions = self.db.get_transactions_by_date_range(
            self.start_date.date().toPyDate(),
            self.end_date.date().toPyDate()
        )
        for trans in transactions:
            categories.add(trans.category)
        
        dialog = TransactionDialog(self, categories=sorted(categories))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_transaction_data()
            self.db.add_transaction(
                description=data["description"],
                amount=data["amount"],
                type=data["type"],
                category=data["category"]
            )
            self.load_transactions()
    
    def edit_transaction(self):
        """Seçili işlemi düzenler"""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlenecek işlemi seçin.")
            return
        
        row = selected_rows[0].row()
        transaction_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Kategorileri al
        categories = set()
        transactions = self.db.get_transactions_by_date_range(
            self.start_date.date().toPyDate(),
            self.end_date.date().toPyDate()
        )
        for trans in transactions:
            categories.add(trans.category)
        
        # İşlemi bul
        transaction = None
        for trans in transactions:
            if trans.id == transaction_id:
                transaction = trans
                break
        
        if transaction:
            dialog = TransactionDialog(self, transaction, sorted(categories))
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_transaction_data()
                # İşlemi güncelle
                transaction.date = data["date"]
                transaction.description = data["description"]
                transaction.amount = data["amount"]
                transaction.type = data["type"]
                transaction.category = data["category"]
                self.db.session.commit()
                self.load_transactions()
    
    def delete_transaction(self):
        """Seçili işlemi siler"""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek işlemi seçin.")
            return
        
        row = selected_rows[0].row()
        transaction_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "Onay", 
            "Bu işlemi silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # İşlemi bul ve sil
            transaction = self.db.session.query(self.db.Transaction).get(transaction_id)
            if transaction:
                self.db.session.delete(transaction)
                self.db.session.commit()
                self.load_transactions()
    
    def import_transactions(self):
        """CSV dosyasından işlemleri içe aktarır"""
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
                    if len(row) >= 5:
                        date = datetime.strptime(row[0], "%Y-%m-%d").date()
                        description = row[1]
                        type_ = row[2]
                        category = row[3]
                        amount = float(row[4])
                        
                        self.db.add_transaction(
                            description=description,
                            amount=amount,
                            type=type_,
                            category=category
                        )
            
            QMessageBox.information(self, "Başarılı", "İşlemler başarıyla içe aktarıldı.")
            self.load_transactions()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"İçe aktarma sırasında bir hata oluştu: {str(e)}")
    
    def export_transactions(self):
        """İşlemleri CSV dosyasına dışa aktarır"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "CSV Dosyası Kaydet", "", "CSV Dosyaları (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Tarih", "Açıklama", "Tür", "Kategori", "Tutar"])
                
                for row in range(self.table.rowCount()):
                    date = self.table.item(row, 0).text()
                    description = self.table.item(row, 1).text()
                    type_ = self.table.item(row, 2).text()
                    category = self.table.item(row, 3).text()
                    amount = self.table.item(row, 4).text().replace(" TL", "")
                    
                    writer.writerow([date, description, type_, category, amount])
            
            QMessageBox.information(self, "Başarılı", "İşlemler başarıyla dışa aktarıldı.")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dışa aktarma sırasında bir hata oluştu: {str(e)}")
    
    def show_context_menu(self, position):
        """Sağ tıklama menüsünü gösterir"""
        menu = QMenu()
        
        edit_action = QAction("Düzenle", self)
        edit_action.triggered.connect(self.edit_transaction)
        menu.addAction(edit_action)
        
        delete_action = QAction("Sil", self)
        delete_action.triggered.connect(self.delete_transaction)
        menu.addAction(delete_action)
        
        menu.exec(self.table.mapToGlobal(position)) 