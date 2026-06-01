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

## Día 2 — _(pendiente)_

_Por escribirse después de hacer el EDA del dataset SROIE._

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
