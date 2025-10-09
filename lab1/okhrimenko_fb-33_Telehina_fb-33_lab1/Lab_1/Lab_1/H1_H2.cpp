#include <iostream>
#include <fstream>
#include <map>
#include <vector>
#include <algorithm>
#include <cmath>
#include <string>
#include <iomanip>
using namespace std;

// -------------function for H1------------
double entropy1(const map<char, int> freq, int total) {
    double H = 0;
    for (auto p : freq) {
        double prob = (double)p.second / total;
        if (prob > 0)
            H -= prob * log2(prob);
    }
    return H;
}

// -----------function for H2------------
double entropy2(const map<string, int> freq, int total) {
    double H = 0;
    for (auto p : freq) {
        double prob = (double)p.second / total;
        if (prob > 0)
            H -= prob * log2(prob);
    }
    return H / 2.0;
}

// ---------- Function for symbol in csv ----------
void saveSymbolFrequencyCSV(ofstream& fout, const map<char, int>& freq, int total, const string& title) {
    // Сортування за спаданням
    vector<pair<char, int>> sorted(freq.begin(), freq.end());
    sort(sorted.begin(), sorted.end(), [](auto& a, auto& b) { return a.second > b.second; });

    fout << title << "\n";
    fout << "Symbol,Count,Probability\n";
    for (auto& p : sorted) {
        double prob = (double)p.second / total;
        fout << (p.first == ' ' ? '_' : p.first) << "," << p.second << "," << fixed << setprecision(6) << prob << "\n";
    }
    fout << "\n";
}

// ---------- function for matrix for bigrams in csv ----------
void saveBigramMatrixCSV(ofstream& fout, const map<string, int>& freq2, const vector<char>& alphabet, int total, const string& title) {
    fout << title << "\n";
    fout << ",";
    for (char col : alphabet)
        fout << (col == ' ' ? '_' : col) << ",";
    fout << "\n";

    for (char row : alphabet) {
        fout << (row == ' ' ? '_' : row) << ",";
        for (char col : alphabet) {
            string bigram;
            bigram += row;
            bigram += col;
            double prob = 0;
            if (freq2.count(bigram))
                prob = (double)freq2.at(bigram) / total;
            fout << fixed << setprecision(6) << prob << ",";
        }
        fout << "\n";
    }
    fout << "\n";
}

int main() {
    //===================WITHOUT SPACE============================
    ifstream fin("input.txt");
    ofstream fout("results.csv");
    if (!fin.is_open()) {
        cout << "Error: cannot open input.txt\n";
        return 1;
    }

    string text, line;
    while (getline(fin, line)) {
        for (char c : line) {
            if (isalpha((unsigned char)c)) {
                text += tolower((unsigned char)c);
            }
        }
    }

    int total = text.size();

    // frequency of words
    map<char, int> freq1;
    for (char c : text) freq1[c]++;

    //bigrams with overlaping
    map<string, int> freq2_overlap;
    for (size_t i = 0; i + 1 < text.size(); i++) {
        string bigram = { text[i], text[i + 1] };
        freq2_overlap[bigram]++;
    }

    //bigrams without overlaping
    map<string, int> freq2_non;
    for (size_t i = 0; i + 1 < text.size(); i += 2) {
        string bigram = { text[i], text[i + 1] };
        freq2_non[bigram]++;
    }

    //find enthropy
    double H1_no_space = entropy1(freq1, total);
    double H2_overlap_no_space = entropy2(freq2_overlap, total - 1);
    double H2_non_no_space = entropy2(freq2_non, total / 2);

    //write in table .csv
    saveSymbolFrequencyCSV(fout, freq1, total, "WITHOUT SPACES: Symbol Frequency Table");
    vector<char> alphabet_no_space;
    for (auto& p : freq1) alphabet_no_space.push_back(p.first);
    sort(alphabet_no_space.begin(), alphabet_no_space.end());
    saveBigramMatrixCSV(fout, freq2_overlap, alphabet_no_space, total - 1, "WITHOUT SPACES: Bigram Matrix (Overlapping)");
    saveBigramMatrixCSV(fout, freq2_non, alphabet_no_space, total / 2, "WITHOUT SPACES: Bigram Matrix (Non-overlapping)");

    fout << "WITHOUT SPACES SUMMARY\n";
    fout << "H1," << H1_no_space << "\n";
    fout << "H2 overlapping," << H2_overlap_no_space << "\n";
    fout << "H2 non-overlapping," << H2_non_no_space << "\n\n";

    //===============WITH SPACES====================

    fin.clear(); //pointer to start
    fin.seekg(0, ios::beg);

    string text2, line2;
    while (getline(fin, line2)) {
        for (char c : line2) {
            if (isalpha((unsigned char)c) || c == ' ')
                text2 += tolower((unsigned char)c);
        }
        text2 += ' ';
    }

    int total2 = text2.size();
    map<char, int> freq1_space;
    for (char c : text2) freq1_space[c]++;

    //bigrams with sapce + overlaping
    map<string, int> freq2_space_overlap;
    for (size_t i = 0; i + 1 < text2.size(); i++) {
        string bigram = { text2[i], text2[i + 1] };
        freq2_space_overlap[bigram]++;
    }

    // bigrams with sapce + non overlaping
    map<string, int> freq2_space_non;
    for (size_t i = 0; i + 1 < text2.size(); i += 2) {
        string bigram = { text2[i], text2[i + 1] };
        freq2_space_non[bigram]++;
    }

    //enthropy with spaces
    double H1_space = entropy1(freq1_space, total2);
    double H2_overlap_space = entropy2(freq2_space_overlap, total2 - 1);
    double H2_non_space = entropy2(freq2_space_non, total2 / 2);

    // write into csv
    saveSymbolFrequencyCSV(fout, freq1_space, total2, "WITH SPACES: Symbol Frequency Table");
    vector<char> alphabet_space;
    for (auto& p : freq1_space) alphabet_space.push_back(p.first);
    sort(alphabet_space.begin(), alphabet_space.end());
    saveBigramMatrixCSV(fout, freq2_space_overlap, alphabet_space, total2 - 1, "WITH SPACES: Bigram Matrix (Overlapping)");
    saveBigramMatrixCSV(fout, freq2_space_non, alphabet_space, total2 / 2, "WITH SPACES: Bigram Matrix (Non-overlapping)");

    fout << "WITH SPACES SUMMARY\n";
    fout << "H1," << H1_space << "\n";
    fout << "H2 overlapping," << H2_overlap_space << "\n";
    fout << "H2 non-overlapping," << H2_non_space << "\n\n";

    fout.close();
    cout << "All results saved to results.csv\n";
    return 0;
}