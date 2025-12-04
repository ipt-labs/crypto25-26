#include <iostream>
#include <fstream>
#include <map>
#include <vector>
#include <algorithm>
#include <string>
#include <codecvt>
using namespace std;

int main() {
    ifstream fin("08utf8.txt");
    
    if (!fin.is_open()) {
        cout << "Помилка: не вдалося відкрити 08utf8.txt\n";
        return 1;
    }

    string line;
    u32string text;
    // Зчитуємо лише літери (російський текст)
    std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> conv;

    while (getline(fin, line)) {
        
        std::u32string line32 = conv.from_bytes(line);

        for (char32_t c : line32) {
            text += tolower(c);
        }
    }
    fin.close();

    // Частоти біграм (з перекриттям)
    map<u32string, int> bigrams;
    for (size_t i = 0; i + 1 < text.size(); i++) {
        u32string bigram = { text[i], text[i + 1] };
        bigrams[bigram]++;
    }

    // Перетворимо на вектор і відсортуємо за спаданням частоти
    vector<pair<u32string, int>> sorted(bigrams.begin(), bigrams.end());
    sort(sorted.begin(), sorted.end(), [](auto& a, auto& b) {
        return a.second > b.second;
        });

    cout << "5 найчастіших біграм:\n";
    for (int i = 0; i < 5 && i < (int)sorted.size(); i++) {
        string bigramUTF8 = conv.to_bytes(sorted[i].first);
        cout << bigramUTF8 << " — " << sorted[i].second << endl;
    }

    return 0;
}
