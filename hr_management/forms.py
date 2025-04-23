from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Employee, Department, Salary, Payroll, Leave

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'identity_number', 'birth_date',
            'gender', 'marital_status', 'address', 'phone', 'email',
            'emergency_contact', 'emergency_phone', 'hire_date',
            'department', 'position', 'employment_status',
            'bank_account', 'iban', 'is_active'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'first_name': _('Ad'),
            'last_name': _('Soyad'),
            'identity_number': _('TC Kimlik No'),
            'birth_date': _('Doğum Tarihi'),
            'gender': _('Cinsiyet'),
            'marital_status': _('Medeni Hal'),
            'address': _('Adres'),
            'phone': _('Telefon'),
            'email': _('E-posta'),
            'emergency_contact': _('Acil Durum İletişim Kişisi'),
            'emergency_phone': _('Acil Durum Telefonu'),
            'hire_date': _('İşe Başlama Tarihi'),
            'department': _('Departman'),
            'position': _('Pozisyon'),
            'employment_status': _('Çalışma Durumu'),
            'bank_account': _('Banka Hesabı'),
            'iban': _('IBAN'),
            'is_active': _('Aktif'),
        }

    def clean_identity_number(self):
        identity_number = self.cleaned_data['identity_number']
        if not identity_number.isdigit() or len(identity_number) != 11:
            raise forms.ValidationError(_('Geçerli bir TC Kimlik Numarası giriniz.'))
        return identity_number

    def clean_email(self):
        email = self.cleaned_data['email']
        if Employee.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError(_('Bu e-posta adresi zaten kullanılıyor.'))
        return email

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'parent', 'manager', 'budget', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'name': _('Departman Adı'),
            'code': _('Departman Kodu'),
            'parent': _('Üst Departman'),
            'manager': _('Departman Müdürü'),
            'budget': _('Bütçe'),
            'description': _('Açıklama'),
        }

    def clean_code(self):
        code = self.cleaned_data['code']
        if Department.objects.filter(code=code).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError(_('Bu departman kodu zaten kullanılıyor.'))
        return code

class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = ['employee', 'base_salary', 'effective_date', 'currency', 'payment_frequency']
        widgets = {
            'effective_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'employee': _('Çalışan'),
            'base_salary': _('Baz Maaş'),
            'effective_date': _('Geçerlilik Tarihi'),
            'currency': _('Para Birimi'),
            'payment_frequency': _('Ödeme Sıklığı'),
        }

    def clean_base_salary(self):
        base_salary = self.cleaned_data['base_salary']
        if base_salary <= 0:
            raise forms.ValidationError(_('Maaş 0\'dan büyük olmalıdır.'))
        return base_salary

class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = [
            'employee', 'period_start', 'period_end', 'base_salary',
            'overtime_hours', 'overtime_pay', 'bonus', 'deductions',
            'net_salary', 'gross_salary', 'payment_date', 'payment_status',
            'payment_reference', 'notes'
        ]
        widgets = {
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'employee': _('Çalışan'),
            'period_start': _('Dönem Başlangıcı'),
            'period_end': _('Dönem Bitişi'),
            'base_salary': _('Baz Maaş'),
            'overtime_hours': _('Fazla Mesai Saati'),
            'overtime_pay': _('Fazla Mesai Ücreti'),
            'bonus': _('Bonus'),
            'deductions': _('Kesintiler'),
            'net_salary': _('Net Maaş'),
            'gross_salary': _('Brüt Maaş'),
            'payment_date': _('Ödeme Tarihi'),
            'payment_status': _('Ödeme Durumu'),
            'payment_reference': _('Ödeme Referansı'),
            'notes': _('Notlar'),
        }

    def clean(self):
        cleaned_data = super().clean()
        period_start = cleaned_data.get('period_start')
        period_end = cleaned_data.get('period_end')
        
        if period_start and period_end and period_start > period_end:
            raise forms.ValidationError(_('Dönem başlangıcı, dönem bitişinden sonra olamaz.'))

        return cleaned_data

class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['employee', 'leave_type', 'start_date', 'end_date', 'total_days', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'employee': _('Çalışan'),
            'leave_type': _('İzin Tipi'),
            'start_date': _('Başlangıç Tarihi'),
            'end_date': _('Bitiş Tarihi'),
            'total_days': _('Toplam Gün'),
            'reason': _('Sebep'),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        total_days = cleaned_data.get('total_days')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(_('Başlangıç tarihi, bitiş tarihinden sonra olamaz.'))
        
        if start_date and end_date and total_days:
            calculated_days = (end_date - start_date).days + 1
            if calculated_days != total_days:
                raise forms.ValidationError(_('Toplam gün sayısı, tarih aralığına uygun olmalıdır.'))

        return cleaned_data

class LeaveApprovalForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['status', 'rejection_reason']
        widgets = {
            'rejection_reason': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'status': _('Durum'),
            'rejection_reason': _('Red Sebebi'),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        if status == 'R' and not rejection_reason:
            raise forms.ValidationError(_('Red durumunda red sebebi belirtilmelidir.'))

        return cleaned_data 