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
  vector<vector<string>> groupAnagrams(vector<string>& strs) {
    opt
    unordered_map<string, vector<string>> groups;
    for (const string& s : strs) {
      string key = s;
      ranges::sort(key);
      groups[key].push_back(s);
    }
    vector<vector<string>> result;
    result.reserve(groups.size());
    for (auto& [key, group] : groups) {
      result.push_back(std::move(group));
    }
    return result;
  }
};