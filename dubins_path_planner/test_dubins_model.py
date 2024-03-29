import sys
import math
import random
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from car_models.dubins_optimal_planner import DubinsOptimalPlanner
from car_models.dubins_model import DubinsCar

def plot_path(path, origin, target, acceptableError, iteration):

    # draw car path as arrows on plot 
    i = 0
    rho = np.linalg.norm(target[:2] - origin[:2])

    for x,y,theta in zip(path['x'], path['y'], path['theta']):
        plt.quiver(x, y, math.cos(theta), math.sin(theta)) 
        i += 1

    # text coordinate label shifts
    xShift = 0.1
    yShift = -0.2

    # origin
    plt.plot(origin[0], origin[1], 'x', color='red', markersize=25)
    originStr = 'x: {:.2f}\ny: {:.2f}'.format(origin[0], origin[1])

    # target
    targetArea = plt.Circle((target[0], target[1]), acceptableError, color='blue', fill=False)
    plt.gca().add_patch(targetArea)
    targetStr = 'x: {:.2f}\ny: {:.2f}'.format(target[0], target[1])

    # display
    plt.title('Dubins Optimal Path Planner')
    plt.xlabel('X Position (m)')
    plt.ylabel('Y Position (m)')
    plt.axis("equal")
    plt.show()

def simulate_dubins_optimal_path_planner(startPosition, target, animate=True, iteration=0):

    # configure and create dubins car
    velocity = 1.0 
    maxSteeringAngle = (math.pi / 4.0) 
    U = [-1.0 * math.tan(maxSteeringAngle), math.tan(maxSteeringAngle)]
    dubinsCar = DubinsCar(startPosition, velocity, U)

    # create planner
    planner = DubinsOptimalPlanner(dubinsCar, startPosition, target)

    # don't simulate if target is within minimum turning radius
    distanceFromStartToTarget = abs(np.linalg.norm(target[:2] - startPosition[:2]))
    #if (2.0*planner.minTurningRadius) > distanceFromStartToTarget: 
        #print('target within minimum turning radius')
        #return

    # get planner's path
    path = planner.run()

    # graph path
    acceptableError = 0.1
    if animate:
        plot_path(path, startPosition, target, acceptableError, iteration)

    # test car made it to goal
    carFinalPosition = np.array([path['x'][-1], path['y'][-1]])
    distanceToGoal = abs(np.linalg.norm(carFinalPosition[:2] - target[:2]))
    assert distanceToGoal < acceptableError, 'Car did not reach goal'

def train(animate=True):

    # set starting position and target
    startPosition = np.array([0.0, 0.0, 0.0])
    target = np.array([0.5, 0.5, 0.0])
    simulate_dubins_optimal_path_planner(startPosition, target, animate)

def test(animate=True):

    numTestCases = 100
    if animate:
        numTestCases = 10

    for i in tqdm(range(numTestCases)):

        # set starting position 
        startPosition = np.random.uniform(low = -1.0, high = 1.0, size = (3,)) 
        theta = random.uniform(0.0, 2.0 * math.pi)
        startPosition[2] = theta

        # set random target
        target = np.random.uniform(low = -1.0, high = 1.0, size = (3,)) 

        # run simulation
        try:
            simulate_dubins_optimal_path_planner(startPosition, target, animate, i)
        except Exception as e:
            print(e)
            print('planner failed on:')
            print('start:', startPosition)
            print('target:', target)
            plt.plot(target[0], target[1], 'x', color='red', markersize=25)
            plt.quiver(startPosition[0], startPosition[1], math.cos(theta), math.sin(theta)) 
            plt.show()
            exit(-1)

    print('passed all tests!')

if __name__ == '__main__':

    testOrTrain = 'test'
    animate = False 

    # unpack command line arguments
    if len(sys.argv) < 2:
        print('Usage: {} train/test [animate]'.format(sys.argv[0]))
        exit(2)
    else:
        testOrTrain = sys.argv[1].lower()

    if len(sys.argv) == 3:
        if sys.argv[2].lower() == 'animate':
            animate = True

    # run_simulation
    if testOrTrain== 'train':
        train(animate)
    else:
        test(animate)
