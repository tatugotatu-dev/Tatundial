// =====================================================================
// EJERCICIO 4 — "PRESION ALTA" (version 2: CORRECTA PERO LENTA)
// Real C++ FC - Sistema de tracking GPS en tiempo real
// =====================================================================
//
// CONTEXTO:
// Despues de reportar el bug de la v1, el tecnico del club "arreglo"
// el problema agregando un mutex. El resultado ahora es SIEMPRE
// correcto (11 de 22 rivales detectados), pero el tiempo de ejecucion
// se disparo un 28x respecto a la v1 (ver benchmark_results.txt).
//
// Este archivo compila y corre. Analizalo junto con tracker_v1_buggy.cpp
// y responde en ANSWER.md.
//
// =====================================================================

#include <vector>
#include <thread>
#include <mutex>
#include <iostream>
#include <cmath>

bool isNearby(int opponentId) {
    double acc = 0.0;
    for (int i = 0; i < 200000; ++i) {
        acc += std::sin(opponentId * 0.0001 + i);
    }
    (void)acc;
    return opponentId % 2 == 0;
}

struct PlayerTrackerV2 {
    int pressureCount = 0;
    std::mutex bigLock;

    void trackOpponent(int opponentId) {
        std::lock_guard<std::mutex> lock(bigLock);
        if (isNearby(opponentId)) {
            pressureCount++;
        }
    }

    void runDetection(const std::vector<int>& opponents) {
        std::vector<std::thread> workers;
        for (int id : opponents) {
            workers.emplace_back([this, id] { trackOpponent(id); });
        }
        for (auto& w : workers) w.join();
    }
};

int main() {
    std::vector<int> opponents;
    for (int i = 0; i < 22; ++i) opponents.push_back(i);

    PlayerTrackerV2 tracker;
    tracker.runDetection(opponents);

    std::cout << "Presion detectada: " << tracker.pressureCount << "\n";
    return 0;
}
