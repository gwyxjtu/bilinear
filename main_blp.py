'''
Author: guo_idpc
Date: 2023-02-23 17:19:03
LastEditors: guo_idpc 867718012@qq.com
LastEditTime: 2023-02-27 14:57:20
FilePath: /bilinear/main_blp.py
Description: 人一生会遇到约2920万人,两个人相爱的概率是0.000049,所以你不爱我,我不怪你.

Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
'''
from main_model.model import *
from main_model.method import *

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
    period = len(g_demand)
    # m_ht_1,m_ht_2   = 100000,1000000
    m_fc_1   =[0 for _ in range(period)]
    m_fc_2   =[100000 for _ in range(period)]
    # m_cdu_1,m_cdu_2 = 100000,1000000
    # m_he_1,m_he_2   = 10000,100000
    # m_ct_1,m_ct_2   = 10000,100000
    t_ht_1  = [40 for _ in range(period)]
    t_ht_2  = [65 for _ in range(period)]
     
    t_fc_1  = [40 for _ in range(period)]
    t_fc_2  = [65 for _ in range(period)]

    # t_cdu_1 = [65 for _ in range(period)]
    # t_cdu_2 = [95 for _ in range(period)]

    # t_he_1  = [40 for _ in range(period)]
    # t_he_2  = [95 for _ in range(period)]

    # t_ct_1  = [20 for _ in range(period)]
    # t_ct_2  = [95 for _ in range(period)]
    #m_el_1,m_el_2 =10000,100000
    #t_el_1 = [50 for _ in range(period+1)]
    #t_el_2 = [80 for _ in range(period+1)]
    n =1
    #gap = ggggap
    obj = 100000000000
    max_err=[]
    mean_err=[]
    slack_num_list=[]
    #error = [1 for _ in range(period*nn*3)]
    error = {
        # "H_ht_ht"   : [0.1 for _ in range(period)],
        "H_fc_fc"   : [0.1 for _ in range(period)],
        "H_fc_ht"   : [0.1 for _ in range(period)],
        # "H_fc_cdu"  : [0.1 for _ in range(period)],
        # "H_cdu_cdu" : [0.1 for _ in range(period)],
        # "H_cdu_ht"  : [0.1 for _ in range(period)],
        # "H_he_he"   : [0.1 for _ in range(period)],
        # "H_he_cdu"  : [0.1 for _ in range(period)],
        # "H_ct_cdu"  : [0.1 for _ in range(period)],
        # "H_ct_ct"   : [0.1 for _ in range(period)]
    }
    M = {
        # "m_ht"   :[m_ht_1,m_ht_2],
        "m_fc"   :[m_fc_1,m_fc_2],
        # "m_cdu"  :[m_cdu_1,m_cdu_2],
        # "m_he"   :[m_he_1,m_he_2],
        # "m_ct"   :[m_ct_1,m_ct_2]
    }
    T = {
        "t_ht"   :[t_ht_1,t_ht_2],
        "t_fc"   :[t_fc_1,t_fc_2],
        # "t_cdu"  :[t_cdu_1,t_cdu_2],
        # "t_he"   :[t_he_1,t_he_2],
        # "t_ct"   :[t_ct_1,t_ct_2]
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
        M,T,res_M_T,H,error,res,slack_num = opt(M,T,error,0,res_M_T,H)

        if slack_num == 10000000:
            pd.DataFrame(res_last).to_csv("res_for_test/test.csv")
            pd.DataFrame(error_last).to_csv("res_for_test/error.csv")
            # to_csv(res_last,"test")
            # to_csv(error_last,"error")
            print("g")
            exit(0)
        # if obj == 404:
        #     break
        #res = res_new
        M_l,T_l = M,T
        M,T = bound_con(period,H,gap,M,T,res_M_T,n,0.8)
        #print(t_el_1,t_el_2)
        obj_print.append(res['objective'])
        errorl = [abs(ee[i]) for ee in error.values() for i in range(len(ee))]
        #error = [abs(error[i])for i in range(len(error))]
        max_err.append(max(errorl))
        mean_err.append(np.mean(errorl))
        slack_num_list.append(slack_num)
        if max(errorl)>0.7:
            pd.DataFrame(error).to_csv("res_for_test/errorbig.csv")
            # to_csv(error,"errorbig")
            #input()
        print(max_err)
        print(mean_err)
        print(slack_num_list)
        n += 1
        print(obj_print)
    print("n:")
    print(n)
    
    print('------')


    # #计算一次fix后的可行解
    M,T,res_M_T,H,error,res,slack_num = opt(M_l,T_l,error,1,res_M_T,H)
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