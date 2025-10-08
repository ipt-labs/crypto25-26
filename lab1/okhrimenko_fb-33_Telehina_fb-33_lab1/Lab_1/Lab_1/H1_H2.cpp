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
    ifstream fin("input.txt"); 
    string text, line;
    while (getline(fin, line)) {
        for (char c : line) {
            if (isalpha(c)) {
                c = tolower(c); 
                text += c;
            }
        }
    }

    int total = text.size();

    // frequency of words
    map<char, int> freq1;
    for (char c : text) freq1[c]++;

    cout << "For H1: " << endl;

    //output is H1+frequency every letter
    for (auto p : freq1) {
        double prob = (double)p.second / total;
        cout << p.first << "  " << p.second << "  " << prob << endl;
    }

    cout << "H1 = " << entropy1(freq1, text.size()) << endl;
    
    cout << "For H2: " << endl;

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

    cout << "H2 = " << entropy2(freq2, total - 1);

    return 0;
}
