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

## Día 3 — _(pendiente)_

_Por escribirse después del OCR pipeline (TrOCR / Donut)._

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
