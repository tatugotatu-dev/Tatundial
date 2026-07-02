// =====================================================================
// EJERCICIO 4 — "PRESION ALTA" (version 1)
// Real C++ FC - Sistema de tracking GPS en tiempo real
// =====================================================================
//
// El sistema detecta cuantos rivales "presionan" al jugador con la
// pelota. El resultado varia entre corridas: a veces da 11, a veces 8.
//
// Analizalo junto con tracker_v2_slow.cpp y benchmark_results.txt,
// y responde en ANSWER.md.
//
// =====================================================================

#include <vector>
#include <thread>
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

struct PlayerTracker {
    int pressureCount = 0;
    std::vector<std::thread> workers;

    void trackOpponent(int opponentId) {
        if (isNearby(opponentId)) {
            pressureCount++;
        }
    }

    void runDetection(const std::vector<int>& opponents) {
        for (int id : opponents) {
            workers.emplace_back([this, id] { trackOpponent(id); });
        }
        for (auto& w : workers) w.join();
    }
};

int main() {
    std::vector<int> opponents;
    for (int i = 0; i < 22; ++i) opponents.push_back(i);

    PlayerTracker tracker;
    tracker.runDetection(opponents);

    std::cout << "Presion detectada: " << tracker.pressureCount << "\n";
    return 0;
}
