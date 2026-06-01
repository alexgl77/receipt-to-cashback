# Bitácora simple — Receipt-to-Cashback

> **Para qué sirve este doc:** poder explicar el proyecto a alguien que no sabe programar, en menos de 5 minutos. Es el guion del PPT y del video del demo. Cada vez que construimos algo, escribimos una entrada aquí **inmediatamente después**.
>
> **Formato de cada entrada:**
> 1. **Qué hicimos** (1 frase, sin jerga)
> 2. **Para qué sirve en la app** (analogía concreta)
> 3. **De qué semana del bootcamp viene**
> 4. **Trozo de código clave** (3-5 líneas con explicación humana)

---

## Día 1 — 2026-06-01 — Setup inicial

### Qué hicimos
Armamos los cimientos del proyecto: la carpeta donde vive el código, los archivos que le dicen al computador qué librerías necesita, y los documentos donde vamos a ir contando lo que hagamos.

### Para qué sirve en la app
Es como antes de cocinar: pones la tabla, los cuchillos, el delantal y la receta a la vista. No estás cocinando todavía, pero sin esto no podés empezar bien.

### De qué semana del bootcamp viene
Esto es buen oficio de programación — no es de una semana específica, es lo que cualquier proyecto Python decente necesita para no convertirse en un desastre a los 3 días.

### Trozo clave
El archivo `requirements.txt` es la lista de ingredientes del proyecto. Cada línea es una librería que instalamos con `pip install -r requirements.txt`. Por ejemplo:

```
tensorflow>=2.15.0      # para entrenar la red neuronal (CNN, Week 6)
transformers>=4.40.0    # para usar el modelo de OCR pre-entrenado (Week 7-8)
faiss-cpu>=1.7.4        # la base de datos vectorial para matchear productos (Week 8)
google-generativeai     # para llamar a Gemini, el LLM que estructura los datos (Week 9)
streamlit>=1.30.0       # para hacer la interfaz web (lo aprendemos sobre la marcha)
```

Cada librería tiene un nombre de semana al lado: así, cuando alguien me pregunte "¿por qué usas FAISS?", puedo responder "porque en la semana 8 vimos vector databases y RAG, y FAISS es la implementación más simple para empezar".

---

### Qué más pasó el día 1
- Se creó el **repositorio público en GitHub**: https://github.com/alexgl77/receipt-to-cashback
- Se hizo el **primer commit** con la estructura base
- Se redactaron las **cards de Trello** listas para pegar (en [docs/06_trello_cards.md](06_trello_cards.md))
- Se separó este proyecto del repo del bootcamp (la carpeta `final project/` ahora es repo aparte)

### Lo que queda como acción humana del día 1
- Mandar la idea a Yossi por Slack (mensaje preparado) y esperar aprobación
- Una vez aprobada: pegar el contenido de [docs/01_proposal.md](01_proposal.md) en el form de la plataforma
- Crear el Trello board copiando las cards de [docs/06_trello_cards.md](06_trello_cards.md) y mandar el link a Yossi
- (Cuando llegue el día 4) Generar la API key de Gemini en https://aistudio.google.com/app/apikey

### Decisión de scope ajustada al final del día 1
Cambiamos "boletas chilenas reales para el demo" por "SROIE para todo (training y demo)". Razón: simplicidad y reproducibilidad — la app no necesita salir del laboratorio para demostrar el pipeline. Como consecuencia, el catálogo de productos también se cambia de "chileno" a "genérico internacional" (Coca-Cola, Pepsi, etc.), para que los items extraídos por el OCR matcheen contra el catálogo. La narrativa pierde el toque local pero gana coherencia técnica.

---

## Día 2 — 2026-06-02 — Datos y catálogo

### Qué hicimos
Bajamos el dataset público de boletas, lo miramos por dentro para entender qué tan parecido es a lo que vamos a recibir en producción, y construimos un catálogo de 110 productos contra el que la app va a hacer match.

### Para qué sirve en la app
Si la app fuera un restaurante, el dataset son los "platos de muestra" con los que el cocinero practicó. El catálogo es el menú real: cuando llega una nueva boleta, hay que mapear cada línea ("Iced Tea", "Nasi Putih") a un ítem del menú para saber qué cashback corresponde.

### De qué semana del bootcamp viene
**Week 3 y 4** — Data Analysis y aplicación de data analysis. Pandas para cargar el catálogo, Seaborn y Matplotlib para los gráficos del EDA, y la libreria `datasets` de HuggingFace para cargar el dataset público.

### Cambio importante de dataset
Originalmente íbamos a usar **SROIE**, pero el loader oficial está deprecado en la versión nueva de `datasets`. Cambiamos a **CORD-v2** (Naver Clova), que además tiene mejor anotación: SROIE solo etiqueta 4 campos (empresa, fecha, dirección, total), mientras que CORD-v2 etiqueta cada **línea de producto individual** con su nombre, cantidad y precio. Esto es exactamente lo que necesitamos para evaluar la pipeline OCR → LLM → FAISS.

Yossi específicamente alertó este punto: "SROIE doesn't have product-line-item labels". Cambiar a CORD-v2 resuelve el problema antes de que se vuelva uno.

### Lo que aprendimos mirando los datos
- CORD-v2 tiene 1000 boletas: 800 train + 100 validation + 100 test
- Las boletas son de restaurantes, cafés y panaderías (en su mayoría del sudeste asiático)
- Cada boleta tiene **promedio 2.6 items** — la app va a hacer 2-3 lookups FAISS por boleta, muy barato
- Hay 1479 nombres de productos únicos en el corpus de train, en una mezcla de inglés e indonesio transliterado ("Nasi Putih" = arroz blanco, "Iced Tea", "TWIST DONUT", etc.)
- Esto **justificó cambiar el plan original** del catálogo: pensábamos en productos retail tipo Coca-Cola, pero CORD es comida — entonces el catálogo es F&B genérico (rice, donut, iced tea, etc.) que sí puede matchear

### El catálogo final
110 productos en 6 categorías: food (50), beverage (26), bakery (16), dessert (8), snack (5), misc (5). Cada uno con un nombre genérico, precio referencial y tasa de cashback (0% a 5%). Está en `data/catalog.csv`.

### Trozo clave
El notebook `notebooks/01_eda.ipynb` parsea los ground-truths así:

```python
def items_from(example):
    gt = json.loads(example['ground_truth'])['gt_parse']
    menu = gt.get('menu', [])
    if isinstance(menu, dict):
        menu = [menu]  # a veces es 1 item suelto, no lista
    return [it['nm'].strip()
            for it in menu
            if isinstance(it, dict) and isinstance(it.get('nm'), str)]
```

Cada boleta es JSON con una llave `menu` que es lista de items, cada uno con su `nm` (nombre), `cnt` (cantidad) y `price` (precio). Esto es **exactamente la estructura que vamos a pedirle a Gemini que devuelva** cuando le pasemos el texto OCR — así la salida del LLM y el ground-truth tienen el mismo schema y podemos evaluar precisión directo.

---

## Día 3 — 2026-06-03 — OCR pipeline

### Qué hicimos
Construimos la parte de la app que **lee el texto de una boleta**. Le pasás una foto y te devuelve las líneas de texto que aparecen en ella, en orden de arriba hacia abajo. Probamos sobre 20 boletas reales del dataset y medimos qué tan bien funciona.

### Para qué sirve en la app
Es el primer paso "real" del pipeline. Sin esto, no hay texto que el LLM pueda procesar. Volviendo a la analogía del restaurante: el OCR es la persona que recibe la boleta arrugada en la mano, la endereza, y la lee en voz alta. Después viene otra persona (el LLM) que toma esa lectura y la organiza en una lista limpia.

### De qué semana del bootcamp viene
**Week 7** (LLM and Gen AI) y **Week 8** (NLP & Architecture). Específicamente la idea de **usar modelos pre-entrenados** sin entrenarlos nosotros. EasyOCR usa dos modelos ya entrenados (uno para detectar dónde hay texto en la imagen, otro para reconocer cada palabra). Nosotros no entrenamos nada; los usamos directo.

### Qué herramienta elegimos y por qué
**EasyOCR.** Lo comparamos contra otras dos opciones:
- **TrOCR (Microsoft):** modelo más moderno, basado en transformers (lo mismo que GPT/BERT), pero requiere un detector de texto separado — más trabajo de integración.
- **Donut (Naver):** un modelo "todo-en-uno" pero ya está fine-tuned al dataset CORD, lo cual sería "trampa" (mataría el caso de uso del LLM más adelante).

EasyOCR es la opción más práctica: una sola llamada (`reader.readtext(image)`) hace detección + reconocimiento. Funciona en CPU. Demoró 5-11 segundos por boleta en este equipo, aceptable para una demo (no para producción real-time, pero eso lo discutimos en la sección de ética).

### Cómo medimos qué tan bien funciona
Sobre 20 boletas:
- **Recall promedio del 85%** — en promedio recuperamos 85% de los items que el ground-truth dice que están en la boleta
- **100% de recall en 16 de las 20 boletas** — la mayoría sale perfecta
- **Latencia: 13 segundos promedio, 24 segundos en el peor caso**

El 15% que se pierde son boletas con texto muy borroso o escritura no-latina compleja. El LLM en el día 4 va a poder recuperar parte de esto.

### Trozo clave
La pipeline está encapsulada en una clase para que el resto de la app no se preocupe del backend:

```python
class OCRPipeline:
    def __init__(self, languages=('en',), gpu=False):
        # EasyOCR descarga modelos la primera vez, se queda en memoria
        self._reader = easyocr.Reader(list(languages), gpu=gpu, verbose=False)

    def read_text(self, image, separator='\n') -> str:
        # Acepta PIL Image, numpy array, bytes, o path
        return separator.join(ln.text for ln in self.read_lines(image))
```

Esto cumple con el requisito de **OOP del brief** (Week 1-2): clase con `__init__`, métodos públicos, encapsulación. Si mañana quisiéramos cambiar EasyOCR por TrOCR, sería un cambio de una sola clase, no de toda la app.

### Branch usada
`feat/ocr-pipeline` → merged a `main` cuando funcionó end-to-end. Esto cumple el requisito explícito del brief de "use branches".

---

## Día 4 — 2026-06-04 — LLM extractor (con Gemini)

### Qué hicimos
Conectamos la app con Gemini 2.5 Flash (un LLM de Google) y le enseñamos, con dos ejemplos, a leer el texto crudo que sale del OCR y devolver una **lista limpia y estructurada de productos, precios y total**. Y además le pusimos un "candado": si por alguna razón el LLM devuelve algo raro, el sistema lo detecta y lo rechaza antes de que llegue a la siguiente etapa.

### Para qué sirve en la app
Es el "ordenador" del pipeline. El OCR del día 3 nos da texto desordenado tipo:
```
Nasi Campur Bali
75,000
Ice Lemon Tea
24,000
TOTAL
99,000
```
Y el LLM nos devuelve algo limpio que el código puede usar directo:
```python
items = [
  {name: "Nasi Campur Bali", quantity: 1, line_total: 75000},
  {name: "Ice Lemon Tea",   quantity: 1, line_total: 24000},
]
total = 99000
currency = "IDR"
```

Volviendo a la analogía del restaurante: si el OCR es la persona que lee la boleta en voz alta, el LLM es el que toma nota organizada en una libreta. Sin esta etapa, el resto de la app no sabría qué hacer con la lista de palabras sueltas.

### De qué semana del bootcamp viene
**Week 7 (LLM and Gen AI)** y **Week 9 (Prompt Engineering)**. Concretamente:
- **Uso de un modelo pre-entrenado** (Gemini 2.5 Flash) sin entrenarlo nosotros — Week 7
- **Few-shot prompting**: en el prompt incluímos 2 ejemplos completos (boleta + JSON esperado) para que el modelo aprenda el formato a la primera — Week 9
- **Structured output con schema strict**: en lugar de pedirle "devuelve JSON por favor" y rezar, le pasamos un schema Pydantic y el SDK de Gemini se encarga de forzarlo — patrón moderno de Gen AI

### El "candado" anti-error
Yossi específicamente nos alertó: *"el LLM va a devolver JSON malformado de vez en cuando o va a alucinar un total — manejá ese caso o la demo se rompe en vivo"*.

Lo que hicimos:
1. **Schema obligatorio** en la llamada a Gemini → el SDK rechaza output que no sea JSON válido antes de que llegue a nuestro código
2. **Validación con Pydantic** después → si el JSON no respeta los tipos esperados, lo capturamos
3. **Un reintento** con el mensaje de error pegado al prompt → "tu intento anterior falló porque X, corregilo"
4. **Excepción tipada** (`LLMExtractionError`) si después de 2 intentos sigue sin funcionar → la app muestra un error amigable al usuario, no se cae

Tres capas de defensa. La demo no se va a romper porque el LLM tuvo un mal día.

### Cómo nos fue (medido en vivo sobre 5 receipts reales)
- **80% de los productos del ground-truth se extrajeron correctamente** (recall por nombre)
- **Total exacto coincide en 2/5 boletas** — esto NO es crítico porque el cashback lo calculamos sobre los precios de cada línea (line_total), no sobre el total agregado
- **Latencia end-to-end (OCR + LLM): ~40 segundos por boleta** en CPU. Lento para producción, aceptable para demo con spinner

### Trozo clave
El schema Pydantic que define el contrato entre el LLM y el resto del código:

```python
class LineItem(BaseModel):
    name: str                          # "Nasi Campur Bali"
    quantity: int = 1
    unit_price: float | None = None    # 75000.0
    line_total: float | None = None    # 75000.0

class ReceiptExtraction(BaseModel):
    items: list[LineItem]
    total: float | None = None         # 99000.0
    currency: str | None = None        # "IDR"
    merchant: str | None = None
    date: str | None = None
```

Cuando el resto de la app (FAISS, CashbackEngine, Streamlit) recibe un `ReceiptExtraction`, ya sabe exactamente qué campos hay y de qué tipo son. No hay parsing de strings ni "espero que el campo total exista".

### Bug que encontramos y arreglamos
La primera versión del módulo usaba `prompt.format(ocr_text=...)`, lo que rompía porque el prompt tiene llaves `{}` literales en los ejemplos JSON. Cambiamos a `prompt.replace("{ocr_text}", ...)`. Está documentado en el código con un comentario corto explicando por qué — esto evita que alguien vuelva a "arreglarlo" en el futuro.

### Branch usada
`feat/llm-extractor` → merged a `main` cuando funcionó end-to-end.

---

## Día 5 — 2026-06-05 — FAISS matcher + CashbackEngine (¡SPINE COMPLETO!)

### Qué hicimos
Construimos las dos últimas piezas del pipeline antes de la interfaz: el **matcher semántico** (que mapea "Iced Tea" del recibo a "BEV003 / Iced Tea" del catálogo, aunque estén escritos distinto), y el **motor de cashback** (que calcula cuánto dinero recibe el usuario aplicando reglas de negocio). Con esto, la app **ya hace todo el trabajo de extremo a extremo**: foto → cashback. Solo falta envolverlo en una UI.

### Para qué sirve en la app
**Matcher (FAISS):** el LLM nos da items como "MilkShake 3tarwb" (con error de OCR), "Nasi Putih" (en indonesio), "Carbonara Pasta" (mezcla de idiomas). El catálogo tiene "Milkshake", "White Rice", "Carbonara". Hacer un match con `==` no funciona. Lo que hace FAISS es convertir cada nombre en un vector (384 números) que representa su significado, y luego comparar vectores en lugar de strings. Así "Nasi Putih" se acerca a "White Rice" porque significan lo mismo.

**CashbackEngine:** una vez que sabemos qué producto del catálogo es cada línea, aplicamos la tasa de cashback que ese producto tiene (3% para bebidas, 5% para comida, 0% para bolsas plásticas) y sumamos.

Analogía: el matcher es como un mesero que recibe el ticket impreso, mira el menú interno del restaurante, y dice "ah, esto que dice 'Marg.Pizza' es nuestra Margherita Pizza". El CashbackEngine es la caja registradora que aplica los descuentos correspondientes.

### De qué semana del bootcamp viene
- **Week 8 Day 2** (Vector Databases and RAG Chatbots): la idea de embeddear textos y buscar por similitud. Usamos exactamente la misma técnica que un sistema RAG usa para encontrar contexto relevante, pero aquí la usamos para matchear items.
- **Week 1-2** (Python OOP): `CashbackEngine` y `CashbackStrategy` son clases con interface clara. El patrón "Strategy" (cambiar el comportamiento de un objeto pasándole una estrategia distinta) nos prepara para el A/B testing del día 7 sin tener que tocar el motor.

### Cómo funciona el matcher por dentro
1. Al construirlo, lee `data/catalog.csv` (110 productos)
2. Embeddea el `name` de cada uno con `sentence-transformers/all-MiniLM-L6-v2` (un modelo pre-entrenado de Hugging Face, ~22 MB)
3. Guarda los embeddings en un índice FAISS
4. Cuando le preguntás `idx.match("Iced Tea")`, embeddea la query y busca el más cercano en el índice

Probamos el matcher con strings reales (incluyendo basura):
- `'ICED TEA'` → `Iced Tea` (score 0.95+)
- `'Nasi Putih'` → `White Rice` (semantic match en otro idioma)
- `'TWIST DONUT'` → `Donut`
- `'OP CODE 12345'` (basura) → score muy bajo, **rechazado por el threshold de 0.35**

El threshold de 0.35 evita que items basura (códigos de operador, números sueltos) reciban cashback fantasma.

### El strategy pattern del CashbackEngine
El brief pide A/B testing (día 7). En lugar de hardcodear las reglas y tener que reescribirlas, hicimos esto:

```python
class CashbackStrategy(Protocol):
    def rate_for(self, m: MatchedLineItem) -> float: ...

class PerSkuStrategy:
    # usa la tasa del catálogo (3% bebidas, 5% comida, etc.)
    def rate_for(self, m): return m.match.cashback_rate if m.accepted else 0.0

class FlatStrategy:
    # tasa fija para todo lo que matchea
    def __init__(self, flat_rate=0.03): self.flat_rate = flat_rate
    def rate_for(self, m): return self.flat_rate if m.accepted else 0.0

engine_A = CashbackEngine(PerSkuStrategy())
engine_B = CashbackEngine(FlatStrategy(0.04))
```

El día 7 vamos a tomar las 100 boletas del validation split, calcular el cashback con cada estrategia, y comparar los resultados con un test estadístico. **Cero cambios al motor** — solo cambiamos la estrategia que le pasamos.

### Tests
Por primera vez en el proyecto tenemos tests unitarios. `tests/test_cashback_engine.py` con **5 casos que todos pasan**:
- Cálculo correcto sumando por línea
- Líneas rechazadas (score bajo) no aportan cashback
- Líneas sin precio se tratan como 0
- FlatStrategy aplica tasa fija
- Effective rate computa bien la tasa efectiva

Esto cumple el requisito del brief de tener tests. Y más importante: si mañana alguien rompe el motor sin querer (porque está moviendo otra cosa), los tests fallan inmediatamente y se entera.

### Spine completo, end-to-end, verificado
Corrimos el pipeline COMPLETO sobre una boleta real de CORD-v2:
- **20 items extraídos**
- **Spend total: 1,280,066 IDR** (rupias indonesias del receipt)
- **Cashback total: 44,322 IDR**
- **Effective rate: 3.5%**
- **FAISS matching: <1 segundo** (rapidísimo)
- **Pipeline total: ~135s** en CPU (OCR 30s + LLM 105s + FAISS 1s)

La latencia sigue alta por OCR + LLM (no por FAISS). Para el demo se aguanta con un spinner; para producción habría que cachear/batchear.

### Trozo clave
El spine completo en 5 líneas:

```python
text       = ocr.read_text(image)              # día 3
extraction = ext.extract(text)                 # día 4
matched    = match_extraction(extraction, idx) # día 5 (FAISS)
result     = engine.compute(matched)           # día 5 (CashbackEngine)
# result.total_cashback → el número que va a la pantalla
```

Cada paso tiene un tipo bien definido (str → ReceiptExtraction → list[MatchedLineItem] → CashbackResult), así que el día 6 cuando armemos Streamlit, no vamos a estar peleando con strings.

### Branch usada
`feat/faiss-cashback` → merged a `main` cuando todo funcionó end-to-end y los tests pasaron.

---

## Día 6 — Streamlit MVP — la app que la gente ve

### Qué hicimos
Envolvimos todo el pipeline en una **interfaz web**: subís una foto, ves la lista de productos detectados, y te aparece cuánto cashback ganaste. También agregamos la opción de probar con una boleta de ejemplo del dataset, para que la demo funcione aunque no tengamos boleta a mano.

### Para qué sirve en la app
Es **la cara de todo**. Hasta ayer, el proyecto era código que funcionaba pero solo en consola. Hoy se convirtió en algo que cualquier persona puede usar abriendo un navegador.

Analogía: hasta el día 5 teníamos motor, ruedas, asientos y tablero — pero todo desarmado en el suelo. El día 6 los atornillamos al chasis y le pusimos las puertas. Ahora es un auto.

### De qué semana del bootcamp viene
**No vino del bootcamp** — Streamlit es la tecnología que el brief pide pero el curso no enseñó. La aprendimos en el camino. Es un framework de Python donde escribís código secuencial normal y él lo convierte en página web (botones, sliders, gráficos, tablas) automáticamente.

### Decisiones de diseño que importan
1. **Caching de recursos pesados.** El modelo de OCR (~200 MB), el cliente de Gemini, y el índice FAISS se cargan **una sola vez por sesión** usando `@st.cache_resource`. Sin esto, cada vez que el usuario sube una foto se reinstalaría todo desde cero (10+ segundos extra cada vez).
2. **Progress bar en tiempo real.** El pipeline tarda ~40 segundos. Sin feedback visual el usuario piensa que la app se colgó. Mostramos % de progreso con texto: "Running OCR... Asking Gemini... Matching items... Done".
3. **Manejo de errores tipado.** Si Gemini falla persistentemente y se levanta `LLMExtractionError`, mostramos un mensaje amigable ("could not structure this receipt") en lugar de stack trace. Esto es lo que Yossi nos dijo: *"handle that path or the demo breaks live"*.
4. **Sample receipts incluidas.** En la sidebar hay un selector de "Sample receipt" que carga una boleta de CORD-v2 sin que el usuario tenga que subir nada. Critico para la demo del día 11 — si la wifi falla, igual podemos demostrar.
5. **Selector de estrategia de cashback en sidebar.** Per-SKU vs Flat 4%. Esto pre-arma el A/B test del día 7 visualmente.
6. **Dos páginas:** "Upload Receipt" (el producto) y "About this project" (descripción no técnica para la audiencia del demo).

### Cómo se ve la pantalla principal
Una vez que subís foto (o eliges sample):
- **Columna izquierda:** la foto de la boleta
- **Columna derecha:**
  - Número grande en verde: el cashback total (con la moneda inferida)
  - Tabla con cada línea: item del recibo, SKU matcheado, gasto, tasa aplicada, cashback, accepted yes/no
  - Dos expanders: "Show raw OCR text" y "Show Gemini extraction JSON" — útiles para el demo cuando alguien pregunta "¿pero qué hace por dentro?"

### Cómo correrla
Desde la carpeta del proyecto:
```bash
./.venv/Scripts/streamlit run app/streamlit_app.py
```
Esto abre el navegador en http://localhost:8501.

### Trozo clave
Toda la magia está en una función de 4 líneas que orquesta el spine:

```python
def run_spine(image, strategy_name):
    ocr_text   = get_ocr().read_text(image)
    extraction = get_llm().extract(ocr_text)
    matched    = match_extraction(extraction, get_index())
    return get_cashback_engine(strategy_name).compute(matched)
```

Esto es **toda** la lógica de negocio de la app. El resto es Streamlit pidiéndole inputs al usuario y mostrando los outputs. La separación entre "cerebro" (módulos `src/`) y "cara" (app) es lo que va a permitir, en el futuro, reemplazar Streamlit por una app de iPhone sin reescribir nada del cerebro.

### Branch usada
`feat/streamlit-app` → merged a `main` cuando se verificó que arranca limpio.

---

## Día 7 — _(pendiente)_

_Por escribirse después del clustering, A/B test y B2B view._

---

## Cómo usar este doc para la presentación

Al final del proyecto (día 9), este archivo va a tener ~10 entradas. Para el PPT:
- Los puntos 1 y 2 ("qué hicimos" + "para qué sirve") van en los slides.
- Los puntos 3 y 4 ("semana" + "código") van en el speech: te permiten responder "¿de dónde sacaste eso?" sin dudar.

Para el video Loom de 3 minutos:
- Slide 1: el problema (no necesita explicación técnica).
- Slide 2-4: las 3 etapas clave del pipeline (CNN → OCR + LLM → FAISS), una por slide, usando las analogías del punto 2 de cada entrada.
- Slide 5: la demo en vivo (subir una foto, mostrar el cashback).
- Slide 6: ética y siguientes pasos.
