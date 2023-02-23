'''
Author: guo_idpc
Date: 2023-02-23 19:15:43
LastEditors: guo_idpc 867718012@qq.com
LastEditTime: 2023-02-23 20:01:11
FilePath: /bilinear/main_model/model.py
Description: 人一生会遇到约2920万人,两个人相爱的概率是0.000049,所以你不爱我,我不怪你.

Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
'''
'''
                       ::
                      :;J7, :,                        ::;7:
                      ,ivYi, ,                       ;LLLFS:
                      :iv7Yi                       :7ri;j5PL
                     ,:ivYLvr                    ,ivrrirrY2X,
                     :;r@Wwz.7r:                :ivu@kexianli.
                    :iL7::,:::iiirii:ii;::::,,irvF7rvvLujL7ur
                   ri::,:,::i:iiiiiii:i:irrv177JX7rYXqZEkvv17
                ;i:, , ::::iirrririi:i:::iiir2XXvii;L8OGJr71i
              :,, ,,:   ,::ir@mingyi.irii:i:::j1jri7ZBOS7ivv,
                 ,::,    ::rv77iiiriii:iii:i::,rvLq@huhao.Li
             ,,      ,, ,:ir7ir::,:::i;ir:::i:i::rSGGYri712:
           :::  ,v7r:: ::rrv77:, ,, ,:i7rrii:::::, ir7ri7Lri
          ,     2OBBOi,iiir;r::        ,irriiii::,, ,iv7Luur:
        ,,     i78MBBi,:,:::,:,  :7FSL: ,iriii:::i::,,:rLqXv::
        :      iuMMP: :,:::,:ii;2GY7OBB0viiii:i:iii:i:::iJqL;::
       ,     ::::i   ,,,,, ::LuBBu BBBBBErii:i:i:i:i:i:i:r77ii
      ,       :       , ,,:::rruBZ1MBBqi, :,,,:::,::::::iiriri:
     ,               ,,,,::::i:  @arqiao.       ,:,, ,:::ii;i7:
    :,       rjujLYLi   ,,:::::,:::::::::,,   ,:i,:,,,,,::i:iii
    ::      BBBBBBBBB0,    ,,::: , ,:::::: ,      ,,,, ,,:::::::
    i,  ,  ,8BMMBBBBBBi     ,,:,,     ,,, , ,   , , , :,::ii::i::
    :      iZMOMOMBBM2::::::::::,,,,     ,,,,,,:,,,::::i:irr:i:::,
    i   ,,:;u0MBMOG1L:::i::::::  ,,,::,   ,,, ::::::i:i:iirii:i:i:
    :    ,iuUuuXUkFu7i:iii:i:::, :,:,: ::::::::i:i:::::iirr7iiri::
    :     :rk@Yizero.i:::::, ,:ii:::::::i:::::i::,::::iirrriiiri::,
     :      5BMBBBBBBSr:,::rv2kuii:::iii::,:i:,, , ,,:,:i@petermu.,
          , :r50EZ8MBBBBGOBBBZP7::::i::,:::::,: :,:,::i;rrririiii::
              :jujYY7LS0ujJL7r::,::i::,::::::::::::::iirirrrrrrr:ii:
           ,:  :@kevensun.:,:,,,::::i:i:::::,,::::::iir;ii;7v77;ii;i,
           ,,,     ,,:,::::::i:iiiii:i::::,, ::::iiiir@xingjief.r;7:i,
        , , ,,,:,,::::::::iiiiiiiiii:,:,:::::::::iiir;ri7vL77rrirri::
         :,, , ::::::::i:::i:::i:i::,,,,,:,::i:i:::iir;@Secbone.ii:::
'''



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
