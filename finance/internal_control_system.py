# -*- coding: utf-8 -*-
# type: ignore[reportAttributeAccessIssue]
"""
FinAsis - İç Denetim ve Kontrol Sistemleri
GRC (Governance, Risk & Compliance) modülleri
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.conf import settings as dj_settings
import uuid

from accounting.models import Company


class AuditTrail(models.Model):
    """
    Kapsamlı Denetim İzi (Audit Trail)
    Tüm sistem işlemlerinin kayıt altına alınması
    """

    ACTION_TYPES = [
        ("CREATE", _("Oluştur")),
        ("UPDATE", _("Güncelle")),
        ("DELETE", _("Sil")),
        ("VIEW", _("Görüntüle")),
        ("EXPORT", _("Dışa Aktar")),
        ("PRINT", _("Yazdır")),
        ("LOGIN", _("Giriş")),
        ("LOGOUT", _("Çıkış")),
        ("APPROVE", _("Onayla")),
        ("REJECT", _("Reddet")),
        ("CANCEL", _("İptal Et")),
        ("POST", _("Kaydet")),
        ("UNPOST", _("Kaydı Geri Al")),
    ]

    RISK_LEVELS = [
        ("LOW", _("Düşük")),
        ("MEDIUM", _("Orta")),
        ("HIGH", _("Yüksek")),
        ("CRITICAL", _("Kritik")),
    ]

    # Temel bilgiler
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="audit_trails"
    )
    user = models.ForeignKey(
        dj_settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    session_id = models.CharField(_("Oturum ID"), max_length=100, blank=True)

    # İşlem bilgileri
    action_type = models.CharField(_("İşlem Tipi"), max_length=20, choices=ACTION_TYPES)
    table_name = models.CharField(_("Tablo Adı"), max_length=100)
    record_id = models.CharField(_("Kayıt ID"), max_length=100)

    # İçerik tipi için generic foreign key
    content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    # Değişiklik bilgileri
    old_values = models.JSONField(_("Eski Değerler"), default=dict, blank=True)
    new_values = models.JSONField(_("Yeni Değerler"), default=dict, blank=True)
    changed_fields = models.JSONField(_("Değişen Alanlar"), default=list, blank=True)

    # Güvenlik bilgileri
    ip_address = models.GenericIPAddressField(_("IP Adresi"), null=True, blank=True)
    user_agent = models.TextField(_("Tarayıcı Bilgisi"), blank=True)
    risk_level = models.CharField(
        _("Risk Seviyesi"), max_length=20, choices=RISK_LEVELS, default="LOW"
    )

    # İşlem detayları
    description = models.TextField(_("Açıklama"), blank=True)
    module_name = models.CharField(_("Modül Adı"), max_length=100, blank=True)
    function_name = models.CharField(_("Fonksiyon Adı"), max_length=100, blank=True)

    # Başarı durumu
    success = models.BooleanField(_("Başarılı"), default=True)
    error_message = models.TextField(_("Hata Mesajı"), blank=True)

    # Zaman bilgileri
    timestamp = models.DateTimeField(_("Zaman"), auto_now_add=True)
    duration_ms = models.PositiveIntegerField(_("Süre (ms)"), null=True, blank=True)

    class Meta:
        app_label = "finance"
        verbose_name = _("Denetim İzi")
        verbose_name_plural = _("Denetim İzleri")
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["company", "timestamp"]),
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["table_name", "record_id"]),
            models.Index(fields=["action_type", "timestamp"]),
            models.Index(fields=["risk_level", "timestamp"]),
        ]

    def __str__(self):
        return (
            f"{self.user} - {self.action_type} - {self.table_name} ({self.timestamp})"
        )

    @classmethod
    def log_action(
        cls,
        user,
        company,
        action_type,
        obj=None,
        old_values=None,
        new_values=None,
        description="",
        ip_address=None,
        user_agent="",
        **kwargs,
    ):
        """İşlem kaydı oluştur"""

        audit_entry = cls(
            company=company,
            user=user,
            action_type=action_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            **kwargs,
        )

        if obj:
            audit_entry.content_object = obj
            audit_entry.table_name = obj._meta.model_name
            audit_entry.record_id = str(obj.pk)

        if old_values:
            audit_entry.old_values = old_values
        if new_values:
            audit_entry.new_values = new_values

        # Değişen alanları tespit et
        if old_values and new_values:
            changed_fields = []
            for key, new_value in new_values.items():
                old_value = old_values.get(key)
                if old_value != new_value:
                    changed_fields.append(key)
            audit_entry.changed_fields = changed_fields

        # Risk seviyesini belirle
        audit_entry.risk_level = cls._determine_risk_level(
            action_type, audit_entry.table_name
        )

        audit_entry.save()
        return audit_entry

    @staticmethod
    def _determine_risk_level(action_type, table_name):
        """Risk seviyesini belirle"""
        # Kritik işlemler
        if action_type in ["DELETE", "UNPOST"] or table_name in [
            "journal_voucher",
            "payment",
            "invoice",
        ]:
            return "CRITICAL"
        elif action_type in ["UPDATE", "APPROVE", "POST"]:
            return "HIGH"
        elif action_type in ["CREATE", "CANCEL"]:
            return "MEDIUM"
        else:
            return "LOW"


class UserPermission(models.Model):
    """
    Kullanıcı İzin Matrisi
    Rol bazlı erişim kontrolü (RBAC)
    """

    PERMISSION_TYPES = [
        ("READ", _("Okuma")),
        ("CREATE", _("Oluşturma")),
        ("UPDATE", _("Güncelleme")),
        ("DELETE", _("Silme")),
        ("APPROVE", _("Onaylama")),
        ("EXPORT", _("Dışa Aktarma")),
        ("REPORT", _("Raporlama")),
        ("ADMIN", _("Yönetici")),
    ]

    user = models.ForeignKey(
        dj_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="custom_permissions",
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="user_permissions"
    )

    # İzin detayları
    module_name = models.CharField(
        _("Modül Adı"), max_length=100, help_text="accounting, finance, inventory vb."
    )
    permission_type = models.CharField(
        _("İzin Tipi"), max_length=20, choices=PERMISSION_TYPES
    )

    # Kısıtlamalar
    amount_limit = models.DecimalField(
        _("Tutar Limiti"),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Bu tutarın üstündeki işlemlerde izin yok",
    )
    date_restriction = models.CharField(
        _("Tarih Kısıtı"),
        max_length=50,
        blank=True,
        help_text="current_month, last_3_months, current_year vb.",
    )

    # Geçerlilik
    valid_from = models.DateTimeField(_("Geçerlilik Başlangıcı"), default=timezone.now)
    valid_to = models.DateTimeField(_("Geçerlilik Bitişi"), null=True, blank=True)
    is_active = models.BooleanField(_("Aktif"), default=True)

    # Onay bilgileri
    granted_by = models.ForeignKey(
        dj_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="granted_permissions",
        verbose_name=_("İzin Veren"),
    )
    granted_at = models.DateTimeField(_("İzin Verme Zamanı"), auto_now_add=True)
    reason = models.TextField(_("Gerekçe"), blank=True)

    class Meta:
        app_label = "finance"
        verbose_name = _("Kullanıcı İzni")
        verbose_name_plural = _("Kullanıcı İzinleri")
        unique_together = [["user", "company", "module_name", "permission_type"]]

    def __str__(self):
        try:
            permission_display = self.get_permission_type_display()
        except (AttributeError, Exception):
            permission_display = self.permission_type
        return f"{self.user.username} - {self.module_name} - {permission_display}"

    def is_valid(self):
        """İznin geçerli olup olmadığını kontrol et"""
        now = timezone.now()
        return (
            self.is_active
            and self.valid_from <= now
            and (self.valid_to is None or self.valid_to >= now)
        )

    def check_amount_limit(self, amount):
        """Tutar limitini kontrol et"""
        if self.amount_limit is None:
            return True
        return amount <= self.amount_limit


class ApprovalWorkflow(models.Model):
    """
    Onay İş Akışı
    Çok seviyeli onay süreçleri
    """

    WORKFLOW_TYPES = [
        ("VOUCHER_APPROVAL", _("Fiş Onayı")),
        ("PAYMENT_APPROVAL", _("Ödeme Onayı")),
        ("PURCHASE_APPROVAL", _("Satın Alma Onayı")),
        ("BUDGET_APPROVAL", _("Bütçe Onayı")),
        ("USER_ACCESS", _("Kullanıcı Erişimi")),
        ("REPORT_ACCESS", _("Rapor Erişimi")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="approval_workflows"
    )
    name = models.CharField(_("İş Akışı Adı"), max_length=100)
    workflow_type = models.CharField(
        _("İş Akışı Tipi"), max_length=30, choices=WORKFLOW_TYPES
    )

    # Tetikleme koşulları
    min_amount = models.DecimalField(
        _("Minimum Tutar"), max_digits=15, decimal_places=2, null=True, blank=True
    )
    max_amount = models.DecimalField(
        _("Maksimum Tutar"), max_digits=15, decimal_places=2, null=True, blank=True
    )
    applicable_modules = models.JSONField(
        _("Geçerli Modüller"), default=list, blank=True
    )

    # İş akışı ayarları
    is_sequential = models.BooleanField(
        _("Sıralı Onay"),
        default=True,
        help_text="True: Sırayla onay, False: Paralel onay",
    )
    require_all_approvers = models.BooleanField(
        _("Tüm Onaylayanlar Gerekli"), default=True
    )

    is_active = models.BooleanField(_("Aktif"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "finance"
        verbose_name = _("Onay İş Akışı")
        verbose_name_plural = _("Onay İş Akışları")
        ordering = ["name"]

    def __str__(self):
        try:
            workflow_display = self.get_workflow_type_display()
        except (AttributeError, Exception):
            workflow_display = self.workflow_type
        return f"{self.name} ({workflow_display})"

    def get_next_approver(self, current_step=0):
        """Sonraki onaylayıcıyı al"""
        try:
            steps = self.workflow_steps.filter(is_active=True).order_by("step_order")
        except (AttributeError, Exception):
            # workflow_steps relation eksikse boş liste döndür
            return None

        if current_step < len(steps):
            return steps[current_step]
        return None

    def is_applicable(self, amount=None, module_name=None):
        """İş akışının geçerli olup olmadığını kontrol et"""
        if not self.is_active:
            return False

        # Tutar kontrolü
        if amount is not None:
            if self.min_amount is not None and amount < self.min_amount:
                return False
            if self.max_amount is not None and amount > self.max_amount:
                return False

        # Modül kontrolü
        if module_name and self.applicable_modules:
            if module_name not in self.applicable_modules:
                return False

        return True


class ApprovalWorkflowStep(models.Model):
    """Onay İş Akışı Adımları"""

    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.CASCADE,
        related_name="workflow_steps",
        verbose_name=_("İş Akışı"),
    )
    step_order = models.PositiveIntegerField(_("Adım Sırası"))
    step_name = models.CharField(_("Adım Adı"), max_length=100)

    # Onaylayıcı bilgileri
    approver_user = models.ForeignKey(
        dj_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Onaylayıcı Kullanıcı"),
    )
    approver_role = models.CharField(
        _("Onaylayıcı Rolü"),
        max_length=100,
        blank=True,
        help_text="Belirli bir role sahip herhangi bir kullanıcı",
    )

    # Adım ayarları
    is_mandatory = models.BooleanField(_("Zorunlu"), default=True)
    timeout_hours = models.PositiveIntegerField(_("Zaman Aşımı (Saat)"), default=24)
    auto_approve_after_timeout = models.BooleanField(
        _("Zaman Aşımında Otomatik Onay"), default=False
    )

    # Koşullar
    condition_expression = models.TextField(
        _("Koşul İfadesi"),
        blank=True,
        help_text="Python ifadesi: amount > 10000, user.department == 'finance'",
    )

    is_active = models.BooleanField(_("Aktif"), default=True)

    class Meta:
        app_label = "finance"
        verbose_name = _("İş Akışı Adımı")
        verbose_name_plural = _("İş Akışı Adımları")
        unique_together = [["workflow", "step_order"]]
        ordering = ["step_order"]

    def __str__(self):
        return f"{self.workflow.name} - Adım {self.step_order}: {self.step_name}"

    def get_approver_users(self):
        """Onaylayıcı kullanıcıları al"""
        users = []

        if self.approver_user:
            users.append(self.approver_user)

        # Rol bazlı onaylayıcılar (gelecekte genişletilebilir)
        # if self.approver_role:
        #     role_users = User.objects.filter(groups__name=self.approver_role)
        #     users.extend(role_users)

        return users

    def check_condition(self, context):
        """Koşulu kontrol et"""
        if not self.condition_expression:
            return True

        try:
            # Güvenli değerlendirme için basit koşullar
            # Gerçek uygulamada daha güvenli bir parser kullanılmalı
            # nosec: B307 - Internal control system, limited context
            return eval(  # noqa: B307
                self.condition_expression, {"__builtins__": {}}, context
            )
        except (AttributeError, Exception):
            return False


class ApprovalRequest(models.Model):
    """Onay Talebi"""

    STATUS_CHOICES = [
        ("PENDING", _("Beklemede")),
        ("IN_PROGRESS", _("İşlemde")),
        ("APPROVED", _("Onaylandı")),
        ("REJECTED", _("Reddedildi")),
        ("CANCELLED", _("İptal Edildi")),
        ("TIMEOUT", _("Zaman Aşımı")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="approval_requests"
    )
    workflow = models.ForeignKey(
        ApprovalWorkflow, on_delete=models.PROTECT, related_name="approval_requests"
    )

    # Talep bilgileri
    request_id = models.UUIDField(_("Talep ID"), default=uuid.uuid4, unique=True)
    title = models.CharField(_("Başlık"), max_length=200)
    description = models.TextField(_("Açıklama"))

    # İlgili nesne
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="finance_approval_requests"
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    # Talep eden
    requested_by = models.ForeignKey(
        dj_settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="approval_requests",
        verbose_name=_("Talep Eden"),
    )
    requested_at = models.DateTimeField(_("Talep Zamanı"), auto_now_add=True)

    # Durum
    status = models.CharField(
        _("Durum"), max_length=20, choices=STATUS_CHOICES, default="PENDING"
    )
    current_step = models.PositiveIntegerField(_("Mevcut Adım"), default=0)

    # Tutar bilgisi (iş akışı kontrolü için)
    amount = models.DecimalField(
        _("Tutar"), max_digits=15, decimal_places=2, null=True, blank=True
    )

    # Tamamlanma bilgileri
    completed_at = models.DateTimeField(_("Tamamlanma Zamanı"), null=True, blank=True)
    final_decision = models.TextField(_("Nihai Karar"), blank=True)

    class Meta:
        app_label = "finance"
        verbose_name = _("Onay Talebi")
        verbose_name_plural = _("Onay Talepleri")
        ordering = ["-requested_at"]

    def __str__(self):
        try:
            status_display = self.get_status_display()
        except (AttributeError, Exception):
            status_display = self.status
        return f"{self.title} - {status_display}"

    def process_next_step(self):
        """Sonraki adımı işle"""
        next_step = self.workflow.get_next_approver(self.current_step)

        if not next_step:
            # Tüm adımlar tamamlandı
            self.status = "APPROVED"
            self.completed_at = timezone.now()
            self.save()
            return True

        # Sonraki adım için onay kaydı oluştur
        for approver in next_step.get_approver_users():
            ApprovalRecord.objects.create(
                request=self,
                workflow_step=next_step,
                approver=approver,
                due_date=timezone.now()
                + timezone.timedelta(hours=next_step.timeout_hours),
            )

        self.current_step += 1
        self.status = "IN_PROGRESS"
        self.save()

        return False

    def approve(self, user, comments=""):
        """Onaylama işlemi"""
        # Mevcut adımdaki onay kaydını bul ve güncelle
        approval_record = self.approval_records.filter(
            workflow_step__step_order=self.current_step, approver=user, status="PENDING"
        ).first()

        if approval_record:
            approval_record.approve(comments)

            # Bu adımdaki tüm gerekli onaylar tamamlandı mı?
            step = approval_record.workflow_step
            if self._is_step_completed(step):
                self.process_next_step()

    def reject(self, user, comments=""):
        """Reddetme işlemi"""
        approval_record = self.approval_records.filter(
            workflow_step__step_order=self.current_step, approver=user, status="PENDING"
        ).first()

        if approval_record:
            approval_record.reject(comments)
            self.status = "REJECTED"
            self.completed_at = timezone.now()
            self.final_decision = (
                f"Reddeden: {user.get_full_name()}\nGerekçe: {comments}"
            )
            self.save()

    def _is_step_completed(self, step):
        """Adımın tamamlanıp tamamlanmadığını kontrol et"""
        step_records = self.approval_records.filter(workflow_step=step)

        if step.workflow.require_all_approvers:
            # Tüm onaylayanların onayı gerekli
            return step_records.filter(status="PENDING").count() == 0
        else:
            # En az bir onaylayıcının onayı yeterli
            return step_records.filter(status="APPROVED").exists()


class ApprovalRecord(models.Model):
    """Onay Kaydı"""

    STATUS_CHOICES = [
        ("PENDING", _("Beklemede")),
        ("APPROVED", _("Onaylandı")),
        ("REJECTED", _("Reddedildi")),
        ("TIMEOUT", _("Zaman Aşımı")),
    ]

    request = models.ForeignKey(
        ApprovalRequest,
        on_delete=models.CASCADE,
        related_name="approval_records",
        verbose_name=_("Onay Talebi"),
    )
    workflow_step = models.ForeignKey(
        ApprovalWorkflowStep, on_delete=models.PROTECT, verbose_name=_("İş Akışı Adımı")
    )
    approver = models.ForeignKey(
        dj_settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_("Onaylayıcı"),
    )

    status = models.CharField(
        _("Durum"), max_length=20, choices=STATUS_CHOICES, default="PENDING"
    )
    due_date = models.DateTimeField(_("Vade Tarihi"))

    # Karar bilgileri
    decision_date = models.DateTimeField(_("Karar Tarihi"), null=True, blank=True)
    comments = models.TextField(_("Yorumlar"), blank=True)

    # Bildirim durumu
    notification_sent = models.BooleanField(_("Bildirim Gönderildi"), default=False)
    reminder_count = models.PositiveIntegerField(_("Hatırlatma Sayısı"), default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "finance"
        verbose_name = _("Onay Kaydı")
        verbose_name_plural = _("Onay Kayıtları")
        ordering = ["-created_at"]

    def __str__(self):
        try:
            status_display = self.get_status_display()
        except (AttributeError, Exception):
            status_display = self.status
        return (
            f"{self.request.title} - {self.approver.get_full_name()} - {status_display}"
        )

    def approve(self, comments=""):
        """Onayla"""
        self.status = "APPROVED"
        self.decision_date = timezone.now()
        self.comments = comments
        self.save()

        # Audit log
        AuditTrail.log_action(
            user=self.approver,
            company=self.request.company,
            action_type="APPROVE",
            obj=self.request.content_object,
            description=f"Onay talebi onaylandı: {self.request.title}",
        )

    def reject(self, comments=""):
        """Reddet"""
        self.status = "REJECTED"
        self.decision_date = timezone.now()
        self.comments = comments
        self.save()

        # Audit log
        AuditTrail.log_action(
            user=self.approver,
            company=self.request.company,
            action_type="REJECT",
            obj=self.request.content_object,
            description=f"Onay talebi reddedildi: {self.request.title}",
        )

    def is_overdue(self):
        """Vadesi geçmiş mi?"""
        return timezone.now() > self.due_date and self.status == "PENDING"


class RiskAssessment(models.Model):
    """
    Risk Değerlendirmesi
    Finansal ve operasyonel risk analizi
    """

    RISK_CATEGORIES = [
        ("FINANCIAL", _("Mali Risk")),
        ("OPERATIONAL", _("Operasyonel Risk")),
        ("COMPLIANCE", _("Uyum Riski")),
        ("STRATEGIC", _("Stratejik Risk")),
        ("TECHNOLOGY", _("Teknoloji Riski")),
        ("REPUTATION", _("İtibar Riski")),
    ]

    RISK_LEVELS = [
        ("VERY_LOW", _("Çok Düşük")),
        ("LOW", _("Düşük")),
        ("MEDIUM", _("Orta")),
        ("HIGH", _("Yüksek")),
        ("VERY_HIGH", _("Çok Yüksek")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="risk_assessments"
    )
    assessment_date = models.DateField(_("Değerlendirme Tarihi"))
    assessor = models.ForeignKey(
        dj_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Değerlendiren"),
    )

    # Risk tanımı
    risk_title = models.CharField(_("Risk Başlığı"), max_length=200)
    risk_description = models.TextField(_("Risk Açıklaması"))
    risk_category = models.CharField(
        _("Risk Kategorisi"), max_length=20, choices=RISK_CATEGORIES
    )

    # Risk seviyesi değerlendirmesi
    likelihood = models.CharField(
        _("Olasılık"),
        max_length=20,
        choices=RISK_LEVELS,
        help_text="Riskin gerçekleşme olasılığı",
    )
    impact = models.CharField(
        _("Etki"),
        max_length=20,
        choices=RISK_LEVELS,
        help_text="Gerçekleştiğinde yaratacağı etki",
    )

    # Hesaplanan risk skoru (1-25 arası)
    risk_score = models.PositiveIntegerField(_("Risk Skoru"), null=True, blank=True)
    overall_risk_level = models.CharField(
        _("Genel Risk Seviyesi"),
        max_length=20,
        choices=RISK_LEVELS,
        null=True,
        blank=True,
    )

    # Mali etki tahmini
    potential_financial_impact = models.DecimalField(
        _("Potansiyel Mali Etki"),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # Mevcut kontroller
    existing_controls = models.TextField(_("Mevcut Kontroller"), blank=True)
    control_effectiveness = models.CharField(
        _("Kontrol Etkinliği"), max_length=20, choices=RISK_LEVELS, default="MEDIUM"
    )

    # Önerilen aksiyonlar
    recommended_actions = models.TextField(_("Önerilen Aksiyonlar"), blank=True)
    action_priority = models.CharField(
        _("Aksiyon Önceliği"), max_length=20, choices=RISK_LEVELS, default="MEDIUM"
    )
    target_completion_date = models.DateField(
        _("Hedef Tamamlanma Tarihi"), null=True, blank=True
    )

    # Durum takibi
    status = models.CharField(
        _("Durum"),
        max_length=20,
        choices=[
            ("IDENTIFIED", _("Tespit Edildi")),
            ("UNDER_REVIEW", _("İncelemede")),
            ("ACTION_PLANNED", _("Aksiyon Planlandı")),
            ("IN_PROGRESS", _("Devam Ediyor")),
            ("MITIGATED", _("Azaltıldı")),
            ("ACCEPTED", _("Kabul Edildi")),
            ("CLOSED", _("Kapatıldı")),
        ],
        default="IDENTIFIED",
    )

    # Takip bilgileri
    next_review_date = models.DateField(
        _("Sonraki İnceleme Tarihi"), null=True, blank=True
    )
    responsible_person = models.ForeignKey(
        dj_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_risks",
        verbose_name=_("Sorumlu Kişi"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "finance"
        verbose_name = _("Risk Değerlendirmesi")
        verbose_name_plural = _("Risk Değerlendirmeleri")
        ordering = ["-assessment_date"]

    def __str__(self):
        try:
            risk_display = self.get_overall_risk_level_display()
        except (AttributeError, Exception):
            risk_display = self.overall_risk_level or "N/A"
        return f"{self.risk_title} - {risk_display}"

    def calculate_risk_score(self):
        """Risk skorunu hesapla"""
        likelihood_values = {
            "VERY_LOW": 1,
            "LOW": 2,
            "MEDIUM": 3,
            "HIGH": 4,
            "VERY_HIGH": 5,
        }
        impact_values = {
            "VERY_LOW": 1,
            "LOW": 2,
            "MEDIUM": 3,
            "HIGH": 4,
            "VERY_HIGH": 5,
        }

        likelihood_score = likelihood_values.get(self.likelihood, 3)
        impact_score = impact_values.get(self.impact, 3)

        self.risk_score = likelihood_score * impact_score

        # Genel risk seviyesini belirle
        if self.risk_score <= 5:
            self.overall_risk_level = "LOW"
        elif self.risk_score <= 10:
            self.overall_risk_level = "MEDIUM"
        elif self.risk_score <= 20:
            self.overall_risk_level = "HIGH"
        else:
            self.overall_risk_level = "VERY_HIGH"

        self.save(update_fields=["risk_score", "overall_risk_level"])

    def is_overdue_for_review(self):
        """İnceleme için vadesi geçmiş mi?"""
        if not self.next_review_date:
            return False
        return timezone.now().date() > self.next_review_date


class ControlActivity(models.Model):
    """
    Kontrol Faaliyeti
    İç kontrol sisteminin temel bileşenleri
    """

    CONTROL_TYPES = [
        ("PREVENTIVE", _("Önleyici")),
        ("DETECTIVE", _("Tespit Edici")),
        ("CORRECTIVE", _("Düzeltici")),
        ("COMPENSATING", _("Telafi Edici")),
    ]

    CONTROL_NATURE = [
        ("MANUAL", _("Manuel")),
        ("AUTOMATIC", _("Otomatik")),
        ("IT_DEPENDENT", _("BT Bağımlı")),
        ("IT_GENERAL", _("BT Genel")),
    ]

    FREQUENCY_CHOICES = [
        ("REAL_TIME", _("Gerçek Zamanlı")),
        ("DAILY", _("Günlük")),
        ("WEEKLY", _("Haftalık")),
        ("MONTHLY", _("Aylık")),
        ("QUARTERLY", _("Üç Aylık")),
        ("ANNUALLY", _("Yıllık")),
        ("ON_DEMAND", _("Talep Üzerine")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="control_activities"
    )
    risk_assessment = models.ForeignKey(
        RiskAssessment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="control_activities",
        verbose_name=_("İlgili Risk"),
    )

    # Kontrol tanımı
    control_id = models.CharField(_("Kontrol ID"), max_length=50, unique=True)
    control_name = models.CharField(_("Kontrol Adı"), max_length=200)
    control_description = models.TextField(_("Kontrol Açıklaması"))
    control_objective = models.TextField(_("Kontrol Amacı"))

    # Kontrol özellikleri
    control_type = models.CharField(
        _("Kontrol Tipi"), max_length=20, choices=CONTROL_TYPES
    )
    control_nature = models.CharField(
        _("Kontrol Doğası"), max_length=20, choices=CONTROL_NATURE
    )
    frequency = models.CharField(_("Sıklık"), max_length=20, choices=FREQUENCY_CHOICES)

    # Sorumluluk
    control_owner = models.ForeignKey(
        dj_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_controls",
        verbose_name=_("Kontrol Sahibi"),
    )
    control_performer = models.ForeignKey(
        dj_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_controls",
        verbose_name=_("Kontrol Uygulayıcısı"),
    )

    # Kontrol detayları
    control_procedure = models.TextField(_("Kontrol Prosedürü"))
    evidence_required = models.TextField(_("Gerekli Kanıt"), blank=True)

    # Etkinlik değerlendirmesi
    design_effectiveness = models.CharField(
        _("Tasarım Etkinliği"),
        max_length=20,
        choices=[
            ("EFFECTIVE", _("Etkili")),
            ("INEFFECTIVE", _("Etkisiz")),
            ("NOT_EVALUATED", _("Değerlendirilmedi")),
        ],
        default="NOT_EVALUATED",
    )

    operating_effectiveness = models.CharField(
        _("İşleyiş Etkinliği"),
        max_length=20,
        choices=[
            ("EFFECTIVE", _("Etkili")),
            ("INEFFECTIVE", _("Etkisiz")),
            ("NOT_EVALUATED", _("Değerlendirilmedi")),
        ],
        default="NOT_EVALUATED",
    )

    # Durum ve takip
    is_active = models.BooleanField(_("Aktif"), default=True)
    last_performed_date = models.DateField(
        _("Son Uygulama Tarihi"), null=True, blank=True
    )
    next_due_date = models.DateField(_("Sonraki Vade Tarihi"), null=True, blank=True)

    # İyileştirme önerileri
    improvement_recommendations = models.TextField(
        _("İyileştirme Önerileri"), blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "finance"
        verbose_name = _("Kontrol Faaliyeti")
        verbose_name_plural = _("Kontrol Faaliyetleri")
        ordering = ["control_id"]

    def __str__(self):
        return f"{self.control_id} - {self.control_name}"

    def calculate_next_due_date(self):
        """Sonraki vade tarihini hesapla"""
        if not self.last_performed_date:
            return

        frequency_days = {
            "DAILY": 1,
            "WEEKLY": 7,
            "MONTHLY": 30,
            "QUARTERLY": 90,
            "ANNUALLY": 365,
        }

        days_to_add = frequency_days.get(self.frequency, 30)
        self.next_due_date = self.last_performed_date + timezone.timedelta(
            days=days_to_add
        )
        self.save(update_fields=["next_due_date"])

    def is_overdue(self):
        """Vadesi geçmiş mi?"""
        if not self.next_due_date:
            return False
        return timezone.now().date() > self.next_due_date


class ControlExecution(models.Model):
    """Kontrol Uygulama Kaydı"""

    STATUS_CHOICES = [
        ("PASSED", _("Başarılı")),
        ("FAILED", _("Başarısız")),
        ("NOT_APPLICABLE", _("Uygulanamaz")),
        ("DEFERRED", _("Ertelendi")),
    ]

    control_activity = models.ForeignKey(
        ControlActivity,
        on_delete=models.CASCADE,
        related_name="executions",
        verbose_name=_("Kontrol Faaliyeti"),
    )
    execution_date = models.DateField(_("Uygulama Tarihi"))
    performed_by = models.ForeignKey(
        dj_settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_("Uygulayan"),
    )

    status = models.CharField(_("Durum"), max_length=20, choices=STATUS_CHOICES)

    # Sonuç detayları
    results_description = models.TextField(_("Sonuç Açıklaması"))
    exceptions_noted = models.TextField(_("Tespit Edilen İstisnalar"), blank=True)
    evidence_attached = models.BooleanField(_("Kanıt Ekli"), default=False)

    # İyileştirme ve takip
    management_response = models.TextField(_("Yönetim Yanıtı"), blank=True)
    corrective_actions = models.TextField(_("Düzeltici Aksiyonlar"), blank=True)
    follow_up_required = models.BooleanField(_("Takip Gerekli"), default=False)
    follow_up_date = models.DateField(_("Takip Tarihi"), null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "finance"
        verbose_name = _("Kontrol Uygulama Kaydı")
        verbose_name_plural = _("Kontrol Uygulama Kayıtları")
        ordering = ["-execution_date"]

    def __str__(self):
        try:
            status_display = self.get_status_display()
        except (AttributeError, Exception):
            status_display = self.status
        return f"{self.control_activity.control_id} - {self.execution_date} - {status_display}"


# Yardımcı fonksiyonlar ve servisler
class ComplianceReportGenerator:
    """Uyum Raporu Üretici"""

    def __init__(self, company, start_date, end_date):
        self.company = company
        self.start_date = start_date
        self.end_date = end_date

    def generate_audit_summary(self):
        """Denetim özeti raporu"""
        audit_trails = AuditTrail.objects.filter(
            company=self.company,
            timestamp__date__range=[self.start_date, self.end_date],
        )

        summary = {
            "total_actions": audit_trails.count(),
            "by_action_type": {},
            "by_risk_level": {},
            "by_user": {},
            "failed_actions": audit_trails.filter(success=False).count(),
            "high_risk_actions": audit_trails.filter(
                risk_level__in=["HIGH", "CRITICAL"]
            ).count(),
        }

        # İşlem tipi dağılımı
        for action_type, _label in AuditTrail.ACTION_TYPES:
            count = audit_trails.filter(action_type=action_type).count()
            if count > 0:
                summary["by_action_type"][action_type] = count

        # Risk seviyesi dağılımı
        for risk_level, _label in AuditTrail.RISK_LEVELS:
            count = audit_trails.filter(risk_level=risk_level).count()
            if count > 0:
                summary["by_risk_level"][risk_level] = count

        return summary

    def generate_approval_summary(self):
        """Onay süreci özeti"""
        approval_requests = ApprovalRequest.objects.filter(
            company=self.company,
            requested_at__date__range=[self.start_date, self.end_date],
        )

        summary = {
            "total_requests": approval_requests.count(),
            "approved": approval_requests.filter(status="APPROVED").count(),
            "rejected": approval_requests.filter(status="REJECTED").count(),
            "pending": approval_requests.filter(
                status__in=["PENDING", "IN_PROGRESS"]
            ).count(),
            "average_approval_time": self._calculate_average_approval_time(
                approval_requests
            ),
            "overdue_requests": approval_requests.filter(
                approval_records__due_date__lt=timezone.now(),
                status__in=["PENDING", "IN_PROGRESS"],
            )
            .distinct()
            .count(),
        }

        return summary

    def generate_risk_summary(self):
        """Risk özeti raporu"""
        risk_assessments = RiskAssessment.objects.filter(
            company=self.company,
            assessment_date__range=[self.start_date, self.end_date],
        )

        summary = {
            "total_risks": risk_assessments.count(),
            "by_risk_level": {},
            "by_category": {},
            "high_priority_risks": risk_assessments.filter(
                overall_risk_level__in=["HIGH", "VERY_HIGH"]
            ).count(),
            "overdue_reviews": risk_assessments.filter(
                next_review_date__lt=timezone.now().date()
            ).count(),
        }

        # Risk seviyesi dağılımı
        for risk_level, _label in RiskAssessment.RISK_LEVELS:
            count = risk_assessments.filter(overall_risk_level=risk_level).count()
            if count > 0:
                summary["by_risk_level"][risk_level] = count

        # Kategori dağılımı
        for category, _label in RiskAssessment.RISK_CATEGORIES:
            count = risk_assessments.filter(risk_category=category).count()
            if count > 0:
                summary["by_category"][category] = count

        return summary

    def _calculate_average_approval_time(self, approval_requests):
        """Ortalama onay süresini hesapla (saat cinsinden)"""
        completed_requests = approval_requests.filter(completed_at__isnull=False)

        if not completed_requests.exists():
            return 0

        total_hours = 0
        count = 0

        for request in completed_requests:
            duration = request.completed_at - request.requested_at
            total_hours += duration.total_seconds() / 3600
            count += 1

        return round(total_hours / count, 2) if count > 0 else 0
