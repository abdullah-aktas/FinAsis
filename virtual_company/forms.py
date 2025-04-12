from django import forms
from django.utils.translation import gettext_lazy as _
from .models import (
    VirtualCompany, Department, Employee, Project,
    Task, Budget, Report, ModuleSetting, DailyTask, UserDailyTask
)
from accounting.models import KnowledgeBase, KnowledgeBaseRelatedItem, EDocumentSettings
from django.forms import inlineformset_factory
import random

class VirtualCompanyForm(forms.ModelForm):
    class Meta:
        model = VirtualCompany
        fields = [
            'name', 'description', 'logo', 'industry',
            'founded_date', 'website', 'email', 'phone',
            'address', 'tax_number', 'tax_office', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'founded_date': forms.DateInput(attrs={'type': 'date'}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'manager', 'budget', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'budget': forms.NumberInput(attrs={'step': '0.01'}),
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'user', 'department', 'role', 'position',
            'salary', 'hire_date', 'is_active'
        ]
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'salary': forms.NumberInput(attrs={'step': '0.01'}),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'department', 'manager',
            'start_date', 'end_date', 'budget', 'status',
            'progress', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'budget': forms.NumberInput(attrs={'step': '0.01'}),
            'progress': forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '100'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'assigned_to', 'priority',
            'status', 'start_date', 'due_date', 'progress'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'progress': forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '100'}),
        }

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['type', 'amount', 'description', 'date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['title', 'type', 'content', 'file']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }

class ModuleSettingForm(forms.ModelForm):
    class Meta:
        model = ModuleSetting
        fields = ['module', 'company', 'key', 'value', 'is_global']
        widgets = {
            'value': forms.Textarea(attrs={'rows': 3}),
        }
        
class ModuleCreationForm(forms.Form):
    module_name = forms.CharField(
        label=_('Modül Adı'),
        max_length=100,
        help_text=_('Modül için kısa ve açıklayıcı bir isim giriniz.')
    )
    module_code = forms.SlugField(
        label=_('Modül Kodu'),
        max_length=50,
        help_text=_('Modülün benzersiz kodu. Sadece harfler, sayılar, alt çizgi ve kısa çizgi kullanılabilir.')
    )
    description = forms.CharField(
        label=_('Açıklama'),
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text=_('Modülün işlevini ve amacını kısaca açıklayınız.')
    )
    is_active = forms.BooleanField(
        label=_('Aktif'),
        required=False,
        initial=True,
        help_text=_('Modül oluşturulduktan sonra aktif olsun mu?')
    )
    has_menu = forms.BooleanField(
        label=_('Menüde Göster'),
        required=False,
        initial=True,
        help_text=_('Modül ana menüde görünsün mü?')
    )
    icon = forms.CharField(
        label=_('İkon'),
        required=False,
        max_length=50,
        help_text=_('Modül için Font Awesome ikon kodu (örn: fa-users).')
    )
    
    def clean_module_code(self):
        code = self.cleaned_data.get('module_code')
        # Modül kodunun benzersiz olduğunu kontrol et
        # Burada modül kodunun dosya sisteminde veya veritabanında var olup olmadığını kontrol edebilirsiniz
        return code

class DailyTaskForm(forms.ModelForm):
    """Günlük görev formu"""
    
    class Meta:
        model = DailyTask
        fields = [
            'title', 'description', 'category', 'difficulty', 
            'xp_reward', 'money_reward', 'steps', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'xp_reward': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'money_reward': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'steps': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': _('Her satır bir adımı temsil eder')}),
        }
    
    def clean_steps(self):
        """Adımları temizler ve JSON formatına dönüştürür"""
        steps_text = self.cleaned_data.get('steps', '')
        if not steps_text:
            return []
        
        # Her satırı bir adım olarak al
        steps_list = []
        for i, line in enumerate(steps_text.splitlines()):
            line = line.strip()
            if line:
                steps_list.append({
                    'order': i,
                    'description': line,
                    'completed': False
                })
        
        return steps_list
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Eğer düzenleme modunda ve steps alanı doluysa, adımları satır satır göster
        if self.instance.pk and self.instance.steps:
            steps_text = '\n'.join([step.get('description', '') for step in self.instance.steps])
            self.initial['steps'] = steps_text

class UserDailyTaskNoteForm(forms.ModelForm):
    """Kullanıcı günlük görev notu formu"""
    
    class Meta:
        model = UserDailyTask
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': _('Görev hakkında notlarınız...')})
        }

class DailyTaskRelatedItemForm(forms.Form):
    """Görevle ilişkili kaynak formu"""
    
    title = forms.CharField(
        label=_('Başlık'),
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        label=_('Açıklama'),
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        required=False
    )
    url = forms.URLField(
        label=_('URL'),
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        required=False
    )
    DELETE = forms.BooleanField(
        label=_('Sil'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

DailyTaskRelatedItemFormSet = forms.formset_factory(
    DailyTaskRelatedItemForm,
    extra=1,
    can_delete=True
)

class KnowledgeBaseForm(forms.ModelForm):
    """Bilgi bankası giriş formu"""
    
    class Meta:
        model = KnowledgeBase
        fields = [
            'title', 'content', 'summary', 'category', 
            'level', 'image', 'tags', 'active', 'is_featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Başlık')}),
            'content': forms.Textarea(attrs={'class': 'form-control ckeditor', 'rows': 5}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Özet')}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Etiketler (virgülle ayır)')}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def clean_tags(self):
        """Etiketleri temizler"""
        tags = self.cleaned_data.get('tags', '')
        if tags:
            # Etiketleri virgülle ayır, boş etiketleri kaldır ve birleştir
            cleaned_tags = ','.join([tag.strip() for tag in tags.split(',') if tag.strip()])
            return cleaned_tags
        return tags


class KnowledgeBaseRelatedItemForm(forms.ModelForm):
    """Bilgi bankası ilişkili öğeler formu"""
    
    delete = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input delete-related-item'})
    )
    
    class Meta:
        model = KnowledgeBaseRelatedItem
        fields = ['title', 'description', 'url', 'resource_type', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Başlık')}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': _('Açıklama')}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': _('URL')}),
            'resource_type': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }


# İlişkili öğeler için formset oluştur
KnowledgeBaseRelatedItemFormSet = inlineformset_factory(
    KnowledgeBase,
    KnowledgeBaseRelatedItem,
    form=KnowledgeBaseRelatedItemForm,
    extra=1,
    can_delete=True
)

class APIProviderForm(forms.Form):
    """API Sağlayıcı Form"""
    name = forms.CharField(label=_('Sağlayıcı Adı'), max_length=100)
    api_type = forms.ChoiceField(
        label=_('API Tipi'),
        choices=[
            ('bank', _('Banka API')),
            ('edevlet', _('E-Devlet API')),
            ('efatura', _('E-Fatura API')),
            ('other', _('Diğer'))
        ]
    )
    api_base_url = forms.URLField(label=_('API Temel URL'))
    api_version = forms.CharField(label=_('API Versiyonu'), max_length=20)
    auth_type = forms.ChoiceField(
        label=_('Kimlik Doğrulama Tipi'),
        choices=[
            ('apikey', _('API Anahtarı')),
            ('oauth2', _('OAuth 2.0')),
            ('jwt', _('JWT')),
            ('basic', _('Temel Kimlik Doğrulama'))
        ]
    )
    api_key = forms.CharField(label=_('API Anahtarı'), max_length=255, required=False)
    client_id = forms.CharField(label=_('İstemci ID'), max_length=100, required=False)
    client_secret = forms.CharField(label=_('İstemci Şifresi'), max_length=255, required=False, widget=forms.PasswordInput)
    username = forms.CharField(label=_('Kullanıcı Adı'), max_length=100, required=False)
    password = forms.CharField(label=_('Şifre'), max_length=100, required=False, widget=forms.PasswordInput)
    documentation_url = forms.URLField(label=_('Dokümantasyon URL'), required=False)
    is_active = forms.BooleanField(label=_('Aktif'), required=False, initial=True)
    test_mode = forms.BooleanField(label=_('Test Modu'), required=False, initial=True)
    description = forms.CharField(label=_('Açıklama'), widget=forms.Textarea, required=False)

    def clean(self):
        cleaned_data = super().clean()
        auth_type = cleaned_data.get('auth_type')
        
        # Kimlik doğrulama tipine göre gerekli alanları kontrol et
        if auth_type == 'apikey' and not cleaned_data.get('api_key'):
            self.add_error('api_key', _('API anahtarı gereklidir'))
        elif auth_type == 'oauth2':
            if not cleaned_data.get('client_id'):
                self.add_error('client_id', _('İstemci ID gereklidir'))
            if not cleaned_data.get('client_secret'):
                self.add_error('client_secret', _('İstemci şifresi gereklidir'))
        elif auth_type == 'basic':
            if not cleaned_data.get('username'):
                self.add_error('username', _('Kullanıcı adı gereklidir'))
            if not cleaned_data.get('password'):
                self.add_error('password', _('Şifre gereklidir'))
        
        return cleaned_data

class APIEndpointForm(forms.Form):
    """API Endpoint Form"""
    provider = forms.ChoiceField(label=_('API Sağlayıcı'))
    name = forms.CharField(label=_('Endpoint Adı'), max_length=100)
    endpoint_path = forms.CharField(label=_('Endpoint Yolu'), max_length=255)
    http_method = forms.ChoiceField(
        label=_('HTTP Metodu'),
        choices=[
            ('GET', 'GET'),
            ('POST', 'POST'),
            ('PUT', 'PUT'),
            ('DELETE', 'DELETE'),
            ('PATCH', 'PATCH')
        ]
    )
    request_format = forms.ChoiceField(
        label=_('İstek Formatı'),
        choices=[
            ('json', 'JSON'),
            ('xml', 'XML'),
            ('form', 'Form Data')
        ],
        initial='json'
    )
    response_format = forms.ChoiceField(
        label=_('Yanıt Formatı'),
        choices=[
            ('json', 'JSON'),
            ('xml', 'XML'),
            ('csv', 'CSV'),
            ('pdf', 'PDF')
        ],
        initial='json'
    )
    description = forms.CharField(label=_('Açıklama'), widget=forms.Textarea, required=False)
    example_request = forms.CharField(label=_('Örnek İstek'), widget=forms.Textarea, required=False)
    example_response = forms.CharField(label=_('Örnek Yanıt'), widget=forms.Textarea, required=False)
    
    def __init__(self, *args, **kwargs):
        providers = kwargs.pop('providers', [])
        super().__init__(*args, **kwargs)
        self.fields['provider'].choices = providers

class BankIntegrationForm(forms.Form):
    """Banka Entegrasyon Form"""
    bank_name = forms.CharField(label=_('Banka Adı'), max_length=100)
    bank_code = forms.CharField(label=_('Banka Kodu'), max_length=20)
    account_number = forms.CharField(label=_('Hesap Numarası'), max_length=30)
    iban = forms.CharField(label=_('IBAN'), max_length=34)
    account_type = forms.ChoiceField(
        label=_('Hesap Tipi'),
        choices=[
            ('checking', _('Vadesiz Hesap')),
            ('savings', _('Vadeli Hesap')),
            ('credit', _('Kredi Hesabı')),
            ('other', _('Diğer'))
        ]
    )
    currency = forms.ChoiceField(
        label=_('Para Birimi'),
        choices=[
            ('TRY', _('Türk Lirası')),
            ('USD', _('Amerikan Doları')),
            ('EUR', _('Euro')),
            ('GBP', _('İngiliz Sterlini'))
        ]
    )
    api_provider = forms.ChoiceField(label=_('API Sağlayıcı'))
    is_active = forms.BooleanField(label=_('Aktif'), required=False, initial=True)
    
    def __init__(self, *args, **kwargs):
        providers = kwargs.pop('providers', [])
        super().__init__(*args, **kwargs)
        self.fields['api_provider'].choices = providers
    
    def clean_iban(self):
        iban = self.cleaned_data.get('iban')
        if iban:
            # IBAN formatını kontrol et (boşlukları kaldır)
            iban = iban.replace(' ', '')
            if len(iban) != 26 or not iban.startswith('TR'):
                raise forms.ValidationError(_('Geçersiz IBAN formatı. IBAN, TR ile başlamalı ve 26 karakter uzunluğunda olmalıdır.'))
        return iban

class EDevletIntegrationForm(forms.Form):
    """E-Devlet Entegrasyon Form"""
    system_name = forms.CharField(label=_('Sistem Adı'), max_length=100)
    system_code = forms.CharField(label=_('Sistem Kodu'), max_length=50)
    api_provider = forms.ChoiceField(label=_('API Sağlayıcı'))
    service_type = forms.ChoiceField(
        label=_('Servis Tipi'),
        choices=[
            ('tax', _('Vergi Hizmetleri')),
            ('social_security', _('SGK Hizmetleri')),
            ('company_registry', _('Şirket Sicil Hizmetleri')),
            ('other', _('Diğer'))
        ]
    )
    is_active = forms.BooleanField(label=_('Aktif'), required=False, initial=True)
    
    def __init__(self, *args, **kwargs):
        providers = kwargs.pop('providers', [])
        super().__init__(*args, **kwargs)
        self.fields['api_provider'].choices = providers

class EInvoiceIntegrationForm(forms.ModelForm):
    """E-Fatura Entegrasyon Form"""
    class Meta:
        model = EDocumentSettings
        fields = [
            'company_name', 'vkn_tckn', 'tax_office', 'address', 
            'phone', 'email', 'integration_type', 'service_url', 
            'api_key', 'username', 'password', 'is_test_mode', 'is_active'
        ]
        widgets = {
            'password': forms.PasswordInput(),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_vkn_tckn(self):
        vkn_tckn = self.cleaned_data.get('vkn_tckn')
        if vkn_tckn:
            # VKN 10 hane, TCKN 11 hane olmalı
            if len(vkn_tckn) not in [10, 11]:
                raise forms.ValidationError(_('VKN 10 hane, TCKN 11 hane olmalıdır.'))
            if not vkn_tckn.isdigit():
                raise forms.ValidationError(_('VKN/TCKN sadece rakamlardan oluşmalıdır.'))
        return vkn_tckn

class APIDocumentationForm(forms.Form):
    """API Dokümantasyon Form"""
    title = forms.CharField(label=_('Başlık'), max_length=100)
    version = forms.CharField(label=_('Versiyon'), max_length=20)
    description = forms.CharField(label=_('Açıklama'), widget=forms.Textarea)
    base_url = forms.URLField(label=_('Temel URL'))
    auth_description = forms.CharField(label=_('Kimlik Doğrulama Açıklaması'), widget=forms.Textarea)
    is_published = forms.BooleanField(label=_('Yayınla'), required=False, initial=False)
    requires_api_key = forms.BooleanField(label=_('API Anahtarı Gerekli'), required=False, initial=True)

    def __init__(self):
        # Mevcut kod...
        
        # Görev istatistikleri
        self.task_stats = {
            "total_completed": 0,
            "daily_completed": 0,
            "weekly_completed": 0,
            "streak_days": 0,  # Üst üste görev tamamlama
            "best_streak": 0
        }
        
        # Devam eden kod...
    
    def check_daily_task_completion(self, task_type, amount=1):
        # Mevcut kod...
        
        if task["progress"] >= task["target"]:
            # Mevcut kod...
            
            # İstatistikleri güncelle
            self.task_stats["total_completed"] += 1
            self.task_stats["daily_completed"] += 1
            
            # Başarım kontrolü
            if self.task_stats["total_completed"] == 10:
                self.award_badge("Görev Meraklısı")
            elif self.task_stats["total_completed"] == 50:
                self.award_badge("Görev Ustası")
            elif self.task_stats["total_completed"] == 100:
                self.award_badge("Görev Efsanesi")
            
            # Devam eden kod...
    
    def award_badge(self, badge_name):
        """Yeni rozet verir"""
        if badge_name not in self.badges:
            self.badges.append(badge_name)
            self.info_text.text += f"\nYeni Rozet: {badge_name}!"
            self.play_sound('achievement')

    def __init__(self):
        # Mevcut kod...
        
        # Haftalık görevleri tanımla
        self.weekly_tasks = []
        self.weekly_task_reset_day = 1  # Pazartesi
        self.last_weekly_task_reset = 0
        
        # Devam eden kod...
    
    def advance_day(self):
        # Mevcut kod...
        
        # Gün sırasına göre haftanın gününü hesapla (0 = Pazartesi, 6 = Pazar)
        weekday = self.day % 7
        
        # Pazartesi günü ve son sıfırlamadan bu yana 7 gün geçtiyse haftalık görevleri sıfırla
        if weekday == self.weekly_task_reset_day and (self.day - self.last_weekly_task_reset) >= 7:
            self.generate_weekly_tasks()
            self.last_weekly_task_reset = self.day
            
        # Devam eden kod...
    
    def generate_weekly_tasks(self):
        """Haftalık görevler oluşturur"""
        self.weekly_tasks = []  # Önceki görevleri temizle
        
        # Haftalık görev listesi (daha zorlu ve büyük ödüllü)
        possible_weekly_tasks = [
            {"type": "trade_volume", "description": "Haftalık 50,000₺ işlem hacmine ulaş", "target": 50000, "reward_xp": 100, "reward_money": 2000},
            {"type": "portfolio_value", "description": "Portföy değerini 100,000₺'ye çıkar", "target": 100000, "reward_xp": 150, "reward_money": 3000},
            {"type": "followers", "description": "Toplam 200 takipçiye ulaş", "target": 200, "reward_xp": 80, "reward_money": 1500},
            # Daha fazla haftalık görev...
        ]
        
        # Rastgele 2 haftalık görev seç
        selected_tasks = random.sample(possible_weekly_tasks, 2)
        
        for task in selected_tasks:
            task["progress"] = 0
            task["completed"] = False
            self.weekly_tasks.append(task)
        
        # Haftalık görevleri bildirme
        self.queue_dialogue("Sistem", "Yeni haftalık görevler yayınlandı! Bu görevler daha zorlu ancak ödülleri de büyük.", "mentor")

    def generate_daily_tasks(self):
        # Mevcut kod...
        
        # Görev zorluklarına göre kategoriler
        easy_tasks = [
            {"type": "watch_news", "description": "Ekonomi haberleri izle", "target": 1, "reward_xp": 5, "reward_money": 30},
            # Diğer kolay görevler...
        ]
        
        medium_tasks = [
            {"type": "buy_stocks", "description": "Herhangi bir şirketten en az 10 hisse al", "target": 10, "reward_xp": 15, "reward_money": 100},
            # Diğer orta zorlukta görevler...
        ]
        
        hard_tasks = [
            {"type": "earn_money", "description": "Günde en az 5000₺ kazan", "target": 5000, "reward_xp": 50, "reward_money": 1000},
            # Diğer zor görevler...
        ]
        
        # Her zorluk seviyesinden birer görev seç
        selected_tasks = []
        selected_tasks.append(random.choice(easy_tasks))
        selected_tasks.append(random.choice(medium_tasks))
        if self.level > 5:  # Seviye 5'ten sonra zor görevler de ekle
            selected_tasks.append(random.choice(hard_tasks))
        
        # Devam eden kod... 

# Dil seçenekleri ve çoklu dil desteği için form sınıfları

class LanguagePreferenceForm(forms.Form):
    """Kullanıcı dil tercihleri formu"""
    LANGUAGE_CHOICES = [
        ('tr', _('Türkçe')),
        ('en', _('İngilizce')),
        ('de', _('Almanca')),
        ('fr', _('Fransızca')),
        ('ar', _('Arapça')),
        ('ru', _('Rusça')),
        ('es', _('İspanyolca'))
    ]
    
    language = forms.ChoiceField(
        label=_('Tercih Edilen Dil'),
        choices=LANGUAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'onchange': 'this.form.submit()'})
    )
    
    default_language = forms.BooleanField(
        label=_('Bu dili varsayılan olarak ayarla'),
        required=False,
        initial=True,
        help_text=_('Bu ayar, tüm oturumlarınızda seçilen dili kullanmanızı sağlar.')
    )


class ContentTranslationForm(forms.Form):
    """İçerik çeviri formu"""
    title = forms.CharField(
        label=_('Başlık'),
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    content = forms.CharField(
        label=_('İçerik'),
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )
    language = forms.ChoiceField(
        label=_('Dil'),
        choices=LanguagePreferenceForm.LANGUAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    source_content_id = forms.IntegerField(widget=forms.HiddenInput())
    source_content_type = forms.CharField(widget=forms.HiddenInput())
    
    def clean(self):
        cleaned_data = super().clean()
        # Aynı dilde aynı içeriğin çevirisinin olmamasını kontrol et
        # Bu kontrol, views.py'de model verilerine göre yapılacak
        return cleaned_data


class GameLanguageSettingsForm(forms.Form):
    """Oyun dil ayarları formu"""
    interface_language = forms.ChoiceField(
        label=_('Arayüz Dili'),
        choices=LanguagePreferenceForm.LANGUAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    subtitle_language = forms.ChoiceField(
        label=_('Altyazı Dili'),
        choices=LanguagePreferenceForm.LANGUAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    voice_language = forms.ChoiceField(
        label=_('Ses Dili'),
        choices=LanguagePreferenceForm.LANGUAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    show_subtitles = forms.BooleanField(
        label=_('Altyazıları Göster'),
        required=False,
        initial=True
    )
    
    apply_to_all_games = forms.BooleanField(
        label=_('Tüm oyunlara uygula'),
        required=False,
        initial=False,
        help_text=_('Bu ayarları platformdaki tüm oyunlar için kullan')
    )


class TranslationImportForm(forms.Form):
    """Çeviri dosyası içe aktarma formu"""
    file = forms.FileField(
        label=_('Çeviri Dosyası (.po veya .json)'),
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.po,.json'})
    )
    
    language = forms.ChoiceField(
        label=_('Dil'),
        choices=LanguagePreferenceForm.LANGUAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    overwrite_existing = forms.BooleanField(
        label=_('Mevcut çevirilerin üzerine yaz'),
        required=False,
        initial=False
    )


class TranslationExportForm(forms.Form):
    """Çeviri dosyası dışa aktarma formu"""
    language = forms.ChoiceField(
        label=_('Dil'),
        choices=LanguagePreferenceForm.LANGUAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    format_choices = [
        ('po', 'PO (Gettext)'),
        ('json', 'JSON'),
        ('xlsx', 'Excel')
    ]
    
    export_format = forms.ChoiceField(
        label=_('Dışa Aktarma Formatı'),
        choices=format_choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    include_fuzzy = forms.BooleanField(
        label=_('Yaklaşık çevirileri dahil et'),
        required=False,
        initial=True
    )


class TranslatableModelForm(forms.ModelForm):
    """Çevrilebilir model form temel sınıfı"""
    
    def __init__(self, *args, **kwargs):
        # Mevcut dil bilgisini al
        self.language = kwargs.pop('language', None)
        super().__init__(*args, **kwargs)
        
        # Çevrilebilir alanlar için çoklu dil desteği
        if hasattr(self, 'translatable_fields'):
            for field_name in self.translatable_fields:
                if field_name in self.fields:
                    # Orijinal alanı yedekle
                    original_field = self.fields[field_name]
                    
                    # Dil seçeneklerini ekle (varsayılan dil için gizli alan olarak)
                    self.fields[f'{field_name}_language'] = forms.ChoiceField(
                        label=_('Dil'),
                        choices=LanguagePreferenceForm.LANGUAGE_CHOICES,
                        initial=self.language or 'tr',
                        required=False,
                        widget=forms.HiddenInput() if not self.language else forms.Select(attrs={'class': 'form-select mb-2'})
                    )


class DailyTaskMultiLanguageForm(TranslatableModelForm):
    """Çok dilli günlük görev formu"""
    
    translatable_fields = ['title', 'description', 'steps']
    
    class Meta:
        model = DailyTask
        fields = [
            'title', 'description', 'category', 'difficulty', 
            'xp_reward', 'money_reward', 'steps', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'xp_reward': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'money_reward': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'steps': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': _('Her satır bir adımı temsil eder')}),
        }
    
    def clean_steps(self):
        """Adımları temizler ve JSON formatına dönüştürür"""
        steps_text = self.cleaned_data.get('steps', '')
        if not steps_text:
            return []
        
        # Her satırı bir adım olarak al
        steps_list = []
        for i, line in enumerate(steps_text.splitlines()):
            line = line.strip()
            if line:
                steps_list.append({
                    'order': i,
                    'description': line,
                    'completed': False
                })
        
        return steps_list


class KnowledgeBaseMultiLanguageForm(TranslatableModelForm):
    """Çok dilli bilgi bankası formu"""
    
    translatable_fields = ['title', 'content', 'summary']
    
    class Meta:
        model = KnowledgeBase
        fields = [
            'title', 'content', 'summary', 'category', 
            'level', 'image', 'tags', 'active', 'is_featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Başlık')}),
            'content': forms.Textarea(attrs={'class': 'form-control ckeditor', 'rows': 5}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Özet')}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Etiketler (virgülle ayır)')}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        } 