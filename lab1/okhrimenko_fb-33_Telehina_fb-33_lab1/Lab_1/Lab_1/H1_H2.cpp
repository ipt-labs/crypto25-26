#include <iostream>
#include <fstream>
#include <map>
#include <cmath>
#include <string>
using namespace std;

// function for H1
double entropy1(const map<char, int> freq, int total) {
    double H = 0;
    for (auto p : freq) {
        double prob = (double)p.second / total;
        if (prob > 0)
            H -= prob * log2(prob);
    }
    return H;
}

// function for H2
double entropy2(const map<string, int> freq, int total) {
    double H = 0;
    for (auto p : freq) {
        double prob = (double)p.second / total;
        if (prob > 0)
            H -= prob * log2(prob);
    }
    return H / 2.0;
}

int main() {
    //===================WITHOUT SPACE============================
    ifstream fin("input.txt"); 
    string text, line;
    while (getline(fin, line)) {
        for (char c : line) {
            if (isalpha((unsigned char)c)) {
                c = tolower((unsigned char)c);
                text += c;
            }
        }
    }

    int total = text.size();

    // frequency of words
    map<char, int> freq1;
    for (char c : text) freq1[c]++;

    cout << endl << "=== WITHOUT SPACES ===\n";

    cout << "For H1: " << endl;

    //output is H1+frequency every letter
    for (auto p : freq1) {
        double prob = (double)p.second / total;
        cout << p.first << "  " << p.second << "  " << prob << endl;
    }

    cout << "H1 = " << entropy1(freq1, text.size()) << endl;
    
    cout << "===============For H2 (overlapping): " << endl;

    // frequency of bigrams
    map<string, int> freq2;
    for (size_t i = 0; i + 1 < text.size(); i++) {
        string bigram = "";
        bigram += text[i];
        bigram += text[i + 1];
        freq2[bigram]++;
    }

    //output is H2+frequency every bigram
    for (auto p : freq2) {
        double prob = (double)p.second / (total - 1);
        cout << p.first << "  " << p.second << "  " << prob << endl;
    }

    cout << "H2(overlapping) = " << entropy2(freq2, total - 1);

    // ---------- no-overlapping ----------
    cout << "===============For H2 (overlapping): " << endl;
    map<string, int> freq2_nonoverlap;
    for (size_t i = 0; i + 1 < text.size(); i += 2) {
        string bigram = "";
        bigram += text[i];
        bigram += text[i + 1];
        freq2_nonoverlap[bigram]++;
    }

    for (auto p : freq2_nonoverlap) {
        double prob = (double)p.second / (total - 1);
        cout << p.first << "  " << p.second << "  " << prob << endl;
    }

    cout << "H2(non-overlapping) = " << entropy2(freq2_nonoverlap, total / 2) << endl;

    //=====================WITH SPACE==============================

    fin.clear();          //pointer on the start
    fin.seekg(0, ios::beg);

    string text2, line2;
    while (getline(fin, line2)) {
        for (char c : line2) {
            if (isalpha((unsigned char)c) || c == ' ') {
                c = tolower((unsigned char)c);
                text2 += c;
            }
        }
        text2 += ' '; //space between lines
    }

    int total2 = text2.size();

    map<char, int> freq1_space;
    for (char c : text2) freq1_space[c]++;

    map<string, int> freq2_space;
    for (size_t i = 0; i + 1 < text2.size(); i++) {
        string bigram = "";
        bigram += text2[i];
        bigram += text2[i + 1];
        freq2_space[bigram]++;
    }

    cout << endl << "=== WITH SPACES ===\n";
    for (auto p : freq1_space) {
        double prob = (double)p.second / total2;
        cout << (p.first == ' ' ? '_' : p.first) << "  " << p.second << "  " << prob << endl;
    }

    cout << "H1 = " << entropy1(freq1_space, total2) << endl;

    for (auto p : freq2_space) {
        double prob = (double)p.second / (total2 - 1);
        string show = p.first;
        for (char& ch : show) if (ch == ' ') ch = '_';
        cout << show << "  " << p.second << "  " << prob << endl;
    }

    cout << "H2 = " << entropy2(freq2_space, total2 - 1) << endl;

    // ---------- no-overlapping ----------
    cout << "===============For H2 (overlapping): " << endl;
    map<string, int> freq3_nonoverlap;
    for (size_t i = 0; i + 1 < text.size(); i += 2) {
        string bigram = "";
        bigram += text[i];
        bigram += text[i + 1];
        freq3_nonoverlap[bigram]++;
    }

    for (auto p : freq3_nonoverlap) {
        double prob = (double)p.second / (total - 1);
        cout << p.first << "  " << p.second << "  " << prob << endl;
    }

    cout << "H2(non-overlapping) = " << entropy2(freq3_nonoverlap, total / 2) << endl;

    return 0;
}
