

if __name__ == '__main__':
    m_ht_1,m_ht_2 = 10000,100000
    t_ht_1 = [50 for _ in range(period)]
    t_ht_2 = [80 for _ in range(period)]
    m_fc_1,m_fc_2 = 1000,10000
    t_fc_1 = [50 for _ in range(period)]
    t_fc_2 = [80 for _ in range(period)]
    #m_el_1,m_el_2 =10000,100000
    #t_el_1 = [50 for _ in range(period+1)]
    #t_el_2 = [80 for _ in range(period+1)]
    n=1
    gap = ggggap
    obj = 100000000000
    max_err=[]
    mean_err=[]
    slack_num_list=[]
    error = [1 for _ in range(period*nn*3)]
    obj,m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2,H,error,res,slack_num = opt(obj,m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2,error)
    m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2 = bound_con(H,gap,m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2,
        res['m_ht'],res['m_fc'],res['t_ht'],res['t_fc'],n,0.9)
    error = [abs(error[i])for i in range(len(error))]
    max_err.append(max(error))
    mean_err.append(np.mean(error))
    slack_num_list.append(slack_num)
    print(max(error))
    print(min(error))
    #exit(0)
    #all(error[i]>=0.005 for i in range(len(error)))
    start =time.time()
    obj_print=[]
    while max(error)>gap or min(error)<-gap:
        obj,m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2,H,error,res_new,slack_num = opt(obj,m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2,error)
        if obj == 404:
            break
        res = res_new
        m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2 = bound_con(H,gap,m_ht_1,m_ht_2,t_ht_1,t_ht_2,m_fc_1,m_fc_2,t_fc_1,t_fc_2,
            res['m_ht'],res['m_fc'],res['t_ht'],res['t_fc'],n,0.9)
        #print(t_el_1,t_el_2)
        obj_print.append(res['objective'])
        error = [abs(error[i])for i in range(len(error))]
        max_err.append(max(error))
        mean_err.append(np.mean(error))
        slack_num_list.append(slack_num)
        print(max_err)
        print(mean_err)
        print(slack_num_list)
        n += 1
    print(n)
    print(obj_print)
    print('------')


    #计算一次fix后的可行解
    #res = fix_solve(res['m_ht'],res['m_fc'])
    items = list(res.keys())
    wb = xlwt.Workbook()
    total = wb.add_sheet('test')
    for i in range(len(items)):
        total.write(0,i,items[i])
        if type(res[items[i]]) == list:
            sum = 0
            print(items[i])
            for j in range(len(res[items[i]])):
                total.write(j+2,i,(res[items[i]])[j])
                # sum += (res[items[i]])[j]
            # total.write(1,i,sum)
        else:
            total.write(1,i,res[items[i]])
    print(max_err)
    print(mean_err)
    print(slack_num_list)
    filename = 'res/McCormick1' + '.xls'
    wb.save(filename)
    end=time.time()
    print('Running time: %s Seconds'%(end-start))