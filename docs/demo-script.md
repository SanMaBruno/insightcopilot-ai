# Demo Script — InsightCopilot AI

Guión para una demo de **1 a 3 minutos** del producto.

> **Prerequisito:** backend y frontend corriendo, dataset aún no subido.

---

## Apertura (15 seg)

> "InsightCopilot AI es una plataforma que convierte datos crudos en conocimiento accionable. Subes un CSV y obtienes perfilado estadístico, insights inteligentes, visualizaciones, consultas en lenguaje natural y resúmenes ejecutivos — todo desde una sola interfaz."

**Acción:** Mostrar la Home brevemente.

---

## Upload (15 seg)

> "El flujo empieza subiendo un dataset. Voy a cargar un CSV de 30 productos e-commerce."

**Acción:** Ir a Datasets → Subir CSV → seleccionar `ecommerce_products.csv` → mostrar confirmación.

---

## Profile (20 seg)

> "Automáticamente se genera un perfil estadístico completo: 30 filas, 10 columnas, tipo de dato de cada columna, valores nulos y valores únicos."

**Acción:** Hacer clic en el dataset → mostrar tabla de Profile.

---

## Insights (20 seg)

> "El sistema detecta patrones e issues automáticamente. Cada insight está clasificado por severidad — desde información general hasta alertas críticas. Aquí vemos advertencias sobre valores nulos en dos columnas."

**Acción:** Cambiar a pestaña Insights → señalar categorías y colores.

---

## Charts (15 seg)

> "Las visualizaciones se generan automáticamente: histogramas, barras por categoría y matriz de correlación."

**Acción:** Cambiar a pestaña Charts → scroll rápido por los gráficos.

---

## Query (30 seg)

> "Puedo hacer preguntas en lenguaje natural sobre los datos, sin necesidad de API key. Por ejemplo: '¿Cuántas filas tiene el dataset?' — y me responde con el resultado y los datos de soporte."

**Acción:** Cambiar a pestaña Query → escribir la pregunta → mostrar resultado con intent y datos.

---

## Cierre técnico (20 seg)

> "El proyecto usa Clean Architecture con 5 capas, SOLID en cada decisión de diseño, 172 tests unitarios, CI/CD con GitHub Actions y está dockerizado. El código está abierto en GitHub."

**Acción:** (Opcional) mostrar terminal con `pytest` corriendo o la documentación Swagger en `/docs`.

---

## Tiempo total: ~2 minutos 15 segundos

### Si hay más tiempo (extensión a 3 min)

- Mostrar **Summary (LLM)**: generar resumen ejecutivo configurando audiencia y tono.
- Mostrar **API Docs**: abrir Swagger en `/docs` y señalar los 14 endpoints.
- Mencionar que el RAG permite cruzar datos del dataset con documentos indexados.

---

## Tips para la presentación

- No explicar código — mostrar producto funcionando.
- Velocidad natural, no correr. La UI habla por sí sola.
- Si algo falla (ej: LLM sin API key), decir "esta feature requiere configuración de OpenAI, está implementada y testeada".
- Cerrar con: "código abierto, Clean Architecture, 172 tests, CI/CD, Docker ready".
