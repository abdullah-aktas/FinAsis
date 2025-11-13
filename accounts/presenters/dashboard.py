from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from typing import Any, Callable, Dict, List, Mapping, MutableMapping, Optional, Sequence, Tuple

from django.contrib import messages
from django.db.models import Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from accounting.models import BankAccount, BankTransaction, Expense, Invoice
from ai_assistant.services import prompt_registry
from games import task_engine
from accounts.models import Achievement, CustomUser
from common.role_utils import get_user_role
from common.presenters import BasePresenter, PresenterResult

DashboardHandler = Callable[[HttpRequest], HttpResponse]


@dataclass(slots=True)
class FinancialSummary:
    total_invoice: Decimal
    total_expense: Decimal
    total_balance: Decimal

    def as_dict(self) -> Dict[str, float]:
        return {
            'toplam_fatura': float(self.total_invoice),
            'toplam_gider': float(self.total_expense),
            'toplam_bakiye': float(self.total_balance),
        }


class UserDashboardPresenter(BasePresenter):
    """
    Presenter for the main user profile/dashboard screen.
    """

    template_name = 'accounts/profile.html'

    def __init__(self, request: HttpRequest) -> None:
        super().__init__(request)
        self.user: CustomUser = request.user  # type: ignore[assignment]

    # ------------------------------------------------------------------ public
    def build(self) -> PresenterResult:
        redirect_response = self._resolve_role_redirect()
        if redirect_response is not None:
            return PresenterResult(response=redirect_response)

        return PresenterResult(
            template_name=self.template_name,
            context=self.get_context_data(),
        )

    # ----------------------------------------------------------------- context
    def get_context_data(self) -> MutableMapping[str, Any]:
        company = getattr(self.user, 'company', None)
        summary = self._build_financial_summary(company) if company else None

        context: Dict[str, Any] = {
            'user': self.user,
            'finans_ozet': summary.as_dict() if summary else {},
            'son_faturalar': self._get_recent_invoices(company),
            'son_giderler': self._get_recent_expenses(company),
            'trend_aylar': [],
            'trend_gelirler': [],
            'trend_giderler': [],
            'son_basari': self._get_recent_achievements(company),
            'son_banka': self._get_recent_bank_transactions(company),
            'gider_kategori_labels': [],
            'gider_kategori_data': [],
        }

        if company:
            trend_data = self._get_trend_data(company)
            context['trend_aylar'] = [item['label'] for item in trend_data]
            context['trend_gelirler'] = [item['income'] for item in trend_data]
            context['trend_giderler'] = [item['expense'] for item in trend_data]

            categories = self._get_expense_category_breakdown(company)
            context['gider_kategori_labels'] = [label for label, _ in categories]
            context['gider_kategori_data'] = [value for _, value in categories]

        role_code = getattr(getattr(self.user, 'user_type', None), 'code', None)
        if role_code == 'oyuncu':
            missions = task_engine.get_tasks(audience='gamer', kind='mission', limit=3)
            context['gaming_missions'] = missions or [
                {
                    'title': 'Günlük görev: Finansal simülasyon',
                    'description': 'Yeni senaryo ile 500 XP kazan.',
                    'icon': 'bi-lightning-charge-fill',
                }
            ]
            context['simulation_cards'] = task_engine.get_tasks(audience='gamer', kind='simulation', limit=3) or [
                {
                    'title': 'Trade Sim',
                    'description': 'Gerçek zamanlı piyasa senaryolarında pratik yap.',
                    'href': '/games/trade-sim/launch/',
                    'icon': 'bi-controller',
                }
            ]
            brief = task_engine.get_brief(audience='gamer')
            total_xp = brief.get('total_reward_xp', 0)
            level = max(1, (total_xp // 250) + 1)
            progress_pct = min(100, int((total_xp % 250) / 250 * 100)) if total_xp else 0
            context['game_progress'] = {
                'level': level,
                'xp': f"{total_xp} XP",
                'percentage': progress_pct,
            }
            context['ai_cards'] = prompt_registry.get_prompts_for_role('oyuncu', limit=3) or [
                {
                    'title': 'AI Koç: Performans özeti',
                    'body': 'Son üç oyundaki hareketlerini analiz ettik, hatalı karar noktalarını listeledik.',
                    'cta_label': 'Özeti Gör',
                    'cta_href': '/ai-assistant/gaming/performance/',
                    'icon': 'bi-robot',
                }
            ]

        self._inject_role_specific_cards(context)

        return context

    # -------------------------------------------------------------- helpers
    def _resolve_role_redirect(self) -> Optional[HttpResponse]:
        user_type = getattr(self.user, 'user_type', None)
        code = getattr(user_type, 'code', None)
        if not code:
            return None

        handlers: Mapping[str, str] = {
            'kobi': 'kobi_dashboard',
            'muhasebeci': 'muhasebeci_dashboard',
            'mali_musavir': 'mali_musavir_dashboard',
            'yatirimci': 'yatirimci_dashboard',
            'egitimci': 'egitimci_dashboard_new',
            'ogrenci': 'ogrenci_dashboard_new',
        }

        if code == 'oyuncu':
            return render(self.request, 'accounts/dashboard_oyuncu.html', self.get_context_data())

        handler_name = handlers.get(code)
        if not handler_name:
            return None

        try:
            from accounts import views_dashboards

            handler: DashboardHandler = getattr(views_dashboards, handler_name)
            return handler(self.request)
        except Exception as exc:  # pragma: no cover - fallback in unexpected cases
            messages.error(self.request, f'Dashboard yönlendirmesi başarısız: {exc}')
            return None

    def _build_financial_summary(self, company) -> FinancialSummary:
        invoice_total = (
            Invoice.objects.filter(company=company).aggregate(toplam=Sum('total_amount'))['toplam'] or Decimal('0')
        )
        expense_total = (
            Expense.objects.filter(company=company).aggregate(toplam=Sum('amount'))['toplam'] or Decimal('0')
        )
        balance_total = (
            BankAccount.objects.filter(company=company).aggregate(toplam=Sum('balance'))['toplam'] or Decimal('0')
        )
        return FinancialSummary(
            total_invoice=Decimal(invoice_total),
            total_expense=Decimal(expense_total),
            total_balance=Decimal(balance_total),
        )

    def _get_recent_invoices(self, company) -> Sequence[Invoice]:
        if not company:
            return []
        return Invoice.objects.filter(company=company).order_by('-issue_date')[:5]

    def _get_recent_expenses(self, company) -> Sequence[Expense]:
        if not company:
            return []
        return Expense.objects.filter(company=company).order_by('-expense_date')[:5]

    def _get_recent_achievements(self, company) -> Sequence[Achievement]:
        if not company:
            return []
        return Achievement.objects.filter(company=company).order_by('-date_earned')[:5]

    def _get_recent_bank_transactions(self, company) -> Sequence[BankTransaction]:
        if not company:
            return []
        accounts = BankAccount.objects.filter(company=company)
        return BankTransaction.objects.filter(account__in=accounts).order_by('-date')[:5]

    def _get_trend_data(self, company) -> List[Dict[str, Any]]:
        today = timezone.now().date().replace(day=1)
        trend: List[Dict[str, Any]] = []
        for offset in range(5, -1, -1):
            month_start = (today - timedelta(days=offset * 31)).replace(day=1)
            next_month = (month_start + timedelta(days=32)).replace(day=1)
            month_end = next_month - timedelta(days=1)

            income = (
                Invoice.objects.filter(
                    company=company,
                    issue_date__gte=month_start,
                    issue_date__lte=month_end,
                ).aggregate(toplam=Sum('total_amount'))['toplam']
                or Decimal('0')
            )
            expense = (
                Expense.objects.filter(
                    company=company,
                    expense_date__gte=month_start,
                    expense_date__lte=month_end,
                ).aggregate(toplam=Sum('amount'))['toplam']
                or Decimal('0')
            )

            trend.append(
                {
                    'label': month_start.strftime('%b %Y'),
                    'income': float(income),
                    'expense': float(expense),
                }
            )
        return trend

    def _get_expense_category_breakdown(self, company) -> List[Tuple[str, float]]:
        today = timezone.now().date().replace(day=1)
        six_months_ago = today - timedelta(days=180)
        categories = (
            Expense.objects.filter(company=company, expense_date__gte=six_months_ago)
            .values('category')
            .annotate(toplam=Sum('amount'))
            .order_by('-toplam')
        )

        results: List[Tuple[str, float]] = []
        mapping = getattr(Expense, 'EXPENSE_CATEGORIES_DICT', {})
        for item in categories:
            category_code = item.get('category')
            label = mapping.get(category_code, category_code)
            results.append((label, float(item.get('toplam') or 0)))
        return results

    def _inject_role_specific_cards(self, context: MutableMapping[str, Any]) -> None:
        """Populate mission and AI sections based on the user's primary role."""
        primary_role = self._detect_primary_role()
        if not primary_role:
            return

        task_role = self._map_role_for_tasks(primary_role)
        if task_role:
            missions = task_engine.get_tasks(audience=task_role, limit=3)
            if missions:
                context['role_missions'] = missions
                context['role_task_brief'] = task_engine.get_brief(audience=task_role)

        prompt_role = self._map_role_for_prompts(primary_role)
        prompts = prompt_registry.get_prompts_for_role(prompt_role, limit=3) if prompt_role else []
        if prompts:
            # Do not override gamer-specific cards if already populated
            context.setdefault('ai_cards', prompts)

    def _detect_primary_role(self) -> Optional[str]:
        profile = getattr(self.user, 'role_profile', None)
        role_obj = getattr(profile, 'role', None)
        if role_obj and getattr(role_obj, 'name', None):
            return role_obj.name

        return get_user_role(self.user)

    def _map_role_for_tasks(self, role_code: str) -> Optional[str]:
        task_aliases = {
            'super_admin': 'admin',
            'admin': 'admin',
            'kobi_owner': 'kobi_owner',
            'finance_manager': 'finance_manager',
            'accountant': 'accountant',
            'financial_advisor': 'financial_advisor',
            'mali_musavir': 'financial_advisor',
            'kobi_employee': 'kobi_employee',
            'employee': 'kobi_employee',
            'auditor': 'auditor',
            'viewer': 'viewer',
            'player': 'gamer',
        }
        return task_aliases.get(role_code)

    def _map_role_for_prompts(self, role_code: str) -> Optional[str]:
        prompt_aliases = {
            'super_admin': 'admin',
            'admin': 'admin',
            'kobi_owner': 'kobi',
            'finance_manager': 'finance_manager',
            'accountant': 'accountant',
            'financial_advisor': 'financial_advisor',
            'mali_musavir': 'mali_musavir',
            'kobi_employee': 'kobi_employee',
            'employee': 'kobi_employee',
            'auditor': 'auditor',
            'viewer': 'viewer',
            'player': 'oyuncu',
            'student': 'ogrenci',
            'teacher': 'egitimci',
        }
        return prompt_aliases.get(role_code)

