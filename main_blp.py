'''
Author: guo_idpc
Date: 2023-02-23 17:19:03
LastEditors: guo_idpc 867718012@qq.com
LastEditTime: 2023-03-03 23:19:52
FilePath: /bilinear/main_blp.py
Description: 人一生会遇到约2920万人,两个人相爱的概率是0.000049,所以你不爱我,我不怪你.

Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
'''
from main_model.model import *
from main_model.method import *
from mymail import send

receivers = ['guoguoloveu@icloud.com']
bilinear = 2 # 0就是用松弛迭代,2是gurobi直接求解
def plot_for_test(error_max,error_min,obj_print,slack_num_list,res):
    '''
    description: error放在一个图里面，obj单独一个图
    return {*}
    '''    
    import matplotlib.pyplot as plt

    x = [i for i in range(len(error_max))]
    plt.plot(x,error_max)
    plt.plot(x,error_min)
    # plt.plot(x,g_demand)
    # plt.plot(x,q_demand)
    # plt.plot(x,water_load)
    # plt.plot(x,ele_load)
    # plt.show()
    plt.savefig('img/error.png')
    plt.close()
    y = [i for i in range(len(obj_print))]
    plt.plot(y,obj_print)
    plt.savefig('img/obj.png')
    plt.close()
    z = [i for i in range(len(res['t_ht']))]
    plt.plot(z,res['t_ht'])
    plt.savefig('img/t_ht.png')
    plt.close()
    xx = [i for i in range(len(slack_num_list))]
    plt.plot(xx,slack_num_list)
    plt.savefig('img/slack_num.png')
    plt.close()
    # exit(0)

if __name__ == '__main__':
    t_ht_min = 30
    t_ht_max = 80
    t_fc_min = 55
    t_fc_max = 65
    t_g_hp_min = 45
    t_g_hp_max = 50
    t_g_ghp_min = 45
    t_g_ghp_max = 50
    t_g_mp_min = 40
    t_g_mp_max = 65
    t_g_mp_r_min = 20
    t_g_mp_r_max = 40
    t_ct_min = 5
    t_ct_max = 20




    t_q_hp_min = 5
    t_q_hp_max = 10
    t_q_ghp_min = 5
    t_q_ghp_max = 10
    t_q_mp_min = 5
    t_q_mp_max = 15
    t_q_mp_r_min = 20
    t_q_mp_r_max = 30

    period = len(g_demand)
    m_fc_1   =[0 for _ in range(period)]
    m_fc_2   =[100000 for _ in range(period)]
    m_ht_1   =[-100000 for _ in range(period)]
    m_ht_2   =[100000 for _ in range(period)]
    m_g_hp_1 =[0 for _ in range(period)]
    m_g_hp_2 =[100000 for _ in range(period)]
    m_g_ghp_1=[0 for _ in range(period)]
    m_g_ghp_2=[100000 for _ in range(period)]
    m_g_mp_1 =[0 for _ in range(period)]
    m_g_mp_2 =[500000 for _ in range(period)]

    m_q_hp_1 =[0 for _ in range(period)]
    m_q_hp_2 =[100000 for _ in range(period)]
    m_q_ghp_1=[0 for _ in range(period)]
    m_q_ghp_2=[100000 for _ in range(period)]
    m_ct_1 =[-100000 for _ in range(period)]
    m_ct_2 =[100000 for _ in range(period)]
    m_q_mp_1 =[0 for _ in range(period)]
    m_q_mp_2 =[5000000 for _ in range(period)]


    t_ht_1  = [t_ht_min for _ in range(period)]
    t_ht_2  = [t_ht_max for _ in range(period)]
    t_fc_1  = [t_fc_min for _ in range(period)]
    t_fc_2  = [t_fc_max for _ in range(period)]
    t_g_hp_1= [t_g_hp_min for _ in range(period)]
    t_g_hp_2= [t_g_hp_max for _ in range(period)]
    t_g_ghp_1=[t_g_ghp_min for _ in range(period)]
    t_g_ghp_2=[t_g_ghp_max for _ in range(period)]
    t_g_mp_1 = [t_g_mp_min for _ in range(period)]
    t_g_mp_2 = [t_g_mp_max for _ in range(period)]
    t_g_mp_r_1 = [t_g_mp_r_min for _ in range(period)]
    t_g_mp_r_2 = [t_g_mp_r_max for _ in range(period)]

    t_q_hp_1 = [t_q_hp_min for _ in range(period)]
    t_q_hp_2 = [t_q_hp_max for _ in range(period)]
    t_q_ghp_1= [t_q_ghp_min for _ in range(period)]
    t_q_ghp_2= [t_q_ghp_max for _ in range(period)]
    t_ct_1 = [t_ct_min for _ in range(period)]
    t_ct_2 = [t_ct_max for _ in range(period)]
    t_q_mp_1 = [t_q_mp_min for _ in range(period)]
    t_q_mp_2 = [t_q_mp_max for _ in range(period)]
    t_q_mp_r_1 = [t_q_mp_r_min for _ in range(period)]
    t_q_mp_r_2 = [t_q_mp_r_max for _ in range(period)]

    n =1
    #gap = ggggap
    obj = 100000000000
    max_err=[]
    mean_err=[]
    slack_num_list=[]

    error = {
        "H_fc_fc"   : [0.1 for _ in range(period)],
        "H_fc_mp"   : [0.1 for _ in range(period)],
        'H_ht_ht'   : [0.1 for _ in range(period)],
        'H_ht_mp'   : [0.1 for _ in range(period)],
        'H_g_hp_hp' : [0.1 for _ in range(period)],
        'H_g_hp_mp' : [0.1 for _ in range(period)],
        'H_g_ghp_ghp':[0.1 for _ in range(period)],
        'H_g_ghp_mp':[0.1 for _ in range(period)],
        'H_g_mp_mp' : [0.1 for _ in range(period)],
        'H_g_mp_mp_r':[0.1 for _ in range(period)],

        'H_q_hp_hp' : [0.1 for _ in range(period)],
        'H_q_hp_mp' : [0.1 for _ in range(period)],
        'H_q_ghp_ghp':[0.1 for _ in range(period)],
        'H_q_ghp_mp': [0.1 for _ in range(period)],
        'H_q_mp_mp' : [0.1 for _ in range(period)],
        'H_q_mp_mp_r':[0.1 for _ in range(period)],
        'H_ct_ct'   : [0.1 for _ in range(period)],
        'H_ct_mp'   : [0.1 for _ in range(period)],

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
    start =time.time()
    M,T,res_M_T,H,error,ans,slack_num = opt(M,T,error,0,1,1)
    M,T = bound_con(period,H,gap,M,T,res_M_T,n,0.9999)
    errorl = [abs(ee[i]) for ee in error.values() for i in range(len(ee))]
    #print(len(error))
    # max_err.append(max(errorl))
    # mean_err.append(np.mean(errorl))
    slack_num_list.append(slack_num)
    print(max(errorl))
    print(min(errorl))
    #exit(0)
    #all(error[i]>=0.005 for i in range(len(error)))
    res = ans
    obj_print=[]
    M_l,T_l = M,T
    while max(errorl)>gap or min(errorl)<-gap:

        error_last,res_last = error,ans
        M,T,res_M_T,H,error,res,slack_num = opt(M,T,error,bilinear,res_M_T,H)

        if slack_num == 10000000:
            pd.DataFrame(res_last).to_csv("res_for_test/test.csv")
            pd.DataFrame(error_last).to_csv("res_for_test/error.csv")
            # to_csv(res_last,"test")
            # to_csv(error_last,"error")
            # send('寄了',receivers,'松弛迭代',['res_for_test/test.csv',"res_for_test/error.csv"])
            print("g")
            break
            exit(0)
        # if obj == 404:
        #     break
        #res = res_new
        M_l,T_l,res_M_T_l,H_l = M,T,res_M_T,H
        M,T = bound_con(period,H,gap,M,T,res_M_T,n,0.9)
        #print(t_el_1,t_el_2)
        obj_print.append(res['objective'])
        errorl = [abs(ee[i]) for ee in error.values() for i in range(len(ee))]
        #error = [abs(error[i])for i in range(len(error))]
        max_err.append(max(errorl))
        mean_err.append(np.mean(errorl))
        slack_num_list.append(slack_num)
        if max(errorl)>0.7:
            pd.DataFrame(error).to_csv("res_for_test/errorbig.csv")
            # exit(0)
            # to_csv(error,"errorbig")
            #input()
        print(max_err)
        print(mean_err)
        print(slack_num_list)
        pd.DataFrame(res).to_csv("res_for_test/test.csv")
        pd.DataFrame(error).to_csv("res_for_test/error.csv")
        if bilinear == 2:
            # send('双线性计算完毕',receivers,'双线性算法',['res_for_test/test.csv'])
            exit(0)
        n += 1
        print(obj_print)
    print("n:")
    print(n)
    
    print('------')


    # #计算一次fix后的可行解
    M,T,res_M_T,H,error,res,slack_num = opt(M_l,T_l,error,1,res_M_T_l,H_l)
    errorl = [abs(ee[i]) for ee in error.values() for i in range(len(ee))]
    #error = [abs(error[i])for i in range(len(error))]
    max_err.append(max(errorl))
    mean_err.append(np.mean(errorl))
    obj_print.append(res['objective'])
    print(obj_print)
    print(max_err)
    print(mean_err)
    pd.DataFrame(res).to_csv("res_for_test/test.csv")
    pd.DataFrame(error).to_csv("res_for_test/error.csv")
    # to_csv(error,"error")

    plot_for_test(max_err,mean_err,obj_print,slack_num_list,res)
    end=time.time()
    print('Running time: %s Seconds'%(end-start))
    send('计算完毕',receivers,str(obj_print)+str(max_err)+str(mean_err),['res_for_test/test.csv','img/error.png','img/obj.png'])