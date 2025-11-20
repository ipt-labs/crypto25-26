#include <iostream>
#include <vector>
using namespace std;

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

int main() {
    try {
        cout << "Обернений елемент: " << mod_inv(7, 26) << endl;
        auto s = solve_cong(14, 30, 100);
        if (s.empty()) cout << "Немає розв’язків\n";
        else { cout << "Розв’язки: "; for (auto x : s) cout << x << " "; cout << endl; }
    }
    catch (exception& e) { cout << e.what() << endl; }
}
