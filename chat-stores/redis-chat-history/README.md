# Redis Chat History with LlamaIndex + Ollama + Redis

Bu proje, bir sohbet motorunun geçmişini **Redis** veritabanında saklayarak yönetmenizi sağlar. `llama-index`, `Ollama` tabanlı bir LLM ve `Redis` kullanılarak oturum bazlı sohbet geçmişi kaydedilir, listelenir ve dışa aktarılır.

## 🧱 Klasör Yapısı

```

redis-chat-history/
│
├── .env                        # Ortam değişkenleri (Ollama vs. gerekiyorsa)
├── .gitignore                  # Gerekli dosyaları Git'ten hariç tutmak için
├── app.py                      # Ana sohbet motoru (chat engine)
├── export\_chat\_history.py      # Redis'ten geçmişi alıp dosyaya yazan script
├── list\_sessions.py            # Mevcut oturum anahtarlarını listeleyen script
├── redis\_chat\_history.txt      # Dışa aktarılan geçmiş buraya yazılır
├── venv/                  # (Varsa) sanal ortam klasörü

````

## 🧠 Uygulamanın Akışı

### 1. `app.py` – Ana Chat Motoru

* Redis'e bağlanır.
* `RedisChatStore` üzerinden `ChatMemoryBuffer` oluşturur.
* UUID ile benzersiz bir `session_X` key'i yaratılır.
* Her mesaj, bu key altında Redis'e kayıt edilir.
* `SimpleChatEngine` ile LLM üzerinden cevap verilir.
* Sistem prompt'u sayesinde asistan karakteri tanımlanır.
* Kullanıcıdan gelen her mesaj, LLM'e gönderilir, cevap alınır, ve Redis'e kaydedilir.

### 2. `list_sessions.py` – Oturumları Listeleme

* Redis'e bağlanır.
* `session_` ile başlayan tüm key'leri listeler.
* Kullanıcıya hangi oturumlar olduğunu gösterir.

### 3. `export_chat_history.py` – Sohbet Geçmişini Dışa Aktarma

* Kullanıcıdan bir `session_X` key'i alır.
* Redis'ten bu key'e ait tüm mesajları çeker.
* `redis_chat_history.txt` adlı dosyaya düzenli formatta yazar.

---

## 🧪 Nasıl Çalıştırılır?

### Redis’i Docker ile başlat:

```bash
docker run -d --name redis-server -p 6379:6379 redis
```

### Sanal Ortam Kurulumu (opsiyonel ama önerilir)

```bash
python -m venv daryl-env
source daryl-env/bin/activate  # Windows: daryl-env\Scripts\activate
pip install -r requirements.txt
```

### Ana sohbet motorunu başlat:

```bash
python app.py
```

Örnek çıktı:

```
Sohbet motoru hazır! (Oturum anahtarı: session_cda82e3a-bd57-44f7-a2de-6f1317eb19f7)
Çıkmak için Ctrl+C
Kullanıcı: Merhaba!
Asistan: Merhaba! Size nasıl yardımcı olabilirim?
```

### Kayıtlı oturumları listele:

```bash
python list_sessions.py
```

Örnek çıktı:

```
3 adet session bulundu:

- session_19ad8...
- session_a2bc3...
- session_5d3f4...
```

### Bir oturumu dışa aktar:

```bash
python export_chat_history.py
```

Komut sırasında:

```
Hangi oturum key'ini çekmek istiyorsun? (örnek: session_1): session_19ad8...
```

Sonuç:

```
Sohbet geçmişi 'redis_chat_history.txt' dosyasına yazıldı.
```

---

## 📦 Geliştirici Notları

* `RedisChatStore` sayesinde kalıcı hafıza sağlanır.
* `ChatMemoryBuffer`, LLM'e geri gönderilecek geçmişi yönetir.
* UUID kullanımı ile her çalışma ayrı bir oturum olarak saklanır.
* `export_chat_history.py` sayesinde geçmiş dosyaya dökülebilir.
* pip install -r r.txt

---


Hazırladığın yapıyı iyi özetleyen bu `README.md` dosyasını doğrudan projenin kök dizinine kaydedebilirsin. Başka bir modül ya da kullanım senaryosu eklemen gerekirse, README'yi genişletebilirim. Yardımcı olayım mı?
```
