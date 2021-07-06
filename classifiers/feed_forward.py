import tensorflow as tf
from tensorflow.keras import layers 
import numpy as np

class FeedForward(tf.keras.Model):

    def __init__(self, inputShape):
        
        super(FeedForward, self).__init__()
        self.inputLayer = layers.InputLayer(input_shape=(inputShape))
        self.flattenLayer = (layers.Flatten())
        #self.mask = layers.Masking()
        self.H1 = layers.Dense(1028, activation='relu')
        self.H2 = layers.Dense(256, activation='relu')
        self.H3 = layers.Dense(64, activation='relu')
        self.outputLayer = layers.Dense(5, activation='softmax')
		
    def call(self, x):
        
        x = self.inputLayer(x)
        x = self.flattenLayer(x)
        #x = self.mask(x)
        x = self.H1(x)
        x = self.H2(x)
        x = self.H3(x)

        return self.outputLayer(x)
		
class FeedForwardTrainer():

    def __init__(self, model, weightsDir):
        
        self.model = model
        self.optimizer = tf.keras.optimizers.Adam()
        self.loss_fn = tf.keras.losses.CategoricalCrossentropy()
        self.trainAccMetric = tf.keras.metrics.CategoricalAccuracy()
        self.valAccMetric = tf.keras.metrics.CategoricalAccuracy()
        self.trainingHistory = {'trainAcc':[], 'valAcc':[], 'trainLoss':[], 'valLoss':[]}
        self.weightsDir = weightsDir

    def _train_step(self, xBatchTrain, yBatchTrain):

        with tf.GradientTape() as tape:

            tape.watch(xBatchTrain)
            logits = self.model(xBatchTrain)
            lossValue = self.loss_fn(yBatchTrain, logits)

        grads = tape.gradient(lossValue, self.model.trainable_variables)
        self.optimizer.apply_gradients(zip(grads, self.model.trainable_variables))

        self.trainAccMetric.update_state(yBatchTrain, logits)

        return lossValue

    def _save_metrics(self, lossValue, valDataset):

        trainAcc = self.trainAccMetric.result()
        self.trainingHistory['trainAcc'].append(trainAcc)
        self.trainingHistory['trainLoss'].append(float(lossValue))
        self.trainAccMetric.reset_states()

        for xBatchVal, yBatchVal in valDataset:

            valLogits = self.model(xBatchVal, training=False)
            self.valAccMetric.update_state(yBatchVal, valLogits)
            lossValue = self.loss_fn(yBatchVal, valLogits)

        valAcc = self.valAccMetric.result()
        self.trainingHistory['valAcc'].append(valAcc)
        self.trainingHistory['valLoss'].append(float(lossValue))
        self.valAccMetric.reset_states()

    def train(self, trainData, valData, epochs, batchSize, resume):

        if resume:
            self.model.load_weights('{}/feed_forward_final_weights'.format(self.weightsDir))

        x_train, y_train = trainData
        x_val, y_val = valData

        trainDataset = tf.data.Dataset.from_tensor_slices((x_train, y_train))
        trainDataset = trainDataset.shuffle(buffer_size=1024).batch(batchSize)

        valDataset = tf.data.Dataset.from_tensor_slices((x_val, y_val))
        valDataset = valDataset.batch(batchSize)

        for epoch in range(epochs):
            
            print("\nStart of epoch {}\n".format(epoch))

            for step, (xBatchTrain, yBatchTrain) in enumerate(trainDataset):

                lossValue = self._train_step(xBatchTrain, yBatchTrain)

                if step % 2 == 0:
                    print("Training loss at step {}: {:.4f}".format(step, float(lossValue)))
                    print("Seen so far: {} samples".format((step + 1) * batchSize))

            self._save_metrics(lossValue, valDataset)

        self.model.save_weights('{}/feed_forward_final_weights'.format(self.weightsDir))
        self.model.save('{}/feed_forward_model'.format(self.weightsDir))

        return self.trainingHistory
    
class FeedForwardTester():

    def __init__(self, dataset, model, weightsDir):

        self.dataset = dataset
        self.model = model
        self.numSamples = len(dataset[1])
        self.accuracyInfo = {'tp': [], 'label count': []}
        self.weightsDir = weightsDir

    def test(self):

        self.model.load_weights('{}/feed_forward_final_weights'.format(self.weightsDir))
        
        print('model weights were loaded')
        self.dataset = self.dataset[:1000]
        stepSize = 1
        timeSteps = [x*stepSize for x in range(1000)]

        for instance, label in self.dataset:

            for i, timeStep in enumerate(timeSteps):

                if timeStep+stepSize >= instance.shape[1]:
                    break
                
                inputTensor = np.zeros((1, 3, 1000))
                inputTensor[0, :, timeStep:timeStep+stepSize] += instance[:, timeStep:timeStep + stepSize]

                logits = self.model(inputTensor)
                prediction = np.argmax(logits)
                if len(self.accuracyInfo['tp']) < i+1:
                    self.accuracyInfo['tp'].append(0)
                    self.accuracyInfo['label count'].append(0)

                self.accuracyInfo['label count'][i] += 1
                if prediction == np.argmax(label):
                    self.accuracyInfo['tp'][i] += 1
    
        return self.accuracyInfo





            



