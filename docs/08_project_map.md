# El mapa del proyecto — qué hace cada cosa, dónde está, cómo verla

Este doc es para alguien que **no programa** y necesita entender qué construimos. Sirve para la conversación con Yossi, para mostrarle el proyecto a un familiar, y para vos mismo cuando llegue el demo y necesites explicar algo sin abrir el código.

Las cosas existen en cuatro lugares:

- **En tu computador** (carpeta `final project/`) — todo el código fuente y los datos
- **En GitHub** (https://github.com/alexgl77/receipt-to-cashback) — el mismo código, accesible públicamente
- **En tu navegador, en local** (http://localhost:8501) — la app corriendo en tu máquina
- **En la nube** (Hugging Face Spaces, URL cuando termine el deploy) — la app corriendo para que cualquiera la use

---

## 1. La app que ve el usuario final (Streamlit)

**Dónde:** http://localhost:8501 mientras corre local; o la URL pública en Hugging Face Spaces cuando esté deployada.

**Qué es:** una página web con cuatro pestañas en la barra lateral izquierda.

| Pestaña | Qué hace | Analogía |
|---|---|---|
| **Upload Receipt** | El usuario sube la foto de una boleta y recibe un número de cashback. Ve la lista de items que la app reconoció y cuánto cashback dio cada uno. | Es como entregarle el ticket de compras a un cajero que lo lee, lo entiende línea por línea, y te devuelve dinero. |
| **B2B Analytics** | La vista que vería un cliente que **compra** los datos. Muestra clusters de usuarios por patrón de gasto, el resultado del A/B test (¿conviene pagar 2% o 3%?), y totales agregados. | Es el panel de control del gerente que vende los datos a marcas y consultoras. |
| **Ethics** | El documento de ética **dentro** de la app, no escondido en un PDF aparte. | Es el aviso de derechos y privacidad, pero visible y bien escrito. |
| **About this project** | Descripción del proyecto en lenguaje no-técnico para el visitante curioso. | El "Sobre nosotros" típico de cualquier app. |

---

## 2. Las piezas técnicas que la app usa por dentro

Cuando el usuario sube una foto, **detrás del telón** pasa esto, en este orden:

| # | Pieza | Archivo | Qué hace (sin jerga) |
|---|---|---|---|
| 1 | **OCR** | [`src/ocr_pipeline.py`](../src/ocr_pipeline.py) | Lee el texto de la foto, línea por línea, como una persona leyendo en voz alta lo que dice una boleta arrugada. Usa un modelo llamado EasyOCR. |
| 2 | **LLM Extractor** | [`src/llm_extractor.py`](../src/llm_extractor.py) | Le pasa el texto crudo a **Gemini** (el modelo de Google) y le dice: "convertí esto en una lista limpia de productos con precios". Le pone un ejemplo y un molde fijo para que no se invente cosas. |
| 3 | **Matcher / Vector DB** | [`src/vector_store.py`](../src/vector_store.py) + [`src/matcher.py`](../src/matcher.py) | Para cada producto que reconoció, busca en nuestro catálogo de 110 productos cuál se le parece más, **incluso si está en otro idioma**. Usa FAISS, que compara productos por significado, no por letras. |
| 4 | **CashbackEngine** | [`src/cashback_engine.py`](../src/cashback_engine.py) | Aplica la regla de cashback (por defecto 2% sobre cada línea con precio) y devuelve el número final. |
| 5 | **Streamlit App** | [`app/streamlit_app.py`](../app/streamlit_app.py) | Es la pantalla que ve el usuario. Junta todas las piezas anteriores y muestra el resultado lindo. |

**Tiempo total que tarda:** entre 8 y 30 segundos por boleta, dependiendo de cuántos items tenga.

---

## 3. Las piezas que NO se ven en la app pero sirven al negocio

| Pieza | Archivo | Qué hace |
|---|---|---|
| **Generador de usuarios sintéticos** | [`src/synthetic_users.py`](../src/synthetic_users.py) | Crea 400 usuarios falsos con 4 perfiles distintos (café-regular, family-meals, sweet-tooth, office-worker), porque el dataset público no trae identidad de usuario. |
| **Analytics** | [`src/analytics.py`](../src/analytics.py) | Dos funciones: una que **agrupa usuarios** por su patrón de gasto (K-Means clustering) y otra que **compara dos cohortes** con un test estadístico (A/B test con Welch's t-test). |
| **Catálogo de productos** | [`data/catalog.csv`](../data/catalog.csv) | Una tabla con 110 productos de comida y bebida (Iced Tea, Donut, White Rice, etc.), su categoría y la tasa de cashback. Es contra esto que matcheamos cada item de cada boleta. |

---

## 4. La documentación

| Archivo | Para quién | Qué tiene |
|---|---|---|
| [`README.md`](../README.md) | Evaluador / reclutador que abre el repo en GitHub | El proyecto explicado en 2 minutos: tagline, pipeline, tech stack, cómo correrlo, links al live |
| [`docs/00_simple_explanation.md`](00_simple_explanation.md) | Vos para la presentación | **El diario del proyecto día por día**, en lenguaje no-técnico. Es de donde sale el speech del PPT y del video |
| [`docs/01_proposal.md`](01_proposal.md) | Yossi (instructor) | El proposal del scope aprobado |
| [`docs/02_architecture.md`](02_architecture.md) | Quien quiera entender el diseño técnico | Diagrama del pipeline + por qué cada decisión |
| [`docs/04_ethics.md`](04_ethics.md) | Jurado del demo + vos | 7 secciones sobre privacidad, consentimiento, sesgo, hallucination, k-anonimato |
| [`docs/05_demo_script.md`](05_demo_script.md) | Vos para grabar el video Loom | Guion de 3 minutos cronometrado |
| [`docs/06_trello_cards.md`](06_trello_cards.md) | Vos para armar el Trello | Cards listas para pegar |
| [`docs/07_deploy_guide.md`](07_deploy_guide.md) | Vos para subir a HF Spaces | Pasos del deploy |
| [`presentation/PPT_OUTLINE.md`](../presentation/PPT_OUTLINE.md) | Vos para armar el PPT | 8 slides cronometrados, contenido + speech |

---

## 5. Los notebooks (los "experimentos documentados")

Cada notebook es una **sesión de análisis** ejecutada con sus resultados ya guardados. Sirven para mostrar el proceso de toma de decisiones a un evaluador técnico, sin que tenga que correr nada.

| Notebook | Qué muestra |
|---|---|
| [`notebooks/01_eda.ipynb`](../notebooks/01_eda.ipynb) | Exploración del dataset CORD-v2 + del catálogo. Cuántas boletas, qué tan largas, qué items son más comunes. |
| [`notebooks/03_ocr_pipeline.ipynb`](../notebooks/03_ocr_pipeline.ipynb) | Prueba del OCR sobre 20 boletas reales: 85% de recall promedio, 100% en 16/20. |
| [`notebooks/05_faiss_cashback.ipynb`](../notebooks/05_faiss_cashback.ipynb) | Spine end-to-end sobre 3 boletas: foto → cashback final. |
| [`notebooks/07_clustering_ab.ipynb`](../notebooks/07_clustering_ab.ipynb) | El análisis B2B: clustering recupera los 4 archetypes + A/B muestra que 3% trae 29% más datos que 2% (p<0.05). |

---

## 6. Tests

**Dónde:** [`tests/test_cashback_engine.py`](../tests/test_cashback_engine.py)

**Qué hace:** 7 pruebas automáticas que verifican que el motor de cashback hace exactamente lo que dice hacer. Si alguien (vos, yo, un futuro Alex) modifica el motor sin querer y lo rompe, los tests fallan inmediatamente.

**Cómo correrlos** (en una terminal en la carpeta del proyecto):
```bash
.venv\Scripts\python -m unittest tests.test_cashback_engine -v
```

Salida esperada: `Ran 7 tests in 0.002s   OK`.

---

## 7. ¿Cómo está esto conectado con el bootcamp?

Cada pieza del proyecto sale de una semana específica del curso GenAI & ML 2026:

| Semana | Tema del bootcamp | Dónde se usa en el proyecto |
|---|---|---|
| Week 1-2 | Python Fundamentals + OOP | Toda la arquitectura de clases en `src/` |
| Week 3-4 | Data Analysis + applications | Notebook EDA, dashboard B2B |
| Week 5 | Machine Learning + Statistics | K-Means clustering, Welch's t-test |
| Week 6 | Deep Learning (NN, CNN, RNN) | Quality-gate CNN opcional (bonus, no en el spine) |
| Week 7 | LLM and Gen AI | Pre-trained models (Gemini, EasyOCR) |
| Week 8 | NLP & RAG | FAISS + sentence-transformers (vector search) |
| Week 9 | Prompt Engineering | Few-shot prompts + Pydantic schema en `llm_extractor.py` |
| Week 10 | Agentic AI / MCP | No incluido (bonus que cortamos por tiempo) |

**Streamlit es la única tecnología no enseñada en el bootcamp** — la aprendimos en el camino porque el brief la pide explícitamente.

---

## 8. Cómo verificar que todo esto es verdad (no me creas, comprobalo)

| Quiero verificar… | Hago esto |
|---|---|
| Que el código es mío y no inventado | Abro https://github.com/alexgl77/receipt-to-cashback → veo todos los commits con fecha y firma |
| Que la app funciona | Abro http://localhost:8501 → subo una boleta → veo el cashback |
| Que los tests pasan | Corro `python -m unittest tests.test_cashback_engine -v` en terminal |
| Que el análisis B2B es honesto | Abro `notebooks/07_clustering_ab.ipynb` en VS Code → veo gráficos y números |
| Que la ética está pensada | Abro `docs/04_ethics.md` o la pestaña Ethics en la app |

---

## 9. Una frase que resume todo

> *Receipt-to-Cashback es una app que paga a la gente un pequeño cashback por cada boleta que sube, y vende los datos de consumo agregados a la industria. Todo el pipeline (lectura, estructura, clasificación, cálculo) está armado con modelos pre-entrenados y dura unos 8 segundos por boleta. La ética no es decoración: es lo que define qué se puede vender y qué no.*

Esa es la línea que respondés cuando alguien te pregunta "¿qué hiciste?" en 10 segundos.
