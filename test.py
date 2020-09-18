import numpy as np
import matplotlib.pyplot as plt
import h5py

sigmoid = lambda x: 1. / (1 + np.exp(-x))


def load_data():
    train_set = h5py.File('datasets/train_catvnoncat.h5', 'r')
    train_set_feature = np.array(train_set['train_set_x'])  # (209,64,64,3)
    train_set_label = np.array(train_set['train_set_y'])  # (209,)    [0 0 1 0 0]
    train_set_label = train_set_label.reshape((1, train_set_label.shape[0]))  # (1, 209)

    test_set = h5py.File('datasets/test_catvnoncat.h5', 'r')
    test_set_feature = np.array(test_set['test_set_x'])  # (50,64,64,3)
    test_set_label = np.array(test_set['test_set_y'])  # (50,) [1 1 1 1 1 0 1...]
    test_set_label = test_set_label.reshape((1, test_set_label.shape[0]))  # (1, 50)

    classes = np.array(test_set['list_classes'])  # [b'non-cat' b'cat']

    return train_set_feature, train_set_label, test_set_feature, test_set_label, classes


# 读取数据
train_set_feature, train_set_label, test_set_feature, test_set_label, classes = load_data()
train_set_num = train_set_label.shape[1]
test_set_num = test_set_label.shape[1]
num_px = train_set_feature.shape[1]
# 将训练集的特征列表降维为(64*64*3, 209), 并将颜色值/255, 使得每个元素在[0,1]之间
train_set_feature = train_set_feature.reshape(train_set_feature.shape[0], -1).T
train_set_feature = train_set_feature / 255
# 将特征集的特征列表降维为(64*64*3, 50), 并将颜色值/255, 使得每个元素在[0,1]之间
test_set_feature = test_set_feature.reshape(test_set_feature.shape[0], -1).T
test_set_feature = test_set_feature / 255


def initWb(dim):
    W = np.zeros((1, dim))
    b = 0
    return (W, b)


def propagate(W, b, X, Y):
    '''
    实现前向和后向传播的成本函数及其梯度
    :param W: (1,n0)
    :param b: 标量
    :param X: (n0,m)
    :param Y: (1,m)
    :return: Tuple-(grad,L)
    '''
    m = X.shape[1]
    # 正向传播
    A = sigmoid(np.dot(W, X) + b)
    L = np.sum(-Y * np.log(A) - (1 - Y) * np.log(1 - A)) / m
    # 反向传播
    dW = (1 / m) * np.dot(A - Y, X.T)
    db = (1 / m) * np.sum(A - Y)
    grad = {'dW': dW, 'db': db}
    return (grad, L)


def optimize(W, b, X, Y, num_iter, lr, isPrint=True):
    Ls = []
    for i in range(num_iter):
        grad, L = propagate(W, b, X, Y)
        dW = grad['dW']
        db = grad['db']
        W = W - lr * dW
        b = b - lr * db
        # 每迭代100次,记录1次损失函数的值
        if (i % 100 == 0):
            Ls.append(L)
            if (isPrint):
                print("迭代的次数: %i ， 误差值： %f" % (i, L))

    Wb = {'W': W, 'b': b}
    grad = {'dW': dW, 'db': db}
    return (Wb, grad, Ls)


def predict(W, b, X):
    n0 = X.shape[0]
    m = X.shape[1]
    # 初始化 预测结果矩阵Y_hat的初始值为0
    Y_hat = np.zeros((1, m))
    W = W.reshape((1, n0))
    # A.shape = (1,m)
    A = sigmoid(np.dot(W, X) + b)
    # 对预测值逻辑回归,即概率>0.5视为1,否则视为0
    for i in range(m):
        Y_hat[0, i] = 1 if (A[0, i] > 0.5) else 0
    return Y_hat


def model(train_feature, train_label, test_feature, test_label, num_iter=2000, lr=0.5, isPrint=True):
    W, b = initWb(train_feature.shape[0])
    Wb, grad, Ls = optimize(W, b, train_feature, train_label, num_iter, lr, isPrint)
    W, b = Wb['W'], Wb['b']
    Y_hat_train = predict(W, b, train_feature)
    Y_hat_test = predict(W, b, test_feature)
    print("训练集准确性:", 100 - np.mean(np.abs(Y_hat_train - train_label)) * 100, '%')
    print("测试集准确性:", 100 - np.mean(np.abs(Y_hat_test - test_label)) * 100, '%')
    d = {'Ls': Ls, 'Y_hat_train': Y_hat_train, 'Y_hat_test': Y_hat_test, 'W': W, 'b': b, 'lr': lr, 'num_iter': num_iter}
    return d


d = model(train_set_feature, train_set_label, test_set_feature, test_set_label)
Ls = np.squeeze(d['Ls'])
plt.plot(Ls)
plt.xlabel('iteration(per hundreds)')
plt.ylabel('Losses')
plt.title('lr=' + str(d['lr']))
plt.show()
