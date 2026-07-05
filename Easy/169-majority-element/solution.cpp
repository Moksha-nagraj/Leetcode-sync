class Solution {
public:
    int majorityElement(vector<int>& nums) {
        int el,cnt=0;
        for(int i=0;i<nums.size();i++){
            if(cnt==0){
                el=nums[i];
                cnt++;
            }
            else if(nums[i]==el){
                cnt++;
            }
            else cnt--;
        }
        return el;
    }
};