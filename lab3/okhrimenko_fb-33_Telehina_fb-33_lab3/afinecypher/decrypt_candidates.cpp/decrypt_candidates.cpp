#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <stdexcept>
#include <algorithm>
using namespace std;

// === Математичні функції ===
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

// === Параметри шифру ===
const int M = 31;
const long long N = 31LL * 31LL;
const string alphabet = "абвгдежзийклмнопрстуфхцчшщьыэюя";

// === Перетворення біграм ===
long long bigramToNum(const string& bg) {
    int i1 = alphabet.find(bg[0]);
    int i2 = alphabet.find(bg[1]);
    if (i1 == string::npos || i2 == string::npos)
        throw runtime_error("Невідомий символ у біграмі");
    return i1 * M + i2;
}

string numToBigram(long long num) {
    int x1 = num / M;
    int x2 = num % M;
    string s;
    s += alphabet[x1];
    s += alphabet[x2];
    return s;
}

// === Дешифрування афінного шифру ===
string decryptText(const string& cipher, long long a, long long b) {
    long long a_inv = mod_inv(a, N);
    string plain;
    for (size_t i = 0; i + 1 < cipher.size(); i += 2) {
        string bg = cipher.substr(i, 2);
        long long y = bigramToNum(bg);
        long long x = (a_inv * (y - b + N)) % N;
        plain += numToBigram(x);
    }
    return plain;
}

// === Простий "розпізнавач російської мови" ===
bool looksLikeRussian(const string& text) {
    if (text.size() < 50) return false;

    string common = "оеаинтсрвл";
    string rare = "фщьыъэю";

    int commonCount = 0, rareCount = 0;
    for (char c : text) {
        if (common.find(c) != string::npos) commonCount++;
        else if (rare.find(c) != string::npos) rareCount++;
    }

    double total = max((int)text.size(), 1);
    double commonRatio = (double)commonCount / total;
    double rareRatio = (double)rareCount / total;

    // У російській мові багато "о", "е", "а" і мало "ф", "щ"
    return (commonRatio > 0.25 && rareRatio < 0.05);
}

// === Зчитування ключів ===
vector<pair<long long, long long>> loadKeys(const string& filename) {
    vector<pair<long long, long long>> keys;
    ifstream fin(filename);
    if (!fin.is_open()) throw runtime_error("Не вдалося відкрити keys.txt");
    long long a, b;
    while (fin >> a >> b) keys.push_back({ a, b });
    fin.close();
    return keys;
}

// === Основна програма ===
int main() {
    try {
        ifstream fin("cipher.txt");
        if (!fin.is_open()) throw runtime_error("Не вдалося відкрити cipher.txt");
        string cipher; fin >> cipher; fin.close();

        vector<pair<long long, long long>> keys = loadKeys("keys.txt");
        cout << "Зчитано " << keys.size() << " ключів.\n";

        for (auto& key : keys) {
            long long a = key.first;
            long long b = key.second;
            try {
                string plain = decryptText(cipher, a, b);
                if (looksLikeRussian(plain)) {
                    cout << "\n=== Можливий ключ ===\n";
                    cout << "a = " << a << ", b = " << b << endl;
                    cout << plain.substr(0, 300) << "...\n";
                }
            }
            catch (...) { continue; }
        }
    }
    catch (exception& e) {
        cout << "Помилка: " << e.what() << endl;
    }
}
