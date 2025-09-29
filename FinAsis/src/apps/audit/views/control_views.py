# -*- coding: utf-8 -*-
"""
Internal Audit and Control Views
Django views for GRC (Governance, Risk & Compliance) system
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q, Avg, Max
from django.utils import timezone
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from datetime import timedelta
import json

from src.apps.finance.internal_control_system import (
    ControlActivity,
    AuditTrail,
    RiskAssessment,
    ApprovalWorkflow,
    ControlExecution,
)
from src.apps.accounting.models import Company
from ..decorators import require_roles

# Sık kullanılan ContentType objeleri için basit cache
def get_ct(model_cls):
    key = f"audit_ct_{model_cls.__name__.lower()}"
    ct = cache.get(key)
    if ct is None:
        ct = ContentType.objects.get_for_model(model_cls)
        cache.set(key, ct, 3600)  # 1 saat
    return ct


@login_required
@require_roles('Admin','Accountant','Auditor')
def control_dashboard(request):
    """
    İç denetim ve kontrol sistemi ana paneli
    """
    company = request.user.company if hasattr(request.user, 'company') else None
    if not company:
        messages.error(request, _('Şirket bilgisi bulunamadı.'))
        return redirect('finance:kobi_dashboard')
    
    # Ana istatistikler
    active_controls = ControlActivity.objects.filter(company=company, is_active=True)
    # AuditTrail modelinde 'status' alanı yok; bekleyen denetim konsepti ileride eklenecek.
    pending_audits = AuditTrail.objects.none()
    # RiskAssessment modelinde risk_level değil overall_risk_level mevcut.
    open_risks = RiskAssessment.objects.filter(company=company, overall_risk_level__in=['HIGH', 'VERY_HIGH'])
    # ApprovalWorkflow modelinde status alanı yok; aktif olanları sayıyoruz.
    pending_workflows = ApprovalWorkflow.objects.filter(company=company, is_active=True)
    
    context = {
        'company': company,
        'active_controls_count': active_controls.count(),
        'pending_audits_count': pending_audits.count(),
        'open_risks_count': open_risks.count(),
        'pending_workflows_count': pending_workflows.count(),
    }
    
    # Genel uyumluluk skoru hesaplama (cache'li)
    compliance_cache_key = f"audit_compliance_{company.id}"
    cached_compliance = cache.get(compliance_cache_key)
    if cached_compliance is None:
        total_controls = active_controls.count()
        if total_controls > 0:
            effective_controls = active_controls.filter(operating_effectiveness='EFFECTIVE').count()
            if effective_controls == 0:
                effective_controls = active_controls.filter(design_effectiveness='EFFECTIVE').count()
            compliance_percentage = (effective_controls / total_controls) * 100.0
            cached_compliance = {
                'score': compliance_percentage,
                'percentage': compliance_percentage * 3.6,
                'status_text': get_compliance_status_text(compliance_percentage),
                'description': get_compliance_description(compliance_percentage),
                'effective_controls': effective_controls,
                'total_controls': total_controls,
                'completed_audits': AuditTrail.objects.filter(company=company, action_type='CREATE').count(),
                'total_audits': AuditTrail.objects.filter(company=company).count(),
                'risk_level': get_risk_level_from_score(compliance_percentage),
                'risk_level_text': get_risk_level_text(compliance_percentage),
                'last_updated': timezone.now().date(),
            }
        else:
            cached_compliance = {
                'score': 0,
                'percentage': 0,
                'status_text': _('Henüz değerlendirme yapılmamış'),
                'description': _('Kontrol aktivitesi tanımlanmamış'),
                'effective_controls': 0,
                'total_controls': 0,
                'completed_audits': 0,
                'total_audits': 0,
                'risk_level': 'high',
                'risk_level_text': _('Yüksek Risk'),
                'last_updated': timezone.now().date(),
            }
        cache.set(compliance_cache_key, cached_compliance, 60)  # 60 sn TTL
    context['compliance_score'] = cached_compliance
    
    # Kontrol aktiviteleri durumu (defensive attribute access + eksiklik hesapları)
    control_activities = []
    # İlgili execution setlerini tek sorgu ile almak için id listesi
    control_ids = list(active_controls.order_by('-updated_at')[:6].values_list('id', flat=True))
    executions_map = {
        row['control_activity_id']: row
        for row in ControlExecution.objects.filter(control_activity_id__in=control_ids)
            .values('control_activity_id')
            .annotate(
                failed=Count('id', filter=Q(status='FAILED')),
                passed=Count('id', filter=Q(status='PASSED')),
                last_date=Max('execution_date')
            )
    }
    # Bir sonraki test için frekans -> gün haritası
    freq_days = {
        'DAILY': 1,
        'WEEKLY': 7,
        'MONTHLY': 30,
        'QUARTERLY': 90,
        'SEMI_ANNUAL': 180,
        'ANNUAL': 365,
    }
    for control in ControlActivity.objects.filter(id__in=control_ids):
        control_pk = getattr(control, 'id', None)
        data = executions_map.get(control_pk, {})
        last_test_date = data.get('last_date')
        if not last_test_date:
            last_test_date = getattr(control, 'last_performed_date', None) or getattr(control, 'created_at', timezone.now()).date()
        freq = getattr(control, 'frequency', 'MONTHLY') or 'MONTHLY'
        next_test_due = last_test_date + timedelta(days=freq_days.get(freq, 30)) if last_test_date else None
        operating = getattr(control, 'operating_effectiveness', None)
        design = getattr(control, 'design_effectiveness', None)
        effectiveness = operating or design or 'NOT_EVALUATED'
        eff_for_score = 'EFFECTIVE' if effectiveness == 'EFFECTIVE' else 'NEEDS_IMPROVEMENT'
        deficiency_count = data.get('failed', 0)
        control_activities.append({
            'id': control_pk,
            'name': getattr(control, 'control_name', ''),
            'description': getattr(control, 'control_description', ''),
            'effectiveness_level': effectiveness.lower(),
            'effectiveness_text': effectiveness,
            'effectiveness_score': get_effectiveness_score(eff_for_score),
            'last_tested': last_test_date,
            'test_frequency': freq,
            'next_test_due': next_test_due,
            'deficiency_count': deficiency_count,
            'status_icon': get_status_icon(eff_for_score),
            'icon': get_control_icon(getattr(control, 'control_type', '')),
        })
    context['control_activities'] = control_activities

    # Risk özeti (risk_summary) cache'li
    risk_cache_key = f"audit_risk_summary_{company.id}"
    cached_risk = cache.get(risk_cache_key)
    if cached_risk is None:
        risk_summary = (
            RiskAssessment.objects.filter(company=company)
            .values('overall_risk_level')
            .annotate(count=Count('id'))
            .order_by('overall_risk_level')
        )
        total_risk_count = sum(r['count'] for r in risk_summary)
        cached_risk = {
            'by_level': list(risk_summary),
            'total': total_risk_count,
            'high_critical': sum(r['count'] for r in risk_summary if r['overall_risk_level'] in ['HIGH', 'VERY_HIGH']),
            'last_updated': timezone.now().isoformat(),
        }
        cache.set(risk_cache_key, cached_risk, 60)
    context['risk_summary'] = cached_risk
    
    # Risk değerlendirmeleri
    risk_assessments = []
    for risk in RiskAssessment.objects.filter(company=company).order_by('-assessment_date')[:5]:
        risk_assessments.append({
            'risk_description': getattr(risk, 'risk_description', '')[:100],
            'likelihood': getattr(risk, 'likelihood', ''),
            'impact': getattr(risk, 'impact', ''),
            'risk_score': getattr(risk, 'risk_score', None),
            'risk_level': (getattr(risk, 'overall_risk_level', '') or '').lower(),
            'mitigation_plan': getattr(risk, 'mitigation_actions', '')[:120],
            'assessment_date': getattr(risk, 'assessment_date', None),
        })
    
    context['risk_assessments'] = risk_assessments
    
    # Son denetim aktiviteleri
    recent_audits = []
    for audit in AuditTrail.objects.filter(company=company).order_by('-timestamp')[:5]:
        recent_audits.append({
            'audit_type': getattr(audit, 'action_type', ''),
            'description': getattr(audit, 'description', ''),
            'status': getattr(audit, 'action_type', '').lower(),
            'status_text': getattr(audit, 'action_type', ''),
            'audit_date': getattr(audit, 'timestamp', None),
            'auditor': getattr(audit, 'user', None),
        })
    
    context['recent_audits'] = recent_audits
    
    # Bekleyen onay iş akışları
    workflows = []
    for workflow in pending_workflows[:5]:
        steps = []
        # İş akışı adımları (örnek)
        steps.append({'status': 'completed', 'icon': 'check'})
        steps.append({'status': 'pending', 'icon': 'clock'})
        steps.append({'status': 'waiting', 'icon': 'user'})
        
        workflows.append({
            'id': getattr(workflow, 'id', None),
            'workflow_name': getattr(workflow, 'name', ''),
            'description': getattr(workflow, 'name', ''),
            'status': 'active' if getattr(workflow, 'is_active', False) else 'inactive',
            'status_text': _('Aktif') if getattr(workflow, 'is_active', False) else _('Pasif'),
            'initiator': None,
            'created_at': getattr(workflow, 'created_at', None),
            'steps': steps,
        })
    
    context['pending_workflows'] = workflows
    
    # Uyumluluk kontrol listesi
    financial_compliance = [
        {
            'requirement': _('VUK Uyumu'),
            'description': _('Vergi Usul Kanunu\'na uygun kayıt tutma'),
            'status': 'completed',
            'icon': 'check',
            'due_date': None,
        },
        {
            'requirement': _('TTK Uyumu'),
            'description': _('Türk Ticaret Kanunu gereklilikleri'),
            'status': 'pending',
            'icon': 'clock',
            'due_date': timezone.now().date() + timedelta(days=30),
        },
        {
            'requirement': _('Dış Denetim'),
            'description': _('Yıllık bağımsız denetim'),
            'status': 'pending',
            'icon': 'clock',
            'due_date': timezone.now().date() + timedelta(days=90),
        },
    ]
    
    operational_compliance = [
        {
            'requirement': _('İç Kontrol Sistemi'),
            'description': _('İç kontrol prosedürlerinin uygulanması'),
            'status': 'completed',
            'icon': 'check',
            'responsible_person': request.user.get_full_name(),
        },
        {
            'requirement': _('Risk Yönetimi'),
            'description': _('Risk değerlendirme ve yönetim süreçleri'),
            'status': 'pending',
            'icon': 'exclamation-triangle',
            'responsible_person': _('Risk Yöneticisi'),
        },
        {
            'requirement': _('Dokümantasyon'),
            'description': _('Süreç dokümantasyonu ve güncelleme'),
            'status': 'completed',
            'icon': 'check',
            'responsible_person': _('Operasyon Yöneticisi'),
        },
    ]
    
    context.update({
        'financial_compliance': financial_compliance,
        'operational_compliance': operational_compliance,
    })
    
    return render(request, 'audit/control_dashboard.html', context)


@login_required
@require_roles('Admin','Accountant','Auditor')
def risk_assessment_view(request):
    """
    Risk değerlendirme sayfası
    """
    company = getattr(request.user, 'company', None)
    if not company:
        messages.error(request, _('Şirket bilgisi bulunamadı.'))
        return redirect('audit:control_dashboard')
    
    if request.method == 'POST':
        try:
            # Risk değerlendirmesi kaydet
            assessment = RiskAssessment.objects.create(
                company=company,
                assessment_date=timezone.now().date(),
                assessor=request.user,
                risk_title=request.POST.get('risk_title', '')[:200],
                risk_description=request.POST.get('risk_description', ''),
                risk_category=request.POST.get('risk_category'),
                likelihood=request.POST.get('likelihood'),
                impact=request.POST.get('impact'),
                existing_controls=request.POST.get('existing_controls', ''),
                potential_financial_impact=request.POST.get('potential_financial_impact') or None,
            )
            # Model kendi calculate_risk_score metoduna sahipse kullan
            if hasattr(assessment, 'calculate_risk_score'):
                assessment.calculate_risk_score()

            AuditTrail.log_action(
                user=request.user,
                company=company,
                action_type='CREATE',
                obj=assessment,
                description=f'Risk değerlendirmesi oluşturuldu: {assessment.risk_title[:50]}'
            )
            
            messages.success(request, _('Risk değerlendirmesi başarıyla kaydedildi.'))
            return redirect('audit:risk_assessment')
            
        except Exception as e:
            messages.error(request, f'Risk değerlendirmesi kaydedilirken hata oluştu: {str(e)}')
    
    # Mevcut risk değerlendirmeleri
    assessments = RiskAssessment.objects.filter(company=company).order_by('-assessment_date')
    
    # Risk kategorileri
    risk_categories = [
    ('FINANCIAL', _('Mali Risk')),
    ('OPERATIONAL', _('Operasyonel Risk')),
    ('COMPLIANCE', _('Uyum Riski')),
    ('STRATEGIC', _('Stratejik Risk')),
    ('REPUTATION', _('İtibar Riski')),
    ('TECHNOLOGY', _('Teknoloji Riski')),
    ]
    
    context = {
        'assessments': assessments,
        'risk_categories': risk_categories,
    }
    
    return render(request, 'audit/risk_assessment.html', context)


@login_required
@require_roles('Admin','Accountant')
def control_create(request):
    """Yeni kontrol faaliyeti oluştur (gerçek alan adlarıyla)."""
    company = getattr(request.user, 'company', None)
    if not company:
        messages.error(request, _('Şirket bilgisi bulunamadı.'))
        return redirect('audit:control_dashboard')

    if request.method == 'POST':
        try:
            control_id = request.POST.get('control_id') or f"CTRL-{int(timezone.now().timestamp())}"
            control = ControlActivity.objects.create(
                company=company,
                control_id=control_id[:50],
                control_name=request.POST.get('control_name', '')[:200],
                control_description=request.POST.get('control_description', ''),
                control_objective=request.POST.get('control_objective', ''),
                control_type=request.POST.get('control_type') or 'PREVENTIVE',
                control_nature=request.POST.get('control_nature') or 'MANUAL',
                frequency=request.POST.get('frequency') or 'MONTHLY',
                control_owner=request.user,
                control_procedure=request.POST.get('control_procedure', ''),
            )
            AuditTrail.log_action(
                user=request.user,
                company=company,
                action_type='CREATE',
                obj=control,
                description=f'Kontrol oluşturuldu: {control.control_id}'
            )
            messages.success(request, _('Kontrol faaliyeti oluşturuldu.'))
            return redirect('audit:control_dashboard')
        except Exception as e:  # pragma: no cover
            messages.error(request, _('Kontrol oluşturulurken hata: ') + str(e))

    context = {
        'control_types': ControlActivity.CONTROL_TYPES,
        'control_natures': ControlActivity.CONTROL_NATURE,
        'frequencies': ControlActivity.FREQUENCY_CHOICES,
    }
    return render(request, 'audit/control_create.html', context)


@login_required
@require_roles('Admin','Accountant','Auditor')
def control_test(request, control_id):
    """Kontrol testi: ControlExecution kaydı oluşturur ve operating_effectiveness güncelleyebilir."""
    company = getattr(request.user, 'company', None)
    control = get_object_or_404(ControlActivity, id=control_id, company=company)

    if request.method == 'POST':
        test_result = request.POST.get('test_result')
        notes = request.POST.get('notes', '')
        status_map = {
            'EFFECTIVE': 'PASSED',
            'NEEDS_IMPROVEMENT': 'FAILED',
            'INEFFECTIVE': 'FAILED',
            'NOT_APPLICABLE': 'NOT_APPLICABLE'
        }
        execution_status = status_map.get(test_result, 'PASSED')
        try:
            ControlExecution.objects.create(
                control_activity=control,
                execution_date=timezone.now().date(),
                performed_by=request.user,
                status=execution_status,
                results_description=notes or f'Test sonucu: {test_result}',
            )
            if test_result in ('EFFECTIVE', 'INEFFECTIVE'):
                control.operating_effectiveness = test_result
                control.last_performed_date = timezone.now().date()
                control.save(update_fields=['operating_effectiveness', 'last_performed_date'])
            AuditTrail.log_action(
                user=request.user,
                company=company,
                action_type='UPDATE',
                obj=control,
                description=f'Kontrol testi: {control.control_id} -> {test_result}'
            )
            messages.success(request, _('Kontrol testi kaydedildi.'))
            return redirect('audit:control_dashboard')
        except Exception as e:  # pragma: no cover
            messages.error(request, _('Kontrol testi hatası: ') + str(e))

    context = {
        'control': control,
        'test_results': [
            ('EFFECTIVE', _('Etkili')),
            ('NEEDS_IMPROVEMENT', _('İyileştirme Gerekli')),
            ('INEFFECTIVE', _('Etkisiz')),
            ('NOT_APPLICABLE', _('Uygulanamaz')),
        ]
    }
    return render(request, 'audit/control_test.html', context)


@login_required
@require_roles('Admin','Accountant','Auditor')
def audit_trail_report(request):
    """
    Denetim izi raporu
    """
    company = request.user.company
    
    # Filtreleme
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    action_type = request.GET.get('action_type')
    user_filter = request.GET.get('user')
    
    trails = AuditTrail.objects.filter(company=company).order_by('-timestamp')
    
    if date_from:
        trails = trails.filter(timestamp__gte=date_from)
    if date_to:
        trails = trails.filter(timestamp__lte=date_to)
    if action_type:
        trails = trails.filter(action=action_type)
    if user_filter:
        trails = trails.filter(user_id=user_filter)
    
    # Sayfalama
    paginator = Paginator(trails, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Kullanıcı listesi (filtre için)
    users = AuditTrail.objects.filter(company=company).values_list(
        'user__id', 'user__first_name', 'user__last_name'
    ).distinct()
    
    # Aksiyon tipleri
    action_types = AuditTrail.objects.filter(company=company).values_list(
        'action', flat=True
    ).distinct()
    
    context = {
        'page_obj': page_obj,
        'users': users,
        'action_types': action_types,
        'date_from': date_from,
        'date_to': date_to,
        'action_type': action_type,
        'user_filter': user_filter,
    }
    
    return render(request, 'audit/audit_trail_report.html', context)


@login_required
@require_roles('Admin','Accountant','Auditor')
def compliance_report(request):
    """Uyumluluk raporu (model alanlarına uyarlanmış)."""
    company = getattr(request.user, 'company', None)
    controls = ControlActivity.objects.filter(company=company)
    effectiveness_stats = controls.values('operating_effectiveness').annotate(count=Count('id')).order_by('operating_effectiveness')
    risks = RiskAssessment.objects.filter(company=company)
    risk_stats = risks.values('overall_risk_level').annotate(count=Count('id')).order_by('overall_risk_level')
    audits = AuditTrail.objects.filter(company=company, timestamp__gte=timezone.now() - timedelta(days=30))
    audit_stats = audits.values('action_type').annotate(count=Count('id')).order_by('action_type')
    workflows = ApprovalWorkflow.objects.filter(company=company)
    workflow_stats = workflows.values('is_active').annotate(count=Count('id')).order_by('-is_active')
    context = {
        'company': company,
        'effectiveness_stats': effectiveness_stats,
        'risk_stats': risk_stats,
        'audit_stats': audit_stats,
        'workflow_stats': workflow_stats,
        'total_controls': controls.count(),
        'total_risks': risks.count(),
        'total_audits': audits.count(),
        'total_workflows': workflows.count(),
    }
    return render(request, 'audit/compliance_report.html', context)


# Ek placeholder / alias view'lar (template referansları için)
@login_required
@require_roles('Admin','Accountant','Auditor')
def assessment_create(request):  # risk_assessment alias
    return risk_assessment_view(request)


@login_required
@require_roles('Admin','Accountant','Auditor')
def control_test_all(request):  # Basit yönlendirme placeholder
    company = getattr(request.user, 'company', None)
    if not company:
        messages.error(request, _('Şirket bilgisi bulunamadı.'))
        return redirect('audit:control_dashboard')
    controls = ControlActivity.objects.filter(company=company, is_active=True)
    created = 0
    for ctrl in controls:
        try:
            ControlExecution.objects.create(
                control_activity=ctrl,
                execution_date=timezone.now().date(),
                performed_by=request.user,
                status='PASSED',
                results_description=_('Toplu test: otomatik PASS'),
            )
            # Eğer operating_effectiveness boşsa ilk PASS ile EFFECTIVE olarak işaretle
            if not getattr(ctrl, 'operating_effectiveness', None):
                ctrl.operating_effectiveness = 'EFFECTIVE'
                ctrl.last_performed_date = timezone.now().date()
                ctrl.save(update_fields=['operating_effectiveness', 'last_performed_date'])
            created += 1
        except Exception:  # pragma: no cover
            continue
    messages.success(request, _('%(count)d kontrol için test kaydı oluşturuldu.') % {'count': created})
    return redirect('audit:control_dashboard')


@login_required
@require_roles('Admin','Accountant','Auditor')
def ajax_test_control(request, control_id):  # AJAX placeholder
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': _('Yalnızca POST desteklenir.')}, status=405)
    company = getattr(request.user, 'company', None)
    if not company:
        return JsonResponse({'success': False, 'message': _('Şirket bulunamadı.')}, status=400)
    try:
        control = ControlActivity.objects.get(id=control_id, company=company)
    except ControlActivity.DoesNotExist:
        return JsonResponse({'success': False, 'message': _('Kontrol bulunamadı.')}, status=404)

    test_result = request.POST.get('result') or 'EFFECTIVE'
    status_map = {
        'EFFECTIVE': 'PASSED',
        'NEEDS_IMPROVEMENT': 'FAILED',
        'INEFFECTIVE': 'FAILED',
        'NOT_APPLICABLE': 'NOT_APPLICABLE'
    }
    exec_status = status_map.get(test_result, 'PASSED')
    ControlExecution.objects.create(
        control_activity=control,
        execution_date=timezone.now().date(),
        performed_by=request.user,
        status=exec_status,
        results_description=_('Tekil test sonucu: %(res)s') % {'res': test_result}
    )
    if test_result in ('EFFECTIVE', 'INEFFECTIVE'):
        control.operating_effectiveness = test_result
        control.last_performed_date = timezone.now().date()
        control.save(update_fields=['operating_effectiveness', 'last_performed_date'])

    executions_qs = getattr(control, 'executions', None)
    if executions_qs is not None:
        try:
            deficiency_count = executions_qs.filter(status='FAILED').count()
        except Exception:  # pragma: no cover - defensive
            deficiency_count = 0
    else:
        deficiency_count = 0
    eff_for_score = 'EFFECTIVE' if control.operating_effectiveness == 'EFFECTIVE' else 'NEEDS_IMPROVEMENT'
    payload = {
        'success': True,
        'message': _('Test kaydı oluşturuldu.'),
    'control_id': getattr(control, 'id', None),
        'effectiveness': control.operating_effectiveness,
        'effectiveness_score': get_effectiveness_score(eff_for_score),
        'deficiency_count': deficiency_count,
        'last_tested': timezone.now().date().isoformat(),
        'status_icon': get_status_icon(eff_for_score),
    }
    return JsonResponse(payload)


@login_required
@require_roles('Admin','Accountant','Auditor')
def ajax_notifications(request):  # Dashboard periyodik badge güncellemeleri
    company = getattr(request.user, 'company', None)
    data = {
        'pending_audits': 0,
        'open_risks': RiskAssessment.objects.filter(company=company, overall_risk_level__in=['HIGH','VERY_HIGH']).count() if company else 0,
        'pending_workflows': ApprovalWorkflow.objects.filter(company=company, is_active=True).count() if company else 0,
    }
    return JsonResponse(data)


# AJAX Views
@login_required
def ajax_control_detail(request, control_id):
    """AJAX kontrol detayları (ControlExecution kayıtlarıyla)."""
    try:
        company = getattr(request.user, 'company', None)
        control = ControlActivity.objects.get(id=control_id, company=company)
        executions_qs = getattr(control, 'executions', None)
        tests = executions_qs.order_by('-execution_date')[:5] if executions_qs is not None else []
        html = render(request, 'audit/partials/control_detail.html', {'control': control, 'tests': tests}).content.decode('utf-8')
        return JsonResponse({'success': True, 'html': html})
    except ControlActivity.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Kontrol bulunamadı'})


@login_required
def ajax_pending_counts(request):
    """AJAX bekleyen işlem sayıları (alanlara uyumlu)."""
    company = getattr(request.user, 'company', None)
    counts = {
        'pending_audits': 0,  # AuditTrail status alanı yok
        'open_risks': RiskAssessment.objects.filter(company=company, overall_risk_level__in=['HIGH', 'VERY_HIGH']).count(),
        'pending_workflows': ApprovalWorkflow.objects.filter(company=company, is_active=True).count(),
    }
    return JsonResponse(counts)


@login_required
@require_roles('Admin','Accountant')
def ajax_workflow_approve(request, workflow_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': _('Yalnızca POST desteklenir.')}, status=405)
    company = getattr(request.user, 'company', None)
    if not company:
        return JsonResponse({'success': False, 'message': _('Şirket bulunamadı.')}, status=400)
    try:
        workflow = ApprovalWorkflow.objects.get(id=workflow_id, company=company)
    except ApprovalWorkflow.DoesNotExist:
        return JsonResponse({'success': False, 'message': _('İş akışı bulunamadı.')}, status=404)
    # Basit onay: is_active True yap ve audit trail yaz
    if not getattr(workflow, 'is_active', False):
        workflow.is_active = True
        workflow.save(update_fields=['is_active'])
        AuditTrail.log_action(
            user=request.user,
            company=company,
            action_type='UPDATE',
            obj=workflow,
            description=f'Workflow onaylandı: {getattr(workflow, "name", workflow_id)}'
        )
    return JsonResponse({
        'success': True,
        'workflow_id': getattr(workflow, 'id', None),
        'status': 'active',
        'status_text': _('Aktif'),
        'message': _('İş akışı onaylandı.'),
    })


@login_required
@require_roles('Admin','Accountant')
def ajax_workflow_reject(request, workflow_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': _('Yalnızca POST desteklenir.')}, status=405)
    company = getattr(request.user, 'company', None)
    if not company:
        return JsonResponse({'success': False, 'message': _('Şirket bulunamadı.')}, status=400)
    try:
        workflow = ApprovalWorkflow.objects.get(id=workflow_id, company=company)
    except ApprovalWorkflow.DoesNotExist:
        return JsonResponse({'success': False, 'message': _('İş akışı bulunamadı.')}, status=404)
    # Basit red: is_active False yap ve audit trail yaz
    changed = False
    if getattr(workflow, 'is_active', False):
        workflow.is_active = False
        workflow.save(update_fields=['is_active'])
        changed = True
        AuditTrail.log_action(
            user=request.user,
            company=company,
            action_type='UPDATE',
            obj=workflow,
            description=f'Workflow reddedildi: {getattr(workflow, "name", workflow_id)}'
        )
    return JsonResponse({
        'success': True,
        'workflow_id': getattr(workflow, 'id', None),
        'status': 'inactive',
        'status_text': _('Pasif'),
        'changed': changed,
        'message': _('İş akışı reddedildi.'),
    })


# Yardımcı fonksiyonlar
def get_compliance_status_text(score):
    """
    Uyumluluk durumu metni
    """
    if score >= 90:
        return _('Mükemmel Uyum')
    elif score >= 80:
        return _('İyi Uyum')
    elif score >= 70:
        return _('Orta Uyum')
    elif score >= 60:
        return _('Düşük Uyum')
    else:
        return _('Kritik Durum')


def get_compliance_description(score):
    """
    Uyumluluk açıklaması
    """
    if score >= 90:
        return _('Kontrol sistemleriniz çok iyi çalışıyor. Mevcut performansınızı koruyun.')
    elif score >= 80:
        return _('Kontrol sistemleriniz iyi durumda. Küçük iyileştirmeler yapabilirsiniz.')
    elif score >= 70:
        return _('Kontrol sistemleriniz orta seviyede. Bazı alanlarda iyileştirme gerekli.')
    elif score >= 60:
        return _('Kontrol sistemleriniz zayıf. Acil iyileştirme gerekli.')
    else:
        return _('Kontrol sistemleriniz kritik durumda. Derhal müdahale gerekli.')


def get_risk_level_from_score(score):
    """
    Skordan risk seviyesi
    """
    if score >= 80:
        return 'low'
    elif score >= 60:
        return 'medium'
    else:
        return 'high'


def get_risk_level_text(score):
    """
    Risk seviyesi metni
    """
    level = get_risk_level_from_score(score)
    level_map = {
        'low': _('Düşük Risk'),
        'medium': _('Orta Risk'),
        'high': _('Yüksek Risk'),
    }
    return level_map.get(level, _('Bilinmeyen'))


def get_effectiveness_score(level):
    """
    Etkinlik seviyesinden skor
    """
    score_map = {
        'EFFECTIVE': 100,
        'NEEDS_IMPROVEMENT': 70,
        'INEFFECTIVE': 30,
        'NOT_TESTED': 50,
        'NOT_APPLICABLE': 0,
    }
    return score_map.get(level, 50)


def get_status_icon(level):
    """
    Durum ikonu
    """
    icon_map = {
        'EFFECTIVE': 'check-circle',
        'NEEDS_IMPROVEMENT': 'exclamation-triangle',
        'INEFFECTIVE': 'times-circle',
        'NOT_TESTED': 'clock',
        'NOT_APPLICABLE': 'minus-circle',
    }
    return icon_map.get(level, 'question-circle')


def get_control_icon(control_type):
    """
    Kontrol tipi ikonu
    """
    icon_map = {
        'PREVENTIVE': 'shield-alt',
        'DETECTIVE': 'search',
        'CORRECTIVE': 'tools',
        'DIRECTIVE': 'compass',
    }
    return icon_map.get(control_type, 'cog')