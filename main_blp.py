'''
Author: guo_idpc
Date: 2023-02-23 17:19:03
LastEditors: guo_idpc 867718012@qq.com
LastEditTime: 2023-03-07 16:57:56
FilePath: /bilinear/main_blp.py
Description: 人一生会遇到约2920万人,两个人相爱的概率是0.000049,所以你不爱我,我不怪你.

Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
'''
from main_model.model import *
from main_model.method import *
from mymail import send

receivers = ['guoguoloveu@icloud.com']
def plot_for_test(res):
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


    z = [i for i in range(len(res['t_ht']))]
    plt.plot(z,res['t_ht'])
    plt.savefig('img/t_ht.png')
    plt.close()

    # exit(0)

if __name__ == '__main__':


    period = len(g_demand)

    start =time.time()
    res = opt()
   

    print(res['objective'])

    # to_csv(error,"error")
    pd.DataFrame(res).to_csv("res_for_test/test.csv")
    plot_for_test(res)
    end=time.time()
    print('Running time: %s Seconds'%(end-start))
    send('计算完毕',receivers,"ok",['res_for_test/test.csv'])