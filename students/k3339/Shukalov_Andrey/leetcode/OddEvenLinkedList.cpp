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
  ListNode* oddEvenList(ListNode* head) {
    opt
    if (head == nullptr || head->next == nullptr) {
      return head;
    }
    ListNode* odd = head;
    ListNode* even = head->next;
    ListNode* evenHead = even;
    while (even != nullptr && even->next != nullptr) {
      odd->next = even->next;
      odd = odd->next;
      even->next = odd->next;
      even = even->next;
    }
    odd->next = evenHead;
    return head;
  }
};