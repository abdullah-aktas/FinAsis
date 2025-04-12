import api from './api';

// Sanal şirket modülü API servisleri
const virtualCompanyService = {
  // Şirketler
  getCompanies: () => api.get('/virtual-company/companies/'),
  getCompany: (id: number) => api.get(`/virtual-company/companies/${id}/`),
  createCompany: (data: any) => api.post('/virtual-company/companies/', data),
  updateCompany: (id: number, data: any) => api.put(`/virtual-company/companies/${id}/`, data),
  deleteCompany: (id: number) => api.delete(`/virtual-company/companies/${id}/`),
  
  // Departmanlar
  getDepartments: (companyId: number) => api.get(`/virtual-company/companies/${companyId}/departments/`),
  getDepartment: (companyId: number, id: number) => api.get(`/virtual-company/companies/${companyId}/departments/${id}/`),
  createDepartment: (companyId: number, data: any) => api.post(`/virtual-company/companies/${companyId}/departments/`, data),
  updateDepartment: (companyId: number, id: number, data: any) => api.put(`/virtual-company/companies/${companyId}/departments/${id}/`, data),
  deleteDepartment: (companyId: number, id: number) => api.delete(`/virtual-company/companies/${companyId}/departments/${id}/`),
  
  // Çalışanlar
  getEmployees: (companyId: number) => api.get(`/virtual-company/companies/${companyId}/employees/`),
  getEmployee: (companyId: number, id: number) => api.get(`/virtual-company/companies/${companyId}/employees/${id}/`),
  createEmployee: (companyId: number, data: any) => api.post(`/virtual-company/companies/${companyId}/employees/`, data),
  updateEmployee: (companyId: number, id: number, data: any) => api.put(`/virtual-company/companies/${companyId}/employees/${id}/`, data),
  deleteEmployee: (companyId: number, id: number) => api.delete(`/virtual-company/companies/${companyId}/employees/${id}/`),
  
  // Projeler
  getProjects: (companyId: number) => api.get(`/virtual-company/companies/${companyId}/projects/`),
  getProject: (companyId: number, id: number) => api.get(`/virtual-company/companies/${companyId}/projects/${id}/`),
  createProject: (companyId: number, data: any) => api.post(`/virtual-company/companies/${companyId}/projects/`, data),
  updateProject: (companyId: number, id: number, data: any) => api.put(`/virtual-company/companies/${companyId}/projects/${id}/`, data),
  deleteProject: (companyId: number, id: number) => api.delete(`/virtual-company/companies/${companyId}/projects/${id}/`),
  
  // Görevler
  getTasks: (companyId: number, projectId: number) => api.get(`/virtual-company/companies/${companyId}/projects/${projectId}/tasks/`),
  getTask: (companyId: number, projectId: number, id: number) => api.get(`/virtual-company/companies/${companyId}/projects/${projectId}/tasks/${id}/`),
  createTask: (companyId: number, projectId: number, data: any) => api.post(`/virtual-company/companies/${companyId}/projects/${projectId}/tasks/`, data),
  updateTask: (companyId: number, projectId: number, id: number, data: any) => api.put(`/virtual-company/companies/${companyId}/projects/${projectId}/tasks/${id}/`, data),
  deleteTask: (companyId: number, projectId: number, id: number) => api.delete(`/virtual-company/companies/${companyId}/projects/${projectId}/tasks/${id}/`),
};

export default virtualCompanyService; 