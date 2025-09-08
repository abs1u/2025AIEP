import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def logistic(X, y):
    '''
    LR Logistic Regression.

    INPUT:  X: training sample features, P-by-N matrix.
            y: training sample labels, 1-by-N row vector.

    OUTPUT: w: learned parameters, (P+1)-by-1 column vector.
    '''
    P, N = X.shape
    w = np.zeros((P + 1, 1))
    # YOUR CODE HERE
    # begin answer
    #TODO
    X_bias = np.vstack((np.ones((1, N)), X))
    y_logistic = (y + 1) / 2  # 将y的取值从{-1, 1}转换为{0, 1}
    alpha = 0.1 #learning rate
    max_iter = 500

    for i in range(max_iter):
        z = w.T @ X_bias
        predicted = sigmoid(z)
        error = predicted - y_logistic
        gradient = X_bias @ error.T / N
        w -= alpha * gradient
    # end answer
    
    return w
