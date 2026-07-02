// =====================================================================
// EJERCICIO 1 — "LA TRAMPA DEL OFFSIDE"
// RiBer C++ FC - Auditoria del sistema VAR
// =====================================================================
//
// Audita 3 fragmentos de codigo independientes y diagnosticá
// si contienen Undefined Behavior (UB).
//
// IMPORTANTE:
// - No se pide arreglar el codigo, solo diagnosticarlo.
// - Responde en ANSWER.md.
//
// =====================================================================

#include <iostream>
#include <vector>
#include <string>
#include <thread>

// ---------------------------------------------------------------------
// S1
// ---------------------------------------------------------------------
const std::string& getCaptain() {
    std::string captain = "Messi";
    return captain;
}

// ---------------------------------------------------------------------
// S2
// ---------------------------------------------------------------------
std::vector<std::string> getStartingXI() {
    std::vector<std::string> players = {"Messi", "Di Maria", "Alvarez"};
    for (auto it = players.begin(); it != players.end(); ++it) {
        if (*it == "Di Maria") {
            players.push_back("Lautaro");
        }
    }
    return players;
}

// ---------------------------------------------------------------------
// S3
// ---------------------------------------------------------------------
struct Marcador {
    int golesEquipoLocal = 0;

    void registrarGol() {
        golesEquipoLocal++;
    }
};

void simularPartido() {
    Marcador marcador;
    std::vector<std::thread> sensores;
    for (int i = 0; i < 4; ++i) {
        sensores.emplace_back([&marcador]() {
            for (int j = 0; j < 1000; ++j) {
                marcador.registrarGol();
            }
        });
    }
    for (auto& t : sensores) t.join();
    std::cout << "Goles totales: " << marcador.golesEquipoLocal << "\n";
}
