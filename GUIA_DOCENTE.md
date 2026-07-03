# Guía Docente — Tatundial C++

## Ejercicio 1 — Offside Trap (UB)

### S1: Dangling Reference
```cpp
const std::string& getCaptain() {
    std::string captain = "Messi";
    return captain;
}
```
- **UB:** SI
- **Tipo:** `dangling-reference`
- **Línea:** 25 (el `return captain;`)
- **Por qué:** `captain` es una variable LOCAL (vive en el stack de la función). Al salir de `getCaptain()`, se destruye automáticamente. La función devuelve una referencia (`const std::string&`) a algo que ya no existe. Usar esa referencia es UB.
- **Cómo explicarlo:** Es como darle a alguien la dirección de tu casa... después de mudarte. La dirección existe, pero la casa ya no está.
- **Fix:** Devolver por valor (`std::string`).

### S2: Iterator Invalidation
```cpp
for (auto it = players.begin(); it != players.end(); ++it) {
    if (*it == "Di Maria") {
        players.push_back("Lautaro");
    }
}
```
- **UB:** SI
- **Tipo:** `iterator-invalidation`
- **Línea:** 35 (el `players.push_back(...)`)
- **Por qué:** `push_back()` puede realocar el vector si no hay `capacity` suficiente. Cuando el vector se realoca, **todos los iteradores** existentes (incluyendo `it` y `players.end()`) se invalidan. El `++it` después del `push_back` opera sobre un iterador inválido → UB.
- **Dato clave:** Incluso si el `capacity` alcanza (y no hay realocación), el estándar dice que `push_back` invalida `end()`. O sea, aunque no crashee, igual es UB.
- **Fix:** Usar índices (`for int i = 0; i < players.size();`) o hacer `reserve()` antes.

### S3: Data Race
```cpp
struct Marcador {
    int golesEquipoLocal = 0;
    void registrarGol() { golesEquipoLocal++; }
};
// 4 hilos llaman a registrarGol() en paralelo
```
- **UB:** SI
- **Tipo:** `data-race`
- **Línea:** 48 (el `golesEquipoLocal++`)
- **Por qué:** `golesEquipoLocal++` es una operación **read-modify-write**: el CPU lee, suma 1, escribe. Cuando 4 hilos lo hacen sin protección, pueden pisarse entre sí. No es solo "impreciso" — el estándar de C++ dice que cualquier data race es **UB**, el programa puede hacer cualquier cosa.
- **Posibles fixes:** `std::atomic<int>` o `std::mutex`.

---

## Ejercicio 2 — VAR Review (Debugging)

### Q1: Salida exacta (5 líneas)

```
Posesion: 20 Tiros: 10
Messi (95)
Promedio: 91
Goles contador: 2
UB
```

#### L1 — Init order trick
```cpp
class MatchStats {
    int possession;     // declarado PRIMERO
    int totalShots;     // declarado SEGUNDO
public:
    MatchStats(int shots) : totalShots(shots), possession(shots * 2) {}
};
```
El compilador inicializa en orden de **declaración**, no de la lista de inicialización.
1. `possession = 10 * 2 = 20`
2. `totalShots = 10`
Resultado: `Posesion: 20 Tiros: 10`

#### L2 — Object slicing
```cpp
void showPlayer(Player p) {  // p es Player, recibe por VALOR
    p.print();
}
Striker messi;
showPlayer(messi);
```
Al pasar `Striker` donde se espera `Player` por valor, se copia solo la parte `Player`. La parte `Striker` (goals) se pierde. Se llama a `Player::print()`, no a `Striker::print()`.

#### L3 — Integer division
```cpp
double averageRating(...) {
    int sum = 273;
    return sum / ratings.size();  // 273 / 3 = 91 (entero), después 91.0
}
```
`sum / ratings.size()` es división entre enteros. El resultado se trunca a entero **antes** de convertirse a double.

#### L4 — operator+= por valor
```cpp
GoalCounter operator+=(int n) {  // devuelve COPIA
    goals += n;
    return *this;
}
```
Como las llamadas son separadas (`gc += 1; gc += 1;`), el bug no se manifiesta (da 2). El problema está en el **encadenamiento**: `(gc += 1) += 1` modificaría una copia, no a `gc`.

#### L5 — Out of bounds
```cpp
std::vector<int> scores = {1, 2, 3};
std::cout << scores[5];  // UB
```
`operator[]` no chequea límites. Accede a memoria fuera del vector.

### Q2-Q4: Los 3 bugs (fixes)

**Q2 — GoalCounter (línea 56):**
```cpp
// MAL:
GoalCounter operator+=(int n) { ... return *this; }
// BIEN:
GoalCounter& operator+=(int n) { ... return *this; }
```

**Q3 — averageRating (línea 67):**
```cpp
// MAL:
return sum / ratings.size();
// BIEN:
return static_cast<double>(sum) / ratings.size();
```

**Q4 — scores[5] (línea 90):**
```cpp
// MAL:
std::cout << scores[5];
// BIEN (opciones):
if (scores.size() > 5) std::cout << scores[5];
std::cout << scores.at(5);  // lanza out_of_range si no existe
```

---

## Ejercicio 3 — Tiki-Taka API (Concepts)

### Q1: Problema de diseño principal
**Respuesta correcta:** `perfect-forwarding`

**Por qué:** La API actual hace **copias innecesarias**:
1. Constructor: `PassChain(T v) : value_(v) {}` — copia al recibir `v` Y copia otra vez a `value_`
2. `then(F f)` — recibe `f` por valor, y `f(value_)` copia el resultado

Con tipos como `std::vector<Stat>`, cada `.then()` duplica todo el vector. La solución es usar `T&&`, `F&&` y `std::forward<>` (perfect forwarding).

### Q2: Concept PassCallable
```cpp
template <typename F, typename T>
concept PassCallable = std::invocable<F, T>
    && !std::same_as<std::invoke_result_t<F, T>, void>;
```

- `std::invocable<F, T>` → F se puede llamar con un T
- `!std::same_as<..., void>` → el resultado NO es void (porque hay que pasarlo al siguiente `.then()`)

**Sin este concept:** si alguien hace `PassChain("Messi").then([](int x){ return x+1; })`, el compilador genera páginas de errores template.
**Con el concept:** error claro → "constraint not satisfied: PassCallable<F, T>"

---

## Ejercicio 4 — Press High (Concurrencia)

### V1: Buggy — Data Race
```cpp
struct PlayerTracker {
    int pressureCount = 0;  // NO atómico
    void trackOpponent(int id) {
        if (isNearby(id)) pressureCount++;  // data race
    }
};
```
22 hilos ejecutan `pressureCount++` (read-modify-write) en paralelo sin sincronización. Resultado: varía entre 8 y 11 (debería ser 11 siempre).

### V2: Correcta pero 28x más lenta
```cpp
void trackOpponent(int opponentId) {
    std::lock_guard<std::mutex> lock(bigLock);
    if (isNearby(opponentId)) {  // isNearby es carísima
        pressureCount++;
    }
}
```
El mutex protege TODO, incluyendo `isNearby()` (200 mil iteraciones de `sin()`). Los 22 hilos se ejecutan **en serie** en vez de en paralelo.

### Fix: std::atomic<int>
```cpp
std::atomic<int> pressureCount{0};

void trackOpponent(int opponentId) {
    if (isNearby(opponentId)) {            // isNearby no necesita lock
        pressureCount.fetch_add(1, std::memory_order_relaxed);
    }
}
```
- `isNearby()` solo usa `opponentId` (parámetro local por copia) → **no toca memoria compartida** → no necesita sincronización
- Solo `pressureCount++` necesita protección → `std::atomic` alcanza
- `memory_order_relaxed` es suficiente porque solo necesitamos el conteo final, no una relación de orden entre hilos
- **Resultado:** Correcto Y rápido (isNearby corre en paralelo en todos los hilos)

---

## Posibles preguntas que te pueden hacer

**¿Por qué `iterator-invalidation` es UB aunque el vector no se realoque?**
Porque el estándar dice que `push_back` invalida `end()`, independientemente de si hay realocación o no.

**¿Por qué no es suficiente decir que `data-race` da "resultado incorrecto"?**
Porque el estándar de C++ dice que data race es UB, no solo "impreciso". El compilador puede generar código que haga cualquier cosa (crash, valores absurdos, etc.).

**¿El init order del MatchStats es un bug?**
No. Es comportamiento definido. El estándar dice claramente que los miembros se inicializan en orden de declaración. Es contra-intuitivo, pero no es UB.

**¿Por qué no usar `std::mutex` en vez de `std::atomic` para el fix del ej4?**
Se puede, pero es peor. Con mutex tendrías que elegir: ponerlo fuera de `isNearby()` (data race) o ponerlo adentro (serializa todo y es 28x más lento). `std::atomic` es la solución correcta: protege `pressureCount` sin afectar el paralelismo.

**¿Por qué en el ej2 la línea 4 da 2 si el operator+= está mal?**
Porque las llamadas son independientes (`gc += 1; gc += 1;`). Cada una modifica a `gc` y devuelve una copia que se descarta. El bug solo afecta si encadenás: `(gc += 1) += 1`.

**¿Qué es `memory_order_relaxed`?**
Es el orden de memoria más débil para `std::atomic`. Garantiza atomicidad pero no impone barreras de memoria. Es suficiente cuando solo necesitas que la operación sea atómica, sin sincronizar otros accesos.
