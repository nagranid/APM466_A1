import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import pandas as pd
from Get_Data import *
from Calculations import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pandas_datareader.data import DataReader as dr
import scipy.linalg as la
from scipy.interpolate import interp1d
from collections import OrderedDict
Big_Lst=[]

startDate = '2022-3-01'
endDate = '2027-3-01'

cur_date = start = datetime.strptime(startDate, '%Y-%m-%d').date()
end = datetime.strptime(endDate, '%Y-%m-%d').date()

while cur_date < end:
    Big_Lst.append(cur_date)
    cur_date += relativedelta(months=1)   

i=0
while i<len(Big_Lst):
    Big_Lst[i]=0
    i+=3

Maturities = list(filter(lambda x: x!= 0, Big_Lst))

def Plot_YTM(No_of_bonds):
    Bonds= Yield_To_Maturity(No_of_bonds)
    dic={}
    i=0
    while i<len(Bonds):
        dic[Bonds[i]["ISIN"]]=Bonds[i]["YTM"]
        i+=1
    keys=list(dic)
    val=list(dic[keys[0]])
    mod_dic={} 
    for item in val:
        i=0
        temp_dic={}
        while i<len(Bonds):
            temp_dic[datetime.strptime(Bonds[i]["Maturity"], '%m/%d/%Y').date()]=Bonds[i]["YTM"][item]
            i+=1
        j=0
        while j<len(Maturities):
            temp_dic[Maturities[j]]=np.nan
            j+=1        
        ordered=OrderedDict(sorted(temp_dic.items(), key=lambda t: t[0]))
        mod_dic[item]=ordered
    df =pd.DataFrame.from_dict(mod_dic,orient='index')
    df_tr=df.transpose()
    columns=list(df_tr)
    for x in columns:
        df_tr[x]=df_tr[x].interpolate(method='linear')
    print(df_tr)
    graph=df_tr.plot.line()
    graph.set_title('Yield Curve (5 Years)')
    graph.set_xlabel('Date')
    graph.set_ylabel('YTM')  
    graph.set_xlim(pd.Timestamp('2022-03-01'),pd.Timestamp('2027-03-01'))   
    graph.xaxis.set_major_formatter(mdate.DateFormatter('%m/%Y'))  
    graph.xaxis.set_major_locator(mdate.MonthLocator(interval=8))
    graph.legend(loc="lower center")

def Plot_Spot(No_of_bonds):
    Spot= Spot_Rate(No_of_bonds)
    mod_dic={}
    for item in Spot:
        mod_dic[datetime.strptime(item, '%m/%d/%Y').date()]=Spot[item]
    df_tr =pd.DataFrame.from_dict(mod_dic,orient='index')
    print(df_tr)
    graph=df_tr.plot.line()
    graph.set_title('Spot Curve (4 Years)')
    graph.set_xlabel('Date')
    graph.set_ylabel('YTM')  
    graph.set_xlim(pd.Timestamp('2023-03-01'),pd.Timestamp('2027-03-01'))
    graph.xaxis.set_major_formatter(mdate.DateFormatter('%m/%Y'))  
    graph.xaxis.set_major_locator(mdate.MonthLocator(interval=8))
    graph.legend(loc="upper left")
    
def Plot_Future(No_of_bonds):
    Future= Future_Rate(No_of_bonds)
    mod_dic={}
    for item in Future:
        mod_dic[datetime.strptime(item, '%m/%d/%Y').date()]=Future[item]
    df_tr =pd.DataFrame.from_dict(mod_dic,orient='index')
    print(df_tr)
    graph=df_tr.plot.line()
    graph.set_title('Forward Curve (4 Years)')
    graph.set_xlabel('Date')
    graph.set_ylabel('YTM')  
    graph.set_xlim(pd.Timestamp('2023-03-01'),pd.Timestamp('2027-03-01'))
    graph.xaxis.set_major_formatter(mdate.DateFormatter('%m/%Y'))  
    graph.xaxis.set_major_locator(mdate.MonthLocator(interval=8))
    graph.legend(loc="lower right")    

def Cov_Matrix_YTM(No_of_bonds):
    Bonds= Yield_To_Maturity(No_of_bonds)
    dic={}
    i=0
    while i<len(Bonds):
        dic[Bonds[i]["ISIN"]]=Bonds[i]["YTM"]
        i+=1
    keys=list(dic)
    val=list(dic[keys[0]])
    mod_dic={}
    for item in val:
        i=0
        temp_dic={}
        while i<len(Bonds):
            if int(Bonds[i]["Maturity"][2:3])!=1:
                Month=int(Bonds[i]["Maturity"][0])+1
                Year=int(Bonds[i]["Maturity"][-4:])
                Day=int(1)
                Maturity=str(Month)+'/'+str(Day)+'/'+str(Year)
            else:
                Maturity=Bonds[i]["Maturity"]                    
            temp_dic[Maturity]=Bonds[i]["YTM"][item]
            i+=1
        mod_dic[item]=temp_dic
    array=[]
    lst=['3/1/2023','3/1/2024','3/1/2025','3/1/2026','3/1/2027']
    dates=list(mod_dic)
    i=0
    while i<len(lst):
        ast=[]
        j=0
        while j<len(dates):
            temp=0
            temp=mod_dic[dates[j]][lst[i]]
            ast.append(temp)
            j+=1
        array.append(ast)
        i+=1
    log=[]
    i=0
    while i<len(array):
        temp=[]
        lst=array[i]
        l=0
        while l<(len(lst)-1):
            lg=math.log(lst[l+1]/lst[l])
            temp.append(lg)
            l+=1
        log.append(temp)
        i+=1
    covMatrix=np.cov(log)
    results=la.eig(covMatrix)
    print("The eigenvalues are",results[0])
    print("The eigenvectors are",results[1])
    return covMatrix

def Cov_Matrix_Future(No_of_bonds):
    Future= Future_Rate(No_of_bonds)
    print(Future)
    array=[]
    lst=['3/1/2024','3/1/2025','3/1/2026','3/1/2027']
    dates=list(Future['3/1/2024'])
    i=0
    while i<len(lst):
        ast=[]
        j=0
        while j<len(dates):
            temp=0
            temp=Future[lst[i]][dates[j]]
            ast.append(temp)
            j+=1
        array.append(ast)
        i+=1
    log=[]
    i=0
    while i<len(array):
        temp=[]
        lst=array[i]
        l=0
        while l<(len(lst)-1):
            lg=math.log(lst[l+1]/lst[l])
            temp.append(lg)
            l+=1
        log.append(temp)
        i+=1
    covMatrix=np.cov(log)
    results=la.eig(covMatrix)
    print("The eigenvalues are",results[0])
    print("The eigenvectors are",results[1])    
    return covMatrix
    
