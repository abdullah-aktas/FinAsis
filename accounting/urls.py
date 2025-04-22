from django.urls import path
from . import views

app_name = 'accounting'

urlpatterns = [
    # Ana Sayfa
    path('', views.dashboard, name='dashboard'),
    
    # Hesap Planı URL'leri
    path('hesap-plani/', views.ChartOfAccountsListView.as_view(), name='chart_of_accounts_list'),
    path('hesap-plani/<int:pk>/', views.ChartOfAccountsDetailView.as_view(), name='chart_of_accounts_detail'),
    path('hesap-plani/ekle/', views.ChartOfAccountsCreateView.as_view(), name='chart_of_accounts_create'),
    path('hesap-plani/<int:pk>/duzenle/', views.ChartOfAccountsUpdateView.as_view(), name='chart_of_accounts_update'),
    path('hesap-plani/<int:pk>/sil/', views.ChartOfAccountsDeleteView.as_view(), name='chart_of_accounts_delete'),
    
    # Cari Hesap URL'leri
    path('cari-hesaplar/', views.AccountListView.as_view(), name='account_list'),
    path('cari-hesaplar/<int:pk>/', views.AccountDetailView.as_view(), name='account_detail'),
    path('cari-hesaplar/ekle/', views.AccountCreateView.as_view(), name='account_create'),
    path('cari-hesaplar/<int:pk>/duzenle/', views.AccountUpdateView.as_view(), name='account_update'),
    path('cari-hesaplar/<int:pk>/sil/', views.AccountDeleteView.as_view(), name='account_delete'),
    
    # Fatura URL'leri
    path('faturalar/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('faturalar/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('faturalar/ekle/', views.InvoiceCreateView.as_view(), name='invoice_create'),
    path('faturalar/<int:pk>/duzenle/', views.InvoiceUpdateView.as_view(), name='invoice_update'),
    path('faturalar/<int:pk>/sil/', views.InvoiceDeleteView.as_view(), name='invoice_delete'),
    
    # Fatura Kalemi URL'leri
    path('fatura-kalemleri/ekle/', views.InvoiceLineCreateView.as_view(), name='invoice_line_create'),
    path('fatura-kalemleri/<int:pk>/duzenle/', views.InvoiceLineUpdateView.as_view(), name='invoice_line_update'),
    path('fatura-kalemleri/<int:pk>/sil/', views.InvoiceLineDeleteView.as_view(), name='invoice_line_delete'),
    
    # Yevmiye URL'leri
    path('yevmiyeler/', views.TransactionListView.as_view(), name='transaction_list'),
    path('yevmiyeler/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('yevmiyeler/ekle/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('yevmiyeler/<int:pk>/duzenle/', views.TransactionUpdateView.as_view(), name='transaction_update'),
    path('yevmiyeler/<int:pk>/sil/', views.TransactionDeleteView.as_view(), name='transaction_delete'),
    
    # Yevmiye Kalemi URL'leri
    path('yevmiye-kalemleri/ekle/', views.TransactionLineCreateView.as_view(), name='transaction_line_create'),
    path('yevmiye-kalemleri/<int:pk>/duzenle/', views.TransactionLineUpdateView.as_view(), name='transaction_line_update'),
    path('yevmiye-kalemleri/<int:pk>/sil/', views.TransactionLineDeleteView.as_view(), name='transaction_line_delete'),
    
    # Kasa URL'leri
    path('kasalar/', views.CashBoxListView.as_view(), name='cashbox_list'),
    path('kasalar/<int:pk>/', views.CashBoxDetailView.as_view(), name='cashbox_detail'),
    path('kasalar/ekle/', views.CashBoxCreateView.as_view(), name='cashbox_create'),
    path('kasalar/<int:pk>/duzenle/', views.CashBoxUpdateView.as_view(), name='cashbox_update'),
    path('kasalar/<int:pk>/sil/', views.CashBoxDeleteView.as_view(), name='cashbox_delete'),
    
    # Banka URL'leri
    path('bankalar/', views.BankListView.as_view(), name='bank_list'),
    path('bankalar/<int:pk>/', views.BankDetailView.as_view(), name='bank_detail'),
    path('bankalar/ekle/', views.BankCreateView.as_view(), name='bank_create'),
    path('bankalar/<int:pk>/duzenle/', views.BankUpdateView.as_view(), name='bank_update'),
    path('bankalar/<int:pk>/sil/', views.BankDeleteView.as_view(), name='bank_delete'),
    
    # Stok URL'leri
    path('stoklar/', views.StockListView.as_view(), name='stock_list'),
    path('stoklar/<int:pk>/', views.StockDetailView.as_view(), name='stock_detail'),
    path('stoklar/ekle/', views.StockCreateView.as_view(), name='stock_create'),
    path('stoklar/<int:pk>/duzenle/', views.StockUpdateView.as_view(), name='stock_update'),
    path('stoklar/<int:pk>/sil/', views.StockDeleteView.as_view(), name='stock_delete'),
    
    # Stok Hareketi URL'leri
    path('stok-hareketleri/', views.StockTransactionListView.as_view(), name='stock_transaction_list'),
    path('stok-hareketleri/<int:pk>/', views.StockTransactionDetailView.as_view(), name='stock_transaction_detail'),
    path('stok-hareketleri/ekle/', views.StockTransactionCreateView.as_view(), name='stock_transaction_create'),
    path('stok-hareketleri/<int:pk>/duzenle/', views.StockTransactionUpdateView.as_view(), name='stock_transaction_update'),
    path('stok-hareketleri/<int:pk>/sil/', views.StockTransactionDeleteView.as_view(), name='stock_transaction_delete'),
    
    # E-Belge URL'leri
    path('e-belgeler/', views.EDocumentListView.as_view(), name='edocument_list'),
    path('e-belge/<int:pk>/', views.EDocumentDetailView.as_view(), name='edocument_detail'),
    path('fatura/<int:pk>/e-belge-olustur/', views.create_edocument, name='create_edocument'),
    path('e-belge/<int:pk>/iptal/', views.cancel_edocument, name='cancel_edocument'),
    path('e-belge/<int:pk>/durum-kontrol/', views.check_edocument_status, name='check_edocument_status'),
    path('e-belge/<int:pk>/pdf-indir/', views.download_e_document_pdf, name='download_edocument_pdf'),
    path('e-belge-ayarlari/', views.edocument_settings, name='edocument_settings'),
    
    # Günlük Görevler
    path('gunluk-gorevler/', views.DailyTaskListView.as_view(), name='daily_task_list'),
    path('gunluk-gorevler/<int:pk>/', views.DailyTaskDetailView.as_view(), name='daily_task_detail'),
    path('gunluk-gorevler/ekle/', views.DailyTaskCreateView.as_view(), name='daily_task_create'),
    path('gunluk-gorevler/<int:pk>/duzenle/', views.DailyTaskUpdateView.as_view(), name='daily_task_update'),
    path('gunluk-gorevler/<int:pk>/sil/', views.DailyTaskDeleteView.as_view(), name='daily_task_delete'),
    path('gunluk-gorevler/<int:pk>/tamamla/', views.CompleteTaskView.as_view(), name='daily_task_complete'),
    
    # Bilgi Bankası
    path('bilgi-bankasi/', views.KnowledgeBaseListView.as_view(), name='knowledge_base_list'),
    path('bilgi-bankasi/<int:pk>/', views.KnowledgeBaseDetailView.as_view(), name='knowledge_base_detail'),
    path('bilgi-bankasi/ekle/', views.KnowledgeBaseCreateView.as_view(), name='knowledge_base_create'),
    path('bilgi-bankasi/<int:pk>/duzenle/', views.KnowledgeBaseUpdateView.as_view(), name='knowledge_base_update'),
    path('bilgi-bankasi/<int:pk>/sil/', views.KnowledgeBaseDeleteView.as_view(), name='knowledge_base_delete'),
    
    # Kullanıcı İstatistikleri
    path('kullanici-istatistikleri/', views.UserStatsView.as_view(), name='user_statistics'),

    # AccountPlan URLs
    path('accountplan/', views.AccountPlanListView.as_view(), name='accountplan_list'),
    path('accountplan/<int:pk>/', views.AccountPlanDetailView.as_view(), name='accountplan_detail'),
    path('accountplan/create/', views.AccountPlanCreateView.as_view(), name='accountplan_create'),
    path('accountplan/<int:pk>/update/', views.AccountPlanUpdateView.as_view(), name='accountplan_update'),
    path('accountplan/<int:pk>/delete/', views.AccountPlanDeleteView.as_view(), name='accountplan_delete'),

    # BalanceSheet URLs
    path('balancesheet/', views.BalanceSheetListView.as_view(), name='balancesheet_list'),
    path('balancesheet/<int:pk>/', views.BalanceSheetDetailView.as_view(), name='balancesheet_detail'),
    path('balancesheet/create/', views.BalanceSheetCreateView.as_view(), name='balancesheet_create'),
    path('balancesheet/<int:pk>/update/', views.BalanceSheetUpdateView.as_view(), name='balancesheet_update'),
    path('balancesheet/<int:pk>/delete/', views.BalanceSheetDeleteView.as_view(), name='balancesheet_delete'),

    # CashFlow URLs
    path('cashflow/', views.CashFlowListView.as_view(), name='cashflow_list'),
    path('cashflow/<int:pk>/', views.CashFlowDetailView.as_view(), name='cashflow_detail'),
    path('cashflow/create/', views.CashFlowCreateView.as_view(), name='cashflow_create'),
    path('cashflow/<int:pk>/update/', views.CashFlowUpdateView.as_view(), name='cashflow_update'),
    path('cashflow/<int:pk>/delete/', views.CashFlowDeleteView.as_view(), name='cashflow_delete'),

    # JournalEntry URLs
    path('journalentry/', views.JournalEntryListView.as_view(), name='journalentry_list'),
    path('journalentry/<int:pk>/', views.JournalEntryDetailView.as_view(), name='journalentry_detail'),
    path('journalentry/create/', views.JournalEntryCreateView.as_view(), name='journalentry_create'),
    path('journalentry/<int:pk>/update/', views.JournalEntryUpdateView.as_view(), name='journalentry_update'),
    path('journalentry/<int:pk>/delete/', views.JournalEntryDeleteView.as_view(), name='journalentry_delete'),

    # EInvoice URLs
    path('einvoice/settings/', views.EInvoiceSettingsListView.as_view(), name='einvoice_settings_list'),
    path('einvoice/settings/<int:pk>/', views.EInvoiceSettingsDetailView.as_view(), name='einvoice_settings_detail'),
    path('einvoice/settings/create/', views.EInvoiceSettingsCreateView.as_view(), name='einvoice_settings_create'),
    path('einvoice/settings/<int:pk>/update/', views.EInvoiceSettingsUpdateView.as_view(), name='einvoice_settings_update'),
    path('einvoice/settings/<int:pk>/delete/', views.EInvoiceSettingsDeleteView.as_view(), name='einvoice_settings_delete'),

    # EInvoiceLog URLs
    path('einvoice/logs/', views.EInvoiceLogListView.as_view(), name='einvoice_log_list'),
    path('einvoice/logs/<int:pk>/', views.EInvoiceLogDetailView.as_view(), name='einvoice_log_detail'),

    # EDocumentTemplate URLs
    path('edocument/templates/', views.EDocumentTemplateListView.as_view(), name='edocument_template_list'),
    path('edocument/templates/<int:pk>/', views.EDocumentTemplateDetailView.as_view(), name='edocument_template_detail'),
    path('edocument/templates/create/', views.EDocumentTemplateCreateView.as_view(), name='edocument_template_create'),
    path('edocument/templates/<int:pk>/update/', views.EDocumentTemplateUpdateView.as_view(), name='edocument_template_update'),
    path('edocument/templates/<int:pk>/delete/', views.EDocumentTemplateDeleteView.as_view(), name='edocument_template_delete'),

    # KnowledgeBaseRelatedItem URLs
    path('knowledgebase/related/', views.KnowledgeBaseRelatedItemListView.as_view(), name='knowledgebase_related_item_list'),
    path('knowledgebase/related/<int:pk>/', views.KnowledgeBaseRelatedItemDetailView.as_view(), name='knowledgebase_related_item_detail'),
    path('knowledgebase/related/create/', views.KnowledgeBaseRelatedItemCreateView.as_view(), name='knowledgebase_related_item_create'),
    path('knowledgebase/related/<int:pk>/update/', views.KnowledgeBaseRelatedItemUpdateView.as_view(), name='knowledgebase_related_item_update'),
    path('knowledgebase/related/<int:pk>/delete/', views.KnowledgeBaseRelatedItemDeleteView.as_view(), name='knowledgebase_related_item_delete'),
] 