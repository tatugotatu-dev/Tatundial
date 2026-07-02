// =====================================================================
// usage_examples.cpp — como se QUIERE usar la API
// =====================================================================
//
// Archivo de referencia. Lee como se usa la API antes de responder.
//
// =====================================================================

#include "pass_pipeline.hpp"
#include <string>
#include <iostream>
#include <vector>

void caso1() {
    auto result = PassChain(10)
        .then([](int x) { return x * 2; })
        .then([](int x) { return std::to_string(x) + " metros"; })
        .get();

    std::cout << result << "\n";
}

struct Stat { double value; std::string label; };

void caso2() {
    std::vector<Stat> stats = { {7.5, "pases completados"}, {3.2, "km recorridos"} };

    auto result = PassChain(stats)
        .then([](std::vector<Stat> v) {
            for (auto& s : v) s.value *= 2;
            return v;
        })
        .get();

    std::cout << "Stats procesadas: " << result.size() << "\n";
}

int main() {
    caso1();
    caso2();
    return 0;
}
