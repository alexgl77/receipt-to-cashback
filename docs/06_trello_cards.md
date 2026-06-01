# Trello board — Cards listas para crear

> El brief pide explícitamente un Trello dashboard con progreso diario y el link enviado a Yossi.
> Sign in: https://trello.com — usá el template del bootcamp si lo encontrás, si no, creá un board vacío con 4 listas: **Backlog · Doing · Done · Blocked**.

## Cómo usar este doc

Copiá cada bloque debajo como una card. Cada card tiene **título + descripción + checklist + label**. Las cards de "Done" del día 1 las dejás ya marcadas como hechas (porque ya las hicimos).

---

## Lista: `Done` — Día 1 (2026-06-01)

### ✅ Card: "Day 1 — Project scaffolding"
**Label:** `setup`
**Descripción:** Crear estructura inicial del repo, archivos base y documentación. Repo público en GitHub.
**Checklist:**
- [x] Crear carpeta `final project/` con subdirectorios
- [x] Escribir `requirements.txt`, `.gitignore`, `.env.example`
- [x] Redactar contenido del Proposal Form en `docs/01_proposal.md`
- [x] Escribir README skeleton
- [x] Inicializar `docs/00_simple_explanation.md` y `docs/02_architecture.md`
- [x] Crear repo público en GitHub: https://github.com/alexgl77/receipt-to-cashback
- [x] Push del primer commit

### ⏳ Card: "Day 1 — Submit Proposal Form to Yossi"
**Label:** `blocker` `instructor`
**Descripción:** El brief lo marca como mandatorio antes de codear funcionalidades. El contenido está listo en `docs/01_proposal.md`, solo hay que pegarlo en el form.
**Checklist:**
- [ ] Abrir el Final Project Proposal Form (link en plataforma del bootcamp)
- [ ] Copiar/pegar campos desde `docs/01_proposal.md`
- [ ] Enviar
- [ ] Avisar a Yossi por Slack y pedir aprobación
- [ ] Cuando llegue aprobación: mover a `Done`

### ⏳ Card: "Day 1 — Create Trello board and share with Yossi"
**Label:** `setup` `instructor`
**Descripción:** Mandar el link del board a Yossi por Slack.

---

## Lista: `Backlog` — Días 2 a 11

### 📅 Card: "Day 2 — EDA + synthetic catalog"
**Label:** `data` `notebook`
**Descripción:** Explorar el dataset SROIE 2019 (descargar de HuggingFace o Kaggle). Crear catálogo sintético de ~100 productos chilenos con categorías y marcas.
**Checklist:**
- [ ] Descargar dataset SROIE (`datasets` de HuggingFace: `darentang/sroie`)
- [ ] Notebook `01_eda.ipynb`: cantidad de receipts, distribuciones, ejemplos visuales
- [ ] Crear `data/catalog.csv` con ~100 productos chilenos
- [ ] Agregar entrada al `docs/00_simple_explanation.md` día 2

### 📅 Card: "Day 3 — OCR pipeline"
**Label:** `code` `model`
**Descripción:** Probar TrOCR vs Donut sobre 20 receipts del dataset. Elegir el mejor, encapsular en `src/ocr_pipeline.py`.
**Checklist:**
- [ ] Notebook `03_ocr_pipeline.ipynb` comparando TrOCR y Donut
- [ ] Decidir modelo final basándose en calidad y latencia
- [ ] Crear módulo `src/ocr_pipeline.py` con clase `OCRPipeline`
- [ ] Branch `feat/ocr-pipeline`, merge a `main` cuando funcione
- [ ] Doc simple día 3

### 📅 Card: "Day 4 — LLM extractor with Gemini"
**Label:** `code` `llm` `prompt-engineering`
**Descripción:** Few-shot prompts + validación Pydantic para extraer JSON estructurado del texto OCR.
**Checklist:**
- [ ] Obtener `GEMINI_API_KEY` de aistudio.google.com → `.env`
- [ ] Notebook `04_llm_extraction.ipynb` con prompts iterativos
- [ ] Módulo `src/llm_extractor.py` con clase + Pydantic schema
- [ ] Branch `feat/llm-extractor`
- [ ] Doc simple día 4

### 📅 Card: "Day 5 — CNN + FAISS + deploy decision"
**Label:** `code` `model` `deploy`
**Descripción:** Transfer learning sobre MobileNetV2 para clasificar tipo de comercio. FAISS index del catálogo. **Decidir Streamlit Cloud vs HF Spaces.**
**Checklist:**
- [ ] Notebook `02_cnn_classifier.ipynb` con transfer learning
- [ ] Módulo `src/cnn_validator.py` y `src/vector_store.py` + `src/matcher.py`
- [ ] Branches `feat/cnn-classifier` y `feat/faiss-matcher`
- [ ] Probar tamaño total del stack → decidir destino de deploy
- [ ] Doc simple día 5

### 📅 Card: "Day 6 — CashbackEngine + Streamlit MVP"
**Label:** `code` `oop` `ui`
**Descripción:** Lógica de negocio en OOP + app Streamlit end-to-end (upload → resultado).
**Checklist:**
- [ ] `src/cashback_engine.py` con clase `CashbackEngine` y reglas por categoría
- [ ] `tests/test_cashback_engine.py` con al menos 1 caso que pase
- [ ] `app/streamlit_app.py` MVP funcional local
- [ ] Branch `feat/cashback-engine` y `feat/streamlit-app`
- [ ] Doc simple día 6

### 📅 Card: "Day 7 — Clustering, A/B, validity classifier, B2B view"
**Label:** `code` `stats` `ml`
**Descripción:** Cubrir los puntos clustering, A/B testing y clasificación clásica que faltan. Agregar página B2B al Streamlit.
**Checklist:**
- [ ] Notebook `05_clustering_ab.ipynb` (KMeans + A/B test)
- [ ] Notebook `06_validity_classifier.ipynb` (LogisticRegression)
- [ ] Página B2B en Streamlit con visualizaciones
- [ ] Branch `feat/analytics`
- [ ] Doc simple día 7

### 📅 Card: "Day 8 — Deploy + final README + ethics"
**Label:** `deploy` `docs`
**Descripción:** App pública funcionando + README estilo template + sección ética completa.
**Checklist:**
- [ ] Deploy a Streamlit Cloud o HF Spaces
- [ ] Verificar URL pública funcionando
- [ ] README final con template del brief (badges, screenshots, run instructions)
- [ ] `docs/04_ethics.md` redactado completo
- [ ] Tomar 5-10 fotos de boletas chilenas para el demo
- [ ] Doc simple día 8

### 📅 Card: "Day 9 — PPT + Loom video"
**Label:** `presentation`
**Descripción:** PPT con template del bootcamp + video Loom de 3 min.
**Checklist:**
- [ ] PPT con 6-8 slides usando template del bootcamp
- [ ] Grabar video Loom (≤3 min)
- [ ] Subir video al repo o link en README si pesa >100MB
- [ ] Ensayar cronometrado 4+4+2 = 10 min
- [ ] Doc simple día 9

### 📅 Card: "Day 10 — Buffer + submit"
**Label:** `submission`
**Descripción:** Pulir cualquier bug, completar Trello, submission en plataforma.
**Checklist:**
- [ ] Pasar checklist final de "criterios de listo" del plan
- [ ] Submit en plataforma del bootcamp
- [ ] Trello con todas las cards en `Done`
- [ ] Mensaje a Yossi confirmando submission

### 📅 Card: "Day 11 — DEMO DAY 9:30 AM"
**Label:** `demo`
**Descripción:** Presentación de 10 minutos.
**Checklist:**
- [ ] Llegar 30 min antes
- [ ] Probar internet y proyección con anticipación
- [ ] Tener el laptop con la app abierta y receipts de demo listos
- [ ] PPT abierto en pantalla completa

---

## Lista: `Blocked`

Mover cards aquí si algo se traba (ej: Gemini sin créditos, OCR no funciona, deploy se cae).
