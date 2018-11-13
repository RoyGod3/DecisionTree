import math
import pickle
import pandas as pd

def calcShannonEnt(dataSet):
    '''
    计算香农熵  #计算结果标签的信息熵 Ent(D) = -pi * log pi
    :param dataSet:数据集
    :return: 计算结果
    '''

    numEntries = len(dataSet)
    labelCounts = {}
    for featVec in dataSet:  # 遍历每个实例，统计标签的频数
        currentLabel = featVec[-1]
        if currentLabel not in labelCounts.keys():
            labelCounts[currentLabel] = 0
        labelCounts[currentLabel] += 1
    shannonEnt = 0.0
    for key in labelCounts:
        prob = float(labelCounts[key]) / numEntries
        shannonEnt -= prob * math.log(prob, 2)  # 以2为底的对数
    return shannonEnt

def splitDataSet(dataSet, axis, value):
    '''
    按照给定特征划分数据集
    :param dataSet:待划分的数据集
    :param axis:划分数据集的特征
    :param value: 需要返回的特征的值
    :return: 划分结果列表
    '''
    retDataSet = []
    for featVec in dataSet:
        if featVec[axis] == value:
            reducedFeatVec = list(featVec[:axis])  # chop out axis used for splitting
            reducedFeatVec.extend(featVec[axis + 1:])  # 在已存在的列表中添加新的列表内容
            retDataSet.append(reducedFeatVec)
    return retDataSet

def calcConditionalEntropy(dataSet, i, uniqueVals):
    '''
    计算X_i给定的条件下，Y的条件熵
    :param dataSet:数据集
    :param i:维度i
    :param featList: 数据集特征列表
    :param uniqueVals: 数据集特征集合
    :return: 条件熵
    '''
    conditionEnt = 0.0
    for value in uniqueVals:
        subDataSet = splitDataSet(dataSet, i, value)
        prob = len(subDataSet) / float(len(dataSet))  # 极大似然估计概率
        subdataSetEnt = calcShannonEnt(subDataSet)
        conditionEnt += prob * subdataSetEnt  # 条件熵的计算
    return conditionEnt

def calcInformationGain(dataSet, baseEntropy, i):
    '''
    计算信息增益 Gain(D,i) = Ent(D) - pi * Ent(Di)
    :param dataSet:数据集
    :param baseEntropy:数据集的信息熵
    :param i: 特征维度i
    :return: 特征i对数据集的信息增益g(D|X_i)
    '''
    featList = [example[i] for example in dataSet]  # 第i维特征列表
    uniqueVals = set(featList)  # 转换成集合
    newEntropy = calcConditionalEntropy(dataSet, i, uniqueVals)
    infoGain = baseEntropy - newEntropy  # 信息增益，就yes熵的减少，也就yes不确定性的减少
    return infoGain

def calcInformationGainRatio(dataSet, baseEntropy, i):
    '''
    计算信息增益比
    :param dataSet:数据集
    :param baseEntropy:数据集的信息熵
    :param i: 特征维度i
    :return: 特征i对数据集的信息增益比gR(D|X_i)
    '''
    return calcInformationGain(dataSet, baseEntropy, i) / baseEntropy

def chooseBestFeatureToSplitByID3(dataSet):
    '''
    使用ID3算法选择最好的数据集划分方式
    :param dataSet:数据集
    :return: 划分结果
    '''
    numFeatures = len(dataSet[0]) - 1  # 最后一列yes分类标签，不属于特征向量
    baseEntropy = calcShannonEnt(dataSet)
    bestInfoGain = 0.0   # 初始化信息增益
    bestFeature = -1
    for i in range(numFeatures):  # 遍历所有特征
        infoGain = calcInformationGain(dataSet, baseEntropy, i)     # 计算信息增益
        if (infoGain > bestInfoGain):  # 选择最大的信息增益
            bestInfoGain = infoGain
            bestFeature = i
    return bestFeature  # 返回最优特征对应的维度

def chooseBestFeatureToSplitByC4_5(dataSet):
    '''
    使用C4.5算法选择最好的数据集划分方式
    :param dataSet:数据集
    :return: 划分结果
    '''
    numFeatures = len(dataSet[0]) - 1  # 最后一列yes分类标签，不属于特征向量
    baseEntropy = calcShannonEnt(dataSet)
    bestInfoGain = 0.0   # 初始化信息增益
    bestFeature = -1
    for i in range(numFeatures):  # 遍历所有特征
        infoGain = calcInformationGainRatio(dataSet, baseEntropy, i)     # 计算信息增益比
        if (infoGain > bestInfoGain):  # 选择最大的信息增益
            bestInfoGain = infoGain
            bestFeature = i
    return bestFeature  # 返回最优特征对应的维度


def majorityCnt(classList):
    '''
    采用多数表决的方法决定叶结点的分类
    :param: 所有的类标签列表
    :return: 出现次数最多的类
    '''
    import operator
    classCount = {}
    for vote in classList:                  # 统计所有类标签的频数
        if vote not in classCount.keys():
            classCount[vote] = 0
        classCount[vote] += 1
    sortedClassCount = sorted(
        classCount.items(),
        key=operator.itemgetter(1),
        reverse=True)  # 排序
    return sortedClassCount[0][0]

def createTree(dataSet, labels):
    '''
    创建决策树
    :param: dataSet:训练数据集
    :param: labels:所有的类标签
    :return: myTree:决策树模型
    '''
    classList = [example[-1] for example in dataSet]
    length = classList.count(classList[0])  #如果classList里的值是同一个，length = len(classList)
    if length == len(classList):
        return classList[0]             # 第一个递归结束条件：所有的类标签完全相同
    if len(dataSet[0]) == 1:
        return majorityCnt(classList)   # 第二个递归结束条件：用完了所有特征
    bestFeat = chooseBestFeatureToSplitByID3(dataSet)   # 最优划分特征
    bestFeatLabel = labels[bestFeat]
    myTree = {bestFeatLabel: {}}         # 使用字典类型储存树的信息
    del(labels[bestFeat])
    featValues = [example[bestFeat] for example in dataSet]
    uniqueVals = set(featValues)
    for value in uniqueVals:
        subLabels = labels[:]       # 复制所有类标签，保证每次递归调用时不改变原始列表的内容
        myTree[bestFeatLabel][value] = createTree(
            splitDataSet(dataSet, bestFeat, value), subLabels)
    return myTree

def storeTree(inputTree, filename):
    fw = open(filename, 'wb')   #以二进制格式写入文件
    pickle.dump(inputTree, fw)
    fw.close()

def grabTree(filename):
    fr = open(filename, 'rb')
    return pickle.load(fr)

def readCsv():
    df = pd.read_csv("baidu_api_data.csv")  # 读取数据库数据
    data = df.values
    labels = ['completeness', 'illumination', 'blur', 'race_probability']
    return list(data), labels

def classify(inputTree, featLabels, testVec):
    '''
           利用决策树进行分类
    :param: inputTree:构造好的决策树模型
    :param: featLabels:所有的类标签
    :param: testVec:测试数据
    :return: 分类决策结果
    '''
    # firstStr = inputTree.keys()[0]  python2.7
    firstStr = list(inputTree.keys())[0]  # python3 keys() 方法以列表返回一个字典所有的键。
    secondDict = inputTree[firstStr]
    #featLabels.insert(2, 'house?')
    featLabels.insert(3, 'glasses')
    featIndex = featLabels.index(firstStr)
    key = testVec[featIndex]
    valueOfFeat = secondDict[key]
    if isinstance(
            valueOfFeat,
            dict):  # 如果对象的类型与参数二的类型（classinfo）相同则返回 True，否则返回 False
        classLabel = classify(valueOfFeat, featLabels, testVec)
    else:
        classLabel = valueOfFeat
    return classLabel

def createDataSet():
    dataSet = [['high', 'no', 'no', 'no', 'deci1'],
               ['high', 'no', 'no', 'common', 'deci2'],
               ['high', 'yes', 'no', 'common', 'deci1'],
               ['high', 'yes', 'yes', 'no', 'deci2'],
               ['high', 'no', 'no', 'no', 'deci3'],
               ['mid', 'no', 'no', 'no', 'deci4'],
               ['mid', 'no', 'no', 'common', 'deci2'],
               ['mid', 'yes', 'yes', 'common', 'deci1'],
               ['mid', 'no', 'yes', 'sun', 'deci2'],
               ['mid', 'no', 'yes', 'sun', 'deci2'],
               ['low', 'no', 'yes', 'sun', 'deci2'],
               ['low', 'no', 'yes', 'common', 'deci4'],
               ['low', 'yes', 'no', 'common', 'deci3'],
               ['low', 'yes', 'no', 'sun', 'deci2'],
               ['low', 'no', 'no', 'no', 'deci3'],
               ]

    labels = ['faces', 'illumination', 'blur', 'glasses']
    return dataSet, labels




if __name__ == "__main__":
	filename = "myTree.txt"

	myDat, labels = createDataSet()
	#myTree = createTree(myDat, labels)
    #print(type(myTree), myTree)
	#storeTree(myTree, filename)
	testVec = ['high', 'yes', 'yes', 'no']
	inputTree = grabTree(filename)
	classLabel = classify(inputTree, labels, testVec)
	print("样本['high', 'yes', 'yes', 'no']的决策结果是：" + classLabel)



