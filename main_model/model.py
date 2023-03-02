'''
Author: guo_idpc
Date: 2023-02-23 19:15:43
LastEditors: guo_idpc 867718012@qq.com
LastEditTime: 2023-03-02 11:35:21
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



def opt(M,T,error,fix,res_M_T,H):
    '''
    description: 优化主函数，构造物理模型
    fix : 2则是直接双线性求解
    return {*}
    '''
    # 系数
    k_fc = 18
    k_el = 55
    k_pv = 0.16
    k_hp = 3.4
    k_ghp_g = 4
    k_ghp_q = 5
    eta_fc = 0.9
    k_pump = 0.6/1000#0.6/1000


    t_ht_min = 30
    t_ht_max = 80
    t_fc_min = 40
    t_fc_max = 65
    t_g_hp_min = 30
    t_g_hp_max = 65
    t_g_ghp_min = 30
    t_g_ghp_max = 60
    t_g_mp_min = 30
    t_g_mp_max = 80
    t_g_mp_r_min = 20
    t_g_mp_r_max = 80
    t_ct_min = 5
    t_ct_max = 20

    t_q_hp_min = 5
    t_q_hp_max = 20
    t_q_ghp_min = 5
    t_q_ghp_max = 20
    t_q_mp_min = 5
    t_q_mp_max = 20
    t_q_mp_r_min = 5
    t_q_mp_r_max = 30

    c = 4200 # J/kg*C
    c_kWh = 4200/3.6/1000000
    delta_T = 12
    lambda_h = 20

    # 输入的一些初始化
    m_ht_1,m_ht_2   = M["m_ht"][0], M["m_ht"][1]
    m_fc_1,m_fc_2   = M["m_fc"][0], M["m_fc"][1]
    m_g_hp_1,m_g_hp_2 = M["m_g_hp"][0], M["m_g_hp"][1]
    m_g_ghp_1,m_g_ghp_2 = M["m_g_ghp"][0], M["m_g_ghp"][1]
    m_g_mp_1,m_g_mp_2 = M["m_g_mp"][0], M["m_g_mp"][1]

    m_ct_1,m_ct_2   = M["m_ct"][0], M["m_ct"][1]
    m_q_hp_1,m_q_hp_2 = M["m_q_hp"][0], M["m_q_hp"][1]
    m_q_ghp_1,m_q_ghp_2 = M["m_q_ghp"][0], M["m_q_ghp"][1]
    m_q_mp_1,m_q_mp_2 = M["m_q_mp"][0], M["m_q_mp"][1]


    t_ht_1,t_ht_2   = T['t_ht'][0] ,T['t_ht'][1]
    t_fc_1,t_fc_2   = T['t_fc'][0] ,T['t_fc'][1]
    t_g_hp_1,t_g_hp_2 = T['t_g_hp'][0] ,T['t_g_hp'][1]
    t_g_ghp_1,t_g_ghp_2 = T['t_g_ghp'][0] ,T['t_g_ghp'][1]
    t_g_mp_1,t_g_mp_2 = T['t_g_mp'][0] ,T['t_g_mp'][1]
    t_g_mp_r_1,t_g_mp_r_2 = T['t_g_mp_r'][0] ,T['t_g_mp_r'][1]

    t_ct_1,t_ct_2   = T['t_ct'][0] ,T['t_ct'][1]
    t_q_hp_1,t_q_hp_2 = T['t_q_hp'][0] ,T['t_q_hp'][1]
    t_q_ghp_1,t_q_ghp_2 = T['t_q_ghp'][0] ,T['t_q_ghp'][1]
    t_q_mp_1,t_q_mp_2 = T['t_q_mp'][0] ,T['t_q_mp'][1]
    t_q_mp_r_1,t_q_mp_r_2 = T['t_q_mp_r'][0] ,T['t_q_mp_r'][1]
    

    period = len(g_demand)
    # 固定设备容量
    area_pv = 5000#m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub = 2000, name=f"area_pv")
    hst = 200#m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub = 2000, name=f"hst")

    # M_ht = 50000#m.addVar(vtype=GRB.CONTINUOUS, lb=m_ht_1,ub=m_ht_2, name="m_ht") # capacity of hot water tank
    # M_ct = 50000
    # fc_max = 1800
    # el_max = 1000
    # hp_max = 300
    # ghp_max = 100
    # pump_max = 10000
    # Create a new model    



    M_ht = 5000#m.addVar(vtype=GRB.CONTINUOUS, lb=m_ht_1,ub=m_ht_2, name="m_ht") # capacity of hot water tank
    M_ct = 5000
    fc_max = 3000
    el_max = 1000
    hp_max = 1000
    ghp_max = 3000
    pump_max = 10000
    m = gp.Model("bilinear")


    opex = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="opex")
    t_ct = [m.addVar(vtype=GRB.CONTINUOUS, lb=4,ub=20, name=f"t_ct{t}") for t in range(period)] # temperature of cold water tank
    if fix == 1:
        
        m_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_fc{t}") for t in range(period)] # fuel cells water
        m_ht = [m.addVar(vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name=f"m_ht{t}") for t in range(period)] # hot water tank mass flow 
        m_g_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_g_hp{t}") for t in range(period)] # waste heat pump heat sullpy mass flow 
        m_g_ghp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_g_ghp{t}") for t in range(period)] # ground heat pump heat sullpy mass flow
        m_g_mp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_g_mp{t}") for t in range(period)] # heat sullpy main pipe mass flow

        m_ct = [m.addVar(vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name=f"m_ct{t}") for t in range(period)] # cold water tank mass flow
        m_q_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_q_hp{t}") for t in range(period)] # waste heat pump cooling supply mass flow
        m_q_ghp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_q_ghp{t}") for t in range(period)] # ground heat pump cooling supply mass flow
        m_q_mp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"m_q_mp{t}") for t in range(period)] # cooling supply main pipe mass flow

        t_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"t_fc{t}") for t in range(period)] # outlet temperature of fuel cells cooling circuits
        t_ht = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"t_ht{t}") for t in range(period)] # temperature of hot water tank
        t_g_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"t_g_hp{t}") for t in range(period)] # waste heat pump heat sullpy temperature
        t_g_ghp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"t_g_ghp{t}") for t in range(period)] # ground heat pump heat sullpy temperature
        t_g_mp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"t_g_mp{t}") for t in range(period)] # heat sullpy main pipe temperature
        t_g_mp_r = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"t_g_mp_r{t}") for t in range(period)] # heat sullpy main pipe return temperature

        t_ct = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"t_ct{t}") for t in range(period)] # cold water tank temperature
        t_q_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"t_q_hp{t}") for t in range(period)] # waste heat pump cooling supply temperature
        t_q_ghp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"t_q_ghp{t}") for t in range(period)] # ground heat pump cooling supply temperature
        t_q_mp = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"t_q_mp{t}") for t in range(period)] # cooling supply main pipe temperature
        t_q_mp_r = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"t_q_mp_r{t}") for t in range(period)] # cooling supply main pipe return temperature

    else:
        m_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=m_fc_1[t],ub=m_fc_2[t], name=f"m_fc{t}") for t in range(period)] # fuel cells water
        m_ht = [m.addVar(vtype=GRB.CONTINUOUS, lb=m_ht_1[t],ub=m_ht_2[t], name=f"m_ht{t}") for t in range(period)] # hot water tank mass flow
        m_g_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=m_g_hp_1[t],ub=m_g_hp_2[t], name=f"m_g_hp{t}") for t in range(period)] # waste heat pump heat sullpy mass flow
        m_g_ghp = [m.addVar(vtype=GRB.CONTINUOUS, lb=m_g_ghp_1[t],ub=m_g_ghp_2[t], name=f"m_g_ghp{t}") for t in range(period)] # ground heat pump heat sullpy mass flow
        m_g_mp = [m.addVar(vtype=GRB.CONTINUOUS, lb=m_g_mp_1[t],ub=m_g_mp_2[t], name=f"m_g_mp{t}") for t in range(period)] # heat sullpy main pipe mass flow

        m_ct = [m.addVar(vtype=GRB.CONTINUOUS, lb=m_ct_1[t],ub=m_ct_2[t], name=f"m_ct{t}") for t in range(period)] # cold water tank mass flow
        m_q_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=m_q_hp_1[t],ub=m_q_hp_2[t], name=f"m_q_hp{t}") for t in range(period)] # waste heat pump cooling supply mass flow
        m_q_ghp = [m.addVar(vtype=GRB.CONTINUOUS, lb=m_q_ghp_1[t],ub=m_q_ghp_2[t], name=f"m_q_ghp{t}") for t in range(period)] # ground heat pump cooling supply mass flow
        m_q_mp = [m.addVar(vtype=GRB.CONTINUOUS, lb=m_q_mp_1[t],ub=m_q_mp_2[t], name=f"m_q_mp{t}") for t in range(period)] # cooling supply main pipe mass flow

        t_ht = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_ht_1[t],ub=t_ht_2[t], name=f"t_ht{t}") for t in range(period)] # temperature of hot water tank
        t_fc = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_fc_1[t],ub=t_fc_2[t], name=f"t_fc{t}") for t in range(period)] # outlet temperature of fuel cells cooling circuits
        t_g_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_g_hp_1[t],ub=t_g_hp_2[t], name=f"t_g_hp{t}") for t in range(period)] # waste heat pump heat sullpy temperature
        t_g_ghp = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_g_ghp_1[t],ub=t_g_ghp_2[t], name=f"t_g_ghp{t}") for t in range(period)] # ground heat pump heat sullpy temperature
        t_g_mp = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_g_mp_1[t],ub=t_g_mp_2[t], name=f"t_g_mp{t}") for t in range(period)] # heat sullpy main pipe supply temperature
        t_g_mp_r = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_g_mp_r_1[t],ub=t_g_mp_r_2[t], name=f"t_g_mp_r{t}") for t in range(period)] # heat sullpy main pipe return temperature

        t_ct = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_ct_1[t],ub=t_ct_2[t], name=f"t_ct{t}") for t in range(period)] # temperature of cold water tank
        t_q_hp = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_q_hp_1[t],ub=t_q_hp_2[t], name=f"t_q_hp{t}") for t in range(period)] # waste heat pump cooling supply temperature
        t_q_ghp = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_q_ghp_1[t],ub=t_q_ghp_2[t], name=f"t_q_ghp{t}") for t in range(period)] # ground heat pump cooling supply temperature
        t_q_mp = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_q_mp_1[t],ub=t_q_mp_2[t], name=f"t_q_mp{t}") for t in range(period)] # cooling supply main pipe supply temperature
        t_q_mp_r = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_q_mp_r_1[t],ub=t_q_mp_r_2[t], name=f"t_q_mp_r{t}") for t in range(period)] # cooling supply main pipe return temperature
    #m_el = m.addVar(vtype=GRB.CONTINUOUS, lb=m_el_1,ub=m_el_2, name=f"m_el") # fuel cells water
    #t_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=t_el_1[t],ub=t_el_2[t], name=f"t_el{t}") for t in range(period)] # outlet temperature of electrolyzer cooling circuits
    
    # H_ht_ht = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_ht_ht{t}") for t in range(period)]
    H_fc_fc = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_fc_fc{t}") for t in range(period)]
    H_fc_mp = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_fc_mp{t}") for t in range(period)]
    H_ht_ht = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_ht_ht{t}") for t in range(period)]
    H_ht_mp = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_ht_mp{t}") for t in range(period)]
    H_g_hp_hp = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_g_hp_hp{t}") for t in range(period)]
    H_g_hp_mp = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_g_hp_mp{t}") for t in range(period)]
    H_g_ghp_ghp = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_g_ghp_ghp{t}") for t in range(period)]
    H_g_ghp_mp = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_g_ghp_mp{t}") for t in range(period)]
    H_g_mp_mp = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_g_mp_mp{t}") for t in range(period)]
    H_g_mp_mp_r = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_g_mp_mp_r{t}") for t in range(period)]

    H_ct_ct = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_ct_ct{t}") for t in range(period)]
    H_ct_mp = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_ct_mp{t}") for t in range(period)]
    H_q_hp_hp = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_q_hp_hp{t}") for t in range(period)]
    H_q_hp_mp = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_q_hp_mp{t}") for t in range(period)]
    H_q_ghp_ghp = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_q_ghp_ghp{t}") for t in range(period)]
    H_q_ghp_mp = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_q_ghp_mp{t}") for t in range(period)]
    H_q_mp_mp = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_q_mp_mp{t}") for t in range(period)]
    H_q_mp_mp_r = [m.addVar(vtype=GRB.CONTINUOUS,lb=0, name=f"H_q_mp_mp_r{t}") for t in range(period)]


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

    g_ht = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_ht{t}") for t in range(period)]
    q_ct = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_ct{t}") for t in range(period)]
    # t_de = [m.addVar(vtype=GRB.CONTINUOUS, lb=0,name=f"t_de{t}") for t in range(period)] # outlet temparature of heat supply circuits
    # p_eb = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_eb{t}") for t in range(period)]
    # g_eb = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_eb{t}") for t in range(period)]
    # g_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_el{t}") for t in range(period)] # heat generated by Electrolyzer
    h_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_el{t}") for t in range(period)] # hydrogen generated by electrolyzer
    p_el = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_el{t}") for t in range(period)] # power consumption by electrolyzer
    h_sto = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_sto{t}") for t in range(period)] # hydrogen storage
    h_pur = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"h_pur{t}") for t in range(period)] # hydrogen purchase

    
    p_pur = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pur{t}") for t in range(period)] # power purchase
    p_sol = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_sol{t}") for t in range(period)] # power purchase 
    p_pump = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pump{t}") for t in range(period)] # 用于刻画燃料电池换水的电能消耗
    p_pv = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_pv{t}") for t in range(period)] # pv pannel
    g_slack = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"g_slack{t}") for t in range(period)] # 弃掉的热
    q_slack = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"q_slack{t}") for t in range(period)] # 弃掉的冷
    p_slack = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_slack{t}") for t in range(period)] # 弃掉的电
    # p_co = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"p_co{t}") for t in range(period)] 

    for i in range(int(period/24)-1):
        m.addConstr(t_ht[i*24+24] == t_ht[24*i])
        m.addConstr(t_ct[i*24+24] == t_ct[24*i])
    # m.addConstr(t_ht[-1] == t_ht[0])
    # m.addConstr(h_sto[-1] == h_sto[0])


    for i in range(period - 1):
        ###m.addConstr(m_ht * (t_ht[i + 1] - t_ht[i]) == m_fc * (t_cdu[i] - t_ht[i]) + m_cdu * (t_cdu[i] - t_ht[i]) - q_ct[i]/c_kWh- g_sol[i]/c_kWh )
        # m.addConstr(H_ht_ht[i+1]-H_ht_ht[i] == H_fc_cdu[i] - H_fc_ht[i]+H_cdu_cdu[i] - H_cdu_ht[i]-q_ct[i]/c_kWh- g_sol[i]/c_kWh)        
        m.addConstr(g_ht[i] + g_hp[i] + g_fc[i] + g_ghp[i] + g_slack[i]== g_demand[i] + water_load[i])#+ g_slack[i]
        m.addConstr(g_ht[i] == c_kWh*M_ht*(t_ht[i+1] - t_ht[i]))
        m.addConstr(q_ct[i] + q_hp[i] + q_ghp[i] + q_slack[i] == q_demand[i])
        m.addConstr(q_ct[i] == c_kWh*M_ct*(t_ct[i] - t_ct[i+1]))
        m.addConstr(h_sto[i+1] - h_sto[i] == h_pur[i] + h_el[i] - h_fc[i])
        
    m.addConstr(g_ht[-1] + g_hp[-1] + g_fc[-1] + g_ghp[-1] +g_slack[-1]== g_demand[-1] + water_load[-1])
    m.addConstr(g_ht[-1] == c_kWh*M_ht*(t_ht[0] - t_ht[-1]))
    m.addConstr(q_ct[-1] + q_hp[-1] + q_ghp[-1] +q_slack[-1]== q_demand[-1])
    m.addConstr(q_ct[-1] == c_kWh*M_ct*(t_ct[-1] - t_ct[0]))
    m.addConstr(h_sto[0] - h_sto[-1] == h_pur[-1] + h_el[-1] - h_fc[-1])
    piece_count=0
    slack_num=0
    #piece_McCormick(model,H,x,y,x1,x2,y1,y2,piece_count,error,i_number,H_name,n)
    if fix == 0:
        for i in range(period):
            #print(H_fc_fc[i],m_fc,t_fc[i],m_fc_1,m_fc_2,t_fc_1[i],t_fc_2[i])
            m,piece_count,int_tmp = piece_McCormick(m,H_fc_fc[i],m_fc[i],t_fc[i],m_fc_1[i],m_fc_2[i],t_fc_1[i],t_fc_2[i],piece_count,error,i,"H_fc_fc",nn)
            slack_num+=int_tmp

            m,piece_count,int_tmp = piece_McCormick(m,H_fc_mp[i],m_fc[i],t_g_mp_r[i],m_fc_1[i],m_fc_2[i],t_g_mp_r_1[i],t_g_mp_r_2[i],piece_count,error,i,"H_fc_mp",nn)
            slack_num+=int_tmp

            m,piece_count,int_tmp = piece_McCormick(m,H_ht_ht[i],m_ht[i],t_ht[i],m_ht_1[i],m_ht_2[i],t_ht_1[i],t_ht_2[i],piece_count,error,i,"H_ht_ht",nn)
            slack_num+=int_tmp

            m,piece_count,int_tmp = piece_McCormick(m,H_ht_mp[i],m_ht[i],t_g_mp_r[i],m_ht_1[i],m_ht_2[i],t_g_mp_r_1[i],t_g_mp_r_2[i],piece_count,error,i,"H_ht_mp",nn)
            slack_num+=int_tmp

            m,piece_count,int_tmp = piece_McCormick(m,H_g_hp_hp[i],m_g_hp[i],t_g_hp[i],m_g_hp_1[i],m_g_hp_2[i],t_g_hp_1[i],t_g_hp_2[i],piece_count,error,i,"H_g_hp_hp",nn)
            slack_num+=int_tmp
            
            m,piece_count,int_tmp = piece_McCormick(m,H_g_hp_mp[i],m_g_hp[i],t_g_mp_r[i],m_g_hp_1[i],m_g_hp_2[i],t_g_mp_r_1[i],t_g_mp_r_2[i],piece_count,error,i,"H_g_hp_mp",nn)
            slack_num+=int_tmp

            m,piece_count,int_tmp = piece_McCormick(m,H_g_ghp_ghp[i],m_g_ghp[i],t_g_ghp[i],m_g_ghp_1[i],m_g_ghp_2[i],t_g_ghp_1[i],t_g_ghp_2[i],piece_count,error,i,"H_g_ghp_ghp",nn)
            slack_num+=int_tmp

            m,piece_count,int_tmp = piece_McCormick(m,H_g_ghp_mp[i],m_g_ghp[i],t_g_mp_r[i],m_g_ghp_1[i],m_g_ghp_2[i],t_g_mp_r_1[i],t_g_mp_r_2[i],piece_count,error,i,"H_g_ghp_mp",nn)
            slack_num+=int_tmp

            m,piece_count,int_tmp = piece_McCormick(m,H_g_mp_mp[i],m_g_mp[i],t_g_mp[i],m_g_mp_1[i],m_g_mp_2[i],t_g_mp_1[i],t_g_mp_2[i],piece_count,error,i,"H_g_mp_mp",nn)
            slack_num+=int_tmp

            m,piece_count,int_tmp = piece_McCormick(m,H_g_mp_mp_r[i],m_g_mp[i],t_g_mp_r[i],m_g_mp_1[i],m_g_mp_2[i],t_g_mp_r_1[i],t_g_mp_r_2[i],piece_count,error,i,"H_g_mp_mp_r",nn)
            slack_num+=int_tmp
            
            # cooling main pipe
            m,piece_count,int_tmp = piece_McCormick(m,H_ct_ct[i],m_ct[i],t_ct[i],m_ct_1[i],m_ct_2[i],t_ct_1[i],t_ct_2[i],piece_count,error,i,"H_ct_ct",nn)
            slack_num+=int_tmp

            m,piece_count,int_tmp = piece_McCormick(m,H_ct_mp[i],m_ct[i],t_q_mp_r[i],m_ct_1[i],m_ct_2[i],t_q_mp_r_1[i],t_q_mp_r_2[i],piece_count,error,i,"H_ct_mp",nn)
            slack_num+=int_tmp

            m,piece_count,int_tmp = piece_McCormick(m,H_q_hp_hp[i],m_q_hp[i],t_q_hp[i],m_q_hp_1[i],m_q_hp_2[i],t_q_hp_1[i],t_q_hp_2[i],piece_count,error,i,"H_q_hp_hp",nn)
            slack_num+=int_tmp

            m,piece_count,int_tmp = piece_McCormick(m,H_q_hp_mp[i],m_q_hp[i],t_q_mp_r[i],m_q_hp_1[i],m_q_hp_2[i],t_q_mp_r_1[i],t_q_mp_r_2[i],piece_count,error,i,"H_q_hp_mp",nn)
            slack_num+=int_tmp

            m,piece_count,int_tmp = piece_McCormick(m,H_q_ghp_ghp[i],m_q_ghp[i],t_q_ghp[i],m_q_ghp_1[i],m_q_ghp_2[i],t_q_ghp_1[i],t_q_ghp_2[i],piece_count,error,i,"H_q_ghp_ghp",nn)
            slack_num+=int_tmp

            m,piece_count,int_tmp = piece_McCormick(m,H_q_ghp_mp[i],m_q_ghp[i],t_q_mp_r[i],m_q_ghp_1[i],m_q_ghp_2[i],t_q_mp_r_1[i],t_q_mp_r_2[i],piece_count,error,i,"H_q_ghp_mp",nn)
            slack_num+=int_tmp

            m,piece_count,int_tmp = piece_McCormick(m,H_q_mp_mp[i],m_q_mp[i],t_q_mp[i],m_q_mp_1[i],m_q_mp_2[i],t_q_mp_1[i],t_q_mp_2[i],piece_count,error,i,"H_q_mp_mp",nn)
            slack_num+=int_tmp

            m,piece_count,int_tmp = piece_McCormick(m,H_q_mp_mp_r[i],m_q_mp[i],t_q_mp_r[i],m_q_mp_1[i],m_q_mp_2[i],t_q_mp_r_1[i],t_q_mp_r_2[i],piece_count,error,i,"H_q_mp_mp_r",nn)
            slack_num+=int_tmp
            
        #print(piece_count)
    elif fix == 1:

        # m.addConstrs(m_fc[i] == res_M_T['m_fc'][i] for i in range(period))
        # m.addConstrs(m_g_hp[i] == res_M_T['m_g_hp'][i] for i in range(period))
        # m.addConstrs(m_g_ghp[i] == res_M_T['m_g_ghp'][i] for i in range(period))
        # m.addConstrs(m_ht[i] == res_M_T['m_ht'][i] for i in range(period))
        # m.addConstrs(m_g_mp[i] == res_M_T['m_g_mp'][i] for i in range(period))

        # m.addConstrs(m_q_hp[i] == res_M_T['m_q_hp'][i] for i in range(period))
        # m.addConstrs(m_q_ghp[i] == res_M_T['m_q_ghp'][i] for i in range(period))
        # m.addConstrs(m_ct[i] == res_M_T['m_ct'][i] for i in range(period))
        # m.addConstrs(m_q_mp[i] == res_M_T['m_q_mp'][i] for i in range(period))
        
        for i in range(period):
            # m.addConstr(g_fc[i] == c_kWh * m_fc[i]*(t_fc[i] - t_ht[i]))
            m.addConstr(H_fc_fc[i] == m_fc[i]*t_fc[i])
            m.addConstr(H_fc_mp[i] == m_fc[i]*t_g_mp_r[i])

            m.addConstr(H_ht_ht[i] == m_ht[i]*t_ht[i])
            m.addConstr(H_ht_mp[i] == m_ht[i]*t_g_mp_r[i])

            m.addConstr(H_g_hp_hp[i] == m_g_hp[i]*t_g_hp[i])
            m.addConstr(H_g_hp_mp[i] == m_g_hp[i]*t_g_mp_r[i])

            m.addConstr(H_g_ghp_ghp[i] == m_g_ghp[i]*t_g_ghp[i])
            m.addConstr(H_g_ghp_mp[i] == m_g_ghp[i]*t_g_mp_r[i])

            m.addConstr(H_g_mp_mp[i] == m_g_mp[i]*t_g_mp[i])
            m.addConstr(H_g_mp_mp_r[i] == m_g_mp[i]*t_g_mp_r[i])
            
            # cooling 
            m.addConstr(H_ct_ct[i] == m_ct[i]*t_ct[i])
            m.addConstr(H_ct_mp[i] == m_ct[i]*t_q_mp_r[i])

            m.addConstr(H_q_hp_hp[i] == m_q_hp[i]*t_q_hp[i])
            m.addConstr(H_q_hp_mp[i] == m_q_hp[i]*t_q_mp_r[i])

            m.addConstr(H_q_ghp_ghp[i] == m_q_ghp[i]*t_q_ghp[i])
            m.addConstr(H_q_ghp_mp[i] == m_q_ghp[i]*t_q_mp_r[i])

            m.addConstr(H_q_mp_mp[i] == m_q_mp[i]*t_q_mp[i])
            m.addConstr(H_q_mp_mp_r[i] == m_q_mp[i]*t_q_mp_r[i])


            m.addConstr(t_fc[i]*res_M_T['m_fc'][i] == H['H_fc_fc'][i])
            # m.addConstr(t_g_mp_r[i]*res_M_T['m_fc'][i] == H['H_fc_mp'][i])

            m.addConstr(t_ht[i]*res_M_T['m_ht'][i] == H['H_ht_ht'][i])
            # m.addConstr(t_g_mp_r[i]*res_M_T['m_ht'][i] == H['H_ht_mp'][i])

            m.addConstr(t_g_hp[i]*res_M_T['m_g_hp'][i] == H['H_g_hp_hp'][i])
            # m.addConstr(t_g_mp_r[i]*res_M_T['m_g_hp'][i] == H['H_g_hp_mp'][i])

            m.addConstr(t_g_ghp[i]*res_M_T['m_g_ghp'][i] == H['H_g_ghp_ghp'][i])
            # m.addConstr(t_g_mp_r[i]*res_M_T['m_g_ghp'][i] == H['H_g_ghp_mp'][i])

            m.addConstr(t_g_mp[i]*res_M_T['m_g_mp'][i] == H['H_g_mp_mp'][i])
            m.addConstr(t_g_mp_r[i]*res_M_T['m_g_mp'][i] == H['H_g_mp_mp_r'][i])
            

            # cooling
            m.addConstr(t_ct[i]*res_M_T['m_ct'][i] == H['H_ct_ct'][i])
            # m.addConstr(t_q_mp_r[i]*res_M_T['m_ct'][i] == H['H_ct_mp'][i])

            m.addConstr(t_q_hp[i]*res_M_T['m_q_hp'][i] == H['H_q_hp_hp'][i])
            # m.addConstr(t_q_mp_r[i]*res_M_T['m_q_hp'][i] == H['H_q_hp_mp'][i])

            m.addConstr(t_q_ghp[i]*res_M_T['m_q_ghp'][i] == H['H_q_ghp_ghp'][i])
            # m.addConstr(t_q_mp_r[i]*res_M_T['m_q_ghp'][i] == H['H_q_ghp_mp'][i])

            m.addConstr(t_q_mp[i]*res_M_T['m_q_mp'][i] == H['H_q_mp_mp'][i])
            m.addConstr(t_q_mp_r[i]*res_M_T['m_q_mp'][i] == H['H_q_mp_mp_r'][i])
            
    elif fix == 2:
        # 直接双线性
        for i in range(period):
            m.addConstr(H_fc_fc[i] == m_fc[i]*t_fc[i])
            m.addConstr(H_fc_mp[i] == m_fc[i]*t_g_mp_r[i])
            m.addConstr(H_ht_ht[i] == m_ht[i]*t_ht[i])
            m.addConstr(H_ht_mp[i] == m_ht[i]*t_g_mp_r[i])
            m.addConstr(H_g_hp_hp[i] == m_g_hp[i]*t_g_hp[i])
            m.addConstr(H_g_hp_mp[i] == m_g_hp[i]*t_g_mp_r[i])
            m.addConstr(H_g_ghp_ghp[i] == m_g_ghp[i]*t_g_ghp[i])
            m.addConstr(H_g_ghp_mp[i] == m_g_ghp[i]*t_g_mp_r[i])
            m.addConstr(H_g_mp_mp[i] == m_g_mp[i]*t_g_mp[i])
            m.addConstr(H_g_mp_mp_r[i] == m_g_mp[i]*t_g_mp_r[i])

            m.addConstr(H_ct_ct[i] == m_ct[i]*t_ct[i])
            m.addConstr(H_ct_mp[i] == m_ct[i]*t_q_mp_r[i])
            m.addConstr(H_q_hp_hp[i] == m_q_hp[i]*t_q_hp[i])
            m.addConstr(H_q_hp_mp[i] == m_q_hp[i]*t_q_mp_r[i])
            m.addConstr(H_q_ghp_ghp[i] == m_q_ghp[i]*t_q_ghp[i])
            m.addConstr(H_q_ghp_mp[i] == m_q_ghp[i]*t_q_mp_r[i])
            m.addConstr(H_q_mp_mp[i] == m_q_mp[i]*t_q_mp[i])
            m.addConstr(H_q_mp_mp_r[i] == m_q_mp[i]*t_q_mp_r[i])



    m.addConstr(gp.quicksum(p_pur)<=(1-cer)*(sum(ele_load)+sum(q_demand)/5+sum(g_demand)/0.9+sum(water_load)/0.9))
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

        m.addConstr(p_el[i] + p_sol[i] + p_pump[i] + ele_load[i] + p_slack[i] == p_pur[i] + p_fc[i] + p_pv[i])
        m.addConstr(g_fc[i] == eta_fc * k_fc * h_fc[i])
        m.addConstr(p_pump[i] == k_pump * (m_fc[i]+m_ht[i]+m_g_hp[i]+m_g_ghp[i]+m_g_mp[i]+m_ct[i]+m_q_hp[i]+m_q_ghp[i]+m_q_mp[i]))
        m.addConstr(p_fc[i] == k_fc * h_fc[i])#氢燃烧产电


        ###m.addConstr(g_sol[i] == c_kWh * m_he * (t_cdu[i] - t_he[i]))
        # m.addConstr(g_sol[i] <= c_kWh * (H_he_cdu[i] - H_he_he[i]))
        ###m.addConstr(q_ct[i] == c_kWh * m_ct * (t_cdu[i] - t_ct[i]))
        # m.addConstr(q_ct[i] == z_ct[i]*c_kWh * (H_ct_cdu[i] - H_ct_ct[i]))
        # m.addConstr(p_ct[i] >= 0.04 * q_ct[i])
        #m.addConstr(0.95*g_he[i] == c_kWh * m_idc * (t_idc[i] - t_ht[i]))
        #m.addConstr(p_idcpump[i] == 0.6/1000 * (m_ct*z_ct[i]+m_he*z_he[i]))

        m.addConstr(p_el[i] == k_el * h_el[i])
        #m.addConstr(g_el[i] == 0.2017*p_el[i])
        # m.addConstr(g_fc[i] == c_kWh * m_fc[i]*(t_fc[i] - t_ht[i]))

        m.addConstr(100000*z_fc[i] >= p_fc[i])
        m.addConstr(100000*z_el[i] >= p_el[i])
        m.addConstr(z_el[i] + z_fc[i] <= 1)
        #m.addConstr(t_el[i] <= 80)
        #m.addConstr(z_fc[i]+z_el[i]<=1)
        m.addConstr(h_sto[i]<=hst)
        m.addConstr(h_el[i]<=hst)
        #m.addConstr(t_ht[i] >= 50)
        
        # heat sypply
        m.addConstr(g_fc[i] == c_kWh *(H_fc_fc[i] - H_fc_mp[i]))
        m.addConstr(g_hp[i] == c_kWh *(H_g_hp_hp[i] - H_g_hp_mp[i]))
        m.addConstr(g_ghp[i] == c_kWh *(H_g_ghp_ghp[i] - H_g_ghp_mp[i]))
        m.addConstr(g_ht[i] == c_kWh *(H_ht_ht[i] - H_ht_mp[i]))
        m.addConstr(g_demand[i] + g_slack[i] == c_kWh *(H_g_mp_mp[i] - H_g_mp_mp_r[i]))
        
        # cooling supply
        m.addConstr(q_hp[i] == c_kWh *(H_q_hp_mp[i] - H_q_hp_hp[i]))
        m.addConstr(q_ghp[i] == c_kWh *(H_q_ghp_mp[i] - H_q_ghp_ghp[i]))
        m.addConstr(q_ct[i] == c_kWh *(H_ct_mp[i] - H_ct_ct[i]))
        m.addConstr(q_demand[i] + q_slack[i] == c_kWh *(H_q_mp_mp_r[i] - H_q_mp_mp[i]))
        

        m.addConstr(p_fc[i] <= fc_max)
        m.addConstr(p_pump[i]<=pump_max)
        #m.addConstr(p_idcpump[i]<=idcpump_max)
        #m.addConstr(p_eb[i]<=p_eb_max)
        m.addConstr(p_el[i] <= el_max)
        m.addConstr(p_ghp[i] <= ghp_max)
        m.addConstr(p_hp[i] <= hp_max)
        m.addConstr(t_fc[i] <=t_fc_max)###
        # m.addConstr(t_ht[i] <=65)###
        m.addConstr(t_ht[i] >=t_ht_min)###

        # main pipe
        m.addConstr(H_g_mp_mp[i] == H_g_hp_hp[i] + H_g_ghp_ghp[i] + H_fc_fc[i] + H_ht_ht[i])
        m.addConstr(H_q_mp_mp[i] == H_q_hp_hp[i] + H_q_ghp_ghp[i] + H_ct_ct[i])
        m.addConstr(m_g_mp[i] == m_g_hp[i] + m_g_ghp[i] + m_fc[i] + m_ht[i])
        m.addConstr(m_q_mp[i] == m_q_hp[i] + m_q_ghp[i] + m_ct[i])


        m.addConstr(p_pv[i]==k_pv*area_pv*r[i])
        # m.addConstr(t_he[i] >= 30)###
        # m.addConstr(t_cdu[i]<=95)###
        if with_rlt == 1 and fix != 1:
            m.addConstr(H_fc_fc[i]>=m_fc[i]*t_fc_1[i])
            m.addConstr(H_fc_fc[i]<=m_fc[i]*t_fc_2[i])
            m.addConstr(H_fc_mp[i]>=m_fc[i]*t_g_mp_r_1[i])
            m.addConstr(H_fc_mp[i]<=m_fc[i]*t_g_mp_r_2[i])
            m.addConstr(H_g_hp_hp[i]>=m_g_hp[i]*t_g_hp_1[i])
            m.addConstr(H_g_hp_hp[i]<=m_g_hp[i]*t_g_hp_2[i])
            m.addConstr(H_g_hp_mp[i]>=m_g_hp[i]*t_g_mp_r_1[i])
            m.addConstr(H_g_hp_mp[i]<=m_g_hp[i]*t_g_mp_r_2[i])
            m.addConstr(H_g_ghp_ghp[i]>=m_g_ghp[i]*t_g_ghp_1[i])
            m.addConstr(H_g_ghp_ghp[i]<=m_g_ghp[i]*t_g_ghp_2[i])
            m.addConstr(H_g_ghp_mp[i]>=m_g_ghp[i]*t_g_mp_r_1[i])
            m.addConstr(H_g_ghp_mp[i]<=m_g_ghp[i]*t_g_mp_r_2[i])
            m.addConstr(H_ht_ht[i]>=m_ht[i]*t_ht_1[i])
            m.addConstr(H_ht_ht[i]<=m_ht[i]*t_ht_2[i])
            m.addConstr(H_ht_mp[i]>=m_ht[i]*t_g_mp_1[i])
            m.addConstr(H_ht_mp[i]<=m_ht[i]*t_g_mp_2[i])
            m.addConstr(H_g_mp_mp[i]>=m_g_mp[i]*t_g_mp_1[i])
            m.addConstr(H_g_mp_mp[i]<=m_g_mp[i]*t_g_mp_2[i])
            m.addConstr(H_g_mp_mp_r[i]>=m_g_mp[i]*t_g_mp_r_1[i])
            m.addConstr(H_g_mp_mp_r[i]<=m_g_mp[i]*t_g_mp_r_2[i])

            m.addConstr(H_ct_ct[i]>=m_ct[i]*t_ct_1[i])
            m.addConstr(H_ct_ct[i]<=m_ct[i]*t_ct_2[i])
            m.addConstr(H_ct_mp[i]>=m_ct[i]*t_q_mp_r_1[i])
            m.addConstr(H_ct_mp[i]<=m_ct[i]*t_q_mp_r_2[i])
            m.addConstr(H_q_hp_hp[i]>=m_q_hp[i]*t_q_hp_1[i])
            m.addConstr(H_q_hp_hp[i]<=m_q_hp[i]*t_q_hp_2[i])
            m.addConstr(H_q_hp_mp[i]>=m_q_hp[i]*t_q_mp_r_1[i])
            m.addConstr(H_q_hp_mp[i]<=m_q_hp[i]*t_q_mp_r_2[i])
            m.addConstr(H_q_ghp_ghp[i]>=m_q_ghp[i]*t_q_ghp_1[i])
            m.addConstr(H_q_ghp_ghp[i]<=m_q_ghp[i]*t_q_ghp_2[i])
            m.addConstr(H_q_ghp_mp[i]>=m_q_ghp[i]*t_q_mp_r_1[i])
            m.addConstr(H_q_ghp_mp[i]<=m_q_ghp[i]*t_q_mp_r_2[i])
            m.addConstr(H_q_mp_mp[i]>=m_q_mp[i]*t_q_mp_1[i])
            m.addConstr(H_q_mp_mp[i]<=m_q_mp[i]*t_q_mp_2[i])
            m.addConstr(H_q_mp_mp_r[i]>=m_q_mp[i]*t_q_mp_r_1[i])
            m.addConstr(H_q_mp_mp_r[i]<=m_q_mp[i]*t_q_mp_r_2[i])


    
    if with_rlt == 1:
        for i in range(int(period/24)-1):
            # m.addConstr(H_ht_ht[i*24+24] == H_ht_ht[24*i])
            m.addConstr(H_ht_ht[i*24+24] == H_ht_ht[24*i])
            m.addConstr(H_ct_ct[i*24+24] == H_ct_ct[24*i])
            # m.addConstr(H_cdu_ht[i*24+24] == H_cdu_ht[24*i])
        # m.addConstr(H_ht_ht[-1] == H_ht_ht[0])
        # m.addConstr(H_fc_ht[-1] == H_fc_ht[0])
        # m.addConstr(H_cdu_ht[-1] == H_cdu_ht[0])

    # m.addConstr(m_ht>=5*m_cdu)###
    #m.addConstr(h_sto[-1] == h_sto[0])

    # m.setObjective( crf_pv * cost_pv*area_pv+ crf_el*cost_el*el_max
    #     +crf_hst * hst*cost_hst +crf_water* cost_water_hot*m_ht + crf_fc *cost_fc * fc_max + lambda_h*gp.quicksum(h_pur)*365+ 
    #     365*gp.quicksum([p_pur[i]*lambda_ele_in[i] for i in range(24)])-365*gp.quicksum(p_sol)*lambda_ele_out , GRB.MINIMIZE)
    m.setObjective(  lambda_h*gp.quicksum(h_pur)*365/days+ 
        gp.quicksum([p_pur[i]*lambda_ele_in[i] for i in range(period)])*365/days-gp.quicksum(p_sol)*lambda_ele_out*365/days, GRB.MINIMIZE)

    m.addConstr(opex ==  lambda_h*gp.quicksum(h_pur)*365/days+ 
        gp.quicksum([p_pur[i]*lambda_ele_in[i] for i in range(period)])*365/days-gp.quicksum(p_sol)*lambda_ele_out*365/days)
    #-gp.quicksum(p_sol)*lambda_ele_out 
    # First optimize() call will fail - need to set NonConvex to 2
    m.params.NonConvex = 2
    m.params.MIPGap = 0.01
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
        
        print("Irreducible inconsistent subsystem is written to file 'model.ilp'")
        if fix == 1:
            m.write('model_fix.ilp')
            print("fix solve failed")
        else:
            m.write('model.ilp')
        return 1,1,1,1,1,1,10000000
    
    # g_ht = [c_kWh*m_ht*(t_ht[i+1].X-t_ht[i].X) for i in range(period-1)]
    # g_ht.append(c_kWh*m_ht*(t_ht[0].X-t_ht[-1].X))
    # q_ct = [-c_kWh*m_ct*(t_ct[i+1].X-t_ct[i].X) for i in range(period-1)]
    # q_ct.append(-c_kWh*m_ct*(t_ct[0].X-t_ct[-1].X))
    
    ans = {'objective':m.objVal,

            #'m_wwt':m_wwt.X,
            # "capex":capex.x,
            "opex":opex.x,
            


            "cer":1-sum([p_pur[i].X for i in range(period)])/(sum(ele_load)+sum(q_demand)/5+sum(g_demand)/0.9+sum(water_load)/0.9),
            'p_pv':[p_pv[i].x for i in range(period)],
            'p_load':ele_load,
            'p_el':[p_el[i].X for i in range(period)],
            'p_fc':[p_fc[i].X for i in range(period)],
            'p_pur':[p_pur[i].X for i in range(period)],
            'p_pump':[p_pump[i].X for i in range(period)],
            'p_sol':[p_sol[i].X for i in range(period)],
            'p_hp':[p_hp[i].X for i in range(period)],
            'p_ghp':[p_ghp[i].X for i in range(period)],
            

            #'p_idcpump':[p_idcpump[i].X for i in range(period)],
            'g_load':g_demand,
            'g_fc':[g_fc[i].X for i in range(period)],
            'g_hp':[g_hp[i].X for i in range(period)],
            'g_ghp':[g_ghp[i].X for i in range(period)],
            'z_ghpg':[z_ghpg[i].X for i in range(period)],
            'g_ht':[g_ht[i].X for i in range(period)],
            # 'g_slack':[g_slack[i].X for i in range(period)],

            'q_load':q_demand,
            'q_hp':[q_hp[i].X for i in range(period)],
            'q_ct':[q_ct[i].X for i in range(period)],
            'q_ghp':[q_ghp[i].X for i in range(period)],
            'z_gphq':[z_ghpq[i].X for i in range(period)],

            'H_fc_mp':[H_fc_mp[i].X for i in range(period)],
            # 'q_ct':[q_ct[i].X for i in range(period)],
            # 'z_fc':[z_fc[i].X for i in range(period)],
            # #'g_he':[g_he[i].X for i in range(period)],
            # 'g_idc':[c_kWh * m_idc.X  * (t_idc[i].X  - t_ht[i].X )for i in range(period)],
            # 'z_ct':[z_ct[i].X for i in range(period)],
            # 'z_he':[z_he[i].X for i in range(period)],
            # 'z_idc':[z_idc[i].X for i in range(period)],

            't_ht':[t_ht[i].X for i in range(period)],
            't_g_mp':[t_g_mp[i].X for i in range(period)],
            't_g_mp_r':[t_g_mp_r[i].X for i in range(period)],
            't_g_hp':[t_g_hp[i].X for i in range(period)],
            't_g_ghp':[t_g_ghp[i].X for i in range(period)],
            't_fc':[t_fc[i].X for i in range(period)],

            't_ct':[t_ct[i].X for i in range(period)],
            't_q_hp':[t_q_hp[i].X for i in range(period)],
            't_q_ghp':[t_q_ghp[i].X for i in range(period)],
            't_q_mp':[t_q_mp[i].X for i in range(period)],
            't_q_mp_r':[t_q_mp_r[i].X for i in range(period)],

            #'m_cdu':[m_cdu[i].X for i in range(period)],
            'm_fc':[m_fc[i].x for i in range(period)],
            'm_g_mp':[m_g_mp[i].x for i in range(period)],
            'm_g_hp':[m_g_hp[i].x for i in range(period)],
            'm_g_ghp':[m_g_ghp[i].x for i in range(period)],
            'm_ht':[m_ht[i].x for i in range(period)],

            'm_q_hp':[m_q_hp[i].x for i in range(period)],
            'm_q_ghp':[m_q_ghp[i].x for i in range(period)],
            'm_q_mp':[m_q_mp[i].x for i in range(period)],
            'm_ct':[m_ct[i].x for i in range(period)],



            'h_el':[h_el[i].X for i in range(period)],
            'h_fc':[h_fc[i].X for i in range(period)],
            'h_sto':[h_sto[i].X for i in range(period)],
            'h_pur':[h_pur[i].X for i in range(period)]
            }
    H = {
            'H_fc_fc'  :m.getAttr('x', H_fc_fc),
            'H_fc_mp'  :m.getAttr('x', H_fc_mp),
            'H_ht_ht'  :m.getAttr('x', H_ht_ht),
            'H_ht_mp'  :m.getAttr('x', H_ht_mp),
            'H_g_hp_hp':m.getAttr('x', H_g_hp_hp),
            'H_g_hp_mp':m.getAttr('x', H_g_hp_mp),
            'H_g_ghp_ghp':m.getAttr('x', H_g_ghp_ghp),
            'H_g_ghp_mp':m.getAttr('x', H_g_ghp_mp),
            'H_g_mp_mp':m.getAttr('x', H_g_mp_mp),
            'H_g_mp_mp_r':m.getAttr('x', H_g_mp_mp_r),

            'H_q_hp_hp':m.getAttr('x', H_q_hp_hp),
            'H_q_hp_mp':m.getAttr('x', H_q_hp_mp),
            'H_q_ghp_ghp':m.getAttr('x', H_q_ghp_ghp),
            'H_q_ghp_mp':m.getAttr('x', H_q_ghp_mp),
            'H_q_mp_mp':m.getAttr('x', H_q_mp_mp),
            'H_q_mp_mp_r':m.getAttr('x', H_q_mp_mp_r),
            'H_ct_ct'  :m.getAttr('x', H_ct_ct),
            'H_ct_mp'  :m.getAttr('x', H_ct_mp),

        }
    M = {
        "m_fc"   :[m_fc_1,m_fc_2],
        'm_ht'   :[m_ht_1,m_ht_2],
        'm_g_mp' :[m_g_mp_1,m_g_mp_2],
        'm_g_hp' :[m_g_hp_1,m_g_hp_2],
        'm_g_ghp':[m_g_ghp_1,m_g_ghp_2],

        'm_q_hp' :[m_q_hp_1,m_q_hp_2],
        'm_q_ghp':[m_q_ghp_1,m_q_ghp_2],
        'm_q_mp' :[m_q_mp_1,m_q_mp_2],
        'm_ct'   :[m_ct_1,m_ct_2],

    }
    T = {
        "t_ht"   :[t_ht_1,t_ht_2],
        "t_fc"   :[t_fc_1,t_fc_2],
        "t_g_mp" :[t_g_mp_1,t_g_mp_2],
        "t_g_hp" :[t_g_hp_1,t_g_hp_2],
        "t_g_ghp":[t_g_ghp_1,t_g_ghp_2],
        't_g_mp_r':[t_g_mp_r_1,t_g_mp_r_2],

        "t_q_hp" :[t_q_hp_1,t_q_hp_2],
        "t_q_ghp":[t_q_ghp_1,t_q_ghp_2],
        "t_q_mp" :[t_q_mp_1,t_q_mp_2],
        "t_ct"   :[t_ct_1,t_ct_2],
        't_q_mp_r':[t_q_mp_r_1,t_q_mp_r_2],
        

    }
    res_M_T = {

        'm_fc':[m_fc[i].x for i in range(period)],
        'm_ht':[m_ht[i].x for i in range(period)],
        'm_g_mp':[m_g_mp[i].x for i in range(period)],
        'm_g_hp':[m_g_hp[i].x for i in range(period)],
        'm_g_ghp':[m_g_ghp[i].x for i in range(period)],

        'm_q_hp':[m_q_hp[i].x for i in range(period)],
        'm_q_ghp':[m_q_ghp[i].x for i in range(period)],
        'm_q_mp':[m_q_mp[i].x for i in range(period)],
        'm_ct':[m_ct[i].x for i in range(period)],



        't_ht':[t_ht[i].X for i in range(period)],
        't_fc':[t_fc[i].X for i in range(period)],
        't_g_mp':[t_g_mp[i].X for i in range(period)],
        't_g_hp':[t_g_hp[i].X for i in range(period)],
        't_g_ghp':[t_g_ghp[i].X for i in range(period)],
        't_g_mp_r':[t_g_mp_r[i].X for i in range(period)],

        't_q_hp':[t_q_hp[i].X for i in range(period)],
        't_q_ghp':[t_q_ghp[i].X for i in range(period)],
        't_q_mp':[t_q_mp[i].X for i in range(period)],
        't_ct':[t_ct[i].X for i in range(period)],
        't_q_mp_r':[t_q_mp_r[i].X for i in range(period)],

    }
    error = {
        # "H_ht_ht"   : [(H_ht_ht[i].X-m_ht.X*t_ht[i].X)/    (m_ht.X*t_ht[i].X  +0.001)  for i in range(period)],
        "H_fc_fc"   : [(H_fc_fc[i].X-m_fc[i].X*t_fc[i].X)/    (m_fc[i].X*t_fc[i].X  +0.001)  for i in range(period)],
        "H_fc_mp"   : [(H_fc_mp[i].X-m_fc[i].X*t_g_mp_r[i].X)/    (m_fc[i].X*t_g_mp_r[i].X  +0.001)  for i in range(period)],
        'H_ht_ht'   : [(H_ht_ht[i].X-m_ht[i].X*t_ht[i].X)/    (m_ht[i].X*t_ht[i].X  +0.001)  for i in range(period)],
        'H_ht_mp'   : [(H_ht_mp[i].X-m_ht[i].X*t_g_mp_r[i].X)/    (m_ht[i].X*t_g_mp_r[i].X  +0.001)  for i in range(period)],
        'H_g_hp_hp' : [(H_g_hp_hp[i].X-m_g_hp[i].X*t_g_hp[i].X)/    (m_g_hp[i].X*t_g_hp[i].X  +0.001)  for i in range(period)],
        'H_g_hp_mp' : [(H_g_hp_mp[i].X-m_g_hp[i].X*t_g_mp_r[i].X)/    (m_g_hp[i].X*t_g_mp_r[i].X  +0.001)  for i in range(period)],
        'H_g_ghp_ghp':[(H_g_ghp_ghp[i].X-m_g_ghp[i].X*t_g_ghp[i].X)/    (m_g_ghp[i].X*t_g_ghp[i].X  +0.001)  for i in range(period)],
        'H_g_ghp_mp':[(H_g_ghp_mp[i].X-m_g_ghp[i].X*t_g_mp_r[i].X)/    (m_g_ghp[i].X*t_g_mp_r[i].X  +0.001)  for i in range(period)],
        'H_g_mp_mp' : [(H_g_mp_mp[i].X-m_g_mp[i].X*t_g_mp[i].X)/    (m_g_mp[i].X*t_g_mp[i].X  +0.001)  for i in range(period)],
        'H_g_mp_mp_r':[(H_g_mp_mp_r[i].X-m_g_mp[i].X*t_g_mp_r[i].X)/    (m_g_mp[i].X*t_g_mp_r[i].X  +0.001)  for i in range(period)],

        'H_q_hp_hp' : [(H_q_hp_hp[i].X-m_q_hp[i].X*t_q_hp[i].X)/    (m_q_hp[i].X*t_q_hp[i].X  +0.001)  for i in range(period)],
        'H_q_hp_mp' : [(H_q_hp_mp[i].X-m_q_hp[i].X*t_q_mp_r[i].X)/    (m_q_hp[i].X*t_q_mp_r[i].X  +0.001)  for i in range(period)],
        'H_q_ghp_ghp':[(H_q_ghp_ghp[i].X-m_q_ghp[i].X*t_q_ghp[i].X)/    (m_q_ghp[i].X*t_q_ghp[i].X  +0.001)  for i in range(period)],
        'H_q_ghp_mp':[(H_q_ghp_mp[i].X-m_q_ghp[i].X*t_q_mp_r[i].X)/    (m_q_ghp[i].X*t_q_mp_r[i].X  +0.001)  for i in range(period)],
        'H_q_mp_mp' : [(H_q_mp_mp[i].X-m_q_mp[i].X*t_q_mp[i].X)/    (m_q_mp[i].X*t_q_mp[i].X  +0.001)  for i in range(period)],
        'H_q_mp_mp_r':[(H_q_mp_mp_r[i].X-m_q_mp[i].X*t_q_mp_r[i].X)/    (m_q_mp[i].X*t_q_mp_r[i].X  +0.001)  for i in range(period)],
        'H_ct_ct'   : [(H_ct_ct[i].X-m_ct[i].X*t_ct[i].X)/    (m_ct[i].X*t_ct[i].X  +0.001)  for i in range(period)],
        'H_ct_mp'   : [(H_ct_mp[i].X-m_ct[i].X*t_q_mp_r[i].X)/    (m_ct[i].X*t_q_mp_r[i].X  +0.001)  for i in range(period)],

    }
    print('g_fc:')
    print(max([g_fc[i].X for i in range(period)]))
    print('p_fc:')
    print(max([p_fc[i].X for i in range(period)]))
    print("-----")
    return M,T,res_M_T,H,error,ans,slack_num
