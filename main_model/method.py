'''
Author: guo_idpc
Date: 2023-02-23 19:34:32
LastEditors: guo_idpc 867718012@qq.com
LastEditTime: 2023-03-02 11:18:17
FilePath: /bilinear/main_model/method.py
Description: 人一生会遇到约2920万人,两个人相爱的概率是0.000049,所以你不爱我,我不怪你.

Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
'''
'''
                       .::::.
                     .::::::::.
                    :::::::::::
                 ..:::::::::::'
              '::::::::::::'
                .::::::::::
           '::::::::::::::..
                ..::::::::::::.
              ``::::::::::::::::
               ::::``:::::::::'        .:::.
              ::::'   ':::::'       .::::::::.
            .::::'      ::::     .:::::::'::::.
           .:::'       :::::  .:::::::::' ':::::.
          .::'        :::::.:::::::::'      ':::::.
         .::'         ::::::::::::::'         ``::::.
     ...:::           ::::::::::::'              ``::.
    ````':.          ':::::::::'                  ::::..
                       '.:::::'                    ':'````..
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
ggggap=0.00001  #不用分片线性的gap
gap=0.01  #最终的终止条件gap
def McCormick(model,H,x,y,x1,x2,y1,y2,piece_count,n):
    
    model.addConstr(H>=x1*y+x*y1-x1*y1)
    model.addConstr(H>=x2*y+x*y2-x2*y2)
    model.addConstr(H<=x2*y+x*y1-x2*y1)
    model.addConstr(H<=x*y2+x1*y-x1*y2)
    return model
def piece_McCormick(model,H,x,y,x1,x2,y1,y2,piece_count,error,i_number,H_name,n):
    # n piece 
    #int_num = 0
    x_pieces = [model.addVar(vtype=GRB.CONTINUOUS, name=f"x_pieces{t}") for t in range(n)]
    y_pieces = [model.addVar(vtype=GRB.CONTINUOUS, name=f"y_pieces{t}") for t in range(n)]
    #print(piece_count)
    #print(error)
    c = [model.addVar(vtype=GRB.BINARY, lb=0,ub=1,name=f"c{t}") for t in range(n)]
    if abs(error[H_name][i_number])<ggggap and n == 1:
    #if H_name != "H_ct_ct":
            #break
        #print((piece_count%3)*period+int(piece_count/3))
        model.addConstr(H>=x1*y+x*y1-x1*y1)
        model.addConstr(H>=x2*y+x*y2-x2*y2)
        model.addConstr(H<=x2*y+x*y1-x2*y1)
        model.addConstr(H<=x*y2+x1*y-x1*y2)
        piece_count += 1
        return model,piece_count,1
#4 day
# [1.1780303016254399, 0.5810869555111535, 0.2502609894722792, 0.2252123670229009, 0.2026909276227415, 0.18242183303980863, 0.16164192976154745, 0.1453749243316015, 0.13083743190003658, 0.11775368870918547, 0.10333237670293788, 0.09028888827981686]
# [0.12531917513714105, 0.09299806655746894, 0.06389703028219289, 0.052622667652501995, 0.044858496356665806, 0.0479575902589254, 0.037461092909545794, 0.03270782435153799, 0.02870329255173098, 0.02497531806280051, 0.020960999871073287, 0.016089383471688125]
# [0, 133, 131, 172, 195, 196, 200, 219, 219, 227, 232, 236]
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
    #c = c[piece_count*n:piece_count*n+n]
    #y_pieces = y_pieces[piece_count*n:piece_count*n+n]
    #x_pieces = x_pieces[piece_count*n:piece_count*n+n]
    #x1_list = copy.deepcopy([x1+i*(x2-x1)/n for i in range(n)])
    #x2_list = copy.deepcopy([x1+i*(x2-x1)/n for i in range(1,1+n)])
    x1_list = [x1 for _ in range(n)]
    x2_list = [x2 for _ in range(n)]
    y1_list = [y1+i*(y2-y1)/n for i in range(n)]
    y2_list = [y1+i*(y2-y1)/n for i in range(1,1+n)]
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
    model.addConstr(H<=gp.quicksum((x2_list[i]*y_pieces[i]+x_pieces[i]*y1_list[i]-c[i]*x2_list[i]*y1_list[i]) for i in range(n)))
    model.addConstr(H<=gp.quicksum((x_pieces[i]*y2_list[i]+x1_list[i]*y_pieces[i]-c[i]*x1_list[i]*y2_list[i]) for i in range(n)))
    model.addConstr(gp.quicksum(c[i] for i in range(n)) == 1)
    model.addConstr(gp.quicksum(c[i]*x_pieces[i] for i in range(n)) == x)
    model.addConstr(gp.quicksum(c[i]*y_pieces[i] for i in range(n)) == y)
    piece_count+=1
    return model,piece_count,0
def bound_con(period,H,gap,M,T,res_M_T,n,k):
    
    k = k*(1-0.05**n)
    # m_ht_h1,t_ht_h1 = [0 for _ in range(period)],[0 for _ in range(period)]
    # m_fc_h2,t_fc_h2 = [0 for _ in range(period)],[0 for _ in range(period)]
    # m_fc_h3,t_ht_h3 = [0 for _ in range(period)],[0 for _ in range(period)]
    # m_el_h4,t_el_h4 = [0 for _ in range(period)],[0 for _ in range(period)]
    # m_el_h5,t_ht_h5 = [0 for _ in range(period)],[0 for _ in range(period)]

    # for i in range(period):
    #     #烦死了，这也会有冲突！！！！！不如取平均
    #     m_ht_h1[i],t_ht_h1[i] = move_to_feasible(n,m_ht,t_ht[i],H['H_ht_ht'][i])
    #     m_fc_h2[i],t_fc_h2[i] = move_to_feasible(n,m_fc,t_fc[i],H['H_fc_fc'][i])
    #     m_fc_h3[i],t_ht_h3[i] = move_to_feasible(n,m_fc,t_ht[i],H['H_fc_ht'][i])
    #     # m_el_h4[i],t_el_h4[i] = move_to_feasible(n,m_el,t_el[i],H['H_el_el'][i])
    #     # m_el_h5[i],t_ht_h5[i] = move_to_feasible(n,m_el,t_ht[i],H['H_el_ht'][i])
    # #print(np.mean(m_fc_h3),m_fc_h3)
    # m_ht = np.mean(m_ht_h1)
    # m_fc = np.mean(m_fc_h2+m_fc_h3)
    #m_el = np.mean(m_el_h4+m_el_h5)


    #fix





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


    m_fc = res_M_T['m_fc']
    m_ht = res_M_T['m_ht']
    m_g_hp = res_M_T['m_g_hp']
    m_g_ghp = res_M_T['m_g_ghp']
    m_g_mp = res_M_T['m_g_mp']
    m_ct = res_M_T['m_ct']
    m_q_hp = res_M_T['m_q_hp']
    m_q_ghp = res_M_T['m_q_ghp']
    m_q_mp = res_M_T['m_q_mp']

    t_ht = res_M_T['t_ht']
    t_fc = res_M_T['t_fc']
    t_g_hp = res_M_T['t_g_hp']
    t_g_ghp = res_M_T['t_g_ghp']
    t_g_mp = res_M_T['t_g_mp']
    t_g_mp_r = res_M_T['t_g_mp_r']

    t_ct = res_M_T['t_ct']
    t_q_hp = res_M_T['t_q_hp']
    t_q_ghp = res_M_T['t_q_ghp']
    t_q_mp = res_M_T['t_q_mp']
    t_q_mp_r = res_M_T['t_q_mp_r']



    #fix 存在的问题，一个温度对应多个m，按照一个fix别的误差可能会增大。
    # t_ht =  [H['H_ht_ht'][i] / m_ht for i in range(len(H['H_ht_ht']))]
    # t_cdu = res_M_T['t_cdu']
    # t_he =  res_M_T['t_he']
    # t_fc =  res_M_T['t_fc']
    # t_ct = res_M_T['t_ct']




    #init
    d_m_fc = [0 for _ in range(period)]
    d_m_ht = [0 for _ in range(period)]
    d_m_g_hp = [0 for _ in range(period)]
    d_m_g_ghp = [0 for _ in range(period)]
    d_m_g_mp = [0 for _ in range(period)]

    d_m_ct = [0 for _ in range(period)]
    d_m_q_hp = [0 for _ in range(period)]
    d_m_q_ghp = [0 for _ in range(period)]
    d_m_q_mp = [0 for _ in range(period)]
    
    d_t_ht = [0 for _ in range(period)]
    d_t_fc = [0 for _ in range(period)]
    d_t_g_hp = [0 for _ in range(period)]
    d_t_g_ghp = [0 for _ in range(period)]
    d_t_g_mp = [0 for _ in range(period)]
    d_t_g_mp_r = [0 for _ in range(period)]

    d_t_ct = [0 for _ in range(period)]
    d_t_q_hp = [0 for _ in range(period)]
    d_t_q_ghp = [0 for _ in range(period)]
    d_t_q_mp = [0 for _ in range(period)]
    d_t_q_mp_r = [0 for _ in range(period)]


    for i in range(period):

        d_m_fc[i] = max(m_fc[i]-m_fc_1[i],m_fc_2[i]-m_fc[i])
        d_m_ht[i] = max(m_ht[i]-m_ht_1[i],m_ht_2[i]-m_ht[i])
        d_m_g_hp[i] = max(m_g_hp[i]-m_g_hp_1[i],m_g_hp_2[i]-m_g_hp[i])
        d_m_g_ghp[i] = max(m_g_ghp[i]-m_g_ghp_1[i],m_g_ghp_2[i]-m_g_ghp[i])
        d_m_g_mp[i] = max(m_g_mp[i]-m_g_mp_1[i],m_g_mp_2[i]-m_g_mp[i])

        d_m_ct[i] = max(m_ct[i]-m_ct_1[i],m_ct_2[i]-m_ct[i])
        d_m_q_hp[i] = max(m_q_hp[i]-m_q_hp_1[i],m_q_hp_2[i]-m_q_hp[i])
        d_m_q_ghp[i] = max(m_q_ghp[i]-m_q_ghp_1[i],m_q_ghp_2[i]-m_q_ghp[i])
        d_m_q_mp[i] = max(m_q_mp[i]-m_q_mp_1[i],m_q_mp_2[i]-m_q_mp[i])

        d_t_ht[i] = max(t_ht[i]-t_ht_1[i],t_ht_2[i]-t_ht[i]) 
        d_t_fc[i] = max(t_fc[i]-t_fc_1[i],t_fc_2[i]-t_fc[i])
        d_t_g_hp[i] = max(t_g_hp[i]-t_g_hp_1[i],t_g_hp_2[i]-t_g_hp[i])
        d_t_g_ghp[i] = max(t_g_ghp[i]-t_g_ghp_1[i],t_g_ghp_2[i]-t_g_ghp[i])
        d_t_g_mp[i] = max(t_g_mp[i]-t_g_mp_1[i],t_g_mp_2[i]-t_g_mp[i])
        d_t_g_mp_r[i] = max(t_g_mp_r[i]-t_g_mp_r_1[i],t_g_mp_r_2[i]-t_g_mp_r[i])

        d_t_ct[i] = max(t_ct[i]-t_ct_1[i],t_ct_2[i]-t_ct[i])
        d_t_q_hp[i] = max(t_q_hp[i]-t_q_hp_1[i],t_q_hp_2[i]-t_q_hp[i])
        d_t_q_ghp[i] = max(t_q_ghp[i]-t_q_ghp_1[i],t_q_ghp_2[i]-t_q_ghp[i])
        d_t_q_mp[i] = max(t_q_mp[i]-t_q_mp_1[i],t_q_mp_2[i]-t_q_mp[i])
        d_t_q_mp_r[i] = max(t_q_mp_r[i]-t_q_mp_r_1[i],t_q_mp_r_2[i]-t_q_mp_r[i])
        


        m_fc_1[i] = max(m_fc_1[i],m_fc[i]-k*d_m_fc[i])
        m_ht_1[i] = max(m_ht_1[i],m_ht[i]-k*d_m_ht[i])
        m_g_hp_1[i] = max(m_g_hp_1[i],m_g_hp[i]-k*d_m_g_hp[i])
        m_g_ghp_1[i] = max(m_g_ghp_1[i],m_g_ghp[i]-k*d_m_g_ghp[i])
        m_g_mp_1[i] = max(m_g_mp_1[i],m_g_mp[i]-k*d_m_g_mp[i])


        t_ht_1[i] = max(t_ht_1[i],t_ht[i]-k*d_t_ht[i]) #if abs(H['H_ht_ht'][i]-m_ht*t_ht[i])/H['H_ht_ht'][i] >= 0.000001 else t_ht_1[i]
        t_fc_1[i] = max(t_fc_1[i],t_fc[i]-k*d_t_fc[i]) #if abs(H['H_fc_fc'][i]-m_fc*t_fc[i])/H['H_fc_fc'][i] >= 0.000001 else t_fc_1[i]
        t_g_hp_1[i] = max(t_g_hp_1[i],t_g_hp[i]-k*d_t_g_hp[i]) #if abs(H['H_g_hp_g_hp'][i]-m_g_hp*t_g_hp[i])/H['H_g_hp_g_hp'][i] >= 0.000001 else t_g_hp_1[i]
        t_g_ghp_1[i] = max(t_g_ghp_1[i],t_g_ghp[i]-k*d_t_g_ghp[i]) #
        t_g_mp_1[i] = max(t_g_mp_1[i],t_g_mp[i]-k*d_t_g_mp[i])
        t_g_mp_r_1[i] = max(t_g_mp_r_1[i],t_g_mp_r[i]-k*d_t_g_mp_r[i])

        t_ct_1[i] = max(t_ct_1[i],t_ct[i]-k*d_t_ct[i])
        t_q_hp_1[i] = max(t_q_hp_1[i],t_q_hp[i]-k*d_t_q_hp[i])
        t_q_ghp_1[i] = max(t_q_ghp_1[i],t_q_ghp[i]-k*d_t_q_ghp[i])
        t_q_mp_1[i] = max(t_q_mp_1[i],t_q_mp[i]-k*d_t_q_mp[i])
        t_q_mp_r_1[i] = max(t_q_mp_r_1[i],t_q_mp_r[i]-k*d_t_q_mp_r[i])

        # t_cdu_1[i] = max(t_cdu_1[i],t_cdu[i]-k*d_t_cdu[i])
        # t_he_1[i] = max(t_he_1[i],t_he[i]-k*d_t_he[i])
        # t_ct_1[i] = max(t_ct_1[i],t_ct[i]-k*d_t_ct[i])
        #t_el_1[i] = max(t_el_1[i],t_el[i]-k*d_t_el[i]) #if abs(H['H_el_el'][i]-m_el*t_el[i])/H['H_el_el'][i] >= 0.000001 else t_el_1[i]
        m_fc_2[i] = min(m_fc_2[i],m_fc[i]+k*d_m_fc[i])
        m_ht_2[i] = min(m_ht_2[i],m_ht[i]+k*d_m_ht[i])
        m_g_hp_2[i] = min(m_g_hp_2[i],m_g_hp[i]+k*d_m_g_hp[i])
        m_g_ghp_2[i] = min(m_g_ghp_2[i],m_g_ghp[i]+k*d_m_g_ghp[i])
        m_g_mp_2[i] = min(m_g_mp_2[i],m_g_mp[i]+k*d_m_g_mp[i])

        t_ht_2[i] = min(t_ht_2[i],t_ht[i]+k*d_t_ht[i]) #if abs(H['H_ht_ht'][i]-m_ht*t_ht[i])/H['H_ht_ht'][i] >= 0.000001 else t_ht_2[i]
        t_fc_2[i] = min(t_fc_2[i],t_fc[i]+k*d_t_fc[i]) #if abs(H['H_fc_fc'][i]-m_fc*t_fc[i])/H['H_fc_fc'][i] >= 0.000001 else t_fc_2[i]
        t_g_hp_2[i] = min(t_g_hp_2[i],t_g_hp[i]+k*d_t_g_hp[i])
        t_g_ghp_2[i] = min(t_g_ghp_2[i],t_g_ghp[i]+k*d_t_g_ghp[i])
        t_g_mp_2[i] = min(t_g_mp_2[i],t_g_mp[i]+k*d_t_g_mp[i])
        t_g_mp_r_2[i] = min(t_g_mp_r_2[i],t_g_mp_r[i]+k*d_t_g_mp_r[i])

        t_ct_2[i] = min(t_ct_2[i],t_ct[i]+k*d_t_ct[i])
        t_q_hp_2[i] = min(t_q_hp_2[i],t_q_hp[i]+k*d_t_q_hp[i])
        t_q_ghp_2[i] = min(t_q_ghp_2[i],t_q_ghp[i]+k*d_t_q_ghp[i])
        t_q_mp_2[i] = min(t_q_mp_2[i],t_q_mp[i]+k*d_t_q_mp[i])
        t_q_mp_r_2[i] = min(t_q_mp_r_2[i],t_q_mp_r[i]+k*d_t_q_mp_r[i])
        
        # t_cdu_2[i] = min(t_cdu_2[i],t_cdu[i]+k*d_t_cdu[i])
        # t_he_2[i] = min(t_he_2[i],t_he[i]+k*d_t_he[i])
        # t_ct_2[i] = min(t_ct_2[i],t_ct[i]+k*d_t_ct[i])
        #t_el_2[i] = min(t_el_2[i],t_el[i]+k*d_t_el[i]) #if abs(H['H_el_el'][i]-m_el*t_el[i])/H['H_el_el'][i] >= 0.000001 else t_el_2[i]
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
    return M,T