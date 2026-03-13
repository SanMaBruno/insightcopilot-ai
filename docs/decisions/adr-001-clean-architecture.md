# ADR-001: Clean Architecture como patrón base

## Estado

Aceptado

## Contexto

El proyecto necesita una estructura que permita escalar desde un MVP simple hacia un sistema con API, LLMs, RAG, base de datos y visualizaciones, sin reescribir la base.

## Decisión

Adoptamos Clean Architecture con 5 capas: `domain`, `application`, `infrastructure`, `presentation` y `shared`.

## Consecuencias

**Positivas:**
- El núcleo de negocio (`domain`) no depende de frameworks ni librerías externas
- Podemos cambiar la base de datos, el LLM o el framework web sin tocar la lógica de negocio
- Facilita testing unitario al poder mockear infraestructura
- Estructura predecible para cualquier desarrollador que se incorpore

**Negativas:**
- Mayor cantidad de archivos y carpetas que una estructura plana
- Requiere disciplina para respetar la regla de dependencia

## Notas

La regla de dependencia dicta que las capas internas nunca importan de las externas. La dirección es siempre: `presentation → application → domain ← infrastructure`.
