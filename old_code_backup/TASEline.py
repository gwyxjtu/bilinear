#!/usr/bin/env python3.7

# Copyright 2021, Gurobi Optimization, LLC

# This example formulates and solves the following simple bilinear model:
#  maximize    x
#  subject to  x + y + z <= 10
#              x * y <= 2         (bilinear inequality)
#              x * z + y * z = 1  (bilinear equality)
#              x, y, z non-negative (x integral in second version)

import gurobipy as gp
from gurobipy import GRB
import numpy as np
import xlwt
import random
import xlrd
import csv
from RLT.RLT import *
import numpy as np

def crf(year):
    i = 0.08
    crf=((1+i)**year)*i/((1+i)**year-1)
    return crf


cer = 0.5
days=12
nn =1
with_rlt = 0

# book_spr = xlrd.open_workbook('cspringdata.xlsx')
# book_sum = xlrd.open_workbook('csummerdata.xlsx')
# book_aut = xlrd.open_workbook('cautumndata.xlsx')
# book_win = xlrd.open_workbook('cwinterdata.xlsx')
# data_spr = book_spr.sheet_by_index(0)
# data_sum = book_sum.sheet_by_index(0)
# data_aut = book_aut.sheet_by_index(0)
# data_win = book_win.sheet_by_index(0)
ele_load = []
g_demand = []
q_demand = []
m_demand = []
r_solar = []


# g_de = [g_demand[i]*3 for i in range(len(ele_load))]
# r=r_solar
# p_load = [ele_load[i]+q_demand[i] for i in range(len(ele_load))]

##########################################
#预处理，方差变大
# n_g_demand = []
# for i in range(days):
#     tmp=[]
#     g_average = np.mean(g_de[i*24:i*24+24])
#     for j in range(24):
#         tmp.append(max(g_average/5,g_average+(g_de[i*24+j]-g_average)))
#     n_g_demand+=tmp
# import matplotlib.pyplot as plt
# x = [i for i in range(24)]
# plt.plot(x,g_de[:24])
# plt.plot(x,p_load[:24])
# #plt.plot(x,q_demand[:24])
# # x = [i for i in range(len(g_de))]
# # plt.plot(x,g_de)
# # plt.plot(x,ele_load)
# # plt.plot(x,q_demand)

# plt.show()
# exit(0)

c = 4200 # J/kg*C
c_kWh = 4200/3.6/1000000
delta_T = 12
k_pv = 0.16
lambda_h = 20
#------------
cost_fc = 15504
cost_el = 9627.3
cost_hst = 3600
cost_water_hot = 1
cost_pv = 1000
cost_pump = 730
#cost_eb = 434.21
crf_fc = crf(10)
crf_el = crf(7)
crf_hst = crf(20)
crf_water = crf(20)
crf_pv = crf(20)
crf_pump = crf(20)
#crf_eb = crf(15)
k_fc = 18
k_el = 0.022
k_el_1 = 46
k_co = 1.05
k_pv = 0.16
k_ct = 0.04#冷却塔能效等级，三级的耗电比为0.04
#--------------
lambda_ele_in = [0.3748,0.3748,0.3748,0.3748,0.3748,0.3748,0.3748,0.8745,0.8745,0.8745,1.4002,1.4002,1.4002,1.4002,
                 1.4002,0.8745,0.8745,0.8745,1.4002,1.4002,1.4002,0.8745,0.8745,0.3748]*days
#lambda_ele_in = [lambda_ele_in[i]*1.5 for i in range(len(lambda_ele_in))]
lambda_ele_out = 0.3
lambda_g_out = 0.16
#lambda_ele_in = lambda_ele_in*30

# r = [0,0,0,0,0,0,0.01,0.13,0.3,0.4,0.58,0.66,0.67,0.6,0.51,0.36,0.21,0.05,0,0,0,0,0,0]
# g_de = [50]*6 + [80, 150, 290, 250, 200, 80, 60, 150, 180, 220, 360, 480, 550, 420, 320, 280, 180, 110]
# p_load = [30]*6+ [80, 150, 290, 250, 200, 80, 60, 150, 180, 220, 360, 480, 550, 420, 320, 280, 180, 110]
# p_load = [p_load[i]/2 for i in range(len(g_de))]

# # winter
# r_winter = [0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.08,0.19,0.32,0.38,0.40,0.38,0.29,0.17,0.05,0.00,0.00,0.00,0.00,0.00,0.00,0.00]

# p_load_winter = [3,3,3,3,3,3,3,3,90.519,81.874,81.874,81.874,20.582,20.582,50.874,90.519,90.519,90.519,90.519,50,20,3,3,3]
# #p_load_winter = [p_load_winter[i]*4.5 for i in range(len(p_load_winter))]

# g_de_w = [0,0,0,0,0,10,20,156,276.2168321,223.8311127,117.1357871,88.44233614,86.27409099,46.22150325,30.472339355,20,70.078162837,240.01461735,158.06297006,100,80,20,
#     0,0]


# r = r_winter

# g_de = g_de_w*days
# p_load = p_load_winter*days
# lambda_ele_in = lambda_ele_in*days
# r = r*days
ele_load = []
g_demand = []
q_demand = []
r_solar = []

book_cold = xlrd.open_workbook('./data/cold.xlsx')
book_heat = xlrd.open_workbook('./data/heat.xlsx')
data_cold = book_cold.sheet_by_index(0)
data_heat = book_heat.sheet_by_index(0)
for l in range(1,8761):
    q_demand.append(4*data_cold.cell(l,1).value)
    ele_load.append(3/2*4*data_cold.cell(l,1).value)
for l in range(1,2905):
    g_demand.append(3*data_heat.cell(l,3).value)
g_demand = g_demand[:1128]+[0 for _ in range(8760-2904)]+g_demand[1128:]
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
#g_de = [g_demand[i]*3 for i in range(len(ele_load))]
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

elif days == 7:
    q_demand = q_demand[24:8*24]
    g_demand = g_demand[24:8*24]
    r_solar =   r_solar[24:8*24]
    ele_load = ele_load[24:8*24]
elif days == 12:
    g_demand = g_demand[384+24:384+48]+g_demand[1080+24:1080+48]+g_demand[1752:1752+24]+g_demand[2496+48:2496+72]+g_demand[3216:3216+24]+g_demand[3960:3960+24]+g_demand[4680+48:4680+72]+g_demand[5424:5424+24]+g_demand[6168:6168+24]+g_demand[6888+24:6888+48]+g_demand[7632:7632+24]+g_demand[8352:8352+24]
    q_demand = q_demand[384+24:384+48]+q_demand[1080+24:1080+48]+q_demand[1752:1752+24]+q_demand[2496+48:2496+72]+q_demand[3216:3216+24]+q_demand[3960:3960+24]+q_demand[4680+48:4680+72]+q_demand[5424:5424+24]+q_demand[6168:6168+24]+q_demand[6888+24:6888+48]+q_demand[7632:7632+24]+q_demand[8352:8352+24]
    r_solar =   r_solar[384+24:384+48]+ r_solar[1080+24:1080+48]+ r_solar[1752:1752+24]+ r_solar[2496+48:2496+72]+ r_solar[3216:3216+24]+ r_solar[3960:3960+24]+ r_solar[4680+48:4680+72]+ r_solar[5424:5424+24]+ r_solar[6168:6168+24]+r_solar[6888+24:6888+48]+r_solar[7632:7632+24]+r_solar[8352:8352+24]
    ele_load = ele_load[384+24:384+48]+ele_load[1080+24:1080+48]+ele_load[1752:1752+24]+ele_load[2496+48:2496+72]+ele_load[3216:3216+24]+ele_load[3960:3960+24]+ele_load[4680+48:4680+72]+ele_load[5424:5424+24]+ele_load[6168:6168+24]+ele_load[6888+24:6888+48]+ele_load[7632:7632+24]+ele_load[8352:8352+24]
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
#print(g_demand)
# import matplotlib.pyplot as plt
# x = [i for i in range(len(g_demand))]
# plt.plot(x,g_demand)
# plt.plot(x,ele_load)
# plt.plot(x,q_demand)
# plt.show()
# exit(0)
#m_de = [g_de[i]/c_kWh/delta_T for i in range(len(g_de))]

#g_demand =  [g_demand[i]+2000 for i in range(len(ele_load))]
#p_load = [ele_load[i]+q_demand[i] for i in range(len(ele_load))]
#print(q_demand)
#print(111)
def opt(M,T,error,fix,res_M_T,H):
    m_ht_1,m_ht_2   = M["m_ht"][0], M["m_ht"][1]
    m_fc_1,m_fc_2   = M["m_fc"][0], M["m_fc"][1]
    m_cdu_1,m_cdu_2 = M["m_cdu"][0], M["m_cdu"][1]
    m_he_1,m_he_2   = M["m_he"][0], M["m_he"][1]
    t_ht_1,t_ht_2   = T['t_ht'][0] ,T['t_ht'][1]
    t_fc_1,t_fc_2   = T['t_fc'][0] ,T['t_fc'][1]
    t_cdu_1,t_cdu_2 = T['t_cdu'][0],T['t_cdu'][1]
    t_he_1,t_he_2   = T['t_he'][0] ,T['t_he'][1]
    period = len(g_demand)
    print(period)
    #period = 24
    # Create a new model
    m = gp.Model("bilinear")

    H_ht_ht    = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_ht_ht{t}") for t in range(period)]
    H_fc_fc    = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_fc_fc{t}") for t in range(period)]
    H_fc_ht    = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_fc_ht{t}") for t in range(period)]
    H_fc_cdu   = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_fc_cdu{t}") for t in range(period)]
    H_cdu_cdu  = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_cdu_cdu{t}") for t in range(period)]
    H_cdu_ht   = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_cdu_ht{t}") for t in range(period)]
    H_he_he    = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_he_he{t}") for t in range(period)]
    H_he_cdu   = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_he_cdu{t}") for t in range(period)]
    H_ct_cdu   = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_ct_cdu{t}") for t in range(period)]
    H_ct_ct    = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_ct_ct{t}") for t in range(period)]


    g_sol = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_sol{t}") for t in range(period)]
    z_fc  = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_fc{t}") for t in range(period)]
    z_ct  = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_ct{t}") for t in range(period)]
    z_he  = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_he{t}") for t in range(period)]
    z_idc = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_idc{t}") for t in range(period)]

    ce_h = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="ce_h")
    capex = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="capex")
    opex = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="opex")
    #m_wwt = m.addVar(vtype=GRB.CONTINUOUS, lb=10,ub=1000000, name="m_wwt")
    m_ht = m.addVar(vtype=GRB.CONTINUOUS, lb=10,ub=1000000, name="m_ht") # capacity of hot water tank
    
    #t_wwt = [m.addVar(vtype=GRB.CONTINUOUS, lb=20,ub=85, name=f"t_wwt{t}") for t in range(period)] # temperature of hot water tank
    t_ht = [m.addVar(vtype=GRB.CONTINUOUS, lb=30,ub=90, name=f"t_ht{t}") for t in range(period)] # temperature of hot water tank
    t_idc = [m.addVar(vtype=GRB.CONTINUOUS, lb=30,ub=90, name=f"t_idc{t}") for t in range(period)] 
    t_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"t_fc{t}") for t in range(period)] # outlet temperature of fuel cells cooling circuits
    t_ct = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"t_ct{t}") for t in range(period)] 
    g_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_fc{t}") for t in range(period)] # heat generated by fuel cells

    p_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_fc{t}") for t in range(period)]

    p_ct = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_ct{t}") for t in range(period)]
    q_ct = [m.addVar(vtype=GRB.CONTINUOUS, lb=0,ub=3500, name=f"q_ct{t}") for t in range(period)]

    #p_eb = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_eb{t}") for t in range(period)]

    fc_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="fc_max") # rated heat power of fuel cells

    pump_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="pump_max")

    p_eb_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="p_eb_max")

    idcpump_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="p_eb_max")

    el_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="el_max") # rated heat power of fuel cells

    t_de = [m.addVar(vtype=GRB.CONTINUOUS, lb=0,name=f"t_de{t}") for t in range(period)] # outlet temparature of heat supply circuits
    t_cdu = [m.addVar(vtype=GRB.CONTINUOUS, lb=0,name=f"t_cdu{t}") for t in range(period)]
    t_he = [m.addVar(vtype=GRB.CONTINUOUS, lb=0,ub = 100,name=f"t_he{t}") for t in range(period)]
    h_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_fc{t}") for t in range(period)] # hydrogen used in fuel cells

    m_fc  = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_fc") # fuel cells water
    m_ct  = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_ct")
    m_he  = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_he")
    m_idc = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_idc")
    m_cdu = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_cdu")
    #m_cdu = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_cdu{t}") for t in range(period)]
    m_de = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_de{t}") for t in range(period)]
    g_he = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_he{t}") for t in range(period)]

    #g_eb = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_eb{t}") for t in range(period)]

    #g_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_el{t}") for t in range(period)] # heat generated by Electrolyzer

    h_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_el{t}") for t in range(period)] # hydrogen generated by electrolyzer

    p_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_el{t}") for t in range(period)] # power consumption by electrolyzer

    #t_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"t_el{t}") for t in range(period)] # outlet temperature of electrolyzer cooling circuits

    h_sto = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_sto{t}") for t in range(period)] # hydrogen storage

    h_pur = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_pur{t}") for t in range(period)] # hydrogen purchase

    p_pur = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pur{t}") for t in range(period)] # power purchase

    p_sol = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_sol{t}") for t in range(period)] # power purchase

    area_pv = m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub = 12000, name=f"area_pv")

    p_pump = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pump{t}") for t in range(period)] 
    p_idcpump = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_idcpump{t}") for t in range(period)] 

    hst = m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub = 200000, name=f"hst")

    p_co = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_co{t}") for t in range(period)] 
    for i in range(int(period/24)-1):
        m.addConstr(t_ht[i*24+24] == t_ht[24*i])
    # m.addConstr(t_ht[-1] == t_ht[0])
    # m.addConstr(h_sto[-1] == h_sto[0])


    for i in range(period - 1):
        ###m.addConstr(m_ht * (t_ht[i + 1] - t_ht[i]) == m_fc * (t_cdu[i] - t_ht[i]) + m_cdu * (t_cdu[i] - t_ht[i]) - q_ct[i]/c_kWh- g_sol[i]/c_kWh )
        m.addConstr(H_ht_ht[i+1]-H_ht_ht[i] == H_fc_cdu[i] - H_fc_ht[i]+H_cdu_cdu[i] - H_cdu_ht[i]-q_ct[i]/c_kWh- g_sol[i]/c_kWh)        
        m.addConstr(h_sto[i+1] - h_sto[i] == h_pur[i] + h_el[i] - h_fc[i])
        
    #m.addConstr(m_ht * (t_ht[0] - t_ht[-1]) == m_fc * (t_cdu[-1] - t_ht[-1]) + m_cdu * (t_cdu[-1] - t_ht[-1]) - q_ct[-1]/c_kWh- g_sol[-1]/c_kWh)
    m.addConstr(H_ht_ht[0]-H_ht_ht[-1] == H_fc_cdu[-1] - H_fc_ht[-1]+H_cdu_cdu[-1] - H_cdu_ht[-1]-q_ct[-1]/c_kWh- g_sol[-1]/c_kWh)
    #m.addConstr(m_wwt * (t_wwt[0] - t_wwt[i]) == m_cdu* (t_cdu[i] - t_wwt[i]) - q_ct[i]/c_kWh + m_he * (t_he[i] - t_cdu[i]))
    #m.addConstr(m_ht * (t_ht[0] - t_ht[i]) == m_fc * (t_fc[i] - t_ht[i]) + g_eb[i]/c_kWh + m_el * (t_el[i] - t_ht[i]) - m_de[i] * (t_ht[i] - t_de[i]))

    m.addConstr(h_sto[0] - h_sto[-1] == h_pur[-1] + h_el[-1] - h_fc[-1])
    #m.addConstr(t_ht[0] == 60)
    piece_count=0
    slack_num=0
    #piece_McCormick(model,H,x,y,x1,x2,y1,y2,piece_count,error,i_number,H_name,n)
    if fix == 0:
        for i in range(period):
            #print(H_fc_fc[i],m_fc,t_fc[i],m_fc_1,m_fc_2,t_fc_1[i],t_fc_2[i])
            m,piece_count,int_tmp = piece_McCormick(m,H_fc_fc[i],m_fc,t_fc[i],m_fc_1,m_fc_2,t_fc_1[i],t_fc_2[i],piece_count,error,i,"H_fc_fc",nn)
            slack_num+=int_tmp
            #print(i%24)
            #if i%24!=0 or i==0:
            m,piece_count,int_tmp = piece_McCormick(m,H_fc_ht[i],m_fc,t_ht[i],m_fc_1,m_fc_2,t_ht_1[i],t_ht_2[i],  piece_count,error,i, "H_fc_ht",  nn)
            slack_num+=int_tmp  
            m,piece_count,int_tmp = piece_McCormick(m,H_ht_ht[i],m_ht,t_ht[i],m_ht_1,m_ht_2,t_ht_1[i],t_ht_2[i],  piece_count,error,i, "H_ht_ht",  nn)
            slack_num+=int_tmp  
            m,piece_count,int_tmp = piece_McCormick(m,H_fc_cdu[i],m_fc,t_cdu[i],m_fc_1,m_fc_2,t_cdu_1[i],t_cdu_2[i], piece_count,error,i, "H_fc_cdu", nn)
            slack_num+=int_tmp
            m,piece_count,int_tmp = piece_McCormick(m,H_cdu_cdu[i],m_cdu,t_cdu[i],m_cdu_1,m_cdu_2,t_cdu_1[i],t_cdu_2[i],piece_count,error,i, "H_cdu_cdu", nn)
            slack_num+=int_tmp
            m,piece_count,int_tmp = piece_McCormick(m,H_cdu_ht[i],m_cdu,t_ht[i],m_cdu_1,m_cdu_2,t_ht_1[i],t_ht_2[i], piece_count,error,i,"H_cdu_ht",  nn)
            slack_num+=int_tmp
            m,piece_count,int_tmp = piece_McCormick(m,H_he_he[i],m_he,t_he[i],m_he_1,m_he_2,t_he_1[i],t_he_2[i],  piece_count,error,i,"H_he_he",   nn)
            slack_num+=int_tmp
            m,piece_count,int_tmp = piece_McCormick(m,H_he_cdu[i],m_he,t_cdu[i],m_he_1,m_he_2,t_cdu_1[i],t_cdu_2[i], piece_count,error,i,"H_he_cdu",  nn)
            slack_num+=int_tmp
            m,piece_count,int_tmp = piece_McCormick(m,H_ct_cdu[i],m_ct,t_cdu[i],m_ct_1,m_ct_2,t_cdu_1[i],t_cdu_2[i], piece_count,error,i, "H_ct_cdu", nn)
            slack_num+=int_tmp
            m,piece_count,int_tmp = piece_McCormick(m,H_ct_ct[i],m_ct,t_ct[i],m_ct_1,m_ct_2,t_ct_1[i],t_ct_2[i],  piece_count,error,i, "H_ct_ct",  nn)
            slack_num+=int_tmp
        #print(piece_count)
    if fix == 1:
        m.addConstr(m_cdu == res_M_T['m_cdu'])
        m.addConstr(m_he == res_M_T['m_he'])
        m.addConstr(m_fc == res_M_T['m_fc'])
        m.addConstr(m_ht == res_M_T['m_ht'])
        m.addConstr(m_ct == res_M_T['m_ct'])
        for i in range(period):
            #print(H_fc_fc[i],m_fc,t_fc[i],m_fc_1,m_fc_2,t_fc_1[i],t_fc_2[i])
            #m,piece_count,int_tmp = piece_McCormick(m,H_fc_fc[i],m_fc,t_fc[i],m_fc_1,m_fc_2,t_fc_1[i],t_fc_2[i],piece_count,error,i,"H_fc_fc",nn)
            #slack_num+=int_tmp
            m.addConstr(H_ht_ht[i] ==  H['H_ht_ht'][i])
            m.addConstr(H_fc_fc[i] ==  H['H_fc_fc'][i])
            m.addConstr(H_fc_ht[i] ==  H['H_fc_ht'][i])
            m.addConstr(H_fc_cdu[i] == H['H_fc_cdu'][i])
            m.addConstr(H_cdu_cdu[i] == H['H_cdu_cdu'][i])
            m.addConstr(H_cdu_ht[i] == H['H_cdu_ht'][i])
            m.addConstr(H_he_he[i] ==  H['H_he_he'][i])
            m.addConstr(H_he_cdu[i] == H['H_he_cdu'][i])
            m.addConstr(H_ct_cdu[i] == H['H_ct_cdu'][i])
            m.addConstr(H_ct_ct[i] ==  H['H_ct_ct'][i])

            m.addConstr(t_ht[i] == H['H_ht_ht'][i]/res_M_T['m_ht'])
            m.addConstr(t_cdu[i] == H['H_cdu_cdu'][i]/res_M_T['m_cdu'])
            m.addConstr(t_he[i] == H['H_he_he'][i]/res_M_T['m_he'])
            m.addConstr(t_fc[i] == H['H_fc_fc'][i]/res_M_T['m_fc'])
            m.addConstr(t_ct[i] == H['H_ct_ct'][i]/res_M_T['m_ct'])

    m.addConstr(gp.quicksum(p_pur)<=cer*(sum(ele_load)+sum(q_demand)*0.04))
    for i in range(period):
        #m.addConstr(p_pur[i]==0)

        m.addConstr(1000000*z_fc[i]>=g_fc[i])
        m.addConstr(1000000*z_fc[i]>=p_fc[i])
        m.addConstr(1000000*z_ct[i]>=p_ct[i])
        m.addConstr(1000000*z_he[i]>=g_sol[i])
        m.addConstr(g_demand[i]>=g_sol[i])

        
        m.addConstr(p_co[i] + p_el[i] + p_sol[i] + p_pump[i] +p_ct[i] + ele_load[i] == p_pur[i] + p_fc[i] + k_pv*area_pv*r[i])
        m.addConstr(g_fc[i] <= 0.9 * 18 * h_fc[i])

        ###m.addConstr(g_sol[i] == c_kWh * m_he * (t_cdu[i] - t_he[i]))
        m.addConstr(g_sol[i] <= c_kWh * (H_he_cdu[i] - H_he_he[i]))
        ###m.addConstr(q_ct[i] == c_kWh * m_ct * (t_cdu[i] - t_ct[i]))
        m.addConstr(q_ct[i] == z_ct[i]*c_kWh * (H_ct_cdu[i] - H_ct_ct[i]))
        m.addConstr(p_ct[i] >= 0.04 * q_ct[i])
        #m.addConstr(0.95*g_he[i] == c_kWh * m_idc * (t_idc[i] - t_ht[i]))
        #m.addConstr(p_idcpump[i] == 0.6/1000 * (m_ct*z_ct[i]+m_he*z_he[i]))
        m.addConstr(p_pump[i] == 0.6/1000 * (m_cdu+m_he*z_he[i]+m_ct*z_ct[i]+m_fc*z_fc[i]))
        m.addConstr(p_co[i] == k_co * h_el[i])
        m.addConstr(p_fc[i] == 18 * h_fc[i])#氢燃烧产电
        m.addConstr(h_el[i] == k_el * p_el[i])
        #m.addConstr(g_el[i] == 0.2017*p_el[i])
        ###m.addConstr(g_fc[i] == c_kWh * m_fc * (t_fc[i] - t_ht[i]))
        m.addConstr(g_fc[i] == c_kWh *(H_fc_fc[i] - H_fc_ht[i]))

        m.addConstr(m_cdu>=m_he*z_he[i])###
        #m.addConstr(t_el[i] <= 80)
        #m.addConstr(z_fc[i]+z_el[i]<=1)
        m.addConstr(h_sto[i]<=hst)
        m.addConstr(h_el[i]<=hst)
        #m.addConstr(t_ht[i] >= 50)
        

        #m.addConstr(g_demand[i] == c_kWh * m_de[i] * (t_ht[i] - t_de[i]))  
        ###m.addConstr(q_demand[i] == c_kWh * m_cdu * (t_cdu[i] - t_ht[i])-g_fc[i])
        m.addConstr(q_demand[i] == c_kWh *(H_cdu_cdu[i] - H_cdu_ht[i])-g_fc[i])
        
        

        m.addConstr(p_fc[i] <= fc_max)
        m.addConstr(p_pump[i]<=pump_max)
        #m.addConstr(p_idcpump[i]<=idcpump_max)
        #m.addConstr(p_eb[i]<=p_eb_max)
        m.addConstr(p_el[i] <= el_max)
        m.addConstr(t_fc[i] <=65)###
        m.addConstr(t_ht[i] <=65)###
        m.addConstr(t_ht[i] >=30)###
        m.addConstr(t_he[i] >= 30)###
        m.addConstr(t_ct[i] >=26.4)###
        m.addConstr(t_cdu[i]<=95)###
        if with_rlt == 1:
            m.addConstr(H_fc_fc[i]<=65*m_fc)

            m.addConstr(H_ht_ht[i]<=65*m_ht)
            m.addConstr(H_cdu_ht[i]<=65*m_cdu)
            m.addConstr(H_ht_ht[i]>=30*m_ht)
            m.addConstr(H_cdu_ht[i]>=30*m_cdu)

            m.addConstr(H_he_he[i]>=30*m_he)

            m.addConstr(H_ct_ct[i]>=26.4*m_ct)

            m.addConstr(H_fc_cdu[i]<=95*m_fc)
            m.addConstr(H_cdu_cdu[i]<=95*m_cdu)
            m.addConstr(H_he_cdu[i]<=95*m_he)
            m.addConstr(H_ct_cdu[i]<=95*m_ct)



            m.addConstr(H_ht_ht[i]>=5*H_cdu_ht[i])
    
    if with_rlt == 1:
        for i in range(int(period/24)-1):
            m.addConstr(H_ht_ht[i*24+24] == H_ht_ht[24*i])
            m.addConstr(H_fc_ht[i*24+24] == H_fc_ht[24*i])
            m.addConstr(H_cdu_ht[i*24+24] == H_cdu_ht[24*i])
        # m.addConstr(H_ht_ht[-1] == H_ht_ht[0])
        # m.addConstr(H_fc_ht[-1] == H_fc_ht[0])
        # m.addConstr(H_cdu_ht[-1] == H_cdu_ht[0])

    m.addConstr(m_ht>=5*m_cdu)###
    #m.addConstr(h_sto[-1] == h_sto[0])

    # m.setObjective( crf_pv * cost_pv*area_pv+ crf_el*cost_el*el_max
    #     +crf_hst * hst*cost_hst +crf_water* cost_water_hot*m_ht + crf_fc *cost_fc * fc_max + lambda_h*gp.quicksum(h_pur)*365+ 
    #     365*gp.quicksum([p_pur[i]*lambda_ele_in[i] for i in range(24)])-365*gp.quicksum(p_sol)*lambda_ele_out , GRB.MINIMIZE)
    m.setObjective( crf_pv * cost_pv*area_pv+ crf_el*cost_el*el_max
        +crf_hst * hst*cost_hst +crf_water* cost_water_hot*m_ht+ cost_pump*pump_max*crf_pump+crf_fc *cost_fc * fc_max + lambda_h*gp.quicksum(h_pur)*365/days+ 
        gp.quicksum([p_pur[i]*lambda_ele_in[i] for i in range(period)])*365/days-gp.quicksum(p_sol)*lambda_ele_out*365/days-gp.quicksum(g_sol)*lambda_g_out*365/days, GRB.MINIMIZE)
    m.addConstr(capex == cost_pv*area_pv+ cost_el*el_max
        +hst*cost_hst +cost_water_hot*m_ht+ cost_pump*pump_max+cost_fc * fc_max)
    m.addConstr(opex ==  lambda_h*gp.quicksum(h_pur)*365/days+ 
        gp.quicksum([p_pur[i]*lambda_ele_in[i] for i in range(period)])*365/days-gp.quicksum(p_sol)*lambda_ele_out*365/days-gp.quicksum(g_sol)*lambda_g_out*365/days)
    #-gp.quicksum(p_sol)*lambda_ele_out 
    # First optimize() call will fail - need to set NonConvex to 2
    m.params.NonConvex = 1
    m.params.MIPGap = 0.05
    if nn != 1:
        m.params.MIPGap = 0.05
    # m.optimize()
    #m.computeIIS()
    try:
        m.optimize()
        #m.computeIIS()
        #m.write('model.ilp')
    except gp.GurobiError:
        print("Optimize failed due to non-convexity")
    if m.status == GRB.INFEASIBLE or m.status == 4:
        print('Model is infeasible')
        m.computeIIS()
        m.write('model.ilp')
        print("Irreducible inconsistent subsystem is written to file 'model.ilp'")
        return 1,1,1,1,1,1,10000000
    ans = {'objective':m.objVal,

            #'m_wwt':m_wwt.X,
            "capex":capex.x,
            "opex":opex.x,
            
            'fc_max':fc_max.X,
            'el_max':el_max.X,
            #'p_eb_max':p_eb_max.X,
            'area_pv':area_pv.X,
            'idcpump_max':idcpump_max.X,
            'pump_max':pump_max.X,

            "cer":sum([p_pur[i].X for i in range(period)])/(sum(ele_load)+sum(q_demand)*0.04),
            'p_pv':[k_pv*area_pv.X*r[i] for i in range(period)],
            'p_load':ele_load,
            'p_el':[p_el[i].X for i in range(period)],
            'p_fc':[p_fc[i].X for i in range(period)],
            'p_pur':[p_pur[i].X for i in range(period)],
            'p_pump':[p_pump[i].X for i in range(period)],
            'p_sol':[p_sol[i].X for i in range(period)],
            #'p_eb':[p_eb[i].X for i in range(period)],
            'p_ct':[p_ct[i].X for i in range(period)],
            #'p_idcpump':[p_idcpump[i].X for i in range(period)],
            'g_load':g_demand,
            'q_load':q_demand,
            'q_ct':[q_ct[i].X for i in range(period)],
            'g_fc':[g_fc[i].X for i in range(period)],
            'g_sol':[g_sol[i].X for i in range(period)],
            'z_fc':[z_fc[i].X for i in range(period)],
            #'g_he':[g_he[i].X for i in range(period)],
            'g_idc':[c_kWh * m_idc.X  * (t_idc[i].X  - t_ht[i].X )for i in range(period)],
            'z_ct':[z_ct[i].X for i in range(period)],
            'z_he':[z_he[i].X for i in range(period)],
            'z_idc':[z_idc[i].X for i in range(period)],

            't_ht':[t_ht[i].X for i in range(period)],
            #'t_wwt':[t_wwt[i].X for i in range(period)],
            't_ct':[t_ct[i].X for i in range(period)],
            't_cdu':[t_cdu[i].X for i in range(period)],
            't_he':[t_he[i].X for i in range(period)],
            't_fc':[t_fc[i].X for i in range(period)],
            't_de':[t_de[i].X for i in range(period)],
            'm_ct':m_ct.x,

            #'m_cdu':[m_cdu[i].X for i in range(period)],
            'm_cdu':m_cdu.x,
            'm_he':m_he.x,
            'm_fc':m_fc.x,
            'm_ht':m_ht.x,
            'h_el':[h_el[i].X for i in range(period)],
            'h_fc':[h_fc[i].X for i in range(period)],
            'h_sto':[h_sto[i].X for i in range(period)],
            'h_pur':[h_pur[i].X for i in range(period)]
            }
    H = {'H_ht_ht'  :m.getAttr('x', H_ht_ht),
         'H_fc_fc'  :m.getAttr('x', H_fc_fc),
         'H_fc_ht'  :m.getAttr('x', H_fc_ht),
         'H_fc_cdu' :m.getAttr('x', H_fc_cdu),
         'H_cdu_ht' :m.getAttr('x', H_cdu_ht),
         'H_cdu_cdu':m.getAttr('x', H_cdu_cdu),
         'H_he_he'  :m.getAttr('x', H_he_he),
         'H_he_cdu' :m.getAttr('x', H_he_cdu),
         "H_ct_cdu" :m.getAttr('x', H_ct_cdu),
         "H_ct_ct"  :m.getAttr('x', H_ct_ct),
        }
    M = {
        "m_ht"   :[m_ht_1,m_ht_2],
        "m_fc"   :[m_fc_1,m_fc_2],
        "m_cdu"  :[m_cdu_1,m_cdu_2],
        "m_he"   :[m_he_1,m_he_2],
        "m_ct"   :[m_ct_1,m_ct_2]
    }
    T = {
        "t_ht"   :[t_ht_1,t_ht_2],
        "t_fc"   :[t_fc_1,t_fc_2],
        "t_cdu"  :[t_cdu_1,t_cdu_2],
        "t_he"   :[t_he_1,t_he_2],
        "t_ct"   :[t_ct_1,t_ct_2]
    }
    res_M_T = {
        'm_cdu':m_cdu.x,
        'm_he':m_he.x,
        'm_fc':m_fc.x,
        'm_ht':m_ht.x,
        'm_ct':m_ct.x,
        't_ht':[t_ht[i].X for i in range(period)],
        't_cdu':[t_cdu[i].X for i in range(period)],
        't_he':[t_he[i].X for i in range(period)],
        't_fc':[t_fc[i].X for i in range(period)],
        't_ct':[t_ct[i].X for i in range(period)]
    }
    error = {
        "H_ht_ht"   : [(H_ht_ht[i].X-m_ht.X*t_ht[i].X)/    (m_ht.X*t_ht[i].X  +0.001)  for i in range(period)],
        "H_fc_fc"   : [(H_fc_fc[i].X-m_fc.X*t_fc[i].X)/    (m_fc.X*t_fc[i].X  +0.001)  for i in range(period)],
        "H_fc_ht"   : [(H_fc_ht[i].X-m_fc.X*t_ht[i].X)/    (m_fc.X*t_ht[i].X  +0.001)  for i in range(period)],
        "H_fc_cdu"  : [(H_fc_cdu[i].X-m_fc.X*t_cdu[i].X)/  (m_fc.X*t_cdu[i].X +0.001)  for i in range(period)],
        "H_cdu_cdu" : [(H_cdu_cdu[i].X-m_cdu.X*t_cdu[i].X)/(m_cdu.X*t_cdu[i].X+0.001)  for i in range(period)],
        "H_cdu_ht"  : [(H_cdu_ht[i].X-m_cdu.X*t_ht[i].X)/  (m_cdu.X*t_ht[i].X +0.001)  for i in range(period)],
        "H_he_he"   : [(H_he_he[i].X-m_he.X*t_he[i].X)/    (m_he.X*t_he[i].X  +0.001)  for i in range(period)],
        "H_he_cdu"  : [(H_he_cdu[i].X-m_he.X*t_cdu[i].X)/  (m_he.X*t_cdu[i].X +0.001)  for i in range(period)],
        "H_ct_cdu"  : [(H_ct_cdu[i].X-m_ct.X*t_cdu[i].X)/  (m_ct.X*t_cdu[i].X  +0.001)  for i in range(period)],
        "H_ct_ct"   : [(H_ct_ct[i].X-m_ct.X*t_ct[i].X)/    (m_ct.X*t_ct[i].X +0.001)  for i in range(period)],
    }
    return M,T,res_M_T,H,error,ans,slack_num
# Solve bilinear model
# m.params.NonConvex = 2
# m.optimize()

#m.printAttr('x')
# Constrain 'x' to be integral and solve again
# x.vType = GRB.INTEGER
# m.optimize()


# if __name__ == '__main__':
#     res = opt()
#     items = list(res.keys())
#     wb = xlwt.Workbook()
#     total = wb.add_sheet('test')
#     for i in range(len(items)):
#         total.write(0,i,items[i])
#         if type(res[items[i]]) == list:
#             sum = 0
#             print(items[i])
#             for j in range(len(res[items[i]])):
#                 total.write(j+2,i,(res[items[i]])[j])
#                 # sum += (res[items[i]])[j]
#             # total.write(1,i,sum)
#         else:
#             total.write(1,i,res[items[i]])
#     filename = 'res/compare1' + '.xls'
#     wb.save(filename)

def to_csv(res,filename):
    items = list(res.keys())
    wb = xlwt.Workbook()
    total = wb.add_sheet('garden')
    for i in range(len(items)):
        total.write(0,i,items[i])
        if type(res[items[i]]) == list:
            sum = 0
            print(items[i])
            for j in range(len(res[items[i]])):
                total.write(j+2,i,(res[items[i]])[j])
                # sum += (res[items[i]])[j]
            # total.write(1,i,sum)
        else:
            total.write(1,i,res[items[i]])

    #filename = 'res/chicken_plan_2_load_1' + '.xls'
    wb.save("res/"+filename+".xls")



if __name__ == '__main__':
    period = len(g_demand)
    m_ht_1,m_ht_2   = 100000,1000000
    m_fc_1,m_fc_2   = 10000,100000
    m_cdu_1,m_cdu_2 = 100000,1000000
    m_he_1,m_he_2   = 10000,100000
    m_ct_1,m_ct_2   = 10000,100000
    t_ht_1  = [40 for _ in range(period)]
    t_ht_2  = [65 for _ in range(period)]
     
    t_fc_1  = [40 for _ in range(period)]
    t_fc_2  = [65 for _ in range(period)]

    t_cdu_1 = [65 for _ in range(period)]
    t_cdu_2 = [95 for _ in range(period)]

    t_he_1  = [40 for _ in range(period)]
    t_he_2  = [95 for _ in range(period)]

    t_ct_1  = [20 for _ in range(period)]
    t_ct_2  = [95 for _ in range(period)]
    #m_el_1,m_el_2 =10000,100000
    #t_el_1 = [50 for _ in range(period+1)]
    #t_el_2 = [80 for _ in range(period+1)]
    n=1
    #gap = ggggap
    obj = 100000000000
    max_err=[]
    mean_err=[]
    slack_num_list=[]
    #error = [1 for _ in range(period*nn*3)]
    error = {
        "H_ht_ht"   : [0.1 for _ in range(period)],
        "H_fc_fc"   : [0.1 for _ in range(period)],
        "H_fc_ht"   : [0.1 for _ in range(period)],
        "H_fc_cdu"  : [0.1 for _ in range(period)],
        "H_cdu_cdu" : [0.1 for _ in range(period)],
        "H_cdu_ht"  : [0.1 for _ in range(period)],
        "H_he_he"   : [0.1 for _ in range(period)],
        "H_he_cdu"  : [0.1 for _ in range(period)],
        "H_ct_cdu"  : [0.1 for _ in range(period)],
        "H_ct_ct"   : [0.1 for _ in range(period)]
    }
    M = {
        "m_ht"   :[m_ht_1,m_ht_2],
        "m_fc"   :[m_fc_1,m_fc_2],
        "m_cdu"  :[m_cdu_1,m_cdu_2],
        "m_he"   :[m_he_1,m_he_2],
        "m_ct"   :[m_ct_1,m_ct_2]
    }
    T = {
        "t_ht"   :[t_ht_1,t_ht_2],
        "t_fc"   :[t_fc_1,t_fc_2],
        "t_cdu"  :[t_cdu_1,t_cdu_2],
        "t_he"   :[t_he_1,t_he_2],
        "t_ct"   :[t_ct_1,t_ct_2]
    }
    start =time.time()
    M,T,res_M_T,H,error,ans,slack_num = opt(M,T,error,0,1,1)
    M,T = bound_con(period,H,gap,M,T,res_M_T,n,0.99)
    errorl = [abs(ee[i]) for ee in error.values() for i in range(len(ee))]
    #print(len(error))
    max_err.append(max(errorl))
    mean_err.append(np.mean(errorl))
    slack_num_list.append(slack_num)
    print(max(errorl))
    print(min(errorl))
    #exit(0)
    #all(error[i]>=0.005 for i in range(len(error)))
    
    obj_print=[]
    while max(errorl)>gap or min(errorl)<-gap:

        error_last,res_last = error,ans
        M,T,res_M_T,H,error,res,slack_num = opt(M,T,error,0,res_M_T,H)

        if slack_num == 10000000:
            to_csv(res_last,"test")
            to_csv(error_last,"error")
            print("g")
            exit(0)
        # if obj == 404:
        #     break
        #res = res_new
        M,T = bound_con(period,H,gap,M,T,res_M_T,n,0.8)
        #print(t_el_1,t_el_2)
        obj_print.append(res['objective'])
        errorl = [abs(ee[i]) for ee in error.values() for i in range(len(ee))]
        #error = [abs(error[i])for i in range(len(error))]
        max_err.append(max(errorl))
        mean_err.append(np.mean(errorl))
        slack_num_list.append(slack_num)
        if max(errorl)>0.7:
            to_csv(error,"errorbig")
            #input()
        print(max_err)
        print(mean_err)
        print(slack_num_list)
        n += 1
        print(obj_print)
    print(n)
    
    print('------')


    # #计算一次fix后的可行解
    # M,T,res_M_T,H,error,res,slack_num = opt(M,T,error,1,res_M_T,H)
    # #obj_print.append(res['objective'])
    # errorl = [abs(ee[i]) for ee in error.values() for i in range(len(ee))]
    # #error = [abs(error[i])for i in range(len(error))]
    # max_err.append(max(errorl))
    # mean_err.append(np.mean(errorl))
    # obj_print.append(res['objective'])
    # print(obj_print)
    # print(max_err)
    # print(mean_err)
    to_csv(res,"test")
    to_csv(error,"error")


    end=time.time()
    print('Running time: %s Seconds'%(end-start))