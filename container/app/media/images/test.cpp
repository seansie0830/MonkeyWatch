// 窮舉
#include<bits/stdc++.h>
using namespace std;
void solve(unsigned int,unsigned int);
unsigned int solutions=0,sq[65536],num[4]={};
int main(){
    unsigned int n,i;
    std::ios::sync_with_stdio(false);
    std::cin.tie(0);
    map<int,int> sqmp;
    for(i=0;i<65536;i++){
        sq[i]=i*i;

    }
    cin>>n;
    solve(1<<n,0);
    if(solutions==0) cout<<"0"<<endl;
    return 0;
}
void solve(unsigned int remain,unsigned int id){
    if(id==3){
        unsigned int n=sqrt(remain);
        if(sq[n]==remain){
            solutions++;
            num[3]=n;
            cout<<num[0]<<" "<<num[1]<<" "<<num[2]<<" "<<num[3]<<endl;
        }// 測試remain 是否為完全平方數
        else return;
    }
    else{
        unsigned int lbound;
        if(id>0){
            lbound=num[0];
        }
        else lbound=1;
        unsigned int ubound=sqrt(remain/(4-id)); // ! optimization lack using  map table .....
        for(unsigned int n=lbound;n<=ubound;n++){
            num[id]=n;
            solve(remain-sq[n],id+1);
        }
    }
}