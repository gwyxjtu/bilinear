'''
Author: guo_idpc
Date: 2023-03-08 16:36:12
LastEditors: guo_idpc 867718012@qq.com
LastEditTime: 2023-03-09 22:32:55
FilePath: /bilinear/main_model/stohcastic_load.py
Description: 人一生会遇到约2920万人,两个人相爱的概率是0.000049,所以你不爱我,我不怪你.

Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
'''
'''
Author: guo_idpc
Date: 2023-02-24 15:03:18
LastEditors: guo_idpc 867718012@qq.com
LastEditTime: 2023-03-08 16:25:26
FilePath: /bilinear/main_model/model_load.py
Description: 人一生会遇到约2920万人,两个人相爱的概率是0.000049,所以你不爱我,我不怪你.

Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
'''
import pandas as pd
import csv
cer = 0.1
days=12



def crf(year):
    i = 0.08
    crf=((1+i)**year)*i/((1+i)**year-1);
    return crf


def get_sto_load():
    ele_load = []
    g_demand = []
    q_demand = []
    r_solar = []


    #--------------
    lambda_ele_in = [0.3748,0.3748,0.3748,0.3748,0.3748,0.3748,0.3748,0.8745,0.8745,0.8745,1.4002,1.4002,1.4002,1.4002,
                    1.4002,0.8745,0.8745,0.8745,1.4002,1.4002,1.4002,0.8745,0.8745,0.3748]
    lambda_ele_out = 0.1

    ele_load = []
    g_demand = []
    q_demand = []
    r_solar = []

    book_cold = pd.read_excel('./data/cold.xlsx')
    book_heat = pd.read_excel('./data/heat.xlsx')
    for l in range(8760):
        q_demand.append(book_cold.iloc[l,1])
        ele_load.append(4/3*book_cold.iloc[l,1])

    # 热负荷从榆林里面出，包括生活热水
    book_water = pd.read_excel('./data/yulin_water_load.xlsx')
    g_demand = list(book_water['供暖热负荷(kW)'].fillna(0))
    water_load = list(book_water['生活热水负荷kW'].fillna(0))

    r_solar =  [0 for i in range(8760+24)]
    with open("data/"+"solar.csv") as renewcsv:
        renewcsv.readline()
        renewcsv.readline()
        renewcsv.readline()
        renew = csv.DictReader(renewcsv)
        
        i=0
        for row in renew:

            r_solar[i] += float(row['electricity'])
            i+=1
    r_solar = r_solar[-8:]+r_solar[:-8]



    g_demand = [g_demand[i]/2 for i in range(len(ele_load))]
    # g_demand = [1000 if g_demand[i] >=0 else 0 for i in range(len(ele_load))]
    q_demand = [q_demand[i]/2 for i in range(len(ele_load))]
    ele_load = [ele_load[i]/2 for i in range(len(ele_load))]
    water_load = [water_load[i]/2 if water_load[i] != 0 else 1 for i in range(len(ele_load))]
    r=r_solar



    m_month = [31,28,31,30,31,30,31,31,30,31,30,31]
    m_date = [sum(m_month[:i])*24 for i in range(12)]
    m_date.append(8760)
    # g_demand = [0 for i in range(8760)]
    # for h in [1,2,3,11,12]:
    #     g_demand[m_date[h-1]:m_date[h]] = [1 for _ in range(m_date[h]-m_date[h-1])]

    lambda_ele_in = lambda_ele_in*days
    period = len(g_demand)


    # 构建光伏、冷、热、生活热水负荷的随机场景，构造12天，分别峰值最大、均值最大.热负荷优先级最高，没有热负荷的时候是冷负荷

    #峰值最大
    peak_g = [[0 for _ in range(m_month[j])] for j in range(12)]
    mean_g = [[0 for _ in range(m_month[j])] for j in range(12)]
    peak_q = [[0 for _ in range(m_month[j])] for j in range(12)]
    mean_q = [[0 for _ in range(m_month[j])] for j in range(12)]

    for i,date in enumerate(m_date[:-1]):
        for j in range(m_date[i+1]-m_date[i]):
            peak_g[i][j//24] = max(peak_g[i][j//24],g_demand[date+j])
            mean_g[i][j//24] += g_demand[date+j]
            peak_q[i][j//24] = max(peak_q[i][j//24],q_demand[date+j])
            mean_q[i][j//24] += q_demand[date+j]

    peak_g_max_day = [peak_g[i].index(max(peak_g[i])) if max(peak_g[i])!=0 else -1 for i in range(12)]
    peak_g_min_day = [peak_g[i].index(min(peak_g[i])) if max(peak_g[i])!=0 else -1 for i in range(12)]
    peak_q_max_day = [peak_q[i].index(max(peak_q[i])) for i in range(12)]
    peak_q_min_day = [peak_q[i].index(min(peak_q[i])) for i in range(12)]
    mean_g_max_day = [mean_g[i].index(max(mean_g[i])) if max(peak_g[i])!=0 else -1 for i in range(12)]
    mean_g_min_day = [mean_g[i].index(min(mean_g[i])) if max(peak_g[i])!=0 else -1 for i in range(12)]
    mean_q_max_day = [mean_q[i].index(max(mean_q[i])) for i in range(12)]
    mean_q_min_day = [mean_q[i].index(min(mean_q[i])) for i in range(12)]


    return_dict = {}

    g_demand_final = []
    q_demand_final = []
    r_final = []
    water_load_final = []

    g_demand_final = g_demand[384+24:384+48]+g_demand[1080+24:1080+48]+g_demand[1752:1752+24]+g_demand[2496+48:2496+72]+g_demand[3216:3216+24]+g_demand[3960:3960+24]+g_demand[4680+48:4680+72]+g_demand[5424:5424+24]+g_demand[6168:6168+24]+g_demand[6888+24:6888+48]+g_demand[7632:7632+24]+g_demand[8352:8352+24]
    q_demand_final = q_demand[384+24:384+48]+q_demand[1080+24:1080+48]+q_demand[1752:1752+24]+q_demand[2496+48:2496+72]+q_demand[3216:3216+24]+q_demand[3960:3960+24]+q_demand[4680+48:4680+72]+q_demand[5424:5424+24]+q_demand[6168:6168+24]+q_demand[6888+24:6888+48]+q_demand[7632:7632+24]+q_demand[8352:8352+24]
    r_final =   r_solar[384+24:384+48]+ r_solar[1080+24:1080+48]+ r_solar[1752:1752+24]+ r_solar[2496+48:2496+72]+ r_solar[3216:3216+24]+ r_solar[3960:3960+24]+ r_solar[4680+48:4680+72]+ r_solar[5424:5424+24]+ r_solar[6168:6168+24]+r_solar[6888+24:6888+48]+r_solar[7632:7632+24]+r_solar[8352:8352+24]
    water_load_final = water_load[384+24:384+48]+water_load[1080+24:1080+48]+water_load[1752:1752+24]+water_load[2496+48:2496+72]+water_load[3216:3216+24]+water_load[3960:3960+24]+water_load[4680+48:4680+72]+water_load[5424:5424+24]+water_load[6168:6168+24]+water_load[6888+24:6888+48]+water_load[7632:7632+24]+water_load[8352:8352+24]
    return_dict['average'] = [g_demand_final,q_demand_final,r_final,water_load_final]


    g_demand_final = []
    q_demand_final = []
    r_final = []
    water_load_final = []
    # load peak mean
    for i in range(12):
        if peak_g_max_day[i] == -1:
            g_demand_final+=g_demand[m_date[i]+peak_q_min_day[i]*24:m_date[i]+(peak_q_min_day[i]+1)*24]
            q_demand_final += q_demand[m_date[i]+peak_q_min_day[i]*24:m_date[i]+(peak_q_min_day[i]+1)*24]
            r_final += r[m_date[i]+peak_q_min_day[i]*24:m_date[i]+(peak_q_min_day[i]+1)*24]
            water_load_final += water_load[m_date[i]+peak_q_min_day[i]*24:m_date[i]+(peak_q_min_day[i]+1)*24]
        else:
            g_demand_final+=g_demand[m_date[i]+peak_g_min_day[i]*24:m_date[i]+(peak_g_min_day[i]+1)*24]
            q_demand_final += q_demand[m_date[i]+peak_g_min_day[i]*24:m_date[i]+(peak_g_min_day[i]+1)*24]
            r_final += r[m_date[i]+peak_g_min_day[i]*24:m_date[i]+(peak_g_min_day[i]+1)*24]
            water_load_final += water_load[m_date[i]+peak_g_min_day[i]*24:m_date[i]+(peak_g_min_day[i]+1)*24]
    return_dict['peak_max'] = [g_demand_final,q_demand_final,r_final,water_load_final]

    # # load peak max
    g_demand_final = []
    q_demand_final = []
    r_final = []
    water_load_final = []

    for i in range(12):
        if peak_g_max_day[i] == -1:
            g_demand_final+=g_demand[m_date[i]+peak_q_max_day[i]*24:m_date[i]+(peak_q_max_day[i]+1)*24]
            q_demand_final += q_demand[m_date[i]+peak_q_max_day[i]*24:m_date[i]+(peak_q_max_day[i]+1)*24]
            r_final += r[m_date[i]+peak_q_max_day[i]*24:m_date[i]+(peak_q_max_day[i]+1)*24]
            water_load_final += water_load[m_date[i]+peak_q_max_day[i]*24:m_date[i]+(peak_q_max_day[i]+1)*24]
        else:
            g_demand_final+=g_demand[m_date[i]+peak_g_max_day[i]*24:m_date[i]+(peak_g_max_day[i]+1)*24]
            q_demand_final += q_demand[m_date[i]+peak_g_max_day[i]*24:m_date[i]+(peak_g_max_day[i]+1)*24]
            r_final += r[m_date[i]+peak_g_max_day[i]*24:m_date[i]+(peak_g_max_day[i]+1)*24]
            water_load_final += water_load[m_date[i]+peak_g_max_day[i]*24:m_date[i]+(peak_g_max_day[i]+1)*24]
    g_demand_final = [g_demand_final[i]*1.1+100 for i in range(len(g_demand_final))]
    q_demand_final = [q_demand_final[i] for i in range(len(q_demand_final))]
    water_load_final = [water_load_final[i] for i in range(len(water_load_final))]
    return_dict['peak_min'] = [g_demand_final,q_demand_final,r_final,water_load_final]


    # laod mean max
    g_demand_final = []
    q_demand_final = []
    r_final = []
    water_load_final = []
    for i in range(12):
        if mean_g_max_day[i] == -1:
            g_demand_final+=g_demand[m_date[i]+mean_q_max_day[i]*24:m_date[i]+(mean_q_max_day[i]+1)*24]
            q_demand_final += q_demand[m_date[i]+mean_q_max_day[i]*24:m_date[i]+(mean_q_max_day[i]+1)*24]
            r_final += r[m_date[i]+mean_q_max_day[i]*24:m_date[i]+(mean_q_max_day[i]+1)*24]
            water_load_final += water_load[m_date[i]+mean_q_max_day[i]*24:m_date[i]+(mean_q_max_day[i]+1)*24]
        else:
            g_demand_final+=g_demand[m_date[i]+mean_g_max_day[i]*24:m_date[i]+(mean_g_max_day[i]+1)*24]
            q_demand_final += q_demand[m_date[i]+mean_g_max_day[i]*24:m_date[i]+(mean_g_max_day[i]+1)*24]
            r_final += r[m_date[i]+mean_g_max_day[i]*24:m_date[i]+(mean_g_max_day[i]+1)*24]
            water_load_final += water_load[m_date[i]+mean_g_max_day[i]*24:m_date[i]+(mean_g_max_day[i]+1)*24]
    return_dict['mean_max'] = [g_demand_final,q_demand_final,r_final,water_load_final]

    # load mean min
    g_demand_final = []
    q_demand_final = []
    r_final = []
    water_load_final = []
    for i in range(12):
        if mean_g_min_day[i] == -1:
            g_demand_final+=g_demand[m_date[i]+mean_q_min_day[i]*24:m_date[i]+(mean_q_min_day[i]+1)*24]
            q_demand_final += q_demand[m_date[i]+mean_q_min_day[i]*24:m_date[i]+(mean_q_min_day[i]+1)*24]
            r_final += r[m_date[i]+mean_q_min_day[i]*24:m_date[i]+(mean_q_min_day[i]+1)*24]
            water_load_final += water_load[m_date[i]+mean_q_min_day[i]*24:m_date[i]+(mean_q_min_day[i]+1)*24]
        else:
            g_demand_final+=g_demand[m_date[i]+mean_g_min_day[i]*24:m_date[i]+(mean_g_min_day[i]+1)*24]
            q_demand_final += q_demand[m_date[i]+mean_g_min_day[i]*24:m_date[i]+(mean_g_min_day[i]+1)*24]
            r_final += r[m_date[i]+mean_g_min_day[i]*24:m_date[i]+(mean_g_min_day[i]+1)*24]
            water_load_final += water_load[m_date[i]+mean_g_min_day[i]*24:m_date[i]+(mean_g_min_day[i]+1)*24]
    return_dict['mean_min'] = [g_demand_final,q_demand_final,r_final,water_load_final]

    # 按照每一天每一小时的平衡值
    g_demand_final = []
    q_demand_final = []
    r_final = []
    water_load_final = []
    for i in range(12):
        g_demand_tmp = [[0 for _ in range(m_month[i])] for _ in range(24)]
        q_demand_tmp = [[0 for _ in range(m_month[i])] for _ in range(24)]
        r_final_tmp = [[0 for _ in range(m_month[i])] for _ in range(24)]
        water_load_tmp = [[0 for _ in range(m_month[i])] for _ in range(24)]
        for j in range(m_month[i]):
            for t in range(24):
                g_demand_tmp[t][j] = g_demand[m_date[i]+j*24+t]
                q_demand_tmp[t][j] = q_demand[m_date[i]+j*24+t]
                r_final_tmp[t][j] = r[m_date[i]+j*24+t]
                water_load_tmp[t][j] = water_load[m_date[i]+j*24+t]
        g_demand_final += [sum(g_demand_tmp[ii])/len(g_demand_tmp[ii]) for ii in range(24)]
        q_demand_final += [sum(q_demand_tmp[ii])/len(q_demand_tmp[ii]) for ii in range(24)]
        r_final += [sum(r_final_tmp[ii])/len(r_final_tmp[ii]) for ii in range(24)]
        water_load_final += [sum(water_load_tmp[ii])/len(water_load_tmp[ii]) for ii in range(24)]
    return_dict['mean_mean'] = [g_demand_final,q_demand_final,r_final,water_load_final]
    print(1)
    # import matplotlib.pyplot as plt
    # # print(g_demand)
    # # print(q_demand)
    # x = [i for i in range(len(g_demand_final))]
    # plt.plot(x,g_demand_final)
    # plt.plot(x,q_demand_final)
    # plt.plot(x,water_load_final)
    # plt.plot(x,r_final)
    # # plt.show()
    # plt.savefig('img/sto_load_min.png')
    # # exit(0)

    #g_de = g_de_w*days
    #r = r*days
    # m_de = [g_de[i]/c_kWh/delta_T for i in range(len(g_de))]

    return return_dict

get_sto_load()