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

int main() {
    ifstream fin("input.txt"); 
    string text, line;
    while (getline(fin, line)) { //new text without space,numbers etc
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

    //output is H1+frequency every letter
    for (auto p : freq1) {
        double prob = (double)p.second / total;
        cout << p.first << "  " << p.second << "  " << prob << endl;
    }

    cout << "H1 = " << entropy1(freq1, text.size()) << endl;

    return 0;
}
