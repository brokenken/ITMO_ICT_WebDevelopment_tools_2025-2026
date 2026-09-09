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
  vector<vector<int>> threeSum(vector<int>& nums) {
    opt
    vector<vector<int>> result;
    int n = nums.size();
    if (n < 3) return result;
    ranges::sort(nums);
    for (int i = 0; i < n - 2; ++i) {
      if (i > 0 && nums[i] == nums[i - 1]) continue;
      if (nums[i] > 0) break;
      int left = i + 1;
      int right = n - 1;
      while (left < right) {
        int64_t sum = nums[i] + nums[left] + nums[right];
        if (sum == 0) {
          result.push_back({nums[i], nums[left], nums[right]});
          while (left < right && nums[left] == nums[left + 1]) ++left;
          while (left < right && nums[right] == nums[right - 1]) --right;
          ++left;
          --right;
        } else if (sum < 0) {
          ++left;
        } else {
          --right;
        }
      }
    }
    return result;
  }
};