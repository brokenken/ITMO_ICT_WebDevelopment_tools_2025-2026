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
  int lengthOfLongestSubstring(string s) {
    opt
    int n = s.length();
    if (n == 0) return 0;
    unordered_map<char, int> lastIndex;
    int left = 0;
    int maxLen = 0;
    for (int right = 0; right < n; ++right) {
      char c = s[right];
      if (lastIndex.count(c) && lastIndex[c] >= left) {
        left = lastIndex[c] + 1;
      }
      lastIndex[c] = right;
      maxLen = max(maxLen, right - left + 1);
    }
    return maxLen;
  }
};