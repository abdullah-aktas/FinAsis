"""
KOBİ Analysis Admin Panel
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import (
    KOBIFinancialAnalysis, BudgetPlan, BudgetLineItem,
    CashFlowForecast, ForecastScenario, FinancialGoal,
    GoalProgress, IndustryBenchmark, CompetitorAnalysis,
    SWOTAnalysis, RiskAssessment, RiskMitigation,
    PerformanceMetric, MetricTarget, FinancialAlert,
    AdvisoryReport, FinancialHealthSnapshot
)


@admin.register(KOBIFinancialAnalysis)
class KOBIFinancialAnalysisAdmin(admin.ModelAdmin):
    list_display = ['company', 'analysis_type', 'period_display', 'health_status_colored', 'financial_health_score', 'created_at']
    list_filter = ['analysis_type', 'health_status', 'created_at']
    search_fields = ['company__name']
    readonly_fields = ['financial_health_score', 'health_status', 'current_ratio', 'quick_ratio', 'debt_to_equity_ratio', 'profit_margin', 'roa', 'roe']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('company', 'analysis_type', 'analysis_period_start', 'analysis_period_end')
        }),
        ('Finansal Veriler', {
            'fields': ('total_revenue', 'total_expenses', 'net_profit', 'total_assets', 'total_liabilities')
        }),
        ('Finansal Rasyolar', {
            'fields': ('current_ratio', 'quick_ratio', 'debt_to_equity_ratio', 'profit_margin', 'roa', 'roe'),
            'classes': ('collapse',)
        }),
        ('Analiz Sonuçları', {
            'fields': ('financial_health_score', 'health_status', 'recommendations', 'analysis_notes')
        }),
    )
    
    def period_display(self, obj):
        return f"{obj.analysis_period_start} - {obj.analysis_period_end}"
    period_display.short_description = 'Dönem'
    
    def health_status_colored(self, obj):
        colors = {
            'EXCELLENT': '#10b981',
            'GOOD': '#3b82f6',
            'FAIR': '#f59e0b',
            'POOR': '#ef4444',
            'CRITICAL': '#dc2626'
        }
        color = colors.get(obj.health_status, '#6b7280')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600;">{}</span>',
            color,
            obj.get_health_status_display()
        )
    health_status_colored.short_description = 'Sağlık Durumu'


@admin.register(BudgetPlan)
class BudgetPlanAdmin(admin.ModelAdmin):
    list_display = ['budget_name', 'company', 'budget_type', 'fiscal_year', 'status', 'variance_percentage_display']
    list_filter = ['budget_type', 'status', 'fiscal_year']
    search_fields = ['budget_name', 'company__name']
    
    def variance_percentage_display(self, obj):
        if obj.variance_percentage:
            color = '#10b981' if obj.variance_percentage >= 0 else '#ef4444'
            return format_html(
                '<span style="color: {}; font-weight: 600;">{:+.1f}%</span>',
                color,
                obj.variance_percentage
            )
        return '-'
    variance_percentage_display.short_description = 'Varyans %'


@admin.register(BudgetLineItem)
class BudgetLineItemAdmin(admin.ModelAdmin):
    list_display = ['budget', 'line_item_name', 'category', 'planned_amount', 'actual_amount', 'variance']
    list_filter = ['category', 'budget__budget_type']
    search_fields = ['line_item_name', 'budget__budget_name']


@admin.register(CashFlowForecast)
class CashFlowForecastAdmin(admin.ModelAdmin):
    list_display = ['company', 'forecast_period_display', 'net_cash_flow', 'confidence_level', 'created_at']
    list_filter = ['confidence_level', 'created_at']
    search_fields = ['company__name']
    
    def forecast_period_display(self, obj):
        return f"{obj.forecast_period_start} - {obj.forecast_period_end}"
    forecast_period_display.short_description = 'Tahmin Dönemi'


@admin.register(ForecastScenario)
class ForecastScenarioAdmin(admin.ModelAdmin):
    list_display = ['forecast', 'scenario_name', 'scenario_type', 'probability', 'projected_revenue', 'projected_profit']
    list_filter = ['scenario_type']
    search_fields = ['scenario_name', 'forecast__company__name']


@admin.register(FinancialGoal)
class FinancialGoalAdmin(admin.ModelAdmin):
    list_display = ['goal_name', 'company', 'goal_type', 'target_amount', 'deadline', 'status_colored']
    list_filter = ['goal_type', 'status', 'priority']
    search_fields = ['goal_name', 'company__name']
    
    def status_colored(self, obj):
        colors = {
            'NOT_STARTED': '#6b7280',
            'IN_PROGRESS': '#3b82f6',
            'COMPLETED': '#10b981',
            'FAILED': '#ef4444',
            'CANCELLED': '#9ca3af'
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Durum'


@admin.register(GoalProgress)
class GoalProgressAdmin(admin.ModelAdmin):
    list_display = ['goal', 'progress_date', 'current_amount', 'achievement_percentage']
    list_filter = ['progress_date']
    date_hierarchy = 'progress_date'


@admin.register(IndustryBenchmark)
class IndustryBenchmarkAdmin(admin.ModelAdmin):
    list_display = ['industry_sector', 'benchmark_year', 'metric_name', 'average_value', 'top_quartile_value']
    list_filter = ['industry_sector', 'benchmark_year']
    search_fields = ['industry_sector', 'metric_name']


@admin.register(CompetitorAnalysis)
class CompetitorAnalysisAdmin(admin.ModelAdmin):
    list_display = ['company', 'competitor_name', 'analysis_date', 'overall_rating']
    list_filter = ['analysis_date', 'overall_rating']
    search_fields = ['company__name', 'competitor_name']


@admin.register(SWOTAnalysis)
class SWOTAnalysisAdmin(admin.ModelAdmin):
    list_display = ['company', 'analysis_date', 'created_by']
    list_filter = ['analysis_date']
    search_fields = ['company__name']


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ['company', 'risk_name', 'risk_category', 'likelihood', 'impact', 'risk_score_colored', 'status']
    list_filter = ['risk_category', 'likelihood', 'impact', 'status']
    search_fields = ['company__name', 'risk_name']
    
    def risk_score_colored(self, obj):
        if obj.risk_score >= 70:
            color = '#dc2626'
        elif obj.risk_score >= 40:
            color = '#f59e0b'
        else:
            color = '#10b981'
        
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600;">{}</span>',
            color,
            obj.risk_score
        )
    risk_score_colored.short_description = 'Risk Skoru'


@admin.register(RiskMitigation)
class RiskMitigationAdmin(admin.ModelAdmin):
    list_display = ['risk', 'mitigation_action', 'status', 'effectiveness', 'deadline']
    list_filter = ['status', 'effectiveness']
    search_fields = ['risk__risk_name', 'mitigation_action']


@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ['company', 'metric_name', 'metric_category', 'current_value', 'trend', 'last_updated']
    list_filter = ['metric_category', 'trend']
    search_fields = ['company__name', 'metric_name']


@admin.register(MetricTarget)
class MetricTargetAdmin(admin.ModelAdmin):
    list_display = ['metric', 'target_period', 'target_value', 'is_achieved']
    list_filter = ['is_achieved', 'target_period']


@admin.register(FinancialAlert)
class FinancialAlertAdmin(admin.ModelAdmin):
    list_display = ['company', 'alert_type', 'severity', 'is_active', 'triggered_at']
    list_filter = ['alert_type', 'severity', 'is_active']
    search_fields = ['company__name', 'alert_message']
    date_hierarchy = 'triggered_at'


@admin.register(AdvisoryReport)
class AdvisoryReportAdmin(admin.ModelAdmin):
    list_display = ['company', 'report_type', 'report_date', 'generated_by']
    list_filter = ['report_type', 'report_date']
    search_fields = ['company__name', 'report_title']
    date_hierarchy = 'report_date'


@admin.register(FinancialHealthSnapshot)
class FinancialHealthSnapshotAdmin(admin.ModelAdmin):
    list_display = ['company', 'snapshot_date', 'overall_score', 'liquidity_score', 'profitability_score', 'solvency_score']
    list_filter = ['snapshot_date']
    search_fields = ['company__name']
    date_hierarchy = 'snapshot_date'


# ============================================================================
# YENİ KOBİ ANALİZ MODELLERİ - ADMIN KAYITLARI
# ============================================================================

from .models import (
    FinancialRating, BusinessValuation, WorkingCapitalAnalysis,
    BreakEvenAnalysis, SensitivityAnalysis, ScenarioPlanning
)

@admin.register(FinancialRating)
class FinancialRatingAdmin(admin.ModelAdmin):
    list_display = ['company', 'rating_date', 'overall_rating', 'financial_strength', 'outlook', 'rated_by', 'valid_until']
    search_fields = ['company__name', 'rating_rationale']
    list_filter = ['overall_rating', 'outlook', 'rating_date']
    date_hierarchy = 'rating_date'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BusinessValuation)
class BusinessValuationAdmin(admin.ModelAdmin):
    list_display = ['company', 'valuation_date', 'valuation_method', 'enterprise_value', 'equity_value', 'valued_by']
    search_fields = ['company__name', 'methodology_notes']
    list_filter = ['valuation_method', 'valuation_date']
    date_hierarchy = 'valuation_date'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(WorkingCapitalAnalysis)
class WorkingCapitalAnalysisAdmin(admin.ModelAdmin):
    list_display = ['company', 'analysis_date', 'working_capital', 'current_ratio', 'quick_ratio', 'cash_conversion_cycle']
    search_fields = ['company__name']
    list_filter = ['analysis_date']
    date_hierarchy = 'analysis_date'
    readonly_fields = ('working_capital', 'net_working_capital', 'current_ratio', 'quick_ratio', 'cash_ratio', 'cash_conversion_cycle', 'created_at')


@admin.register(BreakEvenAnalysis)
class BreakEvenAnalysisAdmin(admin.ModelAdmin):
    list_display = ['company', 'analysis_date', 'breakeven_units', 'breakeven_sales_revenue', 'margin_of_safety_percentage']
    search_fields = ['company__name']
    list_filter = ['analysis_period', 'analysis_date']
    date_hierarchy = 'analysis_date'
    readonly_fields = ('contribution_margin_per_unit', 'contribution_margin_ratio', 'breakeven_units', 'breakeven_sales_revenue', 'margin_of_safety_units', 'margin_of_safety_percentage', 'created_at')


@admin.register(SensitivityAnalysis)
class SensitivityAnalysisAdmin(admin.ModelAdmin):
    list_display = ['company', 'analysis_date', 'variable_name', 'base_value', 'sensitivity_coefficient']
    search_fields = ['company__name', 'variable_name', 'base_scenario_name']
    list_filter = ['analysis_date']
    date_hierarchy = 'analysis_date'
    readonly_fields = ('created_at',)


@admin.register(ScenarioPlanning)
class ScenarioPlanningAdmin(admin.ModelAdmin):
    list_display = ['company', 'scenario_name', 'scenario_type', 'planning_period_start', 'planning_period_end', 'probability', 'confidence_level']
    search_fields = ['company__name', 'scenario_name']
    list_filter = ['scenario_type', 'confidence_level', 'created_at']
    readonly_fields = ('created_at', 'updated_at')