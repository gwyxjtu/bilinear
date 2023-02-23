import numpy as np

def basic_gauss(A,b):# 基本高斯消去法
    augA = np.concatenate((A,b),axis=1)
    print('augmented A:\n',augA)
    rows = A.shape[0]
    # elimination
    for k in range(rows):
        for i in range(k+1,rows):
            mi = augA[i,k]/augA[k,k]    # augA[k,k]不能为0
            augA[i,:] = augA[i,:] - augA[k,:]*mi
        print('#elimination:\n',augA)     
    print(augA[:,-1].tolist())
    print(augA[:,:-1].tolist())
    # back substitution    
    x = np.zeros(rows)  
    k = rows-1
    x[k] = augA[k,-1]/augA[k,k] 
    for k in range(rows-2,-1,-1):
        tx = x[k+1:]
        ta = augA[k,k+1:-1].flatten()
        x[k] = (augA[k,-1]-np.sum(tx*ta))/augA[k,k]           
    return x
if __name__ == '__main__':    
    A = np.array([[1, 1, 1, 1,2],
                  [0, 4,-1, 2,2],
                  [2,-2, 1, 4,2],
                  [3, 1,-3, 2,2]],dtype='float')
    b = np.array([[10,13,17,4]],dtype='float').T
    x = basic_gauss(A,b)
    print('x =',x)
