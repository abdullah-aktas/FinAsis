# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTableWidget, QTableWidgetItem, QComboBox,
                            QDateEdit, QMessageBox, QMainWindow)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
import pandas as pd
from datetime import datetime, timedelta

class FinancialReportsWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setWindowTitle("Finansal Raporlar")
        self.setGeometry(200, 200, 1000, 600)
        
        # Ana widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.setup_ui(main_widget)
        
    def setup_ui(self, main_widget):
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Başlık
        title = QLabel("Finansal Raporlar")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Filtreler
        filter_layout = QHBoxLayout()
        
        # Tarih aralığı seçimi
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        
        filter_layout.addWidget(QLabel("Başlangıç:"))
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(QLabel("Bitiş:"))
        filter_layout.addWidget(self.end_date)
        
        # Rapor türü seçimi
        self.report_type = QComboBox()
        self.report_type.addItems([
            "Gelir-Gider Raporu",
            "Kategori Bazlı Analiz",
            "Günlük İşlem Özeti"
        ])
        filter_layout.addWidget(QLabel("Rapor Türü:"))
        filter_layout.addWidget(self.report_type)
        
        # Filtreleme butonu
        filter_button = QPushButton("Filtrele")
        filter_button.clicked.connect(self.update_report)
        filter_layout.addWidget(filter_button)
        
        layout.addLayout(filter_layout)
        
        # Rapor tablosu
        self.table = QTableWidget()
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
        
    def update_report(self):
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        report_type = self.report_type.currentText()
        
        # Veritabanından verileri al
        transactions = self.get_transactions(start, end)
        
        if report_type == "Gelir-Gider Raporu":
            self.show_income_expense_report(transactions)
        elif report_type == "Kategori Bazlı Analiz":
            self.show_category_analysis(transactions)
        else:
            self.show_daily_summary(transactions)
    
    def get_transactions(self, start_date, end_date):
        """Veritabanından işlemleri alır"""
        try:
            return self.db.get_transactions_by_date_range(start_date, end_date)
        except Exception as e:
            QMessageBox.warning(self, "Veri Hatası", 
                              f"Veriler alınırken bir hata oluştu: {str(e)}")
            return []
    
    def show_income_expense_report(self, transactions):
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Tarih", "Açıklama", "Tür", "Tutar"])
        
        total_income = 0
        total_expense = 0
        
        # Tabloyu doldur
        self.table.setRowCount(len(transactions))
        for i, trans in enumerate(transactions):
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
    
    def show_category_analysis(self, transactions):
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Kategori", "Toplam Gelir", "Toplam Gider"])
        
        # Kategori bazlı analiz
        categories = {}
        for trans in transactions:
            if trans.category not in categories:
                categories[trans.category] = {"gelir": 0, "gider": 0}
            
            if trans.type == "gelir":
                categories[trans.category]["gelir"] += trans.amount
            else:
                categories[trans.category]["gider"] += trans.amount
        
        # Tabloyu doldur
        self.table.setRowCount(len(categories))
        for i, (category, amounts) in enumerate(categories.items()):
            self.table.setItem(i, 0, QTableWidgetItem(category))
            self.table.setItem(i, 1, QTableWidgetItem(f"{amounts['gelir']:.2f} TL"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{amounts['gider']:.2f} TL"))
    
    def show_daily_summary(self, transactions):
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Tarih", "İşlem Sayısı", "Gelir", "Gider"])
        
        # Günlük özet
        daily_summary = {}
        for trans in transactions:
            date_str = trans.date.strftime("%Y-%m-%d")
            if date_str not in daily_summary:
                daily_summary[date_str] = {"count": 0, "gelir": 0, "gider": 0}
            
            daily_summary[date_str]["count"] += 1
            if trans.type == "gelir":
                daily_summary[date_str]["gelir"] += trans.amount
            else:
                daily_summary[date_str]["gider"] += trans.amount
        
        # Tabloyu doldur
        self.table.setRowCount(len(daily_summary))
        for i, (date, summary) in enumerate(daily_summary.items()):
            self.table.setItem(i, 0, QTableWidgetItem(date))
            self.table.setItem(i, 1, QTableWidgetItem(str(summary["count"])))
            self.table.setItem(i, 2, QTableWidgetItem(f"{summary['gelir']:.2f} TL"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{summary['gider']:.2f} TL")) 