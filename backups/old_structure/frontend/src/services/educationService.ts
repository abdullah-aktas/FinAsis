import api from './api';

// Eğitim modülü API servisleri
const educationService = {
  // Kurslar
  getCourses: () => api.get('/education/courses/'),
  getCourse: (id: number) => api.get(`/education/courses/${id}/`),
  createCourse: (data: any) => api.post('/education/courses/', data),
  updateCourse: (id: number, data: any) => api.put(`/education/courses/${id}/`, data),
  deleteCourse: (id: number) => api.delete(`/education/courses/${id}/`),
  
  // Dersler
  getLessons: (courseId: number) => api.get(`/education/courses/${courseId}/lessons/`),
  getLesson: (courseId: number, id: number) => api.get(`/education/courses/${courseId}/lessons/${id}/`),
  createLesson: (courseId: number, data: any) => api.post(`/education/courses/${courseId}/lessons/`, data),
  updateLesson: (courseId: number, id: number, data: any) => api.put(`/education/courses/${courseId}/lessons/${id}/`, data),
  deleteLesson: (courseId: number, id: number) => api.delete(`/education/courses/${courseId}/lessons/${id}/`),
  
  // Sınavlar
  getQuizzes: (courseId: number) => api.get(`/education/courses/${courseId}/quizzes/`),
  getQuiz: (courseId: number, id: number) => api.get(`/education/courses/${courseId}/quizzes/${id}/`),
  createQuiz: (courseId: number, data: any) => api.post(`/education/courses/${courseId}/quizzes/`, data),
  updateQuiz: (courseId: number, id: number, data: any) => api.put(`/education/courses/${courseId}/quizzes/${id}/`, data),
  deleteQuiz: (courseId: number, id: number) => api.delete(`/education/courses/${courseId}/quizzes/${id}/`),
  
  // Ödevler
  getAssignments: (courseId: number) => api.get(`/education/courses/${courseId}/assignments/`),
  getAssignment: (courseId: number, id: number) => api.get(`/education/courses/${courseId}/assignments/${id}/`),
  createAssignment: (courseId: number, data: any) => api.post(`/education/courses/${courseId}/assignments/`, data),
  updateAssignment: (courseId: number, id: number, data: any) => api.put(`/education/courses/${courseId}/assignments/${id}/`, data),
  deleteAssignment: (courseId: number, id: number) => api.delete(`/education/courses/${courseId}/assignments/${id}/`),
  
  // Ödev Teslimleri
  getSubmissions: (courseId: number, assignmentId: number) => api.get(`/education/courses/${courseId}/assignments/${assignmentId}/submissions/`),
  getSubmission: (courseId: number, assignmentId: number, id: number) => api.get(`/education/courses/${courseId}/assignments/${assignmentId}/submissions/${id}/`),
  createSubmission: (courseId: number, assignmentId: number, data: any) => api.post(`/education/courses/${courseId}/assignments/${assignmentId}/submissions/`, data),
  updateSubmission: (courseId: number, assignmentId: number, id: number, data: any) => api.put(`/education/courses/${courseId}/assignments/${assignmentId}/submissions/${id}/`, data),
  deleteSubmission: (courseId: number, assignmentId: number, id: number) => api.delete(`/education/courses/${courseId}/assignments/${assignmentId}/submissions/${id}/`),
  
  // Rozetler
  getBadges: () => api.get('/education/badges/'),
  getBadge: (id: number) => api.get(`/education/badges/${id}/`),
  createBadge: (data: any) => api.post('/education/badges/', data),
  updateBadge: (id: number, data: any) => api.put(`/education/badges/${id}/`, data),
  deleteBadge: (id: number) => api.delete(`/education/badges/${id}/`),
  
  // Kullanıcı Rozetleri
  getUserBadges: (userId: number) => api.get(`/education/users/${userId}/badges/`),
  getUserBadge: (userId: number, id: number) => api.get(`/education/users/${userId}/badges/${id}/`),
  assignBadge: (userId: number, badgeId: number) => api.post(`/education/users/${userId}/badges/${badgeId}/`),
  removeBadge: (userId: number, badgeId: number) => api.delete(`/education/users/${userId}/badges/${badgeId}/`),
};

export default educationService; 