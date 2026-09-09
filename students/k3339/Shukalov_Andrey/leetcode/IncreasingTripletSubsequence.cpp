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
  bool increasingTriplet(vector<int>& nums) {
    opt
    int first = INT_MAX;
    int second = INT_MAX;
    for (int num : nums) {
      if (num <= first) {
        first = num;
      } else if (num <= second) {
        second = num;
      } else {
        return true;
      }
    }
    return false;
  }
};