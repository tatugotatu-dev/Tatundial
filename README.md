# SEAN BIENVENIDOS AL PRIMER TATUNDIAL

## Reglas generales

- 4 ejercicios, **25 puntos cada uno**, 100 puntos totales.
- Tiempo TOTAL: **60 minutos** (15 minutos por ejercicio).
- Todas las respuestas se escriben en el archivo `ANSWER.md` de cada
  carpeta de ejercicio. **No modifiques los archivos `.cpp` / `.hpp`**
  salvo que la consigna lo pida explícitamente.
- Podés compilar y correr el código para verificar tus hipótesis
- Al terminar, envía la carpeta completa (o los 4 `ANSWER.md`) tal
  como se te indique.

## Estructura del repositorio

```
exercise1_offside_trap/     -> Undefined Behavior & Memoria       (25 pts)
  snippets.hpp
  ANSWER.md

exercise2_var_review/       -> Debugging & Predicción de salida   (25 pts)
  match_stats.cpp
  ANSWER.md

exercise3_tiki_taka_api/    -> Diseño de API + Templates/Concepts (25 pts)
  pass_pipeline.hpp
  usage_examples.cpp
  ANSWER.md

exercise4_press_high/       -> Concurrencia & Performance         (25 pts)
  tracker_v1_buggy.cpp
  tracker_v2_slow.cpp
  benchmark_results.txt
  ANSWER.md
```

## Compilador recomendado

```
g++ -std=c++20 -Wall -Wextra -pthread
```
(o `clang++` equivalente). Ejercicio 3 requiere C++20 (concepts).

## Entrega

Enviá la carpeta completa del repo (con tus 4 `ANSWER.md` completados)
al capo de Tatu. El evaluador automático leerá esos archivos y generará
un JSON con tu puntaje por ejercicio.

¡Suerte!
