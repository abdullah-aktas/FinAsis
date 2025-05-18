# -*- coding: utf-8 -*-
from typing import Dict, Any, List, Optional
from datetime import datetime
from django.conf import settings
from ..base import BaseAPIIntegration
from ..services import IntegrationService, APIService

class ERPService(APIService):
    """ERP entegrasyonu servisi"""
    
    def __init__(self):
        config = IntegrationService.get_integration_config('erp')
        super().__init__(
            base_url=config.get('base_url'),
            headers={
                'Authorization': f"Bearer {config.get('api_key')}",
                'Content-Type': 'application/json'
            }
        )
    
    def get_company_info(self) -> Dict[str, Any]:
        """Şirket bilgilerini al"""
        endpoint = "/company"
        return self.get(endpoint)
    
    def update_company_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Şirket bilgilerini güncelle"""
        endpoint = "/company"
        return self.put(endpoint, json=data)
    
    def get_departments(
        self,
        page: int = 1,
        per_page: int = 50,
        active_only: bool = True
    ) -> Dict[str, Any]:
        """Departmanları listele"""
        endpoint = "/departments"
        params = {
            'page': page,
            'per_page': per_page,
            'active_only': active_only
        }
        return self.get(endpoint, params=params)
    
    def get_department_details(self, department_id: str) -> Dict[str, Any]:
        """Departman detaylarını al"""
        endpoint = f"/departments/{department_id}"
        return self.get(endpoint)
    
    def create_department(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Departman oluştur"""
        endpoint = "/departments"
        return self.post(endpoint, json=data)
    
    def update_department(
        self,
        department_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Departman güncelle"""
        endpoint = f"/departments/{department_id}"
        return self.put(endpoint, json=data)
    
    def get_employees(
        self,
        page: int = 1,
        per_page: int = 50,
        department_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Çalışanları listele"""
        endpoint = "/employees"
        params = {
            'page': page,
            'per_page': per_page
        }
        if department_id:
            params['department_id'] = department_id
        if status:
            params['status'] = status
        return self.get(endpoint, params=params)
    
    def get_employee_details(self, employee_id: str) -> Dict[str, Any]:
        """Çalışan detaylarını al"""
        endpoint = f"/employees/{employee_id}"
        return self.get(endpoint)
    
    def create_employee(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Çalışan oluştur"""
        endpoint = "/employees"
        return self.post(endpoint, json=data)
    
    def update_employee(
        self,
        employee_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Çalışan güncelle"""
        endpoint = f"/employees/{employee_id}"
        return self.put(endpoint, json=data)
    
    def get_employee_attendance(
        self,
        employee_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Çalışan devam durumunu al"""
        endpoint = f"/employees/{employee_id}/attendance"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
        return self.get(endpoint, params=params)
    
    def get_employee_leaves(
        self,
        employee_id: str,
        year: int,
        month: Optional[int] = None
    ) -> Dict[str, Any]:
        """Çalışan izinlerini al"""
        endpoint = f"/employees/{employee_id}/leaves"
        params = {'year': year}
        if month:
            params['month'] = month
        return self.get(endpoint, params=params)
    
    def get_employee_salary(
        self,
        employee_id: str,
        year: int,
        month: int
    ) -> Dict[str, Any]:
        """Çalışan maaş bilgilerini al"""
        endpoint = f"/employees/{employee_id}/salary"
        params = {
            'year': year,
            'month': month
        }
        return self.get(endpoint, params=params)
    
    def get_projects(
        self,
        page: int = 1,
        per_page: int = 50,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Projeleri listele"""
        endpoint = "/projects"
        params = {
            'page': page,
            'per_page': per_page
        }
        if status:
            params['status'] = status
        return self.get(endpoint, params=params)
    
    def get_project_details(self, project_id: str) -> Dict[str, Any]:
        """Proje detaylarını al"""
        endpoint = f"/projects/{project_id}"
        return self.get(endpoint)
    
    def create_project(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Proje oluştur"""
        endpoint = "/projects"
        return self.post(endpoint, json=data)
    
    def update_project(
        self,
        project_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Proje güncelle"""
        endpoint = f"/projects/{project_id}"
        return self.put(endpoint, json=data)
    
    def get_project_tasks(
        self,
        project_id: str,
        page: int = 1,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """Proje görevlerini listele"""
        endpoint = f"/projects/{project_id}/tasks"
        params = {
            'page': page,
            'per_page': per_page
        }
        return self.get(endpoint, params=params)
    
    def get_task_details(self, task_id: str) -> Dict[str, Any]:
        """Görev detaylarını al"""
        endpoint = f"/tasks/{task_id}"
        return self.get(endpoint)
    
    def create_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Görev oluştur"""
        endpoint = "/tasks"
        return self.post(endpoint, json=data)
    
    def update_task(
        self,
        task_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Görev güncelle"""
        endpoint = f"/tasks/{task_id}"
        return self.put(endpoint, json=data)
    
    def get_inventory_items(
        self,
        page: int = 1,
        per_page: int = 50,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Envanter öğelerini listele"""
        endpoint = "/inventory"
        params = {
            'page': page,
            'per_page': per_page
        }
        if category:
            params['category'] = category
        return self.get(endpoint, params=params)
    
    def get_inventory_item_details(self, item_id: str) -> Dict[str, Any]:
        """Envanter öğesi detaylarını al"""
        endpoint = f"/inventory/{item_id}"
        return self.get(endpoint)
    
    def update_inventory_item(
        self,
        item_id: str,
        quantity: int,
        operation: str = 'add'
    ) -> Dict[str, Any]:
        """Envanter öğesi güncelle"""
        endpoint = f"/inventory/{item_id}"
        data = {
            'quantity': quantity,
            'operation': operation
        }
        return self.put(endpoint, json=data)
    
    def get_financial_reports(
        self,
        start_date: datetime,
        end_date: datetime,
        report_type: str
    ) -> Dict[str, Any]:
        """Finansal raporları al"""
        endpoint = "/reports/financial"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'type': report_type
        }
        return self.get(endpoint, params=params)
    
    def get_hr_reports(
        self,
        start_date: datetime,
        end_date: datetime,
        report_type: str
    ) -> Dict[str, Any]:
        """İK raporlarını al"""
        endpoint = "/reports/hr"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'type': report_type
        }
        return self.get(endpoint, params=params)
    
    def get_project_reports(
        self,
        start_date: datetime,
        end_date: datetime,
        report_type: str
    ) -> Dict[str, Any]:
        """Proje raporlarını al"""
        endpoint = "/reports/projects"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'type': report_type
        }
        return self.get(endpoint, params=params)
    
    def get_inventory_reports(
        self,
        start_date: datetime,
        end_date: datetime,
        report_type: str
    ) -> Dict[str, Any]:
        """Envanter raporlarını al"""
        endpoint = "/reports/inventory"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'type': report_type
        }
        return self.get(endpoint, params=params)
    
    def get_system_settings(self) -> Dict[str, Any]:
        """Sistem ayarlarını al"""
        endpoint = "/settings"
        return self.get(endpoint)
    
    def update_system_settings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sistem ayarlarını güncelle"""
        endpoint = "/settings"
        return self.put(endpoint, json=data)
    
    def get_audit_logs(
        self,
        start_date: datetime,
        end_date: datetime,
        page: int = 1,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """Denetim loglarını al"""
        endpoint = "/audit-logs"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'page': page,
            'per_page': per_page
        }
        return self.get(endpoint, params=params)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Sistem durumunu kontrol et"""
        endpoint = "/status"
        return self.get(endpoint)
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Entegrasyon durumunu kontrol et"""
        endpoint = "/integration/status"
        return self.get(endpoint)
    
    def sync_data(self, data_type: str) -> Dict[str, Any]:
        """Veri senkronizasyonu başlat"""
        endpoint = "/sync"
        data = {'data_type': data_type}
        return self.post(endpoint, json=data)
    
    def get_sync_status(self, sync_id: str) -> Dict[str, Any]:
        """Senkronizasyon durumunu kontrol et"""
        endpoint = f"/sync/{sync_id}/status"
        return self.get(endpoint) 