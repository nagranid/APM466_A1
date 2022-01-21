
title: "APM466/MAT1856 Assignment 1"

import requests
import urllib.request
import time
import pandas as pd
import numpy as np
import time
import json
import re
import ast
from datetime import date
from bs4 import BeautifulSoup
from tabulate import tabulate
from openpyxl import load_workbook


urlls = ['https://markets.businessinsider.com/bonds/finder?borrower=71&maturity=shortterm&yield=','https://markets.businessinsider.com/bonds/finder?p=2&borrower=71&maturity=shortterm','https://markets.businessinsider.com/bonds/finder?borrower=71&maturity=midterm&yield=&bondtype=2%2c3%2c4%2c16&coupon=&currency=184&rating=&country=19']
lst=[]

def get_urls():
    urls= []
    for x in urlls:
        response = requests.get(x)
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.table
        for link in table.find_all('a'):
            urls.append(link.get('href'))
    i=0
    while i < len(urls):
        urls[i]= "https://markets.businessinsider.com" + urls[i]
        i+=1
    return urls

def get_basic_data(INPUT):
    ISIN = []
    Issue_D = []
    Coupon_P = []
    Maturity = []
    Coupon_D = []
    i=0
    url= get_urls()
    while i< len(url):
        page = ''
        while page == '':
            try:
                response = requests.get(url[i])
                break
            except:
                print("Connection refused by the server..")
                print("Let me sleep for 5 seconds")
                print("ZZzzzz...")
                time.sleep(5)
                print("Was a nice sleep, now let me continue...")
                continue        
        soup = BeautifulSoup(response.content, "html.parser")
        table= soup.find_all('tr')
        a= table[6].text
        a1=a.split()[1]
        ISIN.append(a1)
        b= table[14].text
        b1=b.split()[2]
        Issue_D.append(b1)
        c = table [16].text
        c1=c.split()[1]
        Coupon_P.append(c1)
        d = table [21].text
        d1=d.split()[2]
        Maturity.append(d1)
        e = table [22].text
        e1=e.split()[3]
        Coupon_D.append(e1) 
        i+=1
    temp=[]
    if INPUT == "file":
        data = pd.DataFrame(list(zip(ISIN, Issue_D, Coupon_D, Coupon_P, Maturity)),columns=["ISIN","Issue Date","Coupon Date","Coupon","Maturity"])
        lst.append(data)
        data= pd.concat(lst)
        data.set_index('ISIN')
    else:
        i=0
        while i< len(ISIN):
            dic={}
            dic["ISIN"]=ISIN[i]
            dic["Issue Date"]=Issue_D[i]
            dic["Coupon"]=Coupon_P[i]
            dic["Maturity"]=Maturity[i]
            dic["Coupon Date"]=Coupon_D[i]
            temp.append(dic)
            i+=1
        return temp
    return data

def get_prices(start_date,end_date,INPUT):
    Price= []
    tkData=[]
    websites=[]
    url= get_urls()
    i=0
    link="https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData="
    date_cap="&from="+str(start_date)+"&to="+str(end_date)
    while i< len(url):
        response = requests.get(url[i])
        soup = BeautifulSoup(response.content, "html.parser")    
        f= soup.find_all('div', attrs={'class': 'responsivePosition'})
        f=str(f)
        f1=f[f.find('detailChartViewmodel'):f.find('}',f.find('detailChartViewmodel'))]
        f2=f1[f1.find("TKData")+11:f1.find("ChartData")-4]
        tkData.append(f2)
        website=link+tkData[i]+date_cap
        websites.append(website)
        i+=1
    i=0    
    while i< len(websites):
        response = requests.get(websites[i])
        soup = BeautifulSoup(response.content, "html.parser")
        strint=str(soup)
        str1= ast.literal_eval(strint)
        j=0
        dic={}
        while j<len(str1):
            a={}
            a=str1[j]
            dic[a["Date"][:-6]]=a["Close"]
            j+=1
        Price.append(dic)
        m=Price[i]
        df1=pd.DataFrame.from_dict(m,orient='index').T
        if i==0:
            df=pd.DataFrame.from_dict(m,orient='index').T
        else:
            df=df.append(df1)
        i+=1
    df.reset_index(drop=True, inplace=True)
    if INPUT=="file":
        return df
    else:
        return Price


def create_file():
    df1 = get_basic_data("file")
    df= get_prices(20220103,20220108)
    Bond_Data = df1.join(df,how='inner')
    file_name = "\Bond_Data_"+str(date.today())+".xlsx"
    Bond_Data.to_excel(r'C:\Users\dhire\Desktop'+file_name)
