'''
Author: guo_idpc
Date: 2023-02-23 19:34:32
LastEditors: guo_idpc 867718012@qq.com
LastEditTime: 2023-02-23 20:04:56
FilePath: /bilinear/main_model/method.py
Description: 人一生会遇到约2920万人,两个人相爱的概率是0.000049,所以你不爱我,我不怪你.

Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
'''

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