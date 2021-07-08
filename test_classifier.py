import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.utils import to_categorical
import argparse
import json
import csv
import numpy as np
import matplotlib.pyplot as plt
import os
from data.val_loader import ValidateDataLoader
from classifiers.lstm import LSTM, LSTMTester
from classifiers.feed_forward import FeedForward, FeedForwardTester

def plot_performance(performance, modelSelection):

    tp = performance['tp']
    labelCount = performance['label count']

    accuracyOverTime = []
    timesteps = []

    for i in range(len(labelCount)):
        percent = float(tp[i])/float(labelCount[i])
        accuracyOverTime.append(percent)
        timesteps.append(i)

    plt.title('{} Accuracy over time'.format(modelSelection))
    plt.plot(timesteps, accuracyOverTime, 'b', label = 'Accuracy')
    plt.xlabel('timestep')
    plt.ylabel('% correct')
    plt.legend()
    plt.show()

def build_model(modelSelection, inputShape):

    print('input shape:', inputShape)

    if modelSelection.lower() == 'feedforward':

        model = FeedForward(inputShape)

    elif modelSelection.lower() == 'lstm':

        model = LSTM()
        
    return model

def get_tester(modelSelection, dataset, model, weightsDir):

    if modelSelection.lower() == 'feedforward':

        tester = FeedForwardTester(dataset, model, weightsDir)

    elif modelSelection.lower() == 'lstm':

        tester = LSTMTester(dataset, model, weightsDir)

    return tester

def test_model(modelSelection, dataDirectory, numBatches, algo='RRT'):

    loader = None

    trainingDataDir = os.path.join(dataDirectory, '{}_batches_validate'.format(algo)) 
    loader =ValidateDataLoader(numBatches, trainingDataDir)
    dataset = loader.load()
    print('dataset loaded')

    inputShape = (3,)
    model = build_model(modelSelection, inputShape)
    print('model loaded')

    weightsDir = os.path.join(dataDirectory, '{}_{}_weights'.format(algo, modelSelection.lower()))
    print(weightsDir)
    tester = get_tester(modelSelection, dataset, model, weightsDir) 
    print('tester loaded')

    performance = tester.test()

    plot_performance(performance, modelSelection)

if __name__ == '__main__':

    argparser = argparse.ArgumentParser(description='Test selected model on validation or test set')
    argparser.add_argument('--model', type=str, default='FeedForward')
    argparser.add_argument('--directory', type=str, default='./data/batches-validate')
    argparser.add_argument('--batches', type=int, default=1)
    argparser.add_argument('--algo', type=str, help='Which path planning algorithm dataset to train over.', default = "RRT")

    args = argparser.parse_args()

    modelSelection = args.model
    dataDirectory = args.directory
    algorithm = args.algo.lower()

    if dataDirectory == 'tower':
        dataDirectory = 'D:\\path_planning_data'
    numBatches = args.batches

    test_model(modelSelection, dataDirectory, numBatches, algorithm)
