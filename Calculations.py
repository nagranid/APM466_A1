from Get_Data import *
import math
import numpy as np
from collections import Counter
import numpy_financial as npf
import copy
from datetime import datetime as dt, timedelta
from dateutil.relativedelta import relativedelta
import copy
from sympy import Symbol
from sympy.solvers import solve

Global_Bonds=['G328','ZU15','H490','A610','J546','B451','K528','D507','L518','E679','M847']

def combine():
    Data = get_basic_data("x")
    Prices= get_prices(20220110,20220124,"x")
    i=0
    while i<len(Prices):
        Data[i]["Prices"]=Prices[i]
        i+=1
    return Data

def Pick_bonds(No_of_Bonds):
    List= combine()
    Selected=[]
    i=0
    Bonds=[]
    while i<int(No_of_Bonds):
        a= Global_Bonds[i]
        Bonds.append(a)
        i+=1 
    i=0
    while i<len(Bonds):
        j=0
        while j<len(List):
            Bond=List[j]["ISIN"][-4:]
            if Bonds[i]==Bond:
                Selected.append(List[j])
            j+=1
        i+=1
    return Selected    
        
def Dirty_Price(No_of_Bonds):
    List= Pick_bonds(No_of_Bonds)
    Prices=[]
    AI=[]
    Coupon=[]
    i=0
    while i <len(List):
        Dates= list(List[i]["Prices"].keys())
        Date=dt.strptime(List[i]["Coupon Date"], '%m/%d/%Y').date()
        Price= list(List[i]["Prices"].values())           
        a=List[i]["Coupon"][:-1]
        Coupon.append(float(math.log(1+float(a))))
        j=0
        while j< len(Dates):    
            start=dt.strptime(Dates[j], '%Y-%m-%d').date()
            end=Date
            days= (end-start)
            count=(days/timedelta (days=1))
            coup=float((days/timedelta (days=1)/(365/2))*(Coupon[i]/2))
            List[i]["Prices"][Dates[j]]=Price[j]+coup
            j+=1
        i+=1             
    return List

def fx(y,CF_schedule,Timing):
    i=0
    function=0
    while i<len(CF_schedule):
        if i==0:
            function+=CF_schedule[i]
        else:
            function+=CF_schedule[i]*math.exp(-y*Timing[i])
        i+=1
    return function

def dx(y,CF_schedule,Timing):
    i=1
    function=0
    while i<len(CF_schedule):
        function+=CF_schedule[i]*math.exp(-y*Timing[i])*-Timing[i]
        i+=1
    return function

def Yield_To_Maturity(No_of_Bonds):
    Bonds= Dirty_Price(No_of_Bonds)
    i=0
    while i<len(Bonds):
        YTM={}
        Price_dic=Bonds[i]["Prices"]
        Price_list=list(Price_dic.values())
        Dates=list(Price_dic)
        Face=100
        s=Bonds[i]["Coupon Date"]
        e=Bonds[i]["Maturity"]
        start= float(s[-4:])
        end=float(e[-4:])
        length= 2*(end-start)+1
        count=0
        while count<len(Dates):
            CF_schedule=[]
            Timing=[]
            j=1
            CF_schedule.append(-Price_list[count])
            Timing.append(float(0))
            Next_Coupon=dt.strptime(s, '%m/%d/%Y').date()
            Today=dt.strptime(Dates[count], '%Y-%m-%d').date()
            difference_in_years = ((Next_Coupon-Today)/365)
            t=difference_in_years / timedelta (days=1)
            Timing.append(t)
            Paym = float(Bonds[i]["Coupon"][:-1])
            while j<length:
                t+=.5
                Timing.append(t)
                CF_schedule.append(float(Paym))
                Timing.append(float(t))
                j+=1
            x=Face+Paym
            CF_schedule.append(x)
            y=float(.1)
            for m in range(0,100):
                y = float(y - (fx(y,CF_schedule,Timing)/dx(y,CF_schedule,Timing))) 
            YTM[Dates[count]]=y
            count+=1
        Bonds[i]["YTM"]=YTM
        i+=1
    return Bonds

def CF_Calculator(No_of_Bonds):
    Bonds= Yield_To_Maturity(No_of_Bonds) 
    i=0
    Total_CF_schedule=[]
    while i<len(Bonds):
        CF={}
        Price_dic=Bonds[i]["Prices"]
        Price_list=list(Price_dic.values())
        Dates=list(Price_dic)
        Face=100
        s=Bonds[i]["Coupon Date"]
        e=Bonds[i]["Maturity"]
        start= float(s[-4:])
        end=float(e[-4:])
        length= 2*(end-start)+1
        count=0
        while count<len(Dates):
            CF_schedule=[]
            j=1
            CF_schedule.append(-Price_list[count])
            Paym = float(Bonds[i]["Coupon"][:-1])
            while j<length:
                CF_schedule.append(Paym)
                j+=1
            x=Face+Paym
            CF_schedule.append(x)
            CF[Dates[count]]=CF_schedule
            count+=1
        Total_CF_schedule.append(CF)
        i+=1
    return Total_CF_schedule
    
    
def r_2(dic):
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("6/1/2022", '%m/%d/%Y').date()
        t=(e-s)/365
        y=-math.log(-lst[0]/lst[-1])/float(t / timedelta (days=1))
        dic[x]=y
    return dic

def extrapolate(d, x):
    y = (d[0][1] + (x - d[0][0]) /
        (d[1][0] - d[0][0]) *
        (d[1][1] - d[0][1]));
    return y


def Spot_Rate(No_of_Bonds):
    Bonds= Yield_To_Maturity(No_of_Bonds)
    Spot_Rates=[]
    CF_Schedules=CF_Calculator(No_of_Bonds)
    i=0
    new_dic={}
    Spot_Rates={'3/1/2022':0,'6/1/2022':0,'9/1/2022':0,'12/1/2022':0,
                '3/1/2023':0,'6/1/2023':0,'9/1/2023':0,'12/1/2023':0,
                '3/1/2024':0,'6/1/2024':0,'9/1/2024':0,'12/1/2024':0,
                '3/1/2025':0,'6/1/2025':0,'9/1/2025':0,'12/1/2025':0,
                '3/1/2026':0,'6/1/2026':0,'9/1/2026':0,'12/1/2026':0,
                '3/1/2027':0}
    while i<len(CF_Schedules):
        if int(Bonds[i]["Maturity"][2:3])!=1:
            Month=int(Bonds[i]["Maturity"][0])+1
            Year=int(Bonds[i]["Maturity"][-4:])
            Day=int(1)
            Maturity=str(Month)+'/'+str(Day)+'/'+str(Year)
        else:
            Maturity=Bonds[i]["Maturity"]
        new_dic[Maturity]=CF_Schedules[i]
        i+=1
    Coupons=list(Spot_Rates)
    new_dic_copy=copy.deepcopy(new_dic)
    dic=new_dic['3/1/2022']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("3/1/2022", '%m/%d/%Y').date()
        t=(e-s)/365
        y=-math.log(-lst[0]/lst[-1])/float(t / timedelta (days=1))
        dic[x]=y
    Spot_Rates['3/1/2022']= dic
    print(new_dic)
    dic=new_dic['6/1/2022']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("6/1/2022", '%m/%d/%Y').date()
        t=(e-s)/365
        y=-math.log(-lst[0]/lst[-1])/float(t / timedelta (days=1))
        dic[x]=y 
    Spot_Rates['6/1/2022']= dic
    dic=new_dic['3/1/2023']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("3/1/2022", '%m/%d/%Y').date()
        t=(e-s)/365
        t=float(t / timedelta (days=1))
        s1=dt.strptime(x, '%Y-%m-%d').date()
        e1=dt.strptime("6/1/2022", '%m/%d/%Y').date()
        t1=(e1-s1)/365
        t1=float(t1 / timedelta (days=1))
        r=Spot_Rates['3/1/2022'][x]
        r1=Spot_Rates['6/1/2022'][x]  
        t2=t+.5
        y=extrapolate([[t,r],[t1,r1]],t2)
        dic[x]=y 
    Spot_Rates['9/1/2022']= dic 
    dic=new_dic['6/1/2023']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("6/1/2022", '%m/%d/%Y').date()
        t=(e-s)/365
        t=float(t / timedelta (days=1))
        r=Spot_Rates['6/1/2022'][x]
        r1=Spot_Rates['9/1/2022'][x]  
        t1=t+.25
        t2=t1+.25
        y=extrapolate([[t,r],[t1,r1]],t2)
        dic[x]=y 
    Spot_Rates['12/1/2022']= dic  
    dic=new_dic_copy['3/1/2023']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("3/1/2022", '%m/%d/%Y').date()
        t=(e-s)/365
        t=float(t / timedelta (days=1))
        r1=Spot_Rates['3/1/2022'][x]
        r2=Spot_Rates['9/1/2022'][x]
        coup1=lst[1]
        coup2=lst[2]
        first=(coup1)*math.e**(-r1*t)
        second=(coup2)*math.e**(-r2*(t+.5))
        discounted_coup=first+second
        y=-math.log((-lst[0]-discounted_coup)/lst[-1])
        dic[x]=y
    Spot_Rates['3/1/2023']= dic
    dic=new_dic_copy['6/1/2023']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("6/1/2022", '%m/%d/%Y').date()
        t=(e-s)/365
        t=float(t / timedelta (days=1))
        r1=Spot_Rates['6/1/2022'][x]
        r2=Spot_Rates['12/1/2022'][x]
        coup1=lst[1]
        coup2=lst[2]
        first=(coup1)*math.e**(-r1*t)
        second=(coup2)*math.e**(-r2*(t+.5))
        discounted_coup=first+second
        y=-math.log((-lst[0]-discounted_coup)/lst[-1])
        dic[x]=y
    Spot_Rates['6/1/2023']= dic     
    dic=new_dic['3/1/2024']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("3/1/2023", '%m/%d/%Y').date()
        t=(e-s)/365
        t=float(t / timedelta (days=1))
        s1=dt.strptime(x, '%Y-%m-%d').date()
        e1=dt.strptime("6/1/2023", '%m/%d/%Y').date()
        t1=(e1-s1)/365
        t1=float(t1 / timedelta (days=1))
        r=Spot_Rates['3/1/2023'][x]
        r1=Spot_Rates['6/1/2023'][x]  
        t2=t+.5
        y=extrapolate([[t,r],[t1,r1]],t2)
        dic[x]=y 
    Spot_Rates['9/1/2023']= dic     
    dic=new_dic['6/1/2024']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("6/1/2023", '%m/%d/%Y').date()
        t=(e-s)/365
        t=float(t / timedelta (days=1))
        r=Spot_Rates['6/1/2023'][x]
        r1=Spot_Rates['9/1/2023'][x]  
        t1=t+.25
        t2=t1+.25
        y=extrapolate([[t,r],[t1,r1]],t2)
        dic[x]=y 
    Spot_Rates['12/1/2023']= dic  
    dic=new_dic_copy['3/1/2024']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("3/1/2022", '%m/%d/%Y').date()
        t=(e-s)/365
        t=float(t / timedelta (days=1))
        r1=Spot_Rates['3/1/2022'][x]
        r2=Spot_Rates['9/1/2022'][x]
        r3=Spot_Rates['3/1/2023'][x]
        r4=Spot_Rates['3/1/2023'][x]
        coup1=lst[1]
        coup2=lst[2]
        coup3=lst[3]
        coup4=lst[4]
        first=(coup1)*math.e**(-r1*t)
        second=(coup2)*math.e**(-r2*(t+.5))
        third=(coup3)*math.e**(-r3*(t+.5))
        fourth=(coup4)*math.e**(-r4*(t+.5))
        discounted_coup=first+second+third+fourth
        y=-math.log((-lst[0]-discounted_coup)/lst[-1])
        dic[x]=y
    Spot_Rates['3/1/2024']= dic
    dic=new_dic_copy['6/1/2024']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("6/1/2022", '%m/%d/%Y').date()
        t=(e-s)/365
        t=float(t / timedelta (days=1))
        r1=Spot_Rates['6/1/2022'][x]
        r2=Spot_Rates['12/1/2022'][x]
        r3=Spot_Rates['6/1/2023'][x]
        r4=Spot_Rates['12/1/2023'][x]
        coup1=lst[1]
        coup2=lst[2]
        coup3=lst[3]
        coup4=lst[4]
        first=(coup1)*math.e**(-r1*t)
        second=(coup2)*math.e**(-r2*(t+.5))
        third=(coup3)*math.e**(-r3*(t+.5))
        fourth=(coup4)*math.e**(-r4*(t+.5))
        discounted_coup=first+second+third+fourth
        y=-math.log((-lst[0]-discounted_coup)/lst[-1])
        dic[x]=y
    Spot_Rates['6/1/2024']= dic
    dic=new_dic['3/1/2025']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("3/1/2024", '%m/%d/%Y').date()
        t=(e-s)/365
        t=float(t / timedelta (days=1))
        s1=dt.strptime(x, '%Y-%m-%d').date()
        e1=dt.strptime("6/1/2024", '%m/%d/%Y').date()
        t1=(e1-s1)/365
        t1=float(t1 / timedelta (days=1))
        r=Spot_Rates['3/1/2024'][x]
        r1=Spot_Rates['6/1/2024'][x]  
        t2=t+.5
        y=extrapolate([[t,r],[t1,r1]],t2)
        dic[x]=y 
    Spot_Rates['9/1/2024']= dic     
    dic=new_dic['6/1/2025']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("6/1/2024", '%m/%d/%Y').date()
        t=(e-s)/365
        t=float(t / timedelta (days=1))
        r=Spot_Rates['6/1/2024'][x]
        r1=Spot_Rates['9/1/2024'][x]  
        t1=t+.25
        t2=t1+.25
        y=extrapolate([[t,r],[t1,r1]],t2)
        dic[x]=y 
    Spot_Rates['12/1/2024']= dic    
    dic=new_dic_copy['3/1/2025']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("3/1/2022", '%m/%d/%Y').date()
        t=(e-s)/365
        t=float(t / timedelta (days=1))
        r1=Spot_Rates['3/1/2022'][x]
        r2=Spot_Rates['9/1/2022'][x]
        r3=Spot_Rates['3/1/2023'][x]
        r4=Spot_Rates['3/1/2023'][x]
        r5=Spot_Rates['3/1/2024'][x]
        r6=Spot_Rates['3/1/2024'][x]        
        coup1=lst[1]
        coup2=lst[2]
        coup3=lst[3]
        coup4=lst[4]
        coup5=lst[5]
        coup6=lst[6]        
        first=(coup1)*math.e**(-r1*t)
        second=(coup2)*math.e**(-r2*(t+.5))
        third=(coup3)*math.e**(-r3*(t+.5))
        fourth=(coup4)*math.e**(-r4*(t+.5))
        fifth=(coup5)*math.e**(-r5*(t+.5))
        sixth=(coup6)*math.e**(-r6*(t+.5))        
        discounted_coup=first+second+third+fourth+fifth+sixth
        y=-math.log((-lst[0]-discounted_coup)/lst[-1])
        dic[x]=y
    Spot_Rates['3/1/2025']= dic
    dic=new_dic_copy['6/1/2025']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("6/1/2022", '%m/%d/%Y').date()
        t=(e-s)/365
        t=float(t / timedelta (days=1))
        r1=Spot_Rates['6/1/2022'][x]
        r2=Spot_Rates['12/1/2022'][x]
        r3=Spot_Rates['6/1/2023'][x]
        r4=Spot_Rates['12/1/2023'][x]
        r5=Spot_Rates['6/1/2024'][x]
        r6=Spot_Rates['12/1/2024'][x]        
        coup1=lst[1]
        coup2=lst[2]
        coup3=lst[3]
        coup4=lst[4]
        coup5=lst[5]
        coup6=lst[6]        
        first=(coup1)*math.e**(-r1*t)
        second=(coup2)*math.e**(-r2*(t+.5))
        third=(coup3)*math.e**(-r3*(t+.5))
        fourth=(coup4)*math.e**(-r4*(t+.5))
        fifth=(coup5)*math.e**(-r5*(t+.5))
        sixth=(coup6)*math.e**(-r6*(t+.5))        
        discounted_coup=first+second+third+fourth+fifth+sixth
        y=-math.log((-lst[0]-discounted_coup)/lst[-1])
        dic[x]=y
    Spot_Rates['6/1/2025']= dic
    dic=new_dic['3/1/2026']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("3/1/2025", '%m/%d/%Y').date()
        t=(e-s)/365
        t=float(t / timedelta (days=1))
        s1=dt.strptime(x, '%Y-%m-%d').date()
        e1=dt.strptime("6/1/2025", '%m/%d/%Y').date()
        t1=(e1-s1)/365
        t1=float(t1 / timedelta (days=1))
        r=Spot_Rates['3/1/2025'][x]
        r1=Spot_Rates['6/1/2025'][x]  
        t2=t+.5
        y=extrapolate([[t,r],[t1,r1]],t2)
        dic[x]=y 
    Spot_Rates['9/1/2025']= dic     
    dic=new_dic['6/1/2026']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("6/1/2025", '%m/%d/%Y').date()
        t=(e-s)/365
        t=float(t / timedelta (days=1))
        r=Spot_Rates['6/1/2025'][x]
        r1=Spot_Rates['9/1/2025'][x]  
        t1=t+.25
        t2=t1+.25
        y=extrapolate([[t,r],[t1,r1]],t2)
        dic[x]=y 
    Spot_Rates['12/1/2025']= dic    
    dic=new_dic_copy['3/1/2026']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("3/1/2022", '%m/%d/%Y').date()
        t=(e-s)/365
        t=float(t / timedelta (days=1))
        r1=Spot_Rates['3/1/2022'][x]
        r2=Spot_Rates['9/1/2022'][x]
        r3=Spot_Rates['3/1/2023'][x]
        r4=Spot_Rates['9/1/2023'][x]
        r5=Spot_Rates['3/1/2024'][x]
        r6=Spot_Rates['9/1/2024'][x]        
        r7=Spot_Rates['3/1/2025'][x]
        r8=Spot_Rates['9/1/2025'][x]        
        coup1=lst[1]
        coup2=lst[2]
        coup3=lst[3]
        coup4=lst[4]
        coup5=lst[5]
        coup6=lst[6]
        coup7=lst[7]
        coup8=lst[8]        
        first=(coup1)*math.e**(-r1*t)
        second=(coup2)*math.e**(-r2*(t+.5))
        third=(coup3)*math.e**(-r3*(t+.5))
        fourth=(coup4)*math.e**(-r4*(t+.5))
        fifth=(coup5)*math.e**(-r5*(t+.5))
        sixth=(coup6)*math.e**(-r6*(t+.5))
        seventh=(coup7)*math.e**(-r7*(t+.5))
        eigth=(coup8)*math.e**(-r8*(t+.5))        
        discounted_coup=first+second+third+fourth+fifth+sixth+seventh+eigth
        y=-math.log((-lst[0]-discounted_coup)/lst[-1])
        dic[x]=y
    Spot_Rates['3/1/2026']= dic    
    dic=new_dic_copy['6/1/2026']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("6/1/2022", '%m/%d/%Y').date()
        t=(e-s)/365
        t=float(t / timedelta (days=1))
        r1=Spot_Rates['6/1/2022'][x]
        r2=Spot_Rates['12/1/2022'][x]
        r3=Spot_Rates['6/1/2023'][x]
        r4=Spot_Rates['12/1/2023'][x]
        r5=Spot_Rates['6/1/2024'][x]
        r6=Spot_Rates['12/1/2024'][x]        
        r7=Spot_Rates['6/1/2025'][x]
        r8=Spot_Rates['12/1/2025'][x]        
        coup1=lst[1]
        coup2=lst[2]
        coup3=lst[3]
        coup4=lst[4]
        coup5=lst[5]
        coup6=lst[6]
        coup7=lst[7]
        coup8=lst[8]        
        first=(coup1)*math.e**(-r1*t)
        second=(coup2)*math.e**(-r2*(t+.5))
        third=(coup3)*math.e**(-r3*(t+.5))
        fourth=(coup4)*math.e**(-r4*(t+.5))
        fifth=(coup5)*math.e**(-r5*(t+.5))
        sixth=(coup6)*math.e**(-r6*(t+.5))
        seventh=(coup7)*math.e**(-r7*(t+.5))
        eigth=(coup8)*math.e**(-r8*(t+.5))        
        discounted_coup=first+second+third+fourth+fifth+sixth+seventh+eigth
        y=-math.log((-lst[0]-discounted_coup)/lst[-1])
        dic[x]=y
    Spot_Rates['6/1/2026']= dic        
    dic=new_dic['3/1/2027']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("3/1/2025", '%m/%d/%Y').date()
        t=(e-s)/365
        t=float(t / timedelta (days=1))
        s1=dt.strptime(x, '%Y-%m-%d').date()
        e1=dt.strptime("6/1/2026", '%m/%d/%Y').date()
        t1=(e1-s1)/365
        t1=float(t1 / timedelta (days=1))
        r=Spot_Rates['3/1/2026'][x]
        r1=Spot_Rates['6/1/2026'][x]  
        t2=t+.5
        y=extrapolate([[t,r],[t1,r1]],t2)
        dic[x]=y 
    Spot_Rates['9/1/2026']= dic     
    dic=new_dic['6/1/2026']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("6/1/2026", '%m/%d/%Y').date()
        t=(e-s)/365
        t=float(t / timedelta (days=1))
        r=Spot_Rates['6/1/2026'][x]
        r1=Spot_Rates['9/1/2026'][x]  
        t1=t+.25
        t2=t1+.25
        y=extrapolate([[t,r],[t1,r1]],t2)
        dic[x]=y 
    Spot_Rates['12/1/2026']= dic    
    dic=new_dic_copy['3/1/2027']
    for x in dic:
        lst=dic[x]
        s=dt.strptime(x, '%Y-%m-%d').date()
        e=dt.strptime("3/1/2022", '%m/%d/%Y').date()
        t=(e-s)/365
        t=float(t / timedelta (days=1))
        r1=Spot_Rates['3/1/2022'][x]
        r2=Spot_Rates['9/1/2022'][x]
        r3=Spot_Rates['3/1/2023'][x]
        r4=Spot_Rates['9/1/2023'][x]
        r5=Spot_Rates['3/1/2024'][x]
        r6=Spot_Rates['9/1/2024'][x]        
        r7=Spot_Rates['3/1/2025'][x]
        r8=Spot_Rates['9/1/2025'][x] 
        r9=Spot_Rates['3/1/2026'][x]
        r10=Spot_Rates['9/1/2026'][x]        
        coup1=lst[1]
        coup2=lst[2]
        coup3=lst[3]
        coup4=lst[4]
        coup5=lst[5]
        coup6=lst[6]
        coup7=lst[7]
        coup8=lst[8]        
        coup9=lst[9]
        coup10=lst[10]                
        first=(coup1)*math.e**(-r1*t)
        second=(coup2)*math.e**(-r2*(t+.5))
        third=(coup3)*math.e**(-r3*(t+.5))
        fourth=(coup4)*math.e**(-r4*(t+.5))
        fifth=(coup5)*math.e**(-r5*(t+.5))
        sixth=(coup6)*math.e**(-r6*(t+.5))
        seventh=(coup7)*math.e**(-r7*(t+.5))
        eigth=(coup8)*math.e**(-r8*(t+.5))
        ninth=(coup9)*math.e**(-r9*(t+.5))
        tenth=(coup10)*math.e**(-r10*(t+.5))                
        discounted_coup=first+second+third+fourth+fifth+sixth+seventh+eigth+ninth+tenth
        y=-math.log((-lst[0]-discounted_coup)/lst[-1])
        dic[x]=y
    Spot_Rates['3/1/2027']= dic            
    return Spot_Rates
            
def Future_Rate(No_of_Bonds):
    Bonds= Yield_To_Maturity(No_of_Bonds) 
    Spot=Spot_Rate(No_of_Bonds)
    dates=list(Bonds[0]["Prices"])
    new_dic={}
    i=2
    while i<len(Bonds):
        Dates={}
        j=0
        while j<len(dates):
            Dates[dates[j]]=0
            j+=1
        if int(Bonds[i]["Maturity"][2:3])!=1:
            Month=int(Bonds[i]["Maturity"][0])+1
            Year=int(Bonds[i]["Maturity"][-4:])
            Day=int(1)
            Maturity=str(Month)+'/'+str(Day)+'/'+str(Year)
        else:
            Maturity=Bonds[i]["Maturity"]        
        new_dic[Maturity]=Dates
        i+=1
    print(new_dic)
    dic=new_dic['3/1/2023']
    for x in dic:
        dic[x]=Spot['3/1/2023'][x]
    new_dic['3/1/2023']=dic
    dic=new_dic['6/1/2023']
    for x in dic:
        r=Spot['3/1/2023'][x]
        r1=Spot['6/1/2023'][x]
        t=1
        s=dt.strptime("3/1/2023", '%m/%d/%Y').date()
        e=dt.strptime("6/1/2023", '%m/%d/%Y').date()
        t_diff=(e-s)/365
        t_diff=float(t_diff / timedelta (days=1))
        t1=t+t_diff
        forward=((r1*t1)-(r*t))/(t1-t)
        dic[x]=forward
    new_dic['5/31/2023']=dic   
    dic=new_dic['3/1/2024']
    for x in dic:
        r=Spot['3/1/2023'][x]
        r1=Spot['3/1/2024'][x]
        t=1
        s=dt.strptime("3/1/2023", '%m/%d/%Y').date()
        e=dt.strptime("3/1/2024", '%m/%d/%Y').date()
        t_diff=(e-s)/365
        t_diff=float(t_diff / timedelta (days=1))
        t1=t+t_diff
        forward=((r1*t1)-(r*t))/(t1-t)
        dic[x]=forward
    new_dic['3/1/2024']=dic        
    dic=new_dic['6/1/2024']
    for x in dic:
        r=Spot['3/1/2023'][x]
        r1=Spot['6/1/2024'][x]
        t=1
        s=dt.strptime("3/1/2023", '%m/%d/%Y').date()
        e=dt.strptime("6/1/2024", '%m/%d/%Y').date()
        t_diff=(e-s)/365
        t_diff=float(t_diff / timedelta (days=1))
        t1=t+t_diff
        forward=((r1*t1)-(r*t))/(t1-t)
        dic[x]=forward
    new_dic['6/1/2024']=dic
    dic=new_dic['3/1/2025']
    for x in dic:
        r=Spot['3/1/2023'][x]
        r1=Spot['3/1/2025'][x]
        t=1
        s=dt.strptime("3/1/2023", '%m/%d/%Y').date()
        e=dt.strptime("3/1/2025", '%m/%d/%Y').date()
        t_diff=(e-s)/365
        t_diff=float(t_diff / timedelta (days=1))
        t1=t+t_diff
        forward=((r1*t1)-(r*t))/(t1-t)
        dic[x]=forward
    new_dic['2/28/2025']=dic    
    dic=new_dic['6/1/2025']
    for x in dic:
        r=Spot['3/1/2023'][x]
        r1=Spot['6/1/2025'][x]
        t=1
        s=dt.strptime("3/1/2023", '%m/%d/%Y').date()
        e=dt.strptime("6/1/2025", '%m/%d/%Y').date()
        t_diff=(e-s)/365
        t_diff=float(t_diff / timedelta (days=1))
        t1=t+t_diff
        forward=((r1*t1)-(r*t))/(t1-t)
        dic[x]=forward
    new_dic['5/31/2025']=dic    
    dic=new_dic['3/1/2026']
    for x in dic:
        r=Spot['3/1/2023'][x]
        r1=Spot['3/1/2026'][x]
        t=1
        s=dt.strptime("3/1/2023", '%m/%d/%Y').date()
        e=dt.strptime("3/1/2026", '%m/%d/%Y').date()
        t_diff=(e-s)/365
        t_diff=float(t_diff / timedelta (days=1))
        t1=t+t_diff
        forward=((r1*t1)-(r*t))/(t1-t)
        dic[x]=forward
    new_dic['3/1/2026']=dic    
    dic=new_dic['6/1/2026']
    for x in dic:
        r=Spot['3/1/2023'][x]
        r1=Spot['6/1/2026'][x]
        t=1
        s=dt.strptime("3/1/2023", '%m/%d/%Y').date()
        e=dt.strptime("6/1/2026", '%m/%d/%Y').date()
        t_diff=(e-s)/365
        t_diff=float(t_diff / timedelta (days=1))
        t1=t+t_diff
        forward=((r1*t1)-(r*t))/(t1-t)
        dic[x]=forward
    new_dic['6/1/2026']=dic        
    dic=new_dic['3/1/2027']
    for x in dic:
        r=Spot['3/1/2023'][x]
        r1=Spot['3/1/2027'][x]
        t=1
        s=dt.strptime("3/1/2023", '%m/%d/%Y').date()
        e=dt.strptime("3/1/2027", '%m/%d/%Y').date()
        t_diff=(e-s)/365
        t_diff=float(t_diff / timedelta (days=1))
        t1=t+t_diff
        forward=((r1*t1)-(r*t))/(t1-t)
        dic[x]=forward
    new_dic['3/1/2027']=dic    
    return new_dic