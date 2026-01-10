# Internship Preparation 🚀

I'm currently preparing for my internship.

![daryl](./images/daryl-dixon.gif)


# Daryl Dixon 🚀

**Doğal Dil → SQL + Embedding ile Akıllı Sorgulama Sistemi**

Bu proje, büyük dil modelleri (Large Language Models - LLM) kullanarak doğal dil sorgularını otomatik olarak SQL sorgularına dönüştüren ve hem yapılandırılmış (veritabanı) hem de yapılandırılmamış (metin belgeleri) veriler üzerinde çalışabilen Python tabanlı bir sistemdir.

> 📍 Bu döküman, projenin genel yapısını anlatır.  
> 💡 Şu anda `sql` branch'inde bulunuyorsunuz: Bu dal, SQL ile ilgili bileşenleri barındırır.

---

## 📁 İçindekiler

- [🔍 Proje Hakkında](#-proje-hakkında)
- [🚀 Özellikler](#-özellikler)
- [📂 Dosya Yapısı](#-dosya-yapısı)
- [🧰 Kurulum ve Çalıştırma](#-kurulum-ve-çalıştırma)
- [💬 Kullanım](#-kullanım)
- [📖 Detaylı Açıklamalar](#-detaylı-açıklamalar)
- [📌 Bağımlılıklar](#-bağımlılıklar)

---

## 🔍 Proje Hakkında

Daryl Dixon, doğal dilde verilen Türkçe sorguları SQL'e çevirerek veritabanı üzerinde çalışan, aynı zamanda metin belgelerinden embedding çıkarabilen çok amaçlı bir yapay zeka destekli sorgu motorudur. 

Staj sürecinde SQL, LLM ve belge analizi konularında pratik yapmak amacıyla geliştirilmiştir.

---

## 🚀 Özellikler

- ✅ Türkçe doğal dil sorgularını SQL'e çevirme
- ✅ SQL sorgularını MSSQL veritabanında çalıştırma
- ✅ PDF ve metin dosyaları için embedding çıkarma
- ✅ LlamaIndex + Ollama + HuggingFace entegrasyonu
- ✅ Yerel çalışır, dış API gerektirmez

---

## 📂 Dosya Yapısı



 Daryl-Dixon/
 ├── data/                  → Kullanılan PDF ve belgeler
 ├── storage/               → Embedding ve vektör indeksleri
 ├── llm_sql_query.py       → LLM ile Türkçe doğal dil → SQL çevirici
 ├── llm_sql_query_twdd.py  → The Walking Dead veritabanı özelinde doğal dil → SQL sorgu motoru ✅
 ├── sql_query.py           → Doğrudan SQL sorgusu çalışan test scripti
 ├── test_embed.py          → Belgelerden embedding çıkaran test scripti
 ├── requirements.txt       → Python bağımlılıkları
 └── README.md              → Proje dokümantasyonu (bu dosya)


---

## 🧰 Kurulum ve Çalıştırma

### 1. Python kurulumu

```bash
python --version  # Python 3.8+ olmalı
````

### 2. Gerekli Python paketlerini yükle

```bash
pip install -r requirements.txt
```

Veya elle yüklemek istersen:

```bash
pip install llama-index sqlalchemy pyodbc ollama
```

### 3. MSSQL kurulumu

* Windows’a **ODBC Driver 17/18 for SQL Server** kurulu olmalı
* Yerel SQL Server instance (örnek: `ZELIS\REEDUS`) çalışır durumda olmalı
* `MyDatabase` isimli bir veritabanı ve `documents` adında tablo oluşturulmalı

---

## 💬 Kullanım

### 🔹 `sql_query.py`

Klasik SQL sorgularını doğrudan çalıştırır:

```bash
python sql_query.py
```

### 🔹 `llm_sql_query.py`

Türkçe doğal dil sorgularını SQL'e çevirir ve çalıştırır:

```bash
python llm_sql_query.py
```

🧪 Örnek sorgu:

```
Sorgunuz: Son 5 belgeyi listele
Yanıt: ...
Oluşturulan SQL: SELECT TOP 5 * FROM documents ORDER BY created_at DESC
```

---

## 📖 Detaylı Açıklamalar

### ✅ `llm_sql_query.py`

* MSSQL'e bağlanır
* `Ollama` içindeki `phi3` modeli ile Türkçe sorguyu SQL'e çevirir
* `llama_index` ile sorguyu optimize eder ve çalıştırır

### ✅ `sql_query.py`

* `pyodbc` ile doğrudan SQL sorgusu çalıştırır
* Test amaçlı örnek: `SELECT id, title, content FROM documents`

### ✅ `test_embed.py`

* `data/` klasöründeki PDF/txt/docx dosyaları yükler
* HuggingFace ile embedding (vektör) çıkarır
* `VectorStoreIndex` oluşturur ve `query_engine` ile anlamlı arama yapar

### ✅ `llm_sql_query_twdd.py`

**The Walking Dead** temalı özel veritabanı için doğal dil → SQL sorgu motorudur.
---

## 📌 Bağımlılıklar

```text
llama-index
sqlalchemy
pyodbc
ollama
torch
transformers
```

> 📦 Bunların çoğu `pip install -r requirements.txt` ile yüklenebilir.

Ek olarak sistemde:

* 🟢 Microsoft SQL Server (ZELIS\REEDUS gibi bir instance)
* 🟢 ODBC Driver 17 veya 18
* 🟢 Ollama kurulumu ([https://ollama.com/download](https://ollama.com/download))

---

