#include <bits/stdc++.h>

// #define int long long
#define ff first
#define ss second
#define pb push_back
#define eb emplace_back
#define opt ios_base::sync_with_stdio(0);cin.tie(nullptr);cout.tie(nullptr);

using namespace std;

class Solution {
public:
  string longestPalindrome(string s) {
    opt
    int n = s.length();
    if (n <= 1) return s;
    int start = 0;
    int maxLen = 1;
    auto expand = [&](int left, int right) {
      while (left >= 0 && right < n && s[left] == s[right]) {
        --left;
        ++right;
      }
      int len = right - left - 1;
      if (len > maxLen) {
        maxLen = len;
        start = left + 1;
      }
    };
    for (int i = 0; i < n; ++i) {
      expand(i, i);
      expand(i, i + 1);
    }
    return s.substr(start, maxLen);
  }
};