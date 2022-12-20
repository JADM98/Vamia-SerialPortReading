from typing import Tuple
import numpy as np

class KalmanFilter():
    
    def __init__(self, numberOfVariables:int=1, secondsToMeasure:float=1, includeVelocity:bool=True) -> None:
        if numberOfVariables < 1:
            raise ValueError("Number of variables must be 1 or Higher.")
        
        self.numberOfVariables = numberOfVariables
        self.includeVelocity = includeVelocity
        self.sizeOfMatrix = self.numberOfVariables * (1+self.includeVelocity)

        self.stateVector = np.zeros( (self.sizeOfMatrix, 1), dtype=np.float64)
        self.transitionMatrix = np.zeros((self.sizeOfMatrix, self.sizeOfMatrix), dtype=np.float64)
        self.observationMatrix = np.zeros((self.numberOfVariables, self.sizeOfMatrix ))

        self.controlMatrix = 0
        self.Q = np.eye( self.sizeOfMatrix )
        self.R = np.eye( self.numberOfVariables )
        self.processCovMatrix = np.eye( self.sizeOfMatrix )
        
        for i in range(self.numberOfVariables):
            self.transitionMatrix[i, i] = 1
            self.observationMatrix[i, i] = 1
            if self.includeVelocity:
                self.transitionMatrix[i+self.numberOfVariables, i+self.numberOfVariables] = 1
                self.transitionMatrix[i, i+self.numberOfVariables] = 1/secondsToMeasure

    def setStdDeviation(self, stdDev:list[int]|Tuple[int]|np.ndarray|float):
        isInstance, stdDev = self.__checkDataInstace(stdDev)
        if isInstance:
            for i in range(self.numberOfVariables):
                self.R[i,i] = stdDev[i]**2

    def setNewMeasureTime(self, time:list[int]|Tuple[int]|np.ndarray|float):
        isInstance, time = self.__checkDataInstace(time)
        if isInstance:
            for i in range(self.numberOfVariables):
                self.transitionMatrix[i, i+self.numberOfVariables] = 1/time[i]
        
    def predict(self, u = 0) -> Tuple[float, ...]:
        self.stateVector = np.dot(self.transitionMatrix, self.stateVector) + np.dot(self.controlMatrix, u)
        self.processCovMatrix = np.dot(np.dot(self.transitionMatrix, self.processCovMatrix), self.transitionMatrix.T) + self.Q
        return tuple([float(var) for var in np.dot(self.observationMatrix, self.stateVector)])

    def update(self, z:list[int]|Tuple[int]|np.ndarray|float) -> Tuple[float, ...]:
        isIstance, z = self.__checkDataInstace(z)
        if isIstance:
            y = z - np.dot(self.observationMatrix, self.stateVector)
            S = self.R + np.dot(self.observationMatrix, np.dot(self.processCovMatrix, self.observationMatrix.T))
            K = np.dot(np.dot(self.processCovMatrix, self.observationMatrix.T), np.linalg.inv(S))
            self.stateVector = self.stateVector + np.dot(K, y)
            I = np.eye( self.numberOfVariables* (1+self.includeVelocity) )
            self.processCovMatrix = np.dot(I - np.dot(K, self.observationMatrix), self.processCovMatrix)
            return tuple([float(var) for var in np.dot(self.observationMatrix, self.stateVector)])

    def __checkDataInstace(self, myData):
        if isinstance(myData, int) or isinstance(myData, float):
            myData = (myData,)

        if isinstance(myData, Tuple) or isinstance(myData, list) or isinstance(myData, np.ndarray):
            myData = np.array(myData)
            if len(myData) is not self.numberOfVariables:
                raise ValueError("Cannot assign values because the expected size of the array was: {}, however the length was: {}".format(self.numberOfVariables, len(myData)))
            else:
                return True, myData
        else:
            raise ValueError("Cannot operate object of type {}, the expected type is float, tuple, list or np.ndarray".format(type(myData)))
