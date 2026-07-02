// =====================================================================
// EJERCICIO 2 — "REVISION DEL VAR"
// RiBer C++ FC - Sala VAR / Estadisticas en vivo
// =====================================================================
//
// El programa de abajo compila y corre, pero el marcador en pantalla
// no coincide con lo esperado.
//
// Tu mision:
//  1) Predecir la salida EXACTA por consola, linea por linea.
//  2) Encontrar los bugs y proponer un fix para cada uno.
//
// No modifiques este archivo: responde todo en ANSWER.md
//
// =====================================================================

#include <iostream>
#include <vector>
#include <string>

struct Player {
    std::string name;
    int rating;
    virtual void print() const { std::cout << name << " (" << rating << ")"; }
    virtual ~Player() = default;
};

struct Striker : Player {
    int goals = 0;
    void print() const override {
        std::cout << name << " [DELANTERO] goles=" << goals;
    }
};

class MatchStats {
    int possession;
    int totalShots;
public:
    MatchStats(int shots) : totalShots(shots), possession(shots * 2) {}

    void report() const {
        std::cout << "Posesion: " << possession << " Tiros: " << totalShots << "\n";
    }
};

void showPlayer(Player p) {
    p.print();
    std::cout << "\n";
}

class GoalCounter {
    int goals;
public:
    GoalCounter() { goals = 0; }

    GoalCounter operator+=(int n) {
        goals += n;
        return *this;
    }

    int total() const { return goals; }
};

double averageRating(const std::vector<int>& ratings) {
    int sum = 0;
    for (int r : ratings) sum += r;
    return sum / ratings.size();
}

int main() {
    MatchStats stats(10);
    stats.report();

    Striker messi;
    messi.name = "Messi";
    messi.rating = 95;
    messi.goals = 2;

    showPlayer(messi);

    std::vector<int> ratings = {90, 91, 92};
    std::cout << "Promedio: " << averageRating(ratings) << "\n";

    GoalCounter gc;
    gc += 1;
    gc += 1;
    std::cout << "Goles contador: " << gc.total() << "\n";

    std::vector<int> scores = {1, 2, 3};
    std::cout << scores[5] << "\n";

    return 0;
}
