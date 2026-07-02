// =====================================================================
// EJERCICIO 3 — "TIKI-TAKA API"
// RiBer C++ FC - Sistema generico de encadenamiento de pases
// =====================================================================
//
// Pipeline al estilo std::ranges: PassChain(valor).then(f1).then(f2)...get()
//
// El diseño actual tiene problemas: copias innecesarias, falta de concepts,
// errores de compilacion ilegibles.
//
// Analiza el diseño y responde en ANSWER.md.
//
// =====================================================================

#include <utility>
#include <type_traits>
#include <concepts>

template <typename T>
class PassChain {
public:
    template <typename F>
    auto then(F f) {
        return PassChain<decltype(f(std::declval<T>()))>(f(value_));
    }

    PassChain(T v) : value_(v) {}

    T get() const { return value_; }

private:
    T value_;
};

template <typename T>
PassChain(T) -> PassChain<T>;
