import numpy as np
import json
import os
import math
import tensorflow as tf
from tensorflow.keras.utils import to_categorical

class ValidationDataSet:

    def __init__(self, stepSize):
        
        self.stepSize = stepSize
        data = None

class ValidateDataLoader:

    def __init__(self, numBatches, dataDirectory = './data/batches-validate/', stepSize = 100):

        self.numBatchesToLoad = int(numBatches)
        self.dataDirectory = dataDirectory
        self.batches = None
        self.numSamples = 0
        self.x = None
        self.y = None
        self.dataset = ValidationDataSet(stepSize) 

    def _package_data_for_testing(self):

        # package data in a zipped list of instance label pairs

        data = []

        for i in range(len(self.x)):

            pair = (self.x[i], self.y[i])
            data.append(pair)

        self.dataset.data=data

    def _transform_timeseries(self, instance):

        timeSeries = []

        for i in range(len(instance[0])):

            timeSeries.append([instance[0][i], instance[1][i], instance[2][i]])

        return np.array([timeSeries])

    def _downsample(self):

        newX = []

        for i in range(len(self.x)):
            
            timeSeries = self._transform_timeseries(self.x[i])
            downSampledTimeSeries = timeSeries[:, ::self.dataset.stepSize, :]
            newX.append(downSampledTimeSeries)

        self.x = newX

    def _normalize_instances(self):

        numInstances = len(self.x)
        numFeatures = len(self.x[0])

        for i in range(numInstances):
            numTimesteps = len(self.x[i][0])
            for k in range(numTimesteps):
                self.x[i][0][k] /= 10.0
                self.x[i][1][k] /= 10.0
                self.x[i][2][k] -= math.pi 
                self.x[i][2][k] /= math.pi 

    def _combine_batches(self):

        print('batches:',len(self.batches))
        print('batch size:',len(self.batches[0][0]))
        print('features:',len(self.batches[0][0][0]), flush=True)

        self.x = self.batches[0][0]
        self.y = self.batches[0][1]

        for i in range(1, len(self.batches)):

            self.x.extend(self.batches[i][0])
            self.y.extend(self.batches[i][1])

        self.numSamples = len(self.x)

    def _pre_process_data(self):

        self._combine_batches()
        self.y = to_categorical(np.array(self.y))
        self._normalize_instances()
        self._downsample()

    def load_batch_json(self, batchFileName):

        # load raw json dict
        rawData = {}
        with open('{}/{}'.format(self.dataDirectory, batchFileName), 'r') as f:
            rawData = json.load(f)

        # build a list of instances and labels
        instances = [] 
        labels = [] 

        for sampleNumber in range(len(rawData)):

            sample = rawData[str(sampleNumber)]
            
            x = sample['path']['x']
            y = sample['path']['y']
            theta = sample['path']['theta']
            instance = np.array([x,y,theta])
            label = sample['target']['index']

            instances.append(instance)
            labels.append(label)

        x_batch = instances
        y_batch = labels

        return x_batch, y_batch

    def load(self, startBatch=0):

        self.batches = []
        self.batchFileNames = os.listdir(self.dataDirectory)[startBatch: startBatch+self.numBatchesToLoad]
    
        for batchFileName in self.batchFileNames:

            print('loading ' + batchFileName)
            x_batch, y_batch = self.load_batch_json(batchFileName)
            self.batches.append((x_batch, y_batch))
    
        self._pre_process_data()
        self._package_data_for_testing()

        return self.dataset
