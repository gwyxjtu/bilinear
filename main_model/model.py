'''
Author: guo_idpc
Date: 2023-02-23 19:15:43
LastEditors: guo_idpc 867718012@qq.com
LastEditTime: 2023-03-13 16:22:51
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
import pandas as pd
from main_model.method import piece_McCormick

from main_model.model_load import *
from main_model.stohcastic_load import *

def opt():
    '''
    description: 优化主函数，构造物理模型
    fix : 2则是直接双线性求解
    return {*}
    '''

    fix_mode = 0 #0是bilinear，1 是fix 总管t，2是fix 设备温度，3是固定流量。


    # 系数
    k_fc = 18
    k_el = 55
    k_pv = 0.16
    k_hp = 3.4
    k_ghp_g = 4
    k_ghp_q = 5
    eta_fc = 0.9
    k_pump = 0.6/1000#0.6/1000

    # 总管的温度应当固定
    # t_g_mp = 45
    # t_q_mp = 7
    

    t_fc_min = 60
    t_fc_max = 65
    t_g_hp_min = 55
    t_g_hp_max = 60
    t_g_ghp_min = 35
    t_g_ghp_max = 55
    t_g_mp_min = 45
    t_g_mp_max = 55
    t_g_mp_r_min = 30
    t_g_mp_r_max = 45


    t_q_hp_min = 7
    t_q_hp_max = 20
    t_q_ghp_min = 5
    t_q_ghp_max = 20
    t_q_mp_min = 5
    t_q_mp_max = 10
    t_q_mp_r_min = 15
    t_q_mp_r_max = 16

    m_g_pipe_max = 100000
    m_q_pipe_max = 300000


    if fix_mode == 1:#总管
        t_fc_min = 60
        t_fc_max = 65
        t_g_hp_min = 55
        t_g_hp_max = 60
        t_g_ghp_min = 35
        t_g_ghp_max = 55
        t_g_mp_min = 50
        t_g_mp_max = 50
        t_g_mp_r_min = 30
        t_g_mp_r_max = 35


        t_q_hp_min = 5
        t_q_hp_max = 20
        t_q_ghp_min = 5
        t_q_ghp_max = 20
        t_q_mp_min = 7
        t_q_mp_max = 7
        t_q_mp_r_min = 15
        t_q_mp_r_max = 30

    if fix_mode == 2:#设备
        t_fc_min = 60
        t_fc_max = 60
        t_g_hp_min = 55
        t_g_hp_max = 55
        t_g_ghp_min = 50
        t_g_ghp_max = 50
        t_g_mp_min = 50
        t_g_mp_max = 55
        t_g_mp_r_min = 30
        t_g_mp_r_max = 45


        t_q_hp_min = 7
        t_q_hp_max = 7
        t_q_ghp_min = 8
        t_q_ghp_max = 8
        t_q_mp_min = 5
        t_q_mp_max = 10
        t_q_mp_r_min = 15
        t_q_mp_r_max = 30


    fc_max = 2500
    el_max = 1000
    hp_max = 200
    ghp_max = 350
    pump_max = 10000
    area_pv = 20000#m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub = 2000, name=f"area_pv")
    hst = 200#m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub = 2000, name=f"hst")


    c = 4200 # J/kg*C
    c_kWh = 4200/3.6/1000000
    lambda_h = 20

    
    # 读取数据
    dict_load = get_sto_load()
    ele_peak = 3100
    ele_idle = 3100*0.7
    it_rt = [0.5,0.4,0.2,0,0.1,0.3,0.4,0.5,0.7,0.8,1,0.8,0.8,0.7,0.7,0.6,0.4,0.3,0.1,0.2,0.3,0.5,0.4,0.3]*days
    it_dt = it_rt
    it_load_max = 4
    c_dt_max = 6
    


    lambda_q = 3000
    lambda_g = 3000
    lambda_p = 3000
    [g_demand,q_demand,r,water_load] = dict_load['average']
    # ele_load = [3100 for _ in range(len(g_demand))]


  
    g_demand =   dict_load['mean_mean'][0]
    q_demand =   dict_load['mean_mean'][1]
    r =          dict_load['mean_mean'][2]
    water_load = dict_load['mean_mean'][3]
    period = len(g_demand)
    # 固定设备容量



    m = gp.Model("bilinear")


    opex = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="opex")

        
    m_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0,ub = m_g_pipe_max, name=f"m_fc{t}") for t in range(period)] # fuel cells water
    # m_ht_forward = [m.addVar(vtype=GRB.CONTINUOUS, lb=0,ub = m_g_pipe_max, name=f"m_ht{t}") for t in range(period)] # hot water tank forward mass flow 
    # m_ht_reverse = [m.addVar(vtype=GRB.CONTINUOUS, lb=0,ub = m_g_pipe_max, name=f"m_ht{t}") for t in range(period)] # hot water tank reverse mass flow
    m_g_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0,ub = m_g_pipe_max, name=f"m_g_hp{t}") for t in range(period)] # waste heat pump heat sullpy mass flow 
    m_g_ghp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub = m_g_pipe_max,name=f"m_g_ghp{t}") for t in range(period)] # ground heat pump heat sullpy mass flow
    m_g_mp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub = 5*m_g_pipe_max,name=f"m_g_mp{t}") for t in range(period)] # heat sullpy main pipe mass flow

    # m_ct_forward = [m.addVar(vtype=GRB.CONTINUOUS, lb=0,ub = m_q_pipe_max, name=f"m_ct{t}") for t in range(period)] # cold water tank forward mass flow
    # m_ct_reverse = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub = m_q_pipe_max,name=f"m_ct{t}") for t in range(period)] # cold water tank reverse mass flow
    m_q_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0,ub = m_q_pipe_max, name=f"m_q_hp{t}") for t in range(period)] # waste heat pump cooling supply mass flow
    m_q_ghp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0,ub = m_q_pipe_max, name=f"m_q_ghp{t}") for t in range(period)] # ground heat pump cooling supply mass flow
    m_q_mp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0,ub = 3*m_q_pipe_max, name=f"m_q_mp{t}") for t in range(period)] # cooling supply main pipe mass flow

    t_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_fc_min,ub = t_fc_max, name=f"t_fc{t}") for t in range(period)] # outlet temperature of fuel cells cooling circuits
    # t_ht = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_ht_min, ub = t_ht_max, name=f"t_ht{t}") for t in range(period)] # temperature of hot water tank
    t_g_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_g_hp_min,ub=t_g_hp_max,name=f"t_g_hp{t}") for t in range(period)] # waste heat pump heat sullpy temperature
    t_g_ghp = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_g_ghp_min,ub = t_g_ghp_max, name=f"t_g_ghp{t}") for t in range(period)] # ground heat pump heat sullpy temperature
    t_g_mp = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_g_mp_min,ub = t_g_mp_max, name=f"t_g_mp{t}") for t in range(period)] # heat sullpy main pipe temperature
    t_g_mp_r = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_g_mp_r_min,ub = t_g_mp_r_max, name=f"t_g_mp_r{t}") for t in range(period)] # heat sullpy main pipe return temperature

    # t_ct = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_ct_min,ub = t_ct_max, name=f"t_ct{t}") for t in range(period)] # cold water tank temperature
    t_q_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_q_hp_min,ub = t_q_hp_max, name=f"t_q_hp{t}") for t in range(period)] # waste heat pump cooling supply temperature
    t_q_ghp = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_q_ghp_min,ub = t_q_ghp_max, name=f"t_q_ghp{t}") for t in range(period)] # ground heat pump cooling supply temperature
    t_q_mp = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_q_mp_min,ub=t_q_mp_max, name=f"t_q_mp{t}") for t in range(period)] # cooling supply main pipe temperature
    t_q_mp_r = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_q_mp_r_min,ub = t_q_mp_r_max, name=f"t_q_mp_r{t}") for t in range(period)] # cooling supply main pipe return temperature


    z_fc = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_fc{t}") for t in range(period)]
    z_el = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_el{t}") for t in range(period)]

    z_ghpg = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_ghpg{t}") for t in range(period)]
    z_ghpq = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=f"z_ghpq{t}") for t in range(period)]
    p_ghp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_ghp{t}") for t in range(period)] # ground source heat pump
    g_ghp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_ghp{t}") for t in range(period)] # ground source heat pump
    q_ghp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_ghp{t}") for t in range(period)] # ground source heat pump

    p_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_hp{t}") for t in range(period)] # waste heat pump
    g_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_hp{t}") for t in range(period)] # waste heat pump
    q_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_hp{t}") for t in range(period)] # waste heat pump


    #z_ele_in = [m.addVar(lb=-0.0001, ub=1.01, vtype=GRB.BINARY, name=f"z_ele_in{t}") for t in range(period)]

    #z_ele_out = [m.addVar(lb=-0.0001, ub=1.01, vtype=GRB.BINARY, name=f"z_ele_out{t}") for t in range(period)]
    # Create variables
    # ce_h = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="ce_h")
    g_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_fc{t}") for t in range(period)] # heat generated by fuel cells
    p_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_fc{t}") for t in range(period)]
    h_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_fc{t}") for t in range(period)] # hydrogen used in fuel cells

    # g_ht = [m.addVar(vtype=GRB.CONTINUOUS, lb=0,ub=0, name=f"g_ht{t}") for t in range(period)]
    # q_ct = [m.addVar(vtype=GRB.CONTINUOUS, lb=0,ub=0, name=f"q_ct{t}") for t in range(period)]

    h_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_el{t}") for t in range(period)] # hydrogen generated by electrolyzer
    p_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_el{t}") for t in range(period)] # power consumption by electrolyzer
    h_sto = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_sto{t}") for t in range(period)] # hydrogen storage
    h_pur = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_pur{t}") for t in range(period)] # hydrogen purchase

    
    p_pur = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pur{t}") for t in range(period)] # power purchase
    p_sol = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_sol{t}") for t in range(period)] # power purchase 
    p_pump = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pump{t}") for t in range(period)] # 用于刻画燃料电池换水的电能消耗
    g_slack = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_slack{t}") for t in range(period)] # 弃掉的热
    q_slack = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_slack{t}") for t in range(period)] # 弃掉的冷
    p_slack = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_slack{t}") for t in range(period)] # 弃掉的电
    # g_slack = [[m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_slack{t}_{i}") for t in range(period)] for i in range(scenario)] # 弃掉的热
    # q_slack = [[m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_slack{t}_{i}") for t in range(period)] for i in range(scenario)] # 弃掉的冷
    # p_slack = [[m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_slack{t}_{i}") for t in range(period)] for i in range(scenario)] # 弃掉的电

    p_us = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_us{t}") for t in range(period)] # 电的切负荷
    g_us = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_us{t}") for t in range(period)] # 热的切负荷
    q_us = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_us{t}") for t in range(period)] # 冷的切负荷

    c_dt = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"c_dt{t}") for t in range(period)]# 存储的工作负荷
    it_dt_n = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"it_dt_n{t}") for t in range(period)] # 分配给当前时刻的可调度负荷
    it_load = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"it_load{t}") for t in range(period)] # 数据中心workload 计算负荷

    ele_load = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"ele_load{t}") for t in range(period)] # 数据中心电负荷
    p_pv = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pv{t}") for t in range(period)]  # pv pannel

    # for i in range(int(period/24)-1):
    #     m.addConstr(t_ht[i*24+24] == t_ht[24*i])
    #     m.addConstr(t_ct[i*24+24] == t_ct[24*i])
        
    
    # m.addConstr(t_ht[-1] == t_ht[0])
    # m.addConstr(h_sto[-1] == h_sto[0])
    if fix_mode == 3:
        m.addConstrs(m_fc[i]      == 20000 for i in range(period))
        m.addConstrs(m_g_hp[i]    == 20000 for i in range(period))
        m.addConstrs(m_q_hp[i]    == 20000 for i in range(period))
        m.addConstrs(m_g_ghp[i]   == 20000 for i in range(period))
        m.addConstrs(m_q_ghp[i]   == 20000 for i in range(period))
        

    for i in range(period - 1):
        # m.addConstr(g_ht[i] + g_hp[i] + g_fc[i] + g_ghp[i] == g_demand[i] + water_load[i]+ g_slack[i])#+ g_slack[i]
        # m.addConstr(g_ht[i] == c_kWh*M_ht*(t_ht[i+1] - t_ht[i]))
        # m.addConstr(q_ct[i] + q_hp[i] + q_ghp[i] == q_demand[i]+ q_slack[i] )
        # m.addConstr(q_ct[i] == c_kWh*M_ct*(t_ct[i] - t_ct[i+1]))
        m.addConstr(h_sto[i+1] - h_sto[i] == h_pur[i] + h_el[i] - h_fc[i])
        
    # m.addConstr(g_ht[-1] + g_hp[-1] + g_fc[-1] + g_ghp[-1] == g_demand[-1] + water_load[-1]+g_slack[-1])
    # m.addConstr(g_ht[-1] == c_kWh*M_ht*(t_ht[0] - t_ht[-1]))
    # m.addConstr(q_ct[-1] + q_hp[-1] + q_ghp[-1] == q_demand[-1]+q_slack[-1])
    # m.addConstr(q_ct[-1] == c_kWh*M_ct*(t_ct[-1] - t_ct[0]))
    m.addConstr(h_sto[0] - h_sto[-1] == h_pur[-1] + h_el[-1] - h_fc[-1])


    # m.addConstr(gp.quicksum(p_pur)<=(1-cer)*(sum(ele_load)+sum(q_demand)/5+sum(g_demand)/0.9+sum(water_load)/0.9))
    m.addConstr(gp.quicksum(g_ghp)<=gp.quicksum(q_ghp)+gp.quicksum(p_ghp))
    for i in range(period):
        #m.addConstr(p_pur[i]==0)

        # m.addConstr(1000000*z_fc[i]>=g_fc[i])
        # m.addConstr(1000000*z_fc[i]>=p_fc[i])
        # m.addConstr(1000000*z_ct[i]>=p_ct[i])
        # m.addConstr(1000000*z_he[i]>=g_sol[i])
        # m.addConstr(g_demand[i]>=g_sol[i])

        # ghp
        # m.addConstr(g_demand[i]<=M*z_ghpg[i])
        m.addConstr(g_demand[i]<=100000000*(1-z_ghpq[i]))
        m.addConstr(10000000*z_ghpg[i]>=g_ghp[i])
        m.addConstr(10000000*z_ghpq[i]>=q_ghp[i])
        m.addConstr(z_ghpq[i]+z_ghpg[i]<=1)
        m.addConstr(p_ghp[i] == g_ghp[i]/k_ghp_g + q_ghp[i]/k_ghp_q)
        # m.addConstr(g_ghp[i]<=k_ghp_g*p_ghp[i])
        # m.addConstr(q_ghp[i]<=k_ghp_q*p_ghp[i])

        # waste heat pump
        m.addConstr(k_hp*p_hp[i] == g_hp[i])
        m.addConstr(q_hp[i] == g_hp[i]*(1-1/k_hp))
        


        # m.addConstr(p_el[i] + p_sol[i] + p_pump[i] + ele_load[i] + p_slack[i] == p_pur[i] + p_fc[i] + p_pv[i])
        m.addConstr(g_fc[i] == eta_fc * k_fc * h_fc[i])
        m.addConstr(p_pump[i] == k_pump * (m_fc[i]+m_g_hp[i]+m_g_ghp[i]+m_g_mp[i]+m_q_hp[i]+m_q_ghp[i]+m_q_mp[i]))
        m.addConstr(p_fc[i] == k_fc * h_fc[i])#氢燃烧产电




        m.addConstr(p_el[i] == k_el * h_el[i])


        m.addConstr(100000*z_fc[i] >= p_fc[i])
        m.addConstr(100000*z_el[i] >= p_el[i])
        m.addConstr(z_el[i] + z_fc[i] <= 1)

        m.addConstr(h_sto[i]<=hst)
        m.addConstr(h_el[i]<=hst)
        
        # heat sypply
        m.addConstr(g_fc[i] == c_kWh * m_fc[i]*(t_fc[i] - t_g_mp_r[i]))
        m.addConstr(g_hp[i] == c_kWh *m_g_hp[i]*(t_g_hp[i] - t_g_mp_r[i]))
        m.addConstr(g_ghp[i] == c_kWh *m_g_ghp[i]*(t_g_ghp[i] - t_g_mp_r[i]))
        # m.addConstr(g_ht[i] == c_kWh *(m_ht_forward[i]-m_ht_reverse[i])*(t_ht[i] - t_g_mp_r[i]))
        
        # cooling supply
        m.addConstr(q_hp[i] == c_kWh *m_q_hp[i]*(t_q_mp_r[i] - t_q_hp[i]))
        m.addConstr(q_ghp[i] == c_kWh *m_q_ghp[i]*(t_q_mp_r[i] - t_q_ghp[i]))
        # m.addConstr(q_ct[i] == c_kWh *(m_ct_forward[i]-m_ct_reverse[i])*(t_q_mp_r[i] - t_ct[i]))
        
        

        m.addConstr(p_fc[i] <= fc_max)
        m.addConstr(p_pump[i]<=pump_max)

        m.addConstr(p_el[i] <= el_max)
        m.addConstr(p_ghp[i] <= ghp_max)
        m.addConstr(p_hp[i] <= hp_max)
        m.addConstr(t_fc[i] <=t_fc_max)###
        # m.addConstr(t_ht[i] >=t_ht_min)###

        # main pipe
        # m.addConstr(H_g_mp_mp[i] == H_g_hp_hp[i] + H_g_ghp_ghp[i] + H_fc_fc[i] + H_ht_ht[i])
        # m.addConstr(H_q_mp_mp[i] == H_q_hp_hp[i] + H_q_ghp_ghp[i] + H_ct_ct[i])
        # m.addConstr(m_g_mp[i]*t_g_mp[i] == m_g_hp[i]*t_g_hp[i] + m_g_ghp[i]*t_g_ghp[i] + m_fc[i]*t_fc[i] +( m_ht_forward[i]-m_ht_reverse[i])*t_ht[i])
        # m.addConstr(m_q_mp[i]*t_q_mp[i] == m_q_hp[i]*t_q_hp[i] + m_q_ghp[i]*t_q_ghp[i] + ( m_ct_forward[i]-m_ct_reverse[i])*t_ct[i])
        # m.addConstr(m_g_mp[i] == m_g_hp[i] + m_g_ghp[i] + m_fc[i] + m_ht_forward[i] - m_ht_reverse[i])
        # m.addConstr(m_q_mp[i] == m_q_hp[i] + m_q_ghp[i] + m_ct_forward[i] - m_ct_reverse[i])
        m.addConstr(m_g_mp[i]*t_g_mp[i] == m_g_hp[i]*t_g_hp[i] + m_g_ghp[i]*t_g_ghp[i] + m_fc[i]*t_fc[i])
        m.addConstr(m_q_mp[i]*t_q_mp[i] == m_q_hp[i]*t_q_hp[i] + m_q_ghp[i]*t_q_ghp[i] )
        m.addConstr(m_g_mp[i] == m_g_hp[i] + m_g_ghp[i] + m_fc[i] )
        m.addConstr(m_q_mp[i] == m_q_hp[i] + m_q_ghp[i] )
        m.addConstr(m_g_hp[i] <= g_hp[i])
        m.addConstr(m_g_ghp[i] <= 1000000*g_ghp[i])
        m.addConstr(m_q_hp[i] <= 1000000*q_hp[i])
        m.addConstr(m_q_ghp[i] <= 1000000*q_ghp[i])
        m.addConstr(m_fc[i] <= 1000000*g_fc[i])


    for i in range(period-1):
        m.addConstr(c_dt[i+1] == c_dt[i] + it_dt[i] - it_dt_n[i+1])

    for i in range(int(period/24)):
        m.addConstr(c_dt[i*24] == 0)
    m.addConstr(c_dt[-1] == 0)

    for i in range(period):
        # 数据中心电负荷
        m.addConstr(ele_load[i] == ele_idle + (ele_peak - ele_idle) * it_load[i])
        m.addConstr(it_load[i] == it_rt[i] + it_dt_n[i])

        m.addConstr(p_pv[i]==k_pv*area_pv*r[i])

        m.addConstr(p_el[i] + p_sol[i] + p_pump[i] + ele_load[i] + p_ghp[i] + p_hp[i] + p_slack[i] == p_us[i] + p_pur[i] + p_fc[i] + p_pv[i])
        m.addConstr(g_demand[i]+water_load[i] + g_slack[i] == g_us[i] + c_kWh *m_g_mp[i]*(t_g_mp[i] - t_g_mp_r[i]))
        m.addConstr( g_hp[i] + g_fc[i] + g_ghp[i] + g_us[i] == g_demand[i] + water_load[i]+ g_slack[i])
        m.addConstr(q_demand[i] + q_slack[i] == q_us[i] + c_kWh *m_q_mp[i]*(t_q_mp_r[i] - t_q_mp[i]))
        m.addConstr(q_hp[i] + q_ghp[i] + q_us[i] == q_demand[i]+ q_slack[i] )

        m.addConstr(it_load[i] <= it_load_max)
        m.addConstr(c_dt[i] <= c_dt_max)

    m.setObjective(  opex + gp.quicksum(q_us)*lambda_q + gp.quicksum(p_us)*lambda_p + gp.quicksum(g_us)*lambda_g, GRB.MINIMIZE)

    m.addConstr(opex ==  lambda_h*gp.quicksum(h_pur)*365/days+ 
        gp.quicksum([p_pur[i]*lambda_ele_in[i] for i in range(period)])*365/days-gp.quicksum(p_sol)*lambda_ele_out*365/days)
    #-gp.quicksum(p_sol)*lambda_ele_out 
    # First optimize() call will fail - need to set NonConvex to 2
    m.params.NonConvex = 2
    m.params.MIPGap = 0.01

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
        
        print("Irreducible inconsistent subsystem is written to file 'model.ilp'")

        m.write('model.ilp')
        return 1,1,1,1,1,1,10000000
    
    # g_ht = [c_kWh*m_ht*(t_ht[i+1].X-t_ht[i].X) for i in range(period-1)]
    # g_ht.append(c_kWh*m_ht*(t_ht[0].X-t_ht[-1].X))
    # q_ct = [-c_kWh*m_ct*(t_ct[i+1].X-t_ct[i].X) for i in range(period-1)]
    # q_ct.append(-c_kWh*m_ct*(t_ct[0].X-t_ct[-1].X))
    ele_load = [ele_load[i].X for i in range(period)]

    energy_device_res = {
        'objective':m.objVal,
        "opex":opex.x,
        'p_load':ele_load,
        'p_el':[p_el[i].X for i in range(period)],
        'p_fc':[p_fc[i].X for i in range(period)],
        'p_pur':[p_pur[i].X for i in range(period)],
        'p_pump':[p_pump[i].X for i in range(period)],
        'p_sol':[p_sol[i].X for i in range(period)],
        'p_hp':[p_hp[i].X for i in range(period)],
        'p_ghp':[p_ghp[i].X for i in range(period)],
        'p_pv':[p_pv[i].X for i in range(period)],
        "p_us":[p_us[i].X for i in range(period)],
        'p_slack':[p_slack[i].X for i in range(period)],
        'c_dt':[c_dt[i].X for i in range(period)],
        'it_dt_n':[it_dt_n[i].X for i in range(period)],
        'it_load':[it_load[i].X for i in range(period)],
            


            
            
            
        "g_us":[g_us[i].X for i in range(period)],
        'g_slack':[g_slack[i].X for i in range(period)],
        'g_load':g_demand,
        'water_load':water_load,
        'total_g_load':[g_demand[i]+water_load[i] for i in range(period)],
        'g_fc':[g_fc[i].X for i in range(period)],
        'g_hp':[g_hp[i].X for i in range(period)],
        'g_ghp':[g_ghp[i].X for i in range(period)],
        'z_ghpg':[z_ghpg[i].X for i in range(period)],
        # 'g_ht':[g_ht[i].X for i in range(period)],


        'q_load':q_demand,
        "q_us":[q_us[i].X for i in range(period)],
        'q_slack':[q_slack[i].X for i in range(period)],
        'q_hp':[q_hp[i].X for i in range(period)],
        # 'q_ct':[q_ct[i].X for i in range(period)],
        'q_ghp':[q_ghp[i].X for i in range(period)],
        'z_gphq':[z_ghpq[i].X for i in range(period)],

        # 't_ht':[t_ht[i].X for i in range(period)],
        't_g_mp':[t_g_mp[i].x for i in range(period)],
        't_g_mp_r':[t_g_mp_r[i].X for i in range(period)],
        't_g_hp':[t_g_hp[i].X for i in range(period)],
        't_g_ghp':[t_g_ghp[i].X for i in range(period)],
        't_fc':[t_fc[i].X for i in range(period)],

        # 't_ct':[t_ct[i].X for i in range(period)],
        't_q_hp':[t_q_hp[i].X for i in range(period)],
        't_q_ghp':[t_q_ghp[i].X for i in range(period)],
        't_q_mp':[t_q_mp[i].x for i in range(period)],
        't_q_mp_r':[t_q_mp_r[i].X for i in range(period)],
            
        'm_fc':[m_fc[i].x for i in range(period)],
        'm_g_mp':[m_g_mp[i].x for i in range(period)],
        'm_g_hp':[m_g_hp[i].x for i in range(period)],
        'm_g_ghp':[m_g_ghp[i].x for i in range(period)],
        # 'm_ht_forward':[m_ht_forward[i].x for i in range(period)],
        # 'm_ht_reverse':[m_ht_reverse[i].x for i in range(period)],


        'm_q_hp':[m_q_hp[i].x for i in range(period)],
        'm_q_ghp':[m_q_ghp[i].x for i in range(period)],
        'm_q_mp':[m_q_mp[i].x for i in range(period)],
        # 'm_ct_forward':[m_ct_forward[i].x for i in range(period)],
        # 'm_ct_reverse':[m_ct_reverse[i].x for i in range(period)],


        'h_el':[h_el[i].X for i in range(period)],
        'h_fc':[h_fc[i].X for i in range(period)],
        'h_sto':[h_sto[i].X for i in range(period)],
        'h_pur':[h_pur[i].X for i in range(period)]

    } 
     #gp.quicksum([gp.quicksum(q_us[s]) for s in range(scenario)])*lambda_q + gp.quicksum([gp.quicksum(p_us[s]) for s in range(scenario)])*lambda_p + gp.quicksum([gp.quicksum(g_us[s]) for s in range(scenario)])*lambda_g
    # ans_ave = {
    #         "penalty_g":sum([p_us[0][i].X for i in range(period)])*lambda_p,

    #         "cer":1-sum([p_pur[i].X for i in range(period)])/(sum(ele_load[0])+sum(q_demand[0])/5+sum(g_demand[0])/0.9+sum(water_load[0])/0.9),

    #         # 'p_pv':[p_pv[i].x for i in range(period)],
    #         # 'p_load':ele_load,
    #         'c_dt':[c_dt[0][i].X for i in range(period)],
    #         'it_dt_n':[it_dt_n[0][i].X for i in range(period)],
    #         'it_load':[it_load[0][i].X for i in range(period)],
            
    #         'p_pv':[p_pv[0][i].X for i in range(period)],
    #         'g_load':g_demand[0],
    #         'water_load':water_load[0],
    #         'total_g_load':[g_demand[0][i]+water_load[0][i] for i in range(period)],

    #         'g_slack':[g_slack[0][i].X for i in range(period)],
    #         'q_slack':[q_slack[0][i].X for i in range(period)],
    #         'p_slack':[p_slack[0][i].X for i in range(period)],
    #         "p_us":[p_us[0][i].X for i in range(period)],
    #         "q_us":[q_us[0][i].X for i in range(period)],
    #         "g_us":[g_us[0][i].X for i in range(period)],
    #         'q_load':q_demand[0],
    #     }


    # ans_max = {'objective':m.objVal,
    #         "cer":1-sum([p_pur[i].X for i in range(period)])/(sum(ele_load[1])+sum(q_demand[1])/5+sum(g_demand[1])/0.9+sum(water_load[1])/0.9),
    #         # 'p_pv':[p_pv[i].x for i in range(period)],
    #         # 'p_load':ele_load,
    #         'c_dt':[c_dt[1][i].X for i in range(period)],
    #         'it_dt_n':[it_dt_n[1][i].X for i in range(period)],
    #         'it_load':[it_load[1][i].X for i in range(period)],
            
    #         'p_pv':[p_pv[1][i].X for i in range(period)],
    #         'g_load':g_demand[1],
    #         'water_load':water_load[1],
    #         'total_g_load':[g_demand[1][i]+water_load[1][i] for i in range(period)],

    #         'g_slack':[g_slack[1][i].X for i in range(period)],
    #         'q_slack':[q_slack[1][i].X for i in range(period)],
    #         'p_slack':[p_slack[1][i].X for i in range(period)],
    #         "p_us":[p_us[1][i].X for i in range(period)],
    #         "q_us":[q_us[1][i].X for i in range(period)],
    #         "g_us":[g_us[1][i].X for i in range(period)],
    #         'q_load':q_demand[1],
    #         }
    # ans_min = {'objective':m.objVal,
    #         "cer":1-sum([p_pur[i].X for i in range(period)])/(sum(ele_load[2])+sum(q_demand[2])/5+sum(g_demand[2])/0.9+sum(water_load[2])/0.9),
    #         # 'p_pv':[p_pv[i].x for i in range(period)],
    #         # 'p_load':ele_load,
    #         'c_dt':[c_dt[2][i].X for i in range(period)],
    #         'it_dt_n':[it_dt_n[2][i].X for i in range(period)],
    #         'it_load':[it_load[2][i].X for i in range(period)],
            
    #         'p_pv':[p_pv[2][i].X for i in range(period)],
    #         'g_load':g_demand[2],
    #         'water_load':water_load[2],
    #         'total_g_load':[g_demand[2][i]+water_load[2][i] for i in range(period)],

    #         'g_slack':[g_slack[2][i].X for i in range(period)],
    #         'q_slack':[q_slack[2][i].X for i in range(period)],
    #         'p_slack':[p_slack[2][i].X for i in range(period)],
    #         "p_us":[p_us[2][i].X for i in range(period)],
    #         "q_us":[q_us[2][i].X for i in range(period)],
    #         "g_us":[g_us[2][i].X for i in range(period)],
    #         'q_load':q_demand[2],
    #         }
    print("us:")
    print(sum(energy_device_res['p_us']),sum(energy_device_res['q_us']),sum(energy_device_res['g_us']))
    print("opex:")
    print(opex.x)

    return energy_device_res
