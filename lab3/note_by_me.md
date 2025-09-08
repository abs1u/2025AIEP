# numpy 
1. create  
   
   np.array([1,2,3])  
   np.arange(10)  
   np.arange(1,10,2)  
   np.diag([1,2,3,4])  
   >注：diag既可以生成对角，又可以将方阵取对角  
   
   np.ones((5,5))  
   np.zeros((6,6))  
   np.random.rand((10,10))  
   Matric.reshape(3,5)  (或(3,-1),-1处自动补全)  
----

2. caculate  
   |加法|减法|对应元素相乘|矩阵乘法|转置|判断|  
   |----|----|----|----|----|----|  
   |+|-|*|@|.T|>/<(返回布尔)|  

   - np.sum(Matric), np.prod(Matric)
   - np.min(Matric), np.max(Matric)
   - np.any(Matric), np.all(Matric) (不知道干嘛的)
   - np.sum(Matric, axis=1) 等效于 Matric.sum(axis=1)
   - np.cumsum(Y)累加
   - 
----
3. broadcast  
   仅1\*x或x\*1可以扩充  
----
4. slice  
   Matric[:4,1:6:2]  
----
5. index  
   array可以作为array的index：  
   ```python  
   import numpy as np
   a = np.arange(10)
   b = np.array([0,2,4])
   print(a[b])
   ```
   输出`[0,2,4]`  
   ```python  
   X = np.zeros((6, 6))
   X[np.arange(2, 5), np.arange(0, 3)] = 1
   print(X)
   ```
   仅X[2,0] X[3,1] X[4,2]变为1.  
   当然，也可混搭：X[3:, [0, 2, 5]]  
   还可与布尔结合：  
   ```python
   mask = np.array([1, 0, 1, 0, 0, 1], dtype=bool)
   print(mask)
   a[mask, 2]
   ```
   输出：  
   ```python
   [ True False  True False False  True]
   array([ 2, 22, 52])
   ```  
   >104单元格：Matric.where(*condition*)
----

----
----
# sk_learn  
