class Solution {
public:
    vector<int> replaceElements(vector<int>& arr) {
        int n=arr.size();
        int maxi=INT_MIN;
        vector<int> ans(n,0);
        ans[n-1]=-1;
        for(int i=n-2;i>=0;i--){
            if(arr[i+1]>maxi){
                ans[i]=arr[i+1];
            }
            maxi=max(maxi,arr[i+1]);
            ans[i]=maxi;
        }
        return ans;
    }
};