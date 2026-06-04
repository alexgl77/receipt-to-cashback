# Cheat sheet — frases que tenés que poder decir sin pensar

Memorizá estas 8 frases. Te dan el 80% del demo y de las preguntas
del jurado, sin jerga.

---

## 1. ¿Qué es Receipt-to-Cashback en una frase?

> "Es una app de **investigación de mercado**: el usuario escanea
> una boleta, le pagamos un cashback chiquito, y nosotros vendemos
> los datos de consumo agregados a marcas y consultoras."

---

## 2. ¿Cómo funciona el pipeline en 4 pasos?

> "Foto → **OCR** (lee el texto) → **Gemini** (estructura los items) →
> **FAISS** (matchea cada item contra nuestro catálogo) → cashback."

---

## 3. ¿Qué es el "drift guard" / chequeo de cuadre?

> "En cualquier boleta, **la suma de los items debería dar igual al
> total impreso al final**. Como el OCR y el LLM no son perfectos,
> a veces no coinciden. Comparamos los dos números: si difieren
> hasta 10% pagamos normal, entre 10% y 50% confiamos en el total
> impreso, y arriba de 50% rechazamos el pago."

---

## 4. ¿Por qué no entrenan un OCR perfecto?

> "Ni Google ni Amazon lo logran sobre papel térmico arrugado.
> La práctica estándar de la industria es asumir que el OCR falla
> y agregar chequeos posteriores. Eso es lo que hicimos."

---

## 5. ¿Por qué cambiaron el modelo de negocio?

> "El modelo original era partner-rebate — solo pagábamos cashback
> sobre productos con acuerdo. Al probar con receipts reales, la
> mayoría caía afuera del catálogo y el usuario recibía cero. Lo
> pivoteamos: ahora pagamos un cashback flat por cualquier compra
> a cambio del dato, y monetizamos vendiendo los datos agregados."

---

## 6. ¿Por qué no usaron CNN si el brief lo pide?

> "Lo evalué. El instructor dio el feedback de **'spine first,
> garnish after'** — priorizar el flujo principal sobre los nice
> to have. La CNN como filtro de calidad agregaba complejidad sin
> aportar al producto, así que la dejé como future step en el
> README."

---

## 7. ¿Cómo escalarían a miles de boletas por minuto?

> "El cuello de botella es Gemini, no FAISS. Tres palancas: 1)
> batch de varios OCR text en una sola llamada, 2) cache por hash
> de imagen (ya implementado para repetidas), 3) fine-tuning de un
> modelo open-source sobre nuestro dataset propio para sacar Gemini
> del path crítico cuando el volumen lo justifique."

---

## 8. ¿Qué es k-anonimato y por qué importa acá?

> "Antes de vender datos agregados, no podés vender slices de menos
> de K usuarios (típico K=50). Esto evita que un comprador
> re-identifique usuarios cruzando lo que nos compra con datos
> externos. Es el piso ético del modelo: sin K-anonimato no se
> debería vender nada."

---

## Glosario express (por si te traban en vivo)

| Término | Decilo así |
|---|---|
| OCR | "el modelo que lee el texto de la foto" |
| LLM | "el modelo de lenguaje, en nuestro caso Gemini" |
| FAISS | "una base de datos que busca por significado, no por palabras exactas" |
| Embedding | "convertir palabras en números que capturan su significado" |
| Multilingual | "soporta varios idiomas, no solo inglés" |
| Pydantic schema | "un molde estricto al que la respuesta del LLM tiene que ajustarse" |
| Few-shot prompt | "le damos al LLM 2 ejemplos para que entienda qué queremos" |
| K-Means | "agrupar usuarios por patrones similares de gasto" |
| Welch's t-test | "prueba estadística para ver si la diferencia entre dos grupos es real o casualidad" |
| Strategy pattern | "una manera de cambiar las reglas del cashback sin tocar el resto del código" |
| Drift guard | "chequeo de cuadre: comparamos suma de items vs total impreso" |
| Cashback effective rate | "el porcentaje real que terminás pagando, después de los descuentos" |

---

## Lo que NO tenés que decir nunca

- "Drift guard" sin explicarlo → decí "chequeo de cuadre" o "sanity check"
- "Two-tier" → decí "dos niveles" o "dos zonas"
- "Hallucinate" → decí "se equivoca" o "inventa"
- "Schema validation" → decí "validamos la respuesta"
- "Vector embedding" → decí "convertir palabras en números"
- Nombres de modelos largos ("paraphrase-multilingual-MiniLM-L12-v2") → decí "un modelo multilingüe de Hugging Face"
