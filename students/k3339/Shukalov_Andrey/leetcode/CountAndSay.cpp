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
  string countAndSay(int n) {
    opt
    string result = "1";
    for (int i = 2; i <= n; ++i) {
      string next;
      int len = result.length();
      int j = 0;
      while (j < len) {
        char c = result[j];
        int count = 0;
        while (j < len && result[j] == c) {
          ++count;
          ++j;
        }
        next += to_string(count);
        next += c;
      }
      result = std::move(next);
    }
    return result;
  }
};