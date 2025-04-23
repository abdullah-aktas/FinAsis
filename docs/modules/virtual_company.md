# Virtual Company Modülü

## Genel Bakış
Virtual Company modülü, kullanıcıların sanal şirketler oluşturup yönetebileceği, günlük görevler ve raporlar üzerinde çalışabileceği bir sistemdir.

## Temel Özellikler

### 1. Sanal Şirket Yönetimi
- Şirket oluşturma ve düzenleme
- Departman yönetimi
- Çalışan yönetimi
- Proje yönetimi
- Bütçe yönetimi

### 2. Günlük Görevler
- Görev oluşturma ve düzenleme
- Görev adımları
- Görev durumu takibi
- XP ve ödül sistemi
- Not ekleme

### 3. Raporlar
- Rapor oluşturma
- Rapor paylaşımı
- Rapor analizi
- Rapor geçmişi

### 4. Analizler
- Veri analizi
- Performans metrikleri
- Trend analizi
- Öneriler

## Modeller

### DailyTask
```python
class DailyTask(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    steps = models.JSONField()
    xp_reward = models.IntegerField()
    money_reward = models.DecimalField(max_digits=10, decimal_places=2)
    knowledge_reward = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```

### UserDailyTask
```python
class UserDailyTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(DailyTask, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    completed_steps = models.JSONField(default=list)
    notes = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
```

### Report
```python
class Report(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Analysis
```python
class Analysis(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    data = models.JSONField()
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```

## View'lar

### DailyTask Views
- `DailyTaskListView`: Görev listesi görünümü
- `DailyTaskDetailView`: Görev detay görünümü
- `DailyTaskCreateView`: Görev oluşturma görünümü
- `DailyTaskUpdateView`: Görev güncelleme görünümü
- `DailyTaskDeleteView`: Görev silme görünümü
- `StartDailyTaskView`: Görev başlatma görünümü
- `CompleteDailyTaskStepView`: Görev adımı tamamlama görünümü
- `CompleteDailyTaskView`: Görev tamamlama görünümü
- `ToggleDailyTaskActiveView`: Görev aktiflik durumu değiştirme görünümü
- `AddDailyTaskNoteView`: Görev notu ekleme görünümü

### Report Views
- `ReportListView`: Rapor listesi görünümü
- `ReportDetailView`: Rapor detay görünümü
- `ReportCreateView`: Rapor oluşturma görünümü
- `ReportUpdateView`: Rapor güncelleme görünümü
- `ReportDeleteView`: Rapor silme görünümü

### Analysis Views
- `AnalysisListView`: Analiz listesi görünümü
- `AnalysisDetailView`: Analiz detay görünümü
- `AnalysisCreateView`: Analiz oluşturma görünümü
- `AnalysisUpdateView`: Analiz güncelleme görünümü
- `AnalysisDeleteView`: Analiz silme görünümü

## Formlar

### DailyTaskForm
```python
class DailyTaskForm(ModelForm):
    class Meta:
        model = DailyTask
        fields = ['title', 'description', 'category', 'difficulty', 
                 'steps', 'xp_reward', 'money_reward', 'knowledge_reward']
```

### ReportForm
```python
class ReportForm(ModelForm):
    class Meta:
        model = Report
        fields = ['title', 'content', 'is_public']
```

### AnalysisForm
```python
class AnalysisForm(ModelForm):
    class Meta:
        model = Analysis
        fields = ['title', 'description', 'data', 'is_public']
```

## Kullanım Örnekleri

### Görev Oluşturma
```python
form = DailyTaskForm(request.POST)
if form.is_valid():
    task = form.save(commit=False)
    task.created_by = request.user
    task.save()
    messages.success(request, _('Görev başarıyla oluşturuldu.'))
```

### Görev Başlatma
```python
task = get_object_or_404(DailyTask, pk=pk)
user_task, _ = UserDailyTask.objects.get_or_create(
    user=request.user,
    task=task,
    defaults={'status': 'BASLAMADI'}
)
user_task.start_task()
```

### Rapor Oluşturma
```python
form = ReportForm(request.POST)
if form.is_valid():
    report = form.save(commit=False)
    report.created_by = request.user
    report.save()
    messages.success(request, _('Rapor başarıyla oluşturuldu.'))
```

## İzinler ve Güvenlik

- Görev oluşturma, güncelleme ve silme işlemleri sadece yöneticiler tarafından yapılabilir
- Raporlar ve analizler isteğe bağlı olarak herkese açık yapılabilir
- Kullanıcılar sadece kendi görevlerini ve raporlarını düzenleyebilir

## AJAX Desteği

Tüm view'lar AJAX isteklerini destekler ve uygun JSON yanıtları döndürür:
```python
if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    return JsonResponse({
        'success': True,
        'message': _('İşlem başarılı.'),
        'data': {...}
    })
```

## Hata Yönetimi

Tüm view'lar hata durumlarını uygun şekilde yönetir:
```python
try:
    # İşlem
except Exception as e:
    messages.error(request, str(e))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
```

## Önbellekleme

Performans için önemli veriler önbelleğe alınır:
```python
cache_key = f'user_tasks_{user.id}'
user_tasks = cache.get(cache_key)
if not user_tasks:
    user_tasks = UserDailyTask.objects.filter(user=user)
    cache.set(cache_key, user_tasks, 3600)  # 1 saat
``` 