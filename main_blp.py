'''
Author: guo_idpc
Date: 2023-02-23 17:19:03
LastEditors: guo_idpc 867718012@qq.com
LastEditTime: 2023-03-13 22:21:09
FilePath: /bilinear/main_blp.py
Description: 人一生会遇到约2920万人,两个人相爱的概率是0.000049,所以你不爱我,我不怪你.

Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
'''
from main_model.model import *
from main_model.method import *
from mymail import send

receivers = ['guoguoloveu@icloud.com']
def plot_for_test(res,dict_sto):
    '''
    description: error放在一个图里面，obj单独一个图
    return {*}
    '''    
    import matplotlib.pyplot as plt
    x = [i for i in range(len(res['p_fc']))]
    plt.plot(x,res['t_fc'])
    plt.savefig('img/t_fc.png')
    plt.close()
    plt.plot(x,res['t_g_mp'])
    plt.savefig('img/t_g_mp.png')
    plt.close()
    plt.plot(x,res['t_g_mp_r'])
    plt.savefig('img/t_g_mp_r.png')
    plt.close()
    plt.plot(x,res['t_g_hp'])
    plt.savefig('img/t_g_hp.png')
    plt.close()
    plt.plot(x,res['t_g_ghp'])
    plt.savefig('img/t_g_ghp.png')
    plt.close()



    plt.close()

    # [res_ave,res_max,res_min] = dict_sto
    # 不同场景的冷热负荷光伏的图
    x = [i for i in range(len(res['p_fc']))]
    plt.plot(x,dict_sto[0]['c_dt'],label = "ave")
    plt.plot(x,dict_sto[1]['c_dt'],label = "max")
    plt.plot(x,dict_sto[2]['c_dt'],label = "min")
    plt.legend()
    plt.savefig('img/c_dt.png')
    plt.close()

    plt.plot(x,dict_sto[0]['it_load'],label = "ave")
    plt.plot(x,dict_sto[1]['it_load'],label = "max")    
    plt.plot(x,dict_sto[2]['it_load'],label = "min")
    plt.legend()
    plt.savefig('img/it_load.png')
    plt.close()

    plt.plot(x,dict_sto[0]['g_load'],label = "ave")
    plt.plot(x,dict_sto[1]['g_load'],label = "max")
    plt.plot(x,dict_sto[2]['g_load'],label = "min")
    plt.legend()
    plt.savefig('img/g_load.png')
    plt.close()


    plt.plot(x,dict_sto[0]['water_load'],label = "ave")
    plt.plot(x,dict_sto[1]['water_load'],label = "max")
    plt.plot(x,dict_sto[2]['water_load'],label = "min")
    plt.legend()
    plt.savefig('img/water_load.png')
    plt.close()

    plt.plot(x,dict_sto[0]['q_load'],label = "ave")
    plt.plot(x,dict_sto[1]['q_load'],label = "max")
    plt.plot(x,dict_sto[2]['q_load'],label = "min")
    plt.legend()
    plt.savefig('img/q_load.png')
    plt.close()
    # exit(0)

if __name__ == '__main__':


    period = len(g_demand)

    start =time.time()
    #[1,0,0]   [0.8,0.1,0.1]
    res,dict_sto = opt(0,[0.8,0.1,0.1],300)
   

    print(res['objective'])

    # to_csv(error,"error")
    pd.DataFrame(res).to_csv("res_for_test/test.csv")
    [res_ave,res_max,res_min] = dict_sto
    pd.DataFrame(res_ave).to_csv("res_for_test/res_ave.csv")
    pd.DataFrame(res_max).to_csv("res_for_test/res_max.csv")
    pd.DataFrame(res_min).to_csv("res_for_test/res_min.csv")
    plot_for_test(res,dict_sto)
    end=time.time()
    print('Running time: %s Seconds'%(end-start))
    # send('计算完毕',receivers,"ok"+str(res['obj_penalty_plot'])+","+str(res['obj_common_plot']))