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


def crf(year):
    i = 0.08
    crf=((1+i)**year)*i/((1+i)**year-1);
    return crf

cer = 0.5
days=4

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

# r_solar_tmp = []

# for l in range(168):
#     r_solar_tmp.append(data_spr.cell(l,4).value)
# r_solar+=r_solar_tmp[-24*days:]
# r_solar_tmp = []
# for l in range(168):
#     r_solar_tmp.append(data_sum.cell(l,4).value)
# r_solar+=r_solar_tmp[-24*days:]
# r_solar_tmp = []
# for l in range(168):
#     r_solar_tmp.append(data_aut.cell(l,4).value)
# r_solar+=r_solar_tmp[-24*days:]
# r_solar_tmp = []
# for l in range(168):
#     r_solar_tmp.append(data_win.cell(l,4).value)
# r_solar+=r_solar_tmp[-24*days:]

#book = xlrd.open_workbook('harbin.csv')
#data = book.sheet_by_index(0)
with open('CHN_Shaanxi.Xian.570360_CSWD.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        ele_load.append(float(row['Electricity Load [kwh]']))
        q_demand.append(float(row['Cooling Load [kwh]']))
        g_demand.append(float(row['Heating Load [kwh]']))
        r_solar.append(float(row['Environment:Site Direct Solar Radiation Rate per Area [W/m2](Hourly)']))
q_demand = [0 if num == '' else num for num in q_demand]
g_demand = [0 if num == '' else num for num in g_demand]
#m_demand = [0 if num == '' else num for num in m_demand]
ele_load = [0 if num == '' else num for num in ele_load]

if days == 4:
    q_demand = q_demand[384+24:384+48]+q_demand[2496:2496+24]+q_demand[4680:4680+24]+q_demand[6888:6888+24]
    g_demand = g_demand[384+24:384+48]+g_demand[2496:2496+24]+g_demand[4680:4680+24]+g_demand[6888:6888+24]
    r_solar =   r_solar[384+24:384+48]+r_solar[2496:2496+24]+r_solar[4680:4680+24]+r_solar[6888:6888+24]
    ele_load = ele_load[384+24:384+48]+ele_load[2496:2496+24]+ele_load[4680:4680+24]+ele_load[6888:6888+24]

elif days == 7:
    q_demand = q_demand[24:8*24]
    g_demand = g_demand[24:8*24]
    r_solar =   r_solar[24:8*24]
    ele_load = ele_load[24:8*24]
else:

    g_demand = g_demand[384+24:384+48]+g_demand[1080+24:1080+48]+g_demand[1752:1752+24]+g_demand[2496+48:2496+72]+g_demand[3216:3216+24]+g_demand[3960:3960+24]+g_demand[4680+48:4680+72]+g_demand[5424:5424+24]+g_demand[6168:6168+24]+g_demand[6888+24:6888+48]+g_demand[7632:7632+24]+g_demand[8352:8352+24]
    q_demand = q_demand[384+24:384+48]+q_demand[1080+24:1080+48]+q_demand[1752:1752+24]+q_demand[2496+48:2496+72]+q_demand[3216:3216+24]+q_demand[3960:3960+24]+q_demand[4680+48:4680+72]+q_demand[5424:5424+24]+q_demand[6168:6168+24]+q_demand[6888+24:6888+48]+q_demand[7632:7632+24]+q_demand[8352:8352+24]
    r_solar =   r_solar[384+24:384+48]+r_solar[1080+24:1080+48]+r_solar[1752:1752+24]+r_solar[2496+48:2496+72]+r_solar[3216:3216+24]+r_solar[3960:3960+24]+r_solar[4680+48:4680+72]+r_solar[5424:5424+24]+r_solar[6168:6168+24]+r_solar[6888+24:6888+48]+r_solar[7632:7632+24]+r_solar[8352:8352+24]
    ele_load = ele_load[384+24:384+48]+ele_load[1080+24:1080+48]+ele_load[1752:1752+24]+ele_load[2496+48:2496+72]+ele_load[3216:3216+24]+ele_load[3960:3960+24]+ele_load[4680+48:4680+72]+ele_load[5424:5424+24]+ele_load[6168:6168+24]+ele_load[6888+24:6888+48]+ele_load[7632:7632+24]+ele_load[8352:8352+24]

g_de = [g_demand[i]*3 for i in range(len(ele_load))]
r=r_solar
p_load = [ele_load[i]+q_demand[i] for i in range(len(ele_load))]

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
cost_pv = 900
cost_pump = 730
cost_eb = 434.21
crf_fc = crf(10)
crf_el = crf(7)
crf_hst = crf(20)
crf_water = crf(20)
crf_pv = crf(20)
crf_pump = crf(20)
crf_eb = crf(15)
k_fc = 18
k_el = 0.022
k_el_1 = 46
k_co = 1.05
k_pv = 0.16
#--------------
lambda_ele_in = [0.3748,0.3748,0.3748,0.3748,0.3748,0.3748,0.3748,0.8745,0.8745,0.8745,1.4002,1.4002,1.4002,1.4002,
                 1.4002,0.8745,0.8745,0.8745,1.4002,1.4002,1.4002,0.8745,0.8745,0.3748]*days
#lambda_ele_in = [lambda_ele_in[i]*1.5 for i in range(len(lambda_ele_in))]
lambda_ele_out = 0.3
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


# import matplotlib.pyplot as plt
# x = [i for i in range(0,24*6)]
# plt.plot(x,g_de)
# plt.show()
# exit(0)
m_de = [g_de[i]/c_kWh/delta_T for i in range(len(g_de))]



period = len(g_de)
# Create a new model
m = gp.Model("bilinear")

z_fc = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_fc{t}") for t in range(period)]

z_el = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_el{t}") for t in range(period)]

#z_ele_in = [m.addVar(lb=-0.0001, ub=1.01, vtype=GRB.BINARY, name=f"z_ele_in{t}") for t in range(period)]

#z_ele_out = [m.addVar(lb=-0.0001, ub=1.01, vtype=GRB.BINARY, name=f"z_ele_out{t}") for t in range(period)]


# Create variables
ce_h = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="ce_h")

m_ht = m.addVar(vtype=GRB.CONTINUOUS, lb=10,ub=1000000, name="m_ht") # capacity of hot water tank

t_ht = [m.addVar(vtype=GRB.CONTINUOUS, lb=40,ub=80, name=f"t_ht{t}") for t in range(period)] # temperature of hot water tank

t_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"t_fc{t}") for t in range(period)] # outlet temperature of fuel cells cooling circuits

g_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_fc{t}") for t in range(period)] # heat generated by fuel cells

p_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_fc{t}") for t in range(period)]

p_eb = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_eb{t}") for t in range(period)]

fc_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="fc_max") # rated heat power of fuel cells

pump_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="pump_max")

p_eb_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="p_eb_max")

el_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="el_max") # rated heat power of fuel cells

t_de = [m.addVar(vtype=GRB.CONTINUOUS, lb=0,name=f"t_de{t}") for t in range(period)] # outlet temparature of heat supply circuits

h_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_fc{t}") for t in range(period)] # hydrogen used in fuel cells

m_fc = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_fc") # fuel cells water

g_eb = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_eb{t}") for t in range(period)]

g_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_el{t}") for t in range(period)] # heat generated by Electrolyzer

h_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_el{t}") for t in range(period)] # hydrogen generated by electrolyzer

p_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_el{t}") for t in range(period)] # power consumption by electrolyzer

t_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"t_el{t}") for t in range(period)] # outlet temperature of electrolyzer cooling circuits

h_sto = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_sto{t}") for t in range(period)] # hydrogen storage

h_pur = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_pur{t}") for t in range(period)] # hydrogen purchase

p_pur = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pur{t}") for t in range(period)] # power purchase

p_sol = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_sol{t}") for t in range(period)] # power purchase

area_pv = m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub = 2000, name=f"area_pv")

p_pump = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pump{t}") for t in range(period)] 

hst = m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub = 2000, name=f"hst")

p_co = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_co{t}") for t in range(period)] 
for i in range(int(period/24)-1):
    m.addConstr(t_ht[i*24+24] == t_ht[24*i])
m.addConstr(t_ht[-1] == t_ht[0])
#m.addConstr(h_sto[0] == 0)
m.addConstr(h_sto[-1] == h_sto[0])
for i in range(period - 1):
    m.addConstr(m_ht * (t_ht[i + 1] - t_ht[i]) == m_fc * (t_fc[i] - t_ht[i]) + g_eb[i]/c_kWh - m_de[i] * (t_ht[i] - t_de[i]))
    m.addConstr(h_sto[i+1] - h_sto[i] == h_pur[i] + h_el[i] - h_fc[i])
    
m.addConstr(m_ht * (t_ht[0] - t_ht[i]) == m_fc * (t_fc[i] - t_ht[i]) + g_eb[i]/c_kWh  - m_de[i] * (t_ht[i] - t_de[i]))
#m.addConstr(m_ht * (t_ht[0] - t_ht[i]) == m_fc * (t_fc[i] - t_ht[i]) + g_eb[i]/c_kWh + m_el * (t_el[i] - t_ht[i]) - m_de[i] * (t_ht[i] - t_de[i]))

m.addConstr(h_sto[0] - h_sto[-1] == h_pur[-1] + h_el[-1] - h_fc[-1])
#m.addConstr(t_ht[0] == 60)
#m.addConstr(p_eb_max<=500)
m.addConstr(gp.quicksum(p_pur)<=cer*(sum(p_load)+sum(g_de)/0.8))
for i in range(period):
    m.addConstr(10000*z_fc[i]>=g_fc[i])
    #m.addConstr(z_fc[i]+g_fc[i]>=0.01)
    m.addConstr(10000*z_el[i]>=p_el[i])
    #m.addConstr(z_el[i]+g_el[i]>=0.01)
    #m.addConstr(p_pur[i]<=z_ele_in[i]*1000000)
    #m.addConstr(p_sol[i]<=z_ele_out[i]*1000000)
    #m.addConstr(z_ele_in[i]+z_ele_out[i]<=1)
    m.addConstr(t_de[i] >= 40)
    m.addConstr(p_co[i] + p_el[i] + p_sol[i] + p_pump[i] + p_eb[i] + p_load[i] == p_pur[i] + p_fc[i] + k_pv*area_pv*r[i])
    m.addConstr(g_fc[i] == 0.9*18 * h_fc[i])
    #m.addConstr(p_pump[i] == 0.6/1000 * (m_fc*z_fc[i]+m_de[i]+m_el*z_el[i]))#热需求虽然低，水泵耗电高。
    m.addConstr(p_pump[i] == 0.6/1000 * (m_fc*z_fc[i]+m_de[i]))
    m.addConstr(p_co[i] == k_co * h_el[i])
    m.addConstr(p_fc[i] == 18 * h_fc[i])#氢燃烧产电
    m.addConstr(h_el[i] == k_el * p_el[i])
    #m.addConstr(g_el[i] == 0.2017*p_el[i])
    m.addConstr(g_fc[i] == c_kWh * m_fc * (t_fc[i] - t_ht[i]))
    #m.addConstr(g_el[i] == c_kWh * m_el * (t_el[i] - t_ht[i]))
    m.addConstr(g_eb[i] == 0.8*p_eb[i])
    m.addConstr(t_fc[i] <= 80)
    m.addConstr(t_el[i] <= 80)
    #m.addConstr(z_fc[i]+z_el[i]<=1)
    m.addConstr(h_sto[i]<=hst)
    m.addConstr(h_el[i]<=hst)
    #m.addConstr(t_ht[i] >= 50)
    m.addConstr(18*h_fc[i] <= fc_max)
    m.addConstr(p_pump[i]<=pump_max)
    m.addConstr(p_eb[i]<=p_eb_max)
    m.addConstr(p_el[i] <= el_max)
    m.addConstr(g_de[i] == c_kWh * m_de[i] * (t_ht[i] - t_de[i]))
    #m.addConstr(m_fc <= m_ht)
# m.addConstr(m_fc[i] == m_ht/3)
# m.addConstr(m_ht >= 4200*100)
# m.addConstr(t_ht[i] <= 80)#强化条件


# m.setObjective( crf_pv * cost_pv*area_pv+ crf_el*cost_el*el_max
#     +crf_hst * hst*cost_hst +crf_water* cost_water_hot*m_ht + crf_fc *cost_fc * fc_max + lambda_h*gp.quicksum(h_pur)*365+ 
#     365*gp.quicksum([p_pur[i]*lambda_ele_in[i] for i in range(24)])-365*gp.quicksum(p_sol)*lambda_ele_out , GRB.MINIMIZE)
m.setObjective( crf_pv * cost_pv*area_pv+ crf_el*cost_el*el_max +p_eb_max*crf_eb*p_eb_max
    +crf_hst * hst*cost_hst +crf_water* cost_water_hot*m_ht + cost_pump*pump_max*crf_pump+crf_fc *cost_fc * fc_max + lambda_h*gp.quicksum(h_pur)*365/days+ 
    gp.quicksum([p_pur[i]*lambda_ele_in[i] for i in range(period)])*365/days-gp.quicksum(p_sol)*lambda_ele_out*365/days, GRB.MINIMIZE)
#-gp.quicksum(p_sol)*lambda_ele_out 
# First optimize() call will fail - need to set NonConvex to 2
m.params.NonConvex = 2
m.params.MIPGap = 0.001
# m.optimize()
#m.computeIIS()
try:
    m.optimize()
    #m.computeIIS()
    #m.write('model.ilp')
except gp.GurobiError:
    print("Optimize failed due to non-convexity")

res = {'objective':m.objVal,
        'm_ht':m_ht.X,
        'm_fc':m_fc.X,
        'fc_max':fc_max.X,
        'el_max':el_max.X,
        'p_eb_max':p_eb_max.X,
        'area_pv':area_pv.X,

        'p_pv':[k_pv*area_pv.X*r[i] for i in range(period)],
        'p_load':p_load,
        'p_el':[p_el[i].X for i in range(period)],
        'p_fc':[p_fc[i].X for i in range(period)],
        'p_pur':[p_pur[i].X for i in range(period)],
        'p_pump':[p_pump[i].X for i in range(period)],
        'p_sol':[p_sol[i].X for i in range(period)],
        'p_eb':[p_eb[i].X for i in range(period)],
        'g_load':g_de,
        'g_el':[g_el[i].X for i in range(period)],
        'z_el':[z_el[i].X for i in range(period)],
        'g_fc':[g_fc[i].X for i in range(period)],
        'z_fc':[z_fc[i].X for i in range(period)],
        'g_eb':[g_eb[i].X for i in range(period)],

        't_ht':[t_ht[i].X for i in range(period)],
        't_el':[t_el[i].X for i in range(period)],
        'h_el':[h_el[i].X for i in range(period)],
        'h_fc':[h_fc[i].X for i in range(period)],
        't_fc':[t_fc[i].X for i in range(period)],
        't_de':[t_de[i].X for i in range(period)],
        'h_sto':[h_sto[i].X for i in range(period)],
        'h_pur':[h_pur[i].X for i in range(period)]
        }

# Solve bilinear model
# m.params.NonConvex = 2
# m.optimize()

#m.printAttr('x')
m.write('sol_winter.mst')
# Constrain 'x' to be integral and solve again
# x.vType = GRB.INTEGER
# m.optimize()

# m.printAttr('x')
items = list(res.keys())
wb = xlwt.Workbook()
total = wb.add_sheet('test')
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
filename = 'compare' + '.xls'
wb.save(filename)


