'''
Author: guo_idpc
Date: 2023-02-24 15:03:18
LastEditors: guo_idpc 867718012@qq.com
LastEditTime: 2023-03-02 13:17:32
FilePath: /bilinear/main_model/model_load.py
Description: 人一生会遇到约2920万人,两个人相爱的概率是0.000049,所以你不爱我,我不怪你.

Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
'''
import pandas as pd
import csv
cer = 0.1
days=4
nn = 3
with_rlt = 1


def crf(year):
    i = 0.08
    crf=((1+i)**year)*i/((1+i)**year-1);
    return crf


# book_spr = xlrd.open_workbook('data/cspringdata.xlsx')
# book_sum = xlrd.open_workbook('data/csummerdata.xlsx')
# book_aut = xlrd.open_workbook('data/cautumndata.xlsx')
# book_win = xlrd.open_workbook('data/cwinterdata.xlsx')
# data_spr = book_spr.sheet_by_index(0)
# data_sum = book_sum.sheet_by_index(0)
# data_aut = book_aut.sheet_by_index(0)
# data_win = book_win.sheet_by_index(0)
ele_load = []
g_demand = []
q_demand = []
r_solar = []


#------------
cost_fc = 15504
cost_el = 9627.3
cost_hst = 3600
cost_eb = 434.21
cost_water_hot = 1
cost_pv = 900
cost_pump = 730
crf_fc = crf(10)
crf_el = crf(7)
crf_hst = crf(20)
crf_water = crf(20)
crf_pv = crf(20)
crf_pump = crf(20)
crf_eb = crf(15)

#--------------
lambda_ele_in = [0.3748,0.3748,0.3748,0.3748,0.3748,0.3748,0.3748,0.8745,0.8745,0.8745,1.4002,1.4002,1.4002,1.4002,
                1.4002,0.8745,0.8745,0.8745,1.4002,1.4002,1.4002,0.8745,0.8745,0.3748]
#lambda_ele_in = [lambda_ele_in[i]*1.5 for i in range(len(lambda_ele_in))]
lambda_ele_out = 0.1
#lambda_ele_in = lambda_ele_in*30

ele_load = []
g_demand = []
q_demand = []
r_solar = []

book_cold = pd.read_excel('./data/cold.xlsx')
book_heat = pd.read_excel('./data/heat.xlsx')
for l in range(8760):
    q_demand.append(book_cold.iloc[l,1])
    ele_load.append(4/3*book_cold.iloc[l,1])

# 热负荷从文章里面出
# for l in range(2904):
#     g_demand.append(3*book_heat.iloc[l,3])
# g_demand = g_demand[:1128]+[0 for _ in range(8760-2904)]+g_demand[1128:]
# 热负荷从榆林里面出，包括生活热水
book_water = pd.read_excel('./data/yulin_water_load.xlsx')
g_demand = list(book_water['供暖热负荷(kW)'].fillna(0))
water_load = list(book_water['生活热水负荷kW'].fillna(0))
# book_cold = xlrd.open_workbook('./data/cold.xlsx')
# book_heat = xlrd.open_workbook('./data/heat.xlsx')
# data_cold = book_cold.sheet_by_index(0)
# data_heat = book_heat.sheet_by_index(0)
# for l in range(1,8761):
#     q_demand.append(4*data_cold.cell(l,1).value)
#     ele_load.append(3/2*4*data_cold.cell(l,1).value)
# for l in range(1,2905):
#     g_demand.append(3*data_heat.cell(l,3).value)
# g_demand = g_demand[:1128]+[0 for _ in range(8760-2904)]+g_demand[1128:]
r_solar =  [0 for i in range(8760+24)]
with open("data/"+"solar.csv") as renewcsv:
    renewcsv.readline()
    renewcsv.readline()
    renewcsv.readline()
    renew = csv.DictReader(renewcsv)
    
    i=0
    for row in renew:

        r_solar[i] += float(row['electricity'])
        i+=1
r_solar = r_solar[-8:]+r_solar[:-8]



g_demand = [g_demand[i]/2 for i in range(len(ele_load))]
# g_demand = [1000 if g_demand[i] >=0 else 0 for i in range(len(ele_load))]
q_demand = [q_demand[i]/2 for i in range(len(ele_load))]
ele_load = [ele_load[i]/2 for i in range(len(ele_load))]
water_load = [water_load[i]/2 for i in range(len(ele_load))]




m_date = [31,28,31,30,31,30,31,31,30,31,30,31]
m_date = [sum(m_date[:i])*24 for i in range(12)]
m_date.append(8760)
# g_demand = [0 for i in range(8760)]
# for h in [1,2,3,11,12]:
#     g_demand[m_date[h-1]:m_date[h]] = [1 for _ in range(m_date[h]-m_date[h-1])]
r=r_solar
if days == 1:
    q_demand = q_demand[384+24:384+48]
    g_demand = g_demand[384+24:384+48]
    r_solar =   r_solar[384+24:384+48]
    ele_load = ele_load[384+24:384+48]
    #print(q_demand)
elif days == 4:
    q_demand = q_demand[384+24:384+48]+q_demand[2496+48:2496+72]+q_demand[4680+48:4680+72]+q_demand[6888:6888+24]
    g_demand = g_demand[384+24:384+48]+g_demand[2496+48:2496+72]+g_demand[4680+48:4680+72]+g_demand[6888:6888+24]
    r_solar =   r_solar[384+24:384+48]+ r_solar[2496+48:2496+72]+ r_solar[4680+48:4680+72]+ r_solar[6888:6888+24]
    ele_load = ele_load[384+24:384+48]+ele_load[2496+48:2496+72]+ele_load[4680+48:4680+72]+ele_load[6888:6888+24]
    water_load = water_load[384+24:384+48]+water_load[2496+48:2496+72]+water_load[4680+48:4680+72]+water_load[6888:6888+24]
elif days == 7:
    # 供热季的一天？
    q_demand = q_demand[24:8*24]
    g_demand = g_demand[24:8*24]
    r_solar =   r_solar[24:8*24]
    ele_load = ele_load[24:8*24]
elif days == 12:
    g_demand = g_demand[384+24:384+48]+g_demand[1080+24:1080+48]+g_demand[1752:1752+24]+g_demand[2496+48:2496+72]+g_demand[3216:3216+24]+g_demand[3960:3960+24]+g_demand[4680+48:4680+72]+g_demand[5424:5424+24]+g_demand[6168:6168+24]+g_demand[6888+24:6888+48]+g_demand[7632:7632+24]+g_demand[8352:8352+24]
    q_demand = q_demand[384+24:384+48]+q_demand[1080+24:1080+48]+q_demand[1752:1752+24]+q_demand[2496+48:2496+72]+q_demand[3216:3216+24]+q_demand[3960:3960+24]+q_demand[4680+48:4680+72]+q_demand[5424:5424+24]+q_demand[6168:6168+24]+q_demand[6888+24:6888+48]+q_demand[7632:7632+24]+q_demand[8352:8352+24]
    r_solar =   r_solar[384+24:384+48]+ r_solar[1080+24:1080+48]+ r_solar[1752:1752+24]+ r_solar[2496+48:2496+72]+ r_solar[3216:3216+24]+ r_solar[3960:3960+24]+ r_solar[4680+48:4680+72]+ r_solar[5424:5424+24]+ r_solar[6168:6168+24]+r_solar[6888+24:6888+48]+r_solar[7632:7632+24]+r_solar[8352:8352+24]
    ele_load = ele_load[384+24:384+48]+ele_load[1080+24:1080+48]+ele_load[1752:1752+24]+ele_load[2496+48:2496+72]+ele_load[3216:3216+24]+ele_load[3960:3960+24]+ele_load[4680+48:4680+72]+ele_load[5424:5424+24]+ele_load[6168:6168+24]+ele_load[6888+24:6888+48]+ele_load[7632:7632+24]+ele_load[8352:8352+24]
    water_load = water_load[384+24:384+48]+water_load[1080+24:1080+48]+water_load[1752:1752+24]+water_load[2496+48:2496+72]+water_load[3216:3216+24]+water_load[3960:3960+24]+water_load[4680+48:4680+72]+water_load[5424:5424+24]+water_load[6168:6168+24]+water_load[6888+24:6888+48]+water_load[7632:7632+24]+water_load[8352:8352+24]
elif days == 24:
    g_demand = g_demand[384+24:384+48]+g_demand[1080+24:1080+48]+g_demand[1752:1752+24]+g_demand[2496+48:2496+72]+g_demand[3216:3216+24]+g_demand[3960:3960+24]+g_demand[4680+48:4680+72]+g_demand[5424:5424+24]+g_demand[6168:6168+24]+g_demand[6888+24:6888+48]+g_demand[7632:7632+24]+g_demand[8352:8352+24]
    q_demand = q_demand[384+24:384+48]+q_demand[1080+24:1080+48]+q_demand[1752:1752+24]+q_demand[2496+48:2496+72]+q_demand[3216:3216+24]+q_demand[3960:3960+24]+q_demand[4680+48:4680+72]+q_demand[5424:5424+24]+q_demand[6168:6168+24]+q_demand[6888+24:6888+48]+q_demand[7632:7632+24]+q_demand[8352:8352+24]
    r_solar =   r_solar[384+24:384+48]+ r_solar[1080+24:1080+48]+ r_solar[1752:1752+24]+ r_solar[2496+48:2496+72]+ r_solar[3216:3216+24]+ r_solar[3960:3960+24]+ r_solar[4680+48:4680+72]+ r_solar[5424:5424+24]+ r_solar[6168:6168+24]+r_solar[6888+24:6888+48]+r_solar[7632:7632+24]+r_solar[8352:8352+24]
    ele_load = ele_load[384+24:384+48]+ele_load[1080+24:1080+48]+ele_load[1752:1752+24]+ele_load[2496+48:2496+72]+ele_load[3216:3216+24]+ele_load[3960:3960+24]+ele_load[4680+48:4680+72]+ele_load[5424:5424+24]+ele_load[6168:6168+24]+ele_load[6888+24:6888+48]+ele_load[7632:7632+24]+ele_load[8352:8352+24]

    g_demand = g_demand+g_demand
    q_demand = q_demand+q_demand
    r_solar = r_solar+r_solar
    ele_load = ele_load+ele_load
elif days == 36:
    g_demand = g_demand[384+24:384+48]+g_demand[1080+24:1080+48]+g_demand[1752:1752+24]+g_demand[2496+48:2496+72]+g_demand[3216:3216+24]+g_demand[3960:3960+24]+g_demand[4680+48:4680+72]+g_demand[5424:5424+24]+g_demand[6168:6168+24]+g_demand[6888+24:6888+48]+g_demand[7632:7632+24]+g_demand[8352:8352+24]
    q_demand = q_demand[384+24:384+48]+q_demand[1080+24:1080+48]+q_demand[1752:1752+24]+q_demand[2496+48:2496+72]+q_demand[3216:3216+24]+q_demand[3960:3960+24]+q_demand[4680+48:4680+72]+q_demand[5424:5424+24]+q_demand[6168:6168+24]+q_demand[6888+24:6888+48]+q_demand[7632:7632+24]+q_demand[8352:8352+24]
    r_solar =   r_solar[384+24:384+48]+ r_solar[1080+24:1080+48]+ r_solar[1752:1752+24]+ r_solar[2496+48:2496+72]+ r_solar[3216:3216+24]+ r_solar[3960:3960+24]+ r_solar[4680+48:4680+72]+ r_solar[5424:5424+24]+ r_solar[6168:6168+24]+r_solar[6888+24:6888+48]+r_solar[7632:7632+24]+r_solar[8352:8352+24]
    ele_load = ele_load[384+24:384+48]+ele_load[1080+24:1080+48]+ele_load[1752:1752+24]+ele_load[2496+48:2496+72]+ele_load[3216:3216+24]+ele_load[3960:3960+24]+ele_load[4680+48:4680+72]+ele_load[5424:5424+24]+ele_load[6168:6168+24]+ele_load[6888+24:6888+48]+ele_load[7632:7632+24]+ele_load[8352:8352+24]
    
    g_demand = g_demand+g_demand+g_demand
    q_demand = q_demand+q_demand+q_demand
    r_solar = r_solar+r_solar+r_solar
    ele_load = ele_load+ele_load+ele_load

elif days == 365:
    1
# import matplotlib.pyplot as plt
# # print(g_demand)
# # print(q_demand)
# x = [i for i in range(0,24*days)]
# plt.plot(x,g_demand)
# plt.plot(x,q_demand)
# plt.plot(x,water_load)
# plt.plot(x,ele_load)
# plt.show()
# plt.savefig('img/g_de.png')
# exit(0)

#g_de = g_de_w*days
#p_load = p_load_winter*days
lambda_ele_in = lambda_ele_in*days
#r = r*days
# m_de = [g_de[i]/c_kWh/delta_T for i in range(len(g_de))]
period = len(g_demand)
