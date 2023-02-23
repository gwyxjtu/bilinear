
import copy
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import xlwt
import random
import time
import xlrd
import csv
def crf(year):
    i = 0.08
    crf=((1+i)**year)*i/((1+i)**year-1);
    return crf

cer=0.5
days=4
nn=2
ggggap=0.01

book_spr = xlrd.open_workbook('cspringdata.xlsx')
book_sum = xlrd.open_workbook('csummerdata.xlsx')
book_aut = xlrd.open_workbook('cautumndata.xlsx')
book_win = xlrd.open_workbook('cwinterdata.xlsx')
data_spr = book_spr.sheet_by_index(0)
data_sum = book_sum.sheet_by_index(0)
data_aut = book_aut.sheet_by_index(0)
data_win = book_win.sheet_by_index(0)
ele_load = []
g_demand = []
q_demand = []
r_solar = []




c = 4200 # J/kg*C
c_kWh = 4200/3.6/1000000
delta_T = 12
k_pv = 0.16
lambda_h = 20
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
k_fc = 18
k_el = 0.022
k_el_1 = 46
k_co = 1.05
k_pv = 0.16
#--------------
lambda_ele_in = [0.3748,0.3748,0.3748,0.3748,0.3748,0.3748,0.3748,0.8745,0.8745,0.8745,1.4002,1.4002,1.4002,1.4002,
                 1.4002,0.8745,0.8745,0.8745,1.4002,1.4002,1.4002,0.8745,0.8745,0.3748]
#lambda_ele_in = [lambda_ele_in[i]*1.5 for i in range(len(lambda_ele_in))]
lambda_ele_out = 0.3
#lambda_ele_in = lambda_ele_in*30

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

# import matplotlib.pyplot as plt
# x = [i for i in range(0,24*6)]
# plt.plot(x,g_de)
# plt.show()
# exit(0)



#g_de = g_de_w*days
#p_load = p_load_winter*days
lambda_ele_in = lambda_ele_in*days*4
#r = r*days
m_de = [g_de[i]/c_kWh/delta_T for i in range(len(g_de))]
period = len(g_de)
# x1_list=[]
# x2_list=[]
# y1_list=[]
# y2_list=[]
# c=[]
# x_pieces=[]
# y_pieces=[]

def McCormick(model,H,x,y,x1,x2,y1,y2,piece_count,n):
    model.addConstr(H>=x1*y+x*y1-x1*y1)
    model.addConstr(H>=x2*y+x*y2-x2*y2)
    model.addConstr(H<=x2*y+x*y1-x2*y1)
    model.addConstr(H<=x*y2+x1*y-x1*y2)
    return model
def piece_McCormick(model,H,x,y,x1,x2,y1,y2,c,x_pieces,y_pieces,piece_count,error,i_iteration,n):
    # n piece 
    #int_num = 0
    print(piece_count)
    print(len(error))
    if abs(error[(piece_count%3)*period+int(piece_count)])<ggggap:
        #print((piece_count%3)*period+int(piece_count/3))
        model.addConstr(H>=x1*y+x*y1-x1*y1)
        model.addConstr(H>=x2*y+x*y2-x2*y2)
        model.addConstr(H<=x2*y+x*y1-x2*y1)
        model.addConstr(H<=x*y2+x1*y-x1*y2)
        piece_count += 1
        return model,piece_count,1
        
    # model.addConstr(H>=x1*y+x*y1-x1*y1)
    # model.addConstr(H>=x2*y+x*y2-x2*y2)
    # model.addConstr(H<=x2*y+x*y1-x2*y1)
    # model.addConstr(H<=x*y2+x1*y-x1*y2)
    # x1_list.append([])
    # x2_list.append([])
    # y1_list.append([])
    # y2_list.append([])
    # x_pieces.append([])
    # y_pieces.append([])
    c = c[piece_count*n:piece_count*n+n]
    y_pieces = y_pieces[piece_count*n:piece_count*n+n]
    x_pieces = x_pieces[piece_count*n:piece_count*n+n]
    #x1_list = copy.deepcopy([x1+i*(x2-x1)/n for i in range(n)])
    #x2_list = copy.deepcopy([x1+i*(x2-x1)/n for i in range(1,1+n)])
    x1_list = [x1 for _ in range(n)]
    x2_list = [x2 for _ in range(n)]
    y1_list = copy.deepcopy([y1+i*(y2-y1)/n for i in range(n)])
    y2_list = copy.deepcopy([y1+i*(y2-y1)/n for i in range(1,1+n)])
    #minh = min)
    #x1_list = copy.deepcopy([min() for i in range(n)])
    #x2_list = copy.deepcopy([x1+i*(x2-x1)/n for i in range(1,1+n)])
    #print(x1,x2,x1_list,x2_list)
    #c = [model.addVar(vtype=GRB.BINARY, lb=0, name=f"c_x{t}") for t in range(piece_count*n,piece_count*n+n)]
    ##c_y = [m.addVar(vtype=GRB.BINARY, lb=0, name=f"c_y{t}") for t in range(piece_count,piece_count+n)]
    #x_pieces = [model.addVar(vtype=GRB.CONTINUOUS, name=f"x_pieces{t}") for t in range(piece_count*n,piece_count*n+n)]
    #y_pieces = [model.addVar(vtype=GRB.CONTINUOUS, name=f"y_pieces{t}") for t in range(piece_count*n,piece_count*n+n)]
    for i in range(n):
        model.addConstr(y1_list[i]*x_pieces[i]<=H)#x1_list[i]=H/y
        model.addConstr(y2_list[i]*x_pieces[i]>=H)#
        model.addConstr(y_pieces[i]>=y1_list[i])
        model.addConstr(y_pieces[i]<=y2_list[i])


    model.addConstr(H>=gp.quicksum(c[i]*(x1_list[i]*y_pieces[i]+x_pieces[i]*y1_list[i]-x1_list[i]*y1_list[i]) for i in range(n)))
    model.addConstr(H>=gp.quicksum(c[i]*(x2_list[i]*y_pieces[i]+x_pieces[i]*y2_list[i]-x2_list[i]*y2_list[i]) for i in range(n)))
    model.addConstr(H<=gp.quicksum(c[i]*(x2_list[i]*y_pieces[i]+x_pieces[i]*y1_list[i]-x2_list[i]*y1_list[i]) for i in range(n)))
    model.addConstr(H<=gp.quicksum(c[i]*(x_pieces[i]*y2_list[i]+x1_list[i]*y_pieces[i]-x1_list[i]*y2_list[i]) for i in range(n)))
    model.addConstr(gp.quicksum(c[i] for i in range(n)) == 1)
    model.addConstr(gp.quicksum(c[i]*x_pieces[i] for i in range(n)) == x)
    model.addConstr(gp.quicksum(c[i]*y_pieces[i] for i in range(n)) == y)
    piece_count+=1
    return model,piece_count,0
def fix_solve(m_ht,m_fc):
    m = gp.Model("bilinear")

    z_fc = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_fc{t}") for t in range(period)]

    z_el = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_el{t}") for t in range(period)]

    #z_ele_in = [m.addVar(lb=-0.0001, ub=1.01, vtype=GRB.BINARY, name=f"z_ele_in{t}") for t in range(period)]

    #z_ele_out = [m.addVar(lb=-0.0001, ub=1.01, vtype=GRB.BINARY, name=f"z_ele_out{t}") for t in range(period)]


    # Create variables
    ce_h = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="ce_h")

    #m_ht = m.addVar(vtype=GRB.CONTINUOUS, lb=10,ub=1000000, name="m_ht") # capacity of hot water tank

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

    #m_fc = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_fc") # fuel cells water

    m_el = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_el") # fuel cells water

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
    m.params.NonConvex = 1
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
            'm_ht':m_ht,
            'm_fc':m_fc,
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
    return res
def opt(obj,m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2,error):

    # Create a new model
    m = gp.Model("bilinear")
    
    m_ht = m.addVar(vtype=GRB.CONTINUOUS, lb=m_ht_1,ub=m_ht_2, name="m_ht") # capacity of hot water tank
    t_ht = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_ht_1[t],ub=t_ht_2[t], name=f"t_ht{t}") for t in range(period)] # temperature of hot water tank
    m_fc = m.addVar(vtype=GRB.CONTINUOUS, lb=m_fc_1,ub=m_fc_2, name=f"m_fc") # fuel cells water
    t_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_fc_1[t],ub=t_fc_2[t], name=f"t_fc{t}") for t in range(period)] # outlet temperature of fuel cells cooling circuits
    #m_el = m.addVar(vtype=GRB.CONTINUOUS, lb=m_el_1,ub=m_el_2, name=f"m_el") # fuel cells water
    #t_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_el_1[t],ub=t_el_2[t], name=f"t_el{t}") for t in range(period)] # outlet temperature of electrolyzer cooling circuits

    H_ht_ht = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_ht_ht{t}") for t in range(period)]
    H_fc_fc = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_fc_fc{t}") for t in range(period)]
    H_fc_ht = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_fc_ht{t}") for t in range(period)]
    H_el_el = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_el_el{t}") for t in range(period)]
    H_el_ht = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_el_ht{t}") for t in range(period)]


    z_fc = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_fc{t}") for t in range(period)]
    z_el = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_el{t}") for t in range(period)]
    #z_ele_in = [m.addVar(lb=-0.0001, ub=1.01, vtype=GRB.BINARY, name=f"z_ele_in{t}") for t in range(period)]

    #z_ele_out = [m.addVar(lb=-0.0001, ub=1.01, vtype=GRB.BINARY, name=f"z_ele_out{t}") for t in range(period)]
    # Create variables
    ce_h = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="ce_h")
    g_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_fc{t}") for t in range(period)] # heat generated by fuel cells
    p_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_fc{t}") for t in range(period)]
    fc_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="fc_max") # rated heat power of fuel cells
    pump_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="pump_max")
    el_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="el_max") # rated heat power of fuel cells
    p_eb_max = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="p_eb_max")

    t_de = [m.addVar(vtype=GRB.CONTINUOUS, lb=0,name=f"t_de{t}") for t in range(period)] # outlet temparature of heat supply circuits
    h_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_fc{t}") for t in range(period)] # hydrogen used in fuel cells
    p_eb = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_eb{t}") for t in range(period)]
    g_eb = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_eb{t}") for t in range(period)]
    g_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_el{t}") for t in range(period)] # heat generated by Electrolyzer
    h_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_el{t}") for t in range(period)] # hydrogen generated by electrolyzer
    p_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_el{t}") for t in range(period)] # power consumption by electrolyzer
    h_sto = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_sto{t}") for t in range(period)] # hydrogen storage
    h_pur = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_pur{t}") for t in range(period)] # hydrogen purchase
    p_pur = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pur{t}") for t in range(period)] # power purchase
    p_sol = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_sol{t}") for t in range(period)] # power purchase
    area_pv = m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub = 2000, name=f"area_pv")
    p_pump = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pump{t}") for t in range(period)] 
    hst = m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub = 2000, name=f"hst")
    p_co = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_co{t}") for t in range(period)] 

    piece_count = period*nn*3#-int(period/24-1)*2*nn
    #McCormick constrian
    c = [m.addVar(vtype=GRB.BINARY, lb=0,ub=1, name=f"c_x{t}") for t in range(piece_count)]
    #c_y = [m.addVar(vtype=GRB.BINARY, lb=0, name=f"c_y{t}") for t in range(piece_count,piece_count+n)]
    x_pieces = [m.addVar(vtype=GRB.CONTINUOUS, name=f"x_pieces{t}") for t in range(piece_count)]
    y_pieces = [m.addVar(vtype=GRB.CONTINUOUS, name=f"y_pieces{t}") for t in range(piece_count)]
    piece_count=0
    slack_num=0
    for i in range(period):
        #print(nn)
        m,piece_count,int_tmp = piece_McCormick(m,H_fc_fc[i],m_fc,t_fc[i],m_fc_1,m_fc_2,t_fc_1[i],t_fc_2[i],c,x_pieces,y_pieces, piece_count,error,i,nn)
        slack_num+=int_tmp
        #print(i%24)
        #if i%24!=0 or i==0:
        m,piece_count,int_tmp = piece_McCormick(m,H_fc_ht[i],m_fc,t_ht[i],m_fc_1,m_fc_2,t_ht_1[i],t_ht_2[i],c,x_pieces,y_pieces,piece_count,error,i,nn)
        slack_num+=int_tmp
        m,piece_count,int_tmp = piece_McCormick(m,H_ht_ht[i],m_ht,t_ht[i],m_ht_1,m_ht_2,t_ht_1[i],t_ht_2[i],c,x_pieces,y_pieces,piece_count,error,i,nn)
        slack_num+=int_tmp
        #print(piece_count)
    for i in range(int(period/24)-1):
        m.addConstr(t_ht[i*24+24] == t_ht[24*i])
        m.addConstr(H_ht_ht[i*24+24] == H_ht_ht[24*i])
        m.addConstr(H_fc_ht[i*24+24] == H_fc_ht[24*i])

        #m.addConstr(H_el_ht[i*24+24] == H_el_ht[24*i])
    m.addConstr(H_ht_ht[-1] == H_ht_ht[0])
    m.addConstr(H_fc_ht[-1] == H_fc_ht[0])
    m.addConstr(t_ht[-1] == t_ht[0])
    #m.addConstr(h_sto[0] == 0)
    m.addConstr(h_sto[-1] == h_sto[0])
    for i in range(period - 1):
        # m.addConstr(m_ht * (t_ht[i + 1] - t_ht[i]) == 
        #     m_fc * (t_fc[i] - t_ht[i]) + m_el * (t_el[i] - t_ht[i]) - m_de[i] * (t_ht[i] - t_de[i]))
        m.addConstr(H_ht_ht[i+1]-H_ht_ht[i] == H_fc_fc[i]-H_fc_ht[i] + g_eb[i]/c_kWh -m_de[i] * (t_ht[i] - t_de[i]))
        m.addConstr(h_sto[i+1] - h_sto[i] == h_pur[i] + h_el[i] - h_fc[i])
        
    #m.addConstr(m_ht * (t_ht[0] - t_ht[i]) == m_fc * (t_fc[i] - t_ht[i]) + m_el * (t_el[i] - t_ht[i]) - m_de[i] * (t_ht[i] - t_de[i]))
    m.addConstr(H_ht_ht[0] - H_ht_ht[i] == H_fc_fc[i]-H_fc_ht[i] + g_eb[i]/c_kWh -m_de[i]*(t_ht[i]-t_de[i]))
    m.addConstr(h_sto[0] - h_sto[-1] == h_pur[-1] + h_el[-1] - h_fc[-1])
    #m.addConstr(t_ht[0] == 60)
    m.addConstr(p_eb_max<=500)
    for i in range(period):
        #不能用经验公式，因为跟负荷有关，相当于还是使用了商业求解器的部分结果。
        #m.addConstr(m_fc<= 80*g_fc[i])
        #m.addConstr(m_fc>= 60*g_fc[i])
        #m.addConstr(m_el<= 80*g_el[i])
        #m.addConstr(m_el>= 60*g_el[i])

        m.addConstr(10000*z_fc[i]>=g_fc[i])
        #m.addConstr(z_fc[i]+g_fc[i]>=0.01)
        m.addConstr(10000*z_el[i]>=p_el[i])
        #m.addConstr(z_el[i]+g_el[i]>=0.01)
        #m.addConstr(p_pur[i]<=z_ele_in[i]*1000000)
        #m.addConstr(p_sol[i]<=z_ele_out[i]*1000000)
        #m.addConstr(z_ele_in[i]+z_ele_out[i]<=1)
        m.addConstr(t_de[i] >= 40)
        m.addConstr(p_co[i] + p_el[i] + p_sol[i] + p_pump[i] + p_load[i] + p_eb[i]== p_pur[i] + p_fc[i] + k_pv*area_pv*r[i])
        m.addConstr(g_fc[i] <= 0.9*18 * h_fc[i])
        m.addConstr(p_pump[i] >= 0.6/1000 * (m_fc*z_fc[i]+m_de[i]))#热需求虽然低，水泵耗电高。
        m.addConstr(p_co[i] >= k_co * h_el[i])
        m.addConstr(p_fc[i] <= 18 * h_fc[i])#氢燃烧产电
        m.addConstr(h_el[i] <= k_el * p_el[i])
        #m.addConstr(g_el[i] <= 0.2017*p_el[i])
        #m.addConstr(g_fc[i] == c_kWh * m_fc * (t_fc[i] - t_ht[i]))
        #m.addConstr(g_el[i] == c_kWh * m_el * (t_el[i] - t_ht[i]))
        m.addConstr(g_fc[i] == c_kWh * (H_fc_fc[i] - H_fc_ht[i]))
        #m.addConstr(g_el[i] == c_kWh * (H_el_el[i] - H_el_ht[i]))
        m.addConstr(t_fc[i] <= 80)
        #m.addConstr(t_el[i] <= 80)
        m.addConstr(h_sto[i]<=hst)
        m.addConstr(h_el[i]<=hst)
        #m.addConstr(t_ht[i] >= 50)
        m.addConstr(18*h_fc[i] <= fc_max)
        m.addConstr(p_pump[i]<=pump_max)
        m.addConstr(p_el[i] <= el_max)
        m.addConstr(g_de[i] == c_kWh * m_de[i] * (t_ht[i] - t_de[i]))
        m.addConstr(p_eb[i]<=p_eb_max)
        m.addConstr(g_eb[i] == 0.8*p_eb[i])
        #m.addConstr(m_fc <= m_ht)
    # m.addConstr(m_fc[i] == m_ht/3)
    # m.addConstr(m_ht >= 4200*100)
    # m.addConstr(t_ht[i] <= 80)#强化条件
    m.addConstr(gp.quicksum(p_pur)<=cer*(sum(p_load)+sum(g_de)/0.8))
    m.addConstr( crf_pv * cost_pv*area_pv+ crf_el*cost_el*el_max+p_eb_max*crf_eb*p_eb_max
        +crf_hst * hst*cost_hst +crf_water* cost_water_hot*m_ht + cost_pump*pump_max*crf_pump+crf_fc *cost_fc * fc_max + lambda_h*gp.quicksum(h_pur)*365+ 
        gp.quicksum([p_pur[i]*lambda_ele_in[i] for i in range(period)])*365-gp.quicksum(p_sol)*lambda_ele_out*365<=obj)
    # m.addConstr(crf_pv * cost_pv*area_pv+ crf_el*cost_el*el_max
    #         +crf_hst * hst*cost_hst +crf_water* cost_water_hot*m_ht + cost_pump*pump_max*crf_pump+crf_fc *cost_fc * fc_max + lambda_h*gp.quicksum(h_pur)*365+ 
    #         gp.quicksum([p_pur[i]*lambda_ele_in[i] for i in range(period)])*365-gp.quicksum(p_sol)*lambda_ele_out*365 <= obj)
    # m.setObjective( crf_pv * cost_pv*area_pv+ crf_el*cost_el*el_max
    #     +crf_hst * hst*cost_hst +crf_water* cost_water_hot*m_ht + crf_fc *cost_fc * fc_max + lambda_h*gp.quicksum(h_pur)*365+ 
    #     365*gp.quicksum([p_pur[i]*lambda_ele_in[i] for i in range(24)])-365*gp.quicksum(p_sol)*lambda_ele_out , GRB.MINIMIZE)
    m.setObjective( crf_pv * cost_pv*area_pv+ crf_el*cost_el*el_max
        +crf_hst * hst*cost_hst +crf_water* cost_water_hot*m_ht + cost_pump*pump_max*crf_pump+crf_fc *cost_fc * fc_max + lambda_h*gp.quicksum(h_pur)*365/days+ 
        gp.quicksum([p_pur[i]*lambda_ele_in[i] for i in range(period)])*365/days-gp.quicksum(p_sol)*lambda_ele_out*365/days, GRB.MINIMIZE)
    #-gp.quicksum(p_sol)*lambda_ele_out 
    # First optimize() call will fail - need to set NonConvex to 2
    m.params.NonConvex = 1
    m.params.MIPGap = 0.01
    # m.optimize()
    #m.computeIIS()
    #m.write('model.mps')
    #exit(0)
    H = {'H_ht_ht':H_ht_ht,
         'H_fc_fc':H_fc_fc,
         'H_fc_ht':H_fc_ht
        }
    try:
        m.optimize()
        if m.Status != gp.GRB.OPTIMAL:
            m.computeIIS()
            m.write("model1.ilp")

            return 404,m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2,H,[0 for i in range(period*3)],0
    except gp.GurobiError:
        return 404,m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2,H,[0 for i in range(period*3)],0
        print("Optimize failed due to non-convexity")

    # 有的变量出现在不同的双线性项中，边界取并集
    #m_fc_1 = max(m_fc_1,60*max([g_fc[i].X for i in range(period)]))
    #m_fc_2 = min(m_fc_2,80*max([g_fc[i].X for i in range(period)]))
    #m_el_1 = max(m_el_1,60*max([g_el[i].X for i in range(period)]))
    #m_el_2 = max(m_el_2,80*max([g_el[i].X for i in range(period)]))
    error = [(H_ht_ht[i].X-m_ht.X*t_ht[i].X)/H_ht_ht[i].X for i in range(period)]
    error +=[(H_fc_fc[i].X-m_fc.X*t_fc[i].X)/H_fc_fc[i].X for i in range(period)]
    error +=[(H_fc_ht[i].X-m_fc.X*t_ht[i].X)/H_fc_ht[i].X for i in range(period)]
    #error +=[(H_el_el[i].X-m_el.X*t_el[i].X)/H_el_el[i].X for i in range(period)]
    #error +=[(H_el_ht[i].X-m_el.X*t_ht[i].X)/H_el_ht[i].X for i in range(period)]
    print("OBJ\n")
    print(m.objVal)
    ans = {'objective':m.objVal,
            'm_ht':m_ht.X,
            'm_fc':m_fc.X,
            #'m_el':m_el.X,
            'fc_max':fc_max.X,
            'el_max':el_max.X,
            'p_eb_max':p_eb_max.X,
            'area_pv':area_pv.X,
            'error_H_ht_ht':[(H_ht_ht[i].X-m_ht.X*t_ht[i].X)/H_ht_ht[i].X for i in range(period)],
            'error_H_fc_fc':[(H_fc_fc[i].X-m_fc.X*t_fc[i].X)/H_fc_fc[i].X for i in range(period)],
            'error_H_fc_ht':[(H_fc_ht[i].X-m_fc.X*t_ht[i].X)/H_fc_ht[i].X for i in range(period)],
            #'error_H_el_el':[(H_el_el[i].X-m_el.X*t_el[i].X)/H_el_el[i].X for i in range(period)],
            #'error_H_el_ht':[(H_el_ht[i].X-m_el.X*t_ht[i].X)/H_el_ht[i].X for i in range(period)],
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
            #'t_el':[t_el[i].X for i in range(period)],
            'h_el':[h_el[i].X for i in range(period)],
            'h_fc':[h_fc[i].X for i in range(period)],
            't_fc':[t_fc[i].X for i in range(period)],
            't_de':[t_de[i].X for i in range(period)],
            'h_sto':[h_sto[i].X for i in range(period)],
            'h_pur':[h_pur[i].X for i in range(period)]
            }
    H = {'H_ht_ht':m.getAttr('x', H_ht_ht),
         'H_fc_fc':m.getAttr('x', H_fc_fc),
         'H_fc_ht':m.getAttr('x', H_fc_ht)
        }

    return obj,m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2,H,error,ans,slack_num

def move_to_feasible(n,x,y,H,k=0.0,s=0.6):
    k = k*s**n
    
    #print(tmp,H,x,y,H-x*y)
    k1 = k*x/np.sqrt(x**2+y**2)
    k2 = k*y/np.sqrt(x**2+y**2)
    if H>x*y:
        tmp = abs(H-x*y)
        x = x+k1*tmp
        y = y+k2*tmp
        # if H<x*y:
        #     x = x-k1*tmp
        #     y = y-k2*tmp
        #     print('over move')
        #     print('\n\n\n\n\n')
    else:
        tmp = abs(x*y-H)
        x = x-k1*tmp
        y = y-k2*tmp
        # if H>x*y:
        #     x = x+k1*tmp
        #     y = y+k2*tmp
        #     print('over move')
        #     print('\n\n\n\n\n')
    return x,y

def bound_con(H,gap,m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2,
        m_ht,m_fc,t_ht,t_fc,n,k):
    
    k = k*(1-0.01**n)
    m_ht_h1,t_ht_h1 = [0 for _ in range(period)],[0 for _ in range(period)]
    m_fc_h2,t_fc_h2 = [0 for _ in range(period)],[0 for _ in range(period)]
    m_fc_h3,t_ht_h3 = [0 for _ in range(period)],[0 for _ in range(period)]
    # m_el_h4,t_el_h4 = [0 for _ in range(period)],[0 for _ in range(period)]
    # m_el_h5,t_ht_h5 = [0 for _ in range(period)],[0 for _ in range(period)]

    for i in range(period):
        #烦死了，这也会有冲突！！！！！不如取平均
        m_ht_h1[i],t_ht_h1[i] = move_to_feasible(n,m_ht,t_ht[i],H['H_ht_ht'][i])
        m_fc_h2[i],t_fc_h2[i] = move_to_feasible(n,m_fc,t_fc[i],H['H_fc_fc'][i])
        m_fc_h3[i],t_ht_h3[i] = move_to_feasible(n,m_fc,t_ht[i],H['H_fc_ht'][i])
        # m_el_h4[i],t_el_h4[i] = move_to_feasible(n,m_el,t_el[i],H['H_el_el'][i])
        # m_el_h5[i],t_ht_h5[i] = move_to_feasible(n,m_el,t_ht[i],H['H_el_ht'][i])
    #print(np.mean(m_fc_h3),m_fc_h3)
    m_ht = np.mean(m_ht_h1)
    m_fc = np.mean(m_fc_h2+m_fc_h3)
    #m_el = np.mean(m_el_h4+m_el_h5)
    for i in range(period):
        t_ht[i] = np.mean([t_ht_h1[i],t_ht_h3[i]])
        t_fc[i] = t_fc_h2[i]
        #t_el[i] = t_el_h4[i]

    d_m_ht = max(m_ht-m_ht_1,m_ht_2-m_ht)
    d_m_fc = max(m_fc-m_fc_1,m_fc_2-m_fc)
    #d_m_el = max(m_el-m_el_1,m_el_2-m_el)

    m_ht_1 = max(m_ht_1,m_ht-k*d_m_ht) 
    m_fc_1 = max(m_fc_1,m_fc-k*d_m_fc)
    #m_el_1 = max(m_el_1,m_el-k*d_m_el)

    m_ht_2 = min(m_ht_2,m_ht+k*d_m_ht)
    m_fc_2 = min(m_fc_2,m_fc+k*d_m_fc)
    #m_el_2 = min(m_el_2,m_el+k*d_m_el)

    #init
    d_t_ht = [0 for _ in range(period)]
    d_t_fc = [0 for _ in range(period)]
    #d_t_el = [0 for _ in range(period)]
    for i in range(period):
        d_t_ht[i] = max(t_ht[i]-t_ht_1[i],t_ht_2[i]-t_ht[i]) 
        d_t_fc[i] = max(t_fc[i]-t_fc_1[i],t_fc_2[i]-t_fc[i])
        #d_t_el[i] = max(t_el[i]-t_el_1[i],t_el_2[i]-t_el[i])
        t_ht_1[i] = max(t_ht_1[i],t_ht[i]-k*d_t_ht[i]) #if abs(H['H_ht_ht'][i]-m_ht*t_ht[i])/H['H_ht_ht'][i] >= 0.000001 else t_ht_1[i]
        t_fc_1[i] = max(t_fc_1[i],t_fc[i]-k*d_t_fc[i]) #if abs(H['H_fc_fc'][i]-m_fc*t_fc[i])/H['H_fc_fc'][i] >= 0.000001 else t_fc_1[i]
        #t_el_1[i] = max(t_el_1[i],t_el[i]-k*d_t_el[i]) #if abs(H['H_el_el'][i]-m_el*t_el[i])/H['H_el_el'][i] >= 0.000001 else t_el_1[i]
        t_ht_2[i] = min(t_ht_2[i],t_ht[i]+k*d_t_ht[i]) #if abs(H['H_ht_ht'][i]-m_ht*t_ht[i])/H['H_ht_ht'][i] >= 0.000001 else t_ht_2[i]
        t_fc_2[i] = min(t_fc_2[i],t_fc[i]+k*d_t_fc[i]) #if abs(H['H_fc_fc'][i]-m_fc*t_fc[i])/H['H_fc_fc'][i] >= 0.000001 else t_fc_2[i]
        #t_el_2[i] = min(t_el_2[i],t_el[i]+k*d_t_el[i]) #if abs(H['H_el_el'][i]-m_el*t_el[i])/H['H_el_el'][i] >= 0.000001 else t_el_2[i]

    return m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2

# Solve bilinear model
# m.params.NonConvex = 2
# m.optimize()

#m.printAttr('x')
#m.write('sol_winter.mst')
# Constrain 'x' to be integral and solve again
# x.vType = GRB.INTEGER
# m.optimize()

# m.printAttr('x')

# wb = xlwt.Workbook()
# result = wb.add_sheet('result')
# alpha_ele = 1.01
# alpha_heat = 0.351
# ce_c = np.sum(p_load)*alpha_ele + np.sum(g_de)*alpha_heat
# #c_cer == lambda_carbon*(ce_c - ce_h)
# p_pur_tmp = m.getAttr('x', p_pur)
# p_sol_tmp = m.getAttr('x', p_sol)
# h_pur_tmp = m.getAttr('x', h_pur)
# ce_h_1 = np.sum(p_pur_tmp)*alpha_ele - np.sum(p_sol_tmp)*alpha_ele


# item1 = ['m_ht','m_fc','m_el','fc_max','el_max']
# item2 = [g_el,z_el,g_fc,z_fc,p_el,p_fc,p_pur,p_pump,p_sol,t_ht,t_el,h_el,h_fc,t_fc,t_de,h_sto,h_pur]
# a_pv = m.getVarByName('area_pv').getAttr('x')
# item3 = [[k_pv*a_pv*r[i] for i in range(len(r))],p_load,g_de]
# item3_name = ['p_pv','p_load','g_de']
# print(m.getAttr('x', p_el))
# for i in range(len(item1)):
#     result.write(0,i,item1[i])
#     result.write(1,i,m.getVarByName(item1[i]).getAttr('x'))
# for i in range(len(item2)):
#     tmp = m.getAttr('x', item2[i])
#     result.write(0,i+len(item1),item2[i][0].VarName[:-1])
#     for j in range(len(tmp)):
#         result.write(j+1,i+len(item1),tmp[j])

# for i in range(3):
#     tmp = item3[i]
#     result.write(0,i+len(item1)+len(item2),item3_name[i])
#     for j in range(len(tmp)):
#         result.write(j+1,i+len(item1)+len(item2),tmp[j])

# t_ht = m.getAttr('x', t_ht)
# m_ht = m.getVarByName('m_ht').getAttr('x')
# res = []
# for i in range(len(t_ht)-1):
#     res.append(c*m_ht*(t_ht[i+1] - t_ht[i])/3.6/1000000)
# res.append(c*m_ht*(t_ht[0]-t_ht[-1])/3.6/1000000)
# result.write(0,3+len(item1)+len(item2),'g_ht')
# for j in range(len(res)):
#     result.write(j+1,3+len(item1)+len(item2),res[j])
# result.write(0,4+len(item1)+len(item2),'cer')
# result.write(1,4+len(item1)+len(item2),(ce_c - ce_h_1)/ce_c)

# result.write(0,5+len(item1)+len(item2),'capex')
# result.write(0,6+len(item1)+len(item2),'opex')
# capex = crf_pv*cost_pv*a_pv+ crf_el*cost_el*m.getVarByName('el_max').getAttr('x')+crf_hst*m.getVarByName('hst').getAttr('x')*cost_hst +crf_water* cost_water_hot*m.getVarByName('m_ht').getAttr('x') + crf_fc *cost_fc * m.getVarByName('fc_max').getAttr('x')
# opex = np.sum([p_pur_tmp[i] * lambda_ele_in[i] for i in range(len(p_pur_tmp))]) - np.sum(p_sol_tmp)*lambda_ele_out+np.sum(h_pur_tmp)*lambda_h
# opex = opex*365
# print(crf_pv*cost_pv*a_pv,crf_el*cost_el*m.getVarByName('el_max').getAttr('x'),crf_hst*m.getVarByName('hst').getAttr('x')*cost_hst,crf_water* cost_water_hot*m.getVarByName('m_ht').getAttr('x'),crf_fc *cost_fc * m.getVarByName('fc_max').getAttr('x'))
# result.write(1,5+len(item1)+len(item2),capex)
# result.write(1,6+len(item1)+len(item2),opex)
# wb.save("sol_season_12day_1109.xls")
# #print(m.getJSONSolution())


if __name__ == '__main__':
    m_ht_1,m_ht_2 = 10000,100000
    t_ht_1 = [50 for _ in range(period)]
    t_ht_2 = [80 for _ in range(period)]
    m_fc_1,m_fc_2 = 1000,10000
    t_fc_1 = [50 for _ in range(period)]
    t_fc_2 = [80 for _ in range(period)]
    #m_el_1,m_el_2 =10000,100000
    #t_el_1 = [50 for _ in range(period+1)]
    #t_el_2 = [80 for _ in range(period+1)]
    n=1
    gap = ggggap
    obj = 100000000000
    max_err=[]
    mean_err=[]
    slack_num_list=[]
    error = [1 for _ in range(period*nn*3)]
    obj,m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2,H,error,res,slack_num = opt(obj,m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2,error)
    m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2 = bound_con(H,gap,m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2,
        res['m_ht'],res['m_fc'],res['t_ht'],res['t_fc'],n,0.9)
    error = [abs(error[i])for i in range(len(error))]
    max_err.append(max(error))
    mean_err.append(np.mean(error))
    slack_num_list.append(slack_num)
    print(max(error))
    print(min(error))
    #exit(0)
    #all(error[i]>=0.005 for i in range(len(error)))
    start =time.time()
    obj_print=[]
    while max(error)>gap or min(error)<-gap:
        obj,m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2,H,error,res_new,slack_num = opt(obj,m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2,error)
        if obj == 404:
            break
        res = res_new
        m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2 = bound_con(H,gap,m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2,
            res['m_ht'],res['m_fc'],res['t_ht'],res['t_fc'],n,0.9)
        #print(t_el_1,t_el_2)
        obj_print.append(res['objective'])
        error = [abs(error[i])for i in range(len(error))]
        max_err.append(max(error))
        mean_err.append(np.mean(error))
        slack_num_list.append(slack_num)
        print(max_err)
        print(mean_err)
        print(slack_num_list)
        n += 1
    print(n)
    print(obj_print)
    print('------')


    #计算一次fix后的可行解
    #res = fix_solve(res['m_ht'],res['m_fc'])
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
    print(max_err)
    print(mean_err)
    print(slack_num_list)
    filename = 'res/McCormick1' + '.xls'
    wb.save(filename)
    end=time.time()
    print('Running time: %s Seconds'%(end-start))