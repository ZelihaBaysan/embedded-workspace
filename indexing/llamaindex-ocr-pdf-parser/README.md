# 🦙 LlamaIndex OCR PDF Parser

Bu proje, OCR (Optik Karakter Tanıma) gerektiren taranmış PDF’ler dahil olmak üzere çeşitli belge türlerini (PDF, DOCX, PPTX, HTML, TXT) işleyerek metne dönüştürür, vektörlere gömer ve ChromaDB’ye indeksler. LlamaIndex, LlamaParse ve HuggingFace modelleri ile entegre çalışır.

---

## 📁 Klasör Yapısı

```
llamaindex-ocr-pdf-parser/
│
├── documents/                    # İşlenecek belgeler
│   ├── sample_scanned.pdf       # OCR gerektiren taranmış PDF
│   ├── sample_text_based.pdf    # Metin tabanlı PDF
│   └── example.*                # Diğer belgeler
│
├── index.py                     # Ana çalışma dosyası
├── ocr_embedding.py             # Belge okuma, OCR ve içerik çıkarımı
├── .env                         # Ortam değişkenleri (API key vs.)
├── .gitignore                   # Gereksiz dosyalar
└── requirements.txt             # Python bağımlılıkları
```

---

## 🔧 Kurulum

```bash
git clone ...
cd llamaindex-ocr-pdf-parser
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`.env` dosyasını oluştur ve aşağıdaki gibi yapılandır:

```
LLAMA_CLOUD_API_KEY=...
DOCUMENTS_PATH=./documents
CHROMA_DB_PATH=./chroma_db
CHROMA_COLLECTION_NAME=llama_parsed_docs
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
```

---

## 🧠 İş Akışı

### 1. Belge Toplama (`get_documents`)

* Belgeler belirtilen dizinden okunur.
* Uzantısına göre uygun işlemci fonksiyona yönlendirilir.
* PDF'ler LlamaParse ile işlenir. Gerekirse OCR uygulanır.
* Tüm belgeler `llama_index.core.Document` nesnesine dönüştürülür.

### 2. İçerik Çıkarımı

#### `_process_with_llamaparse`

* PDF dosyalarında LlamaParse çağrılır.
* Metin tabanlısa doğrudan ayrıştırılır, değilse OCR uygulanır.
* Markdown formatında temiz bir çıktı elde edilir.

#### `_process_docx`, `_process_pptx`, `_process_html`, `_process_txt`

* PDF dışında kalan belgeler için yedek işlemci fonksiyonlardır.
* Gerekli durumlarda `python-docx`, `python-pptx`, `unstructured` kütüphaneleri kullanılır.

### 3. Metadata Zenginleştirme (`customize_metadata`)

* Belgelerin kaynağı, boyutu, dosya tipi, işlenme yöntemi gibi bilgiler metadata’ya eklenir.

---

## 🧾 `apply_rules()` Fonksiyonu

Henüz tamamlanmamış bir fonksiyondur. Belgelerin filtrelenmesi amacıyla planlanmıştır. Belgelerin yoluna veya adına göre belirli dosyaları dahil etmek ya da hariç tutmak için regex desenleri uygulanması öngörülmektedir.

---

## 📦 Vektörleştirme ve İndeksleme

* Belgeler önce `MarkdownNodeParser` ile bölümlere ayrılır.
* Ardından HuggingFace modeli ile vektör embedding’leri oluşturulur.
* Son olarak ChromaDB’ye aktarılır.

`index.py` çalıştırıldığında:

1. Belgeleri tarar ve içeriklerini çıkarır.
2. Embedding’leri üretir.
3. Chroma koleksiyonuna indeksler.

---

## 📊 Sonuç Raporu

İşlem sonrası aşağıdaki bilgiler konsola yazdırılır:

* İşlenen belge sayısı
* Vektör koleksiyonundaki toplam öğe sayısı
* Kullanılan embedding modeli
* Kullanılan parser türü

---

## 📚 Desteklenen Belge Türleri

| Uzantı | Açıklama                                  |
| ------ | ----------------------------------------- |
| .pdf   | Metin tabanlı ve taranmış PDF (OCR dahil) |
| .docx  | Microsoft Word belgeleri                  |
| .pptx  | Microsoft PowerPoint sunumları            |
| .html  | Web sayfaları (HTML formatında)           |
| .txt   | Düz metin dosyaları                       |

---

## 🧠 Arama Özelliği

Belgeler indekslendikten sonra LlamaIndex’in `VectorIndexQueryEngine` altyapısı kullanılarak semantik arama yapılabilir.

---

## 🛠 Geliştirme Durumu

* [x] LlamaParse ile OCR destekli PDF ayrıştırma
* [x] DOCX, PPTX, HTML ve TXT desteği
* [x] HuggingFace embedding entegrasyonu
* [x] ChromaDB indeksleme
* [ ] Belge filtreleme fonksiyonları
* [ ] Arama motoru arayüzü (isteğe bağlı)

---

