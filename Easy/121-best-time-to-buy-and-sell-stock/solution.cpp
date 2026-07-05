class Solution {
public:
    int maxProfit(vector<int>& prices) {
        int cost=0,maxProfit=0,minSell=prices[0];
        for(int i=1;i<prices.size();i++){
            cost=prices[i]-minSell;
            maxProfit=max(maxProfit,cost);
            minSell=min(prices[i],minSell);
        }
        return maxProfit;
    }
};