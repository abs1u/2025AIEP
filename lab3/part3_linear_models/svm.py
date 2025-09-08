import numpy as np
from scipy.optimize import minimize # -line 1

def svm(X, y):
    '''
    SVM Support vector machine.

    INPUT:  X: training sample features, P-by-N matrix.
            y: training sample labels, 1-by-N row vector.

    OUTPUT: w: learned perceptron parameters, (P+1)-by-1 column vector.
            num: number of support vectors

    '''
    P, N = X.shape
    w = np.zeros((P + 1, 1))
    num = 0

    # YOUR CODE HERE
    # Please implement SVM with scipy.optimize. You should be able to implement
    # it within 20 lines of code. The optimization should converge wtih any method
    # that support constrain.
    #TODO
    # begin answer
    C = 1.0  # Regularization parameter  -line 2
    X_bias = np.vstack((np.ones((1, N)), X))  # -line 3
    y = y.flatten()  # -line 4
    def objective(w):
        return 0.5 * np.dot(w, w) + C * np.sum(np.maximum(0, 1 - y * (w @ X_bias)))

    result = minimize(objective, w.flatten(), method='SLSQP')
    w = result.x.reshape(-1, 1)
    margins = y * (w.T @ X_bias)
    num = np.sum(margins < 1 + 1e-5)
    # end answer
    return w, num

