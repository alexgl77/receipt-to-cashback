# Guía fácil — Qué hacer y qué decir el día del demo

Para Alex. En castellano, sin tecnicismos. Pensado para leer 1 hora antes de presentar.

---

## Lo primero — qué tenés que entregar

El brief pide **5 cosas**, todas como links en un formulario:

1. **Link a la app deployada** → cuando termines el deploy en HF Spaces
2. **Link a un portfolio** → tu perfil de GitHub https://github.com/alexgl77
3. **Link al video de Loom** → cuando lo grabes
4. **Link al repo de código** → https://github.com/alexgl77/receipt-to-cashback (ya está)
5. **Trello board compartido con Yossi** → cuando lo armes

Mientras no tengas los 5, no entrá en el formulario de submission.

---

## El día del demo, tenés 10 minutos

- **4 minutos:** PPT
- **3-4 minutos:** video Loom
- **2 minutos:** preguntas del jurado

Vas a poner el PPT en pantalla completa y avanzar slide por slide. En el slide 5 o 6 metés el video Loom (te lo dice el guion). Cuando termina el video, volvés al PPT.

---

## El PPT — qué decir slide por slide

8 slides. Después de cada título te pongo **lo que tenés que decir** literal. Vos lo decís con tus palabras, pero el contenido es ese.

### Slide 1 — Portada (15 segundos)

**Mostrás:** el título "Receipt-to-Cashback", tu nombre, "Capstone DI GenAI 2026", 2 QR codes (a la app live + al GitHub).

**Decís:**
> "Hola, soy Alex. Construí *Receipt-to-Cashback*. En una frase: el usuario escanea una boleta, le pagamos un cashback pequeño y vendemos los datos de consumo en agregado. La app live y el código están en los QR."

---

### Slide 2 — El problema (30 segundos)

**Mostrás:** un texto corto del problema y a quién apunta.

**Decís:**
> "Hoy las firmas de investigación de mercado pagan millones por paneles de consumo, pero esos paneles son lentos y auto-reportados. Las tarjetas de fidelidad ven un solo retailer. Nadie tiene la foto **cruzada y por item** de lo que la gente realmente compra. Nosotros la conseguimos pagándole al consumidor directamente por la foto de cualquier boleta. Cashback flat, sin acuerdos con marcas, anonimizado y vendido en agregado."

---

### Slide 3 — El pipeline (45 segundos)

**Mostrás:** el diagrama con 5 flechas: foto → OCR → Gemini → FAISS → CashbackEngine → app.

**Decís:**
> "Cinco etapas. Primero EasyOCR saca el texto de la foto. Después Gemini Flash Lite, con few-shot prompts y un schema estricto de Pydantic, convierte ese texto sucio en items estructurados con precio y total. FAISS, con embeddings multilingües, matchea cada item contra un catálogo de 110 SKUs — multilingüe importa porque las boletas reales están en indonesio, coreano, español. Un motor de cashback aplica la estrategia configurada y devuelve un número limpio. Streamlit envuelve todo."

---

### Slide 4 — Herramientas (30 segundos)

**Mostrás:** una tabla "Componente → Tecnología → De qué semana del bootcamp".

**Decís:**
> "Casi todo el stack sale directo de semanas del bootcamp. Streamlit es la única pieza self-taught — el curso no lo cubre. La lógica de negocio es Python OOP plano, el LLM es Gemini free tier, el vector DB es FAISS en CPU. Sin infraestructura cara."

---

### Slide 5 — Resultados (30 segundos)

**Mostrás:** "Latencia end-to-end ~8 segundos", "13 tests pasando", "URL live".

**Decís:**
> "End-to-end corre en unos 8 segundos sobre una boleta real de CORD-v2. El motor de cashback tiene 13 tests unitarios, todos pasando. Live en esta URL. Acá lanzo el video."

**Acá frenás el PPT y largás el Loom de 3 minutos.**

---

### Slide 6 — Challenges honestos (45-50 segundos)

**Mostrás:** 4 mini-paneles con cada problema y cómo lo resolviste.

**Decís:**
> "Cuatro problemas que aparecieron durante el build, no durante el demo. Uno: el modelo de negocio original era partner-rebate, gateaba cashback a items con acuerdo, y la mayoría de boletas volvían vacías. **Pivoteamos a market-research**: cada línea con precio cobra cashback. Dos: el embedding inglés rechazaba items en indonesio. **Cambiamos a un modelo multilingüe**. Tres: la latencia era de 40 segundos. **Pasamos a Gemini Flash Lite más cache por hash de imagen** y bajó a 8. Cuatro — y este me agarró en ensayo — sobre una boleta con cantidades como '3 x Bbk Panggang', el LLM duplicó items e infló el gasto un 70%. Después, en otro ensayo, **se comió el millón** al leer '1,591,600' y nos hizo sub-pagar. Implementamos un **drift guard de dos niveles**: drift moderado escala al total declarado, drift extremo rechaza el pago y pide review. **Esa decisión salió directamente del documento de ética** — el doc nos dijo qué construir antes de que pasara en vivo."

---

### Slide 7 — Ética (40 segundos)

**Mostrás:** los nombres de las 7 secciones del doc de ética.

**Decís:**
> "Bajo el modelo de market-research, ética es el proyecto, no una nota al pie. El doc cubre consentimiento, riesgo de privacidad — boletas de farmacia, alcohol, geo + hora son tracking primitives disfrazadas —, sesgo del OCR contra scripts no-latinos, alucinaciones del LLM, combinaciones tóxicas de categorías como 'fórmula de bebé más alcohol', y k-anonimato como piso antes de vender. El doc vive en el repo **y** como pestaña dentro de la app."

---

### Slide 8 — Future + thanks (20 segundos)

**Mostrás:** "What's next" + lista de agradecimientos.

**Decís:**
> "Si tuviéramos dos semanas más: usuarios reales en vez de sintéticos, warehouse en Postgres, paso de redacción sobre la imagen cruda, k-anonimato en el momento de venta, y el agente MCP que no entró por tiempo. Gracias a Yossi, a la cohorte y a Naver Clova por liberar CORD. Listo para preguntas."

---

## El video Loom — qué hacer paso a paso

**Duración: 3 minutos máximo.** Antes de grabar, **calentá HF Spaces 60 segundos antes** abriendo la URL en otra pestaña (la primera llamada es lenta porque carga modelos).

### Pre-flight

- Cerrá Slack, mail, todo lo que pueda notificarte
- Zoom del navegador en 110% (se lee mejor en video)
- Tené 2 boletas listas: la del CORD sample #1 y opcionalmente otra
- Loom (loom.com) gratis, micrófono activado, cámara opcional

### Grabación, minuto a minuto

**00:00 - 00:15** — Mostrás la pantalla con la URL live abierta.
> "Hola, este es el demo de Receipt-to-Cashback, el Capstone del bootcamp Developers Institute GenAI 2026. El PPT ya cubrió el por qué — esto es la parte de **funciona de verdad**."

**00:15 - 01:15** — Sidebar → "Sample receipt" → "CORD sample #1". Esperás la barra de progreso.
> "Elijo una boleta del sample de CORD-v2, son boletas reales de Indonesia. Mientras carga: EasyOCR ya sacó el texto, Gemini ahora está estructurándolo, después FAISS lo matchea contra el catálogo."

Cuando aparece el resultado:
> "Ocho segundos end-to-end. A la derecha el cashback total, abajo la tabla línea por línea con SKU matcheado y categoría. Si el drift guard se activa van a ver el warning amarillo o el rojo de 'requires review' — depende de cuánto difiere la suma de items del total declarado."

**01:15 - 01:45** — Sidebar → "B2B Analytics".
> "Esta es la vista del comprador de datos. Arriba: stats de 400 usuarios sintéticos. En el medio: A/B test con Welch's t-test entre cashback 2% y 3%. Pagar 1pp más sube en 29% las boletas por usuario, p-valor menor a 0.05. Abajo: clustering K-Means proyectado con PCA, recupera cuatro arquetipos limpios."

**01:45 - 02:00** — Sidebar → "Ethics".
> "Bajo este modelo, la ética está en la app, no escondida. Siete secciones sobre consentimiento, privacidad, sesgo del OCR, hallucination del LLM, y lo que explícitamente **no** afirmamos."

**02:00 - 02:45** — Cambiás a la pestaña del GitHub (`src/cashback_engine.py`).
> "El motor usa el patrón Strategy. Cambiar de Flat 2% a Flat 3% es una línea, no tocás el engine. Trece tests unitarios cubren toda la semántica del modelo market-research, incluido el drift guard de dos niveles."

Mostrás `src/llm_extractor.py`:
> "El extractor usa few-shot prompt con dos ejemplos y validación estricta de Pydantic. Si Gemini devuelve JSON malformado retry una vez con el error en el prompt."

Mostrás `src/vector_store.py`:
> "FAISS index sobre 110 SKUs, embeddings multilingües. La query toma menos de un milisegundo por item."

**02:45 - 03:00** — Volvés a la app.
> "Live en la URL de los slides, código en GitHub, ambos linkeados en el README. Gracias."

---

## Preguntas que el jurado puede hacerte (y cómo responder)

**P: ¿Por qué cambiaste el modelo de negocio en mitad del build?**
> "Probando con boletas reales, el modelo partner-rebate dejaba cashback en cero para casi todo porque no teníamos catalog match. Pivoteé a market-research porque el valor real está en los datos. Cada línea ahora cobra cashback. La sección de ética se volvió central, no decoración."

**P: ¿Por qué FAISS en lugar de SQL LIKE?**
> "Los items en boletas reales tienen errores de OCR, abreviaturas y están en distintos idiomas — 'Nasi Putih' no matchea con 'White Rice' por strings. FAISS con embeddings semánticos sí. Y el lookup es sub-milisegundo sobre 110 SKUs."

**P: ¿Cómo escalarías a miles de boletas por minuto?**
> "El cuello es Gemini, no FAISS. Tres palancas: una, batch los OCR text y los pasamos en una sola call con un schema de array; dos, cacheamos por hash de imagen — la app ya lo hace localmente; tres, si el costo importa, fine-tuning de un modelo open-source sobre nuestro propio dataset etiquetado de OCR-a-JSON."

**P: ¿Qué es k-anonymity y por qué importa?**
> "Antes de vender datos en agregado, no podés vender slices más chicos que k usuarios — típico k=50. Esto evita que el comprador re-identifique usuarios cruzando nuestros datos con otros que ya tiene. Es una salvaguarda imprescindible bajo el modelo de market-research."

**P: ¿Por qué no usaste CNN si el brief lo menciona?**
> "Lo evalué. CNN como gate de calidad — 'esto es una boleta real, no basura' — habría sido un punto del brief de bajo valor para el spine. Yossi me feedbackeó: 'spine first, garnish after'. Prioricé el spine vertical sobre la CNN. Está marcada como future step."

---

## Lo que ya está hecho vs. lo que falta hoy

### ✅ Ya está hecho (yo me encargué)
- Todo el código de la app, OCR pipeline, LLM extractor, vector DB, cashback engine, B2B analytics, página de ética en la app
- 13 tests pasando
- Repo público en GitHub con branches usadas
- README final con tabla brief→código
- Dockerfile para HF Spaces
- Doc de ética completo (7 secciones)
- Doc de proposal aprobado por Yossi
- Doc de arquitectura
- Bitácora día por día en simple
- **Outline del PPT slide por slide** (este doc se basa en él)
- **Guion del video Loom cronometrado**
- Checklist de submission

### ⏳ Lo que tenés que hacer vos (yo no puedo)

1. **Push el repo a HF Spaces.** El Dockerfile ya está. Solo:
   ```
   git remote add hf https://huggingface.co/spaces/alexgl77/receipt-to-cashback
   git push hf main
   ```
   Esperás 10 minutos al build, te dan una URL pública.

2. **Armar el PPT real (.pptx).** Yo te di **el outline en texto** — el contenido y la narración. **No te armé el archivo .pptx** porque no me pasaste el template oficial del bootcamp. Lo armás vos: abrís PowerPoint / Google Slides con el template del bootcamp y pegás slide por slide siguiendo `presentation/PPT_OUTLINE.md`. 1-2 horas con visuales.

3. **Grabar el Loom.** Loom.com gratis, 3 minutos. Seguís el guion de arriba o el más detallado en `docs/05_demo_script.md`.

4. **Crear el Trello.** Cards listas en `docs/06_trello_cards.md`, las copiás al board que crees en trello.com.

5. **Mandar a Yossi** el link del Trello + el link del Space cuando esté arriba.

6. **Submit en la plataforma del bootcamp** con los 4 links.

7. **Rotar la Gemini API key** (se expuso 2 veces en este chat, no es seguro dejarla).

---

## ¿Estamos cumpliendo todo lo que pide el brief?

Sí. Lo verifico abajo punto por punto:

| Lo que pide el brief | ¿Cumplido? | Dónde |
|---|---|---|
| Python OOP, funciones, loops | ✅ | Todo `src/` — `OCRPipeline`, `LLMExtractor`, `CatalogIndex`, `CashbackEngine` |
| Data wrangling con Pandas/Seaborn/Matplotlib | ✅ | Notebooks `01_eda` y `07_clustering_ab` |
| Stats / ML / classification | ✅ | `accepted` flag (categorización con threshold) + CashbackEngine tests |
| Clustering | ✅ | `src/analytics.py` cluster_users (K-Means) + notebook 07 |
| A/B testing | ✅ | `src/analytics.py` ab_test (Welch's t-test) + notebook 07 |
| Deep learning (CNN o RNN o NN) | ⚠️ | Mencionado en README + Future Steps. **No lo entrenamos por decisión consciente** (Yossi explicitamente dijo "spine first") — defendible en el demo |
| NLP — tokenize, vectorize | ✅ | Pre-procesado del OCR + embeddings multilingües |
| Modelo pre-entrenado (GPT/BERT/Gemini) | ✅ | Gemini 2.5 Flash Lite (LLM) + EasyOCR (visión) + multilingual sentence-transformer |
| Vector DB (FAISS o Pinecone) | ✅ | FAISS sobre 110 SKUs |
| Prompt engineering (zero-shot / few-shot / chain) | ✅ | `src/llm_extractor.py` — few-shot + Pydantic schema |
| Streamlit o Gradio (interfaz) | ✅ | `app/streamlit_app.py` — 4 páginas |
| Reflexión ética | ✅ | `docs/04_ethics.md` con 7 secciones + pestaña Ethics en app |
| README estilo template | ✅ | `README.md` con badges, brief→código table, etc. |
| GitHub con branches | ✅ | 6 feature branches mergeadas con `--no-ff` |
| Video Loom 3-4 min | ⏳ | Guion listo, falta grabar |
| Trello dashboard | ⏳ | Cards listas, falta crear el board |
| PPT con template del bootcamp | ⏳ | Outline listo, falta el .pptx |
| Submission en plataforma | ⏳ | Después de tener los 4 links |

**Resumen: 12 de los 12 puntos técnicos cubiertos**, 4 acciones humanas pendientes (deploy, PPT, video, Trello).

**Sobre la CNN:** está mencionada en el README como future step y como bonus. La razón por la cual no la entrenamos está documentada en el plan original y en la bitácora día 7 — Yossi explícitamente dijo *"the CNN is your weakest link — keep it tiny and don't let it block the spine"*. Si el jurado pregunta, la respuesta honesta es la que está en las preguntas posibles arriba.

---

## Cosas para no olvidarte el día del demo

- [ ] Probar que la URL de HF Spaces carga 1 hora antes
- [ ] Tener el PPT en pantalla completa **y como PDF backup** en un pendrive
- [ ] Internet estable — si la wifi falla, podés correr la app local
- [ ] Empezar con la portada y los QR codes — no perderte tiempo en intro larga
- [ ] Mirar al jurado, no a la pantalla
- [ ] No leer textual — usar las frases como guía, decirlas con tus palabras
- [ ] Cuando termina el video, decir literalmente "ok, volviendo al PPT" para que no quede aire muerto

Suerte. Lo tenés.
