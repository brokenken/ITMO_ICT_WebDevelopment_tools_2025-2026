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
  void setZeroes(vector<vector<int>>& matrix) {
    opt
    int m = matrix.size();
    int n = matrix[0].size();
    bool firstRowHasZero = false;
    bool firstColHasZero = false;
    for (int j = 0; j < n; ++j) {
      if (matrix[0][j] == 0) {
        firstRowHasZero = true;
        break;
      }
    }
    for (int i = 0; i < m; ++i) {
      if (matrix[i][0] == 0) {
        firstColHasZero = true;
        break;
      }
    }
    for (int i = 1; i < m; ++i) {
      for (int j = 1; j < n; ++j) {
        if (matrix[i][j] == 0) {
          matrix[i][0] = 0;
          matrix[0][j] = 0;
        }
      }
    }
    for (int i = 1; i < m; ++i) {
      for (int j = 1; j < n; ++j) {
        if (matrix[i][0] == 0 || matrix[0][j] == 0) {
          matrix[i][j] = 0;
        }
      }
    }
    if (firstRowHasZero) {
      for (int j = 0; j < n; ++j) {
        matrix[0][j] = 0;
      }
    }
    if (firstColHasZero) {
      for (int i = 0; i < m; ++i) {
        matrix[i][0] = 0;
      }
    }
  }
};