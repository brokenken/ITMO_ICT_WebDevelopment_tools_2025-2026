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
  ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {
    opt
    ListNode dummy(0);
    ListNode* curr = &dummy;
    int carry = 0;
    while (l1 != nullptr || l2 != nullptr || carry != 0) {
      int sum = carry;
      if (l1 != nullptr) {
        sum += l1->val;
        l1 = l1->next;
      }
      if (l2 != nullptr) {
        sum += l2->val;
        l2 = l2->next;
      }
      carry = sum / 10;
      curr->next = new ListNode(sum % 10);
      curr = curr->next;
    }
    return dummy.next;
  }
};