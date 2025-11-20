#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <algorithm>
#include <stdexcept>
#include <fstream>
using namespace std;

// === Імпорт математичних функцій з afincypher.cpp ===
long long gcd_ext(long long a, long long b, long long& x, long long& y) {
    if (b == 0) { x = 1; y = 0; return a; }
    long long x1, y1;
    long long g = gcd_ext(b, a % b, x1, y1);
    x = y1;
    y = x1 - (a / b) * y1;
    return g;
}

long long mod_inv(long long a, long long n) {
    long long x, y;
    long long g = gcd_ext(a, n, x, y);
    if (g != 1) throw runtime_error("Обернений елемент не існує");
    return (x % n + n) % n;
}

vector<long long> solve_cong(long long a, long long b, long long n) {
    long long x, y;
    long long g = gcd_ext(a, n, x, y);
    vector<long long> sol;
    if (b % g != 0) return sol;
    a /= g; b /= g; n /= g;
    long long x0 = (mod_inv(a, n) * b) % n;
    for (int i = 0; i < g; ++i)
        sol.push_back((x0 + i * n) % (n * g));
    return sol;
}

// === Основна частина ===
const int M = 31; // розмір алфавіту (російський, без 'ё')
const long long N = 31LL * 31LL;

long long bigramToNum(const string& bg, const string& alphabet) {
    int i1 = alphabet.find(bg[0]);
    int i2 = alphabet.find(bg[1]);
    if (i1 == string::npos || i2 == string::npos)
        throw runtime_error("Невідомий символ у біграмі");
    return i1 * M + i2;
}

int main() {
    // === Часті біграми мови та шифру ===
    vector<string> topLang = { "ст", "но", "то", "на", "ен" };
    vector<string> topCipher = { "дэ", "цє", "жц", "нц", "оц" };

    string alphabet = "абвгдежзийклмнопрстуфхцчшщьыэюя";

    ofstream fout("keys.txt");
    if (!fout.is_open()) {
        cout << "Помилка: не вдалося створити keys.txt\n";
        return 1;
    }

    cout << "Перебір пар частих біграм і запис ключів у keys.txt...\n";

    int count = 0;
    // Перебір усіх пар (біграма_мова1, біграма_мова2) × (біграма_шифр1, біграма_шифр2)
    for (int i = 0; i < 5; ++i) {
        for (int j = 0; j < 5; ++j) {
            if (i == j) continue;
            for (int p = 0; p < 5; ++p) {
                for (int q = 0; q < 5; ++q) {
                    if (p == q) continue;

                    long long x1 = bigramToNum(topLang[i], alphabet);
                    long long x2 = bigramToNum(topLang[j], alphabet);
                    long long y1 = bigramToNum(topCipher[p], alphabet);
                    long long y2 = bigramToNum(topCipher[q], alphabet);

                    long long dx = (x1 - x2 + N) % N;
                    long long dy = (y1 - y2 + N) % N;

                    auto a_vals = solve_cong(dx, dy, N);
                    for (auto a : a_vals) {
                        try {
                            long long b = (y1 - a * x1) % N;
                            if (b < 0) b += N;

                            // Запис у файл
                            fout << a << " " << b << "\n";
                            count++;
                        }
                        catch (...) {
                            continue;
                        }
                    }
                }
            }
        }
    }

    fout.close();
    cout << "Готово! Знайдено та збережено " << count << " кандидатів у keys.txt\n";
    return 0;
}
