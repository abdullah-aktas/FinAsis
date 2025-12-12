# Yerel LLM Kurulum Rehberi

FinAsis artık tamamen yerel çalışan yapay zeka desteği sunuyor! Verileriniz Türkiye'de kalır, hiçbir dış servise gönderilmez.

## 🎯 Özellikler

- ✅ **Tamamen Yerel**: Veriler dış servislere gönderilmez
- ✅ **KVKK Uyumlu**: Tüm veriler Türkiye'de işlenir
- ✅ **Ollama Desteği**: Kolay kurulum ve kullanım
- ✅ **Transformers Desteği**: Hugging Face modelleri
- ✅ **Türkçe Destekli**: Türkçe konuşan modeller

## 📦 Kurulum Seçenekleri

### Seçenek 1: Ollama (Önerilen - En Kolay)

Ollama, yerel LLM çalıştırmak için en kolay yöntemdir.

#### 1. Ollama'yı İndirin ve Kurun

**Windows:**
```bash
# https://ollama.ai/download adresinden indirin
# veya PowerShell'de:
winget install Ollama.Ollama
```

**Linux/Mac:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### 2. Ollama Servisini Başlatın

```bash
ollama serve
```

#### 3. Model İndirin

Türkçe destekli modeller:

```bash
# Llama 3.2 3B (Önerilen - Hızlı ve verimli)
ollama pull llama3.2:3b

# Llama 3.2 1B (Çok hızlı, düşük kaynak)
ollama pull llama3.2:1b

# Mistral 7B (Güçlü performans)
ollama pull mistral:7b

# Qwen 2.5 7B (Mükemmel Türkçe desteği)
ollama pull qwen2.5:7b
```

#### 4. Environment Değişkenlerini Ayarlayın

`.env` dosyanıza ekleyin:

```env
# Yerel LLM kullan
FINASIS_AI_PROVIDER=local
LOCAL_LLM_PROVIDER=ollama
LOCAL_LLM_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://localhost:11434

# İsteğe bağlı ayarlar
LOCAL_LLM_MAX_TOKENS=800
LOCAL_LLM_TEMPERATURE=0.7
LOCAL_LLM_TOP_P=0.9
```

### Seçenek 2: Transformers (Hugging Face)

Transformers kullanarak Hugging Face modellerini indirebilirsiniz.

#### 1. Gerekli Paketleri Kurun

```bash
pip install transformers torch accelerate
```

#### 2. Model İndirin

```bash
python manage.py download_llm_model Qwen/Qwen2.5-3B-Instruct
```

#### 3. Environment Değişkenlerini Ayarlayın

```env
FINASIS_AI_PROVIDER=local
LOCAL_LLM_PROVIDER=transformers
LOCAL_LLM_MODEL=Qwen/Qwen2.5-3B-Instruct
LOCAL_LLM_MODEL_PATH=/path/to/models/llm
```

## 🔧 Yapılandırma

### Otomatik Provider Seçimi

Sistem otomatik olarak en uygun provider'ı seçer:

```env
FINASIS_AI_PROVIDER=auto
```

Bu modda:
1. Önce yerel LLM kontrol edilir
2. Yerel LLM yoksa OpenAI kontrol edilir
3. Hiçbiri yoksa mock moduna geçer

### Manuel Provider Seçimi

```env
# Sadece yerel LLM kullan
FINASIS_AI_PROVIDER=local

# Sadece OpenAI kullan
FINASIS_AI_PROVIDER=openai

# Otomatik seçim (önerilen)
FINASIS_AI_PROVIDER=auto
```

## 📊 Önerilen Modeller

### Hızlı ve Verimli (3B-7B)

- **llama3.2:3b** (Ollama) - En hızlı, iyi performans
- **Qwen/Qwen2.5-3B-Instruct** (Transformers) - Mükemmel Türkçe

### Güçlü Performans (7B+)

- **mistral:7b** (Ollama) - Güçlü, genel amaçlı
- **qwen2.5:7b** (Ollama) - En iyi Türkçe desteği

### Düşük Kaynak (1B-3B)

- **llama3.2:1b** (Ollama) - Çok hızlı, minimal kaynak

## 🚀 Kullanım

Kurulum tamamlandıktan sonra, AI asistan otomatik olarak yerel modeli kullanacaktır.

### Test Etme

```python
from ai_assistant.services.local_llm_service import LocalLLMService

# Servisi başlat
llm = LocalLLMService(provider="ollama", model_name="llama3.2:3b")

# Model bilgilerini kontrol et
print(llm.get_model_info())

# Test mesajı
response = llm.generate(
    prompt="Finansal raporlama nedir?",
    system_prompt="Sen bir finans uzmanısın.",
    max_tokens=200
)
print(response)
```

## 🔍 Sorun Giderme

### Ollama Bağlantı Hatası

```bash
# Ollama servisinin çalıştığını kontrol edin
curl http://localhost:11434/api/tags

# Ollama'yı yeniden başlatın
ollama serve
```

### Transformers Model Hatası

```bash
# Model yolunu kontrol edin
python manage.py download_llm_model <model_name>

# GPU kullanımını kontrol edin
python -c "import torch; print(torch.cuda.is_available())"
```

### Yetersiz Bellek

Küçük modeller kullanın:
- `llama3.2:1b` (1B parametre)
- `llama3.2:3b` (3B parametre)

## 📝 Notlar

- **İlk Kullanım**: Model ilk kez kullanıldığında indirme yapılabilir (Ollama)
- **GPU Desteği**: Transformers GPU kullanabilir (CUDA varsa)
- **Bellek**: 3B model için ~4GB RAM, 7B model için ~8GB RAM gerekir
- **Hız**: Ollama genellikle daha hızlıdır, Transformers daha esnektir

## 🎉 Başarı!

Yerel AI modeliniz hazır! Artık verileriniz tamamen Türkiye'de kalıyor ve KVKK uyumlu şekilde işleniyor.

