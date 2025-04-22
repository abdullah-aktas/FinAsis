from django import forms
from django.utils.translation import gettext_lazy as _
from .models import IntegrationProvider, IntegrationTemplate, Integration, WebhookEndpoint

class IntegrationProviderForm(forms.ModelForm):
    class Meta:
        model = IntegrationProvider
        fields = ['name', 'description', 'api_base_url', 'api_version', 'documentation_url', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'documentation_url': forms.URLInput(attrs={'placeholder': 'https://'}),
        }

class IntegrationTemplateForm(forms.ModelForm):
    class Meta:
        model = IntegrationTemplate
        fields = ['name', 'provider', 'category', 'description', 'icon', 'configuration_schema', 'default_settings', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'configuration_schema': forms.Textarea(attrs={'rows': 10}),
            'default_settings': forms.Textarea(attrs={'rows': 10}),
        }

    def clean_configuration_schema(self):
        schema = self.cleaned_data.get('configuration_schema')
        try:
            # JSON Schema doğrulama
            import jsonschema
            jsonschema.Draft7Validator(schema)
        except Exception as e:
            raise forms.ValidationError(_('Geçersiz JSON Schema formatı: {}').format(str(e)))
        return schema

    def clean_default_settings(self):
        settings = self.cleaned_data.get('default_settings')
        try:
            # JSON doğrulama
            import json
            json.dumps(settings)
        except Exception as e:
            raise forms.ValidationError(_('Geçersiz JSON formatı: {}').format(str(e)))
        return settings

class IntegrationForm(forms.ModelForm):
    class Meta:
        model = Integration
        fields = ['name', 'provider', 'template', 'integration_type', 'api_key', 'api_secret', 'webhook_url', 'settings', 'is_active']
        widgets = {
            'settings': forms.Textarea(attrs={'rows': 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Template seçildiğinde varsayılan ayarları yükle
        if 'template' in self.data:
            try:
                template_id = int(self.data.get('template'))
                template = IntegrationTemplate.objects.get(id=template_id)
                self.fields['settings'].initial = template.default_settings
            except (ValueError, IntegrationTemplate.DoesNotExist):
                pass
        elif self.instance.pk and self.instance.template:
            self.fields['settings'].initial = self.instance.template.default_settings

    def clean_settings(self):
        settings = self.cleaned_data.get('settings')
        try:
            # JSON doğrulama
            import json
            json.dumps(settings)
        except Exception as e:
            raise forms.ValidationError(_('Geçersiz JSON formatı: {}').format(str(e)))
        return settings

class WebhookEndpointForm(forms.ModelForm):
    class Meta:
        model = WebhookEndpoint
        fields = ['name', 'integration', 'endpoint_url', 'secret_key', 'is_active']
        widgets = {
            'secret_key': forms.PasswordInput(render_value=True),
        }

    def clean_secret_key(self):
        secret_key = self.cleaned_data.get('secret_key')
        if not secret_key and not self.instance.pk:
            # Yeni endpoint için otomatik gizli anahtar oluştur
            import secrets
            secret_key = secrets.token_urlsafe(32)
        return secret_key 