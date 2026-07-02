# Ejercicio 4 — Presión Alta (15 min)

Participante: __________________________

---

## Q1 - Data race en v1
- Variable(s) involucrada(s):
- Por que es UB (no solo "impreciso"):

## Q2 - Por qué v2 es correcto pero mucho más lento

Respuesta:

## Q3 - Fix propuesto (marca uno con [x])

- [ ] std::atomic<int> para pressureCount
- [ ] mutex solo alrededor del incremento
- [ ] ambos combinados

Justificación (1 linea):

## Q4 - Completá el fix
```cpp
___________________ pressureCount{0};

if (isNearby(opponentId)) {
    pressureCount.___________(1, std::memory_order_relaxed);
}
```
