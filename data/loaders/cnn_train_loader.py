import numpy as np
import os
import json
import math
from tensorflow.keras.utils import to_categorical

class CNNTrainDataLoader():

    def __init__(self, split, numBatches, dataDirectory, batchSize=512, truncatedPathLength=10, stepSize=100):

        self.batchSize = batchSize
        self.numBatchesToLoad = int(numBatches)
        self.dataDirectory = dataDirectory
        self.stepSize=stepSize
        self.batches = None
        self.numSamples = 0
        self.x = None
        self.y = None
        self.x_train = None
        self.y_train = None
        self.x_val = None
        self.y_val = None
        self.trainData = None
        self.valData = None
        self.split = split
        self.truncatedPathLength = truncatedPathLength

    def _split_data(self):

        splitIndex = int(self.x.shape[0] * self.split)
        self.x_train = self.x[:splitIndex]
        self.y_train = self.y[:splitIndex]
        self.x_val = self.x[splitIndex:]
        self.y_val = self.y[splitIndex:]

    def _transform_timeseries(self):

        timeseriesX = np.transpose(self.x, (0, 2, 1))
        self.x = timeseriesX
        print('shape of timeseries:', self.x.shape, flush=True)

    def _normalize_instances(self):

        print('\nShape of data set:')
        print(self.x.shape)

        print('\nmaximum x value before normalization:', np.amax(self.x[:,0,:]))
        print('minimum x value before normalization:', np.amin(self.x[:,0,:]))
        print('maximum y value before normalization:', np.amax(self.x[:,1,:]))
        print('minimum y value before normalization:', np.amin(self.x[:,1,:]))
        self.x[:,:2,:] /= 10.0

        print('\nmaximum x value after normalization:', np.amax(self.x[:,0,:]))
        print('minimum x value after normalization:', np.amin(self.x[:,0,:]))
        print('maximum y value after normalization:', np.amax(self.x[:,1,:]))
        print('minimum y value after normalization:', np.amin(self.x[:,1,:]))

        print('\nmaximum theta value before normalization:', np.amax(self.x[:,2,:]))
        print('minimum theta value before normalization:', np.amin(self.x[:,2,:]))
        self.x[:,2,:] -= (math.pi)
        self.x[:,2,:] /= (math.pi)
        print('maximum theta value after normalization:', np.amax(self.x[:,2,:]))
        print('minimum theta value after normalization:', np.amin(self.x[:,2,:]))
        print('\n')

    def _combine_batches(self):

        self.x = self.batches[0][0]
        self.y = self.batches[0][1]

        for x_batch, y_batch in self.batches[1:]:

            self.x = np.concatenate((self.x, x_batch), axis=0)
            self.y = np.concatenate((self.y, y_batch))

    def _pre_process_data(self):

        # Combine loaded batches into one large dataset
        self._combine_batches()

        # transform labels to one hot
        self.x = np.array(self.x)
        self.y = to_categorical(np.array(self.y))

        # normalize to center mean at zero
        self._normalize_instances()

        self._transform_timeseries()

        # split into train and test sets
        self._split_data()

        self.trainData = (self.x_train, self.y_train)
        self.valData = (self.x_val, self.y_val)

        pass

    def _load_batch_json(self, batchFileName):

        rawData = {}
        with open(os.path.join(self.dataDirectory, batchFileName), 'r') as f:
            rawData = json.load(f)

        instances = []
        labels = []

        for sampleNumber in range(len(rawData)):

            sample = rawData[str(sampleNumber)]
        
            x = sample['path']['x'][::self.stepSize]
            y = sample['path']['y'][::self.stepSize]
            theta = sample['path']['theta'][::self.stepSize]

            if len(x) < self.truncatedPathLength:
                instance = np.zeros((3, self.truncatedPathLength))
                x = np.array(x)
                y = np.array(y)
                theta = np.array(theta)
                instance[0, :x.shape[0]] = x
                instance[0, :y.shape[0]] = y
                instance[0, :theta.shape[0]] = theta
            else:
                instance = np.array([\
                                    x[:self.truncatedPathLength],\
                                    y[:self.truncatedPathLength],\
                                    theta[:self.truncatedPathLength]\
                                    ])

            label = sample['target']['index']

            instances.append(instance)
            labels.append(label)

        x_batch = np.array(instances)
        y_batch = np.array(labels)

        return (x_batch, y_batch)

    def load(self, startBatch):

        self.batches = []

        print('loading data...')
        for i in range(startBatch, startBatch+self.numBatchesToLoad):

            batchFileName = 'batch_{}.json'.format(i)
            print(batchFileName)

            x_batch, y_batch = self._load_batch_json(batchFileName)
            self.batches.append((x_batch, y_batch))

            self.numBatchesToLoad -= 1
            if self.numBatchesToLoad == 0:
                break

        self._pre_process_data()

        return (self.x_train, self.y_train), (self.x_val, self.y_val)
