from abc import ABC, abstractmethod
import serial

from classes.sensor import Sensor
from classes.dataframe_sensor import DataframeSensor
from classes.dataframe_operations import DataframeOperations
from classes.kalman import KalmanFilter

class processDataStrategy(ABC):

    @abstractmethod
    def canProcess(self) -> bool:
        pass
    @abstractmethod
    def hasFinished(self) -> bool:
        pass
    @abstractmethod
    def matchIdentifier(self, identifier:str) -> bool:
        pass

    @abstractmethod
    def getTestCounter(self) -> int:
        pass
    @abstractmethod
    def getMeasurementCounter(self) -> int:
        pass

    @abstractmethod
    def setMainFileName(self, name:str):
        pass

    @abstractmethod
    def setStatisticsFileName(self, name:str):
        pass

    @abstractmethod
    def setIndexValues(self, values:list[str]):
        pass

    @abstractmethod
    def confirmTest(self) -> bool:
        pass
    @abstractmethod
    def isTestCompleted(self) -> bool:
        pass

    @abstractmethod
    def processData(self, mac:str, rssi:int) -> bool:
        pass

    @abstractmethod
    def saveData(self)-> bool:
        pass

class DefaultStrategy(processDataStrategy):

    def __init__(self, numberOfMeasurements:int = 10, numberOfTests:int = 1) -> None:
        self.__canMeasure = True
        self.__measurementsCounter = 0
        self.__testsCounter = 0
        self.__sensor = None
        self.__values = None
        self.__numberOfMeasurements = numberOfMeasurements
        self.__sensorData = DataframeSensor(self.__numberOfMeasurements)
        self.__numberOfTests = numberOfTests
        self.__mainFileName = "measurements.xlsx"
        self.__statisticsFileName = "statistics.xlsx"
        self.__hasFinished = False
    

    def setIndexValues(self, indexList: list[str]):
        if indexList is not None:
            if len(indexList) != self.__numberOfTests:
                raise ValueError("Exception in number of test index values passed. Expected {}, but received {}.".format(self.__numberOfTests, len(indexList)))
        self.__values = indexList

    def setMainFileName(self, name: str):
        self.__mainFileName = name
    def setStatisticsFileName(self, name: str):
        self.__statisticsFileName = name
    def canProcess(self) -> bool:
        return self.__canMeasure
    def hasFinished(self) -> bool:
        return self.__hasFinished
    def isTestCompleted(self) -> bool:
        return not self.__canMeasure and self.__measurementsCounter == self.__numberOfMeasurements
    def matchIdentifier(self, identifier:str) -> bool:
        if self.__sensor is None:
            return True
        else:
            return self.__sensor.checkIMEI(identifier)
    def getTestCounter(self) -> int:
        return self.__testsCounter
    def getMeasurementCounter(self) -> int:
        return self.__measurementsCounter

    def confirmTest(self) -> bool:
        if(not self.__canMeasure and self.__measurementsCounter == self.__numberOfMeasurements):
            self.__canMeasure = True
            self.__measurementsCounter = 0
            self.__testsCounter += 1
            if(self.__testsCounter == self.__numberOfTests):
                self.__hasFinished = True
            return True
        return False

    def processData(self, mac:str, rssi:int) -> bool:
        if(self.__testsCounter < self.__numberOfTests):
            if(self.__canMeasure):
                if self.__sensor is None:
                    self.__sensor = Sensor(mac)
                    self.__sensor.insertRSSI(int(rssi))
                    self.__measurementsCounter += 1
                    print(mac, rssi)
                    return True
                else:
                    if self.__sensor.checkIMEI(mac):
                        print(mac, rssi)
                        self.__sensor.insertRSSI(int(rssi))
                        self.__measurementsCounter += 1

                        if( self.__sensor.checkReadingsLength(self.__numberOfMeasurements) ):
                            self.__sensorData.insertMeasurements(self.__sensor.readings)
                            print("Number of rows: {}".format(self.__testsCounter + 1))
                            self.__sensor.resetRSSI()

                            self.__canMeasure = False

                        return True
            return False

    def saveData(self) -> bool:
        if(self.__testsCounter == self.__numberOfTests):
            stats = DataframeOperations.getStatisticDataframe(self.__sensorData.readingsList)
            DataframeOperations.writeToCsv(self.__sensorData.readingsDataframe, self.__mainFileName, self.__values)
            DataframeOperations.writeToCsv(stats, self.__statisticsFileName, self.__values)
            return True
        return False

class KalmanStrategy(processDataStrategy):

    def __init__(self, numberOfMeasurements:int = 10, numberOfTests:int = 1) -> None:
        self.__canMeasure = True
        self.__measurementsCounter = 0
        self.__testsCounter = 0
        self.__sensor = None
        self.__values = None
        self.__numberOfMeasurements = numberOfMeasurements
        self.__sensorData = DataframeSensor(self.__numberOfMeasurements)
        self.__sensorDataKalman = DataframeSensor(self.__numberOfMeasurements)
        self.__numberOfTests = numberOfTests
        self.__mainFileName = "measurements.xlsx"
        self.__kalmanFileName = "filtered.xlsx"
        self.__statisticsFileName = "statistics.xlsx"
        self.__hasFinished = False
        self.__kalman = KalmanFilter(includeVelocity=False)

    def setIndexValues(self, indexList: list[str]):
        if indexList is not None:
            if len(indexList) != self.__numberOfTests:
                raise ValueError("Exception in number of test index values passed. Expected {}, but received {}.".format(self.__numberOfTests, len(indexList)))
        self.__values = indexList
    def setMainFileName(self, name: str):
        self.__mainFileName = name
    def setKalmanFileName(self, name:str):
        self.__kalmanFileName = name
    def setMeasurementStdDev(self, stdDev:float) -> None:
        self.__kalman.setStdDeviation(stdDev=stdDev)
    def setStatisticsFileName(self, name: str):
        self.__statisticsFileName = name
    def canProcess(self) -> bool:
        return self.__canMeasure
    def hasFinished(self) -> bool:
        return self.__hasFinished
    def isTestCompleted(self) -> bool:
        return not self.__canMeasure and self.__measurementsCounter == self.__numberOfMeasurements
    def matchIdentifier(self, identifier:str) -> bool:
        if self.__sensor is None:
            return True
        else:
            return self.__sensor.checkIMEI(identifier)
    def getTestCounter(self) -> int:
        return self.__testsCounter
    def getMeasurementCounter(self) -> int:
        return self.__measurementsCounter

    def confirmTest(self) -> bool:
        if(not self.__canMeasure and self.__measurementsCounter == self.__numberOfMeasurements):
            self.__canMeasure = True
            self.__measurementsCounter = 0
            self.__testsCounter += 1
            if(self.__testsCounter == self.__numberOfTests):
                self.__hasFinished = True
            return True
        return False

    def processData(self, mac:str, rssi:int) -> bool:
        if(self.__testsCounter < self.__numberOfTests):
            if(self.__canMeasure):
                if self.__sensor is None:
                    self.__sensor = Sensor(mac)
                    self.__sensorKalman = Sensor(mac)
                    # self.__sensor.insertRSSI(int(rssi))
                    self.__measurementsCounter += 1
                    self.__kalman.predict()
                    kalmanRssi = self.__kalman.update(float(rssi))[0]
                    self.__sensor.insertRSSI(rssi)
                    self.__sensorKalman.insertRSSI(int(kalmanRssi))
                    print(mac, rssi, kalmanRssi)
                    return True
                else:
                    if self.__sensor.checkIMEI(mac):
                        
                        # self.__sensor.insertRSSI(int(rssi))

                        self.__kalman.predict()
                        kalmanRssi = self.__kalman.update(float(rssi))[0]
                        self.__sensor.insertRSSI(rssi)
                        self.__sensorKalman.insertRSSI(int(kalmanRssi))

                        print(mac, rssi, kalmanRssi)

                        self.__measurementsCounter += 1

                        if( self.__sensor.checkReadingsLength(self.__numberOfMeasurements) ):
                            self.__sensorData.insertMeasurements(self.__sensor.readings)
                            self.__sensorDataKalman.insertMeasurements(self.__sensorKalman.readings)
                            print("Number of rows: {}".format(self.__testsCounter + 1))
                            self.__sensor.resetRSSI()
                            self.__sensorKalman.resetRSSI()

                            self.__canMeasure = False

                        return True
            return False

    def saveData(self) -> bool:
        if(self.__testsCounter == self.__numberOfTests):
            stats = DataframeOperations.getStatisticDataframe(self.__sensorData.readingsList)
            DataframeOperations.writeToCsv(self.__sensorData.readingsDataframe, self.__mainFileName, self.__values)
            DataframeOperations.writeToCsv(stats, self.__statisticsFileName, self.__values)
            DataframeOperations.writeToCsv(self.__sensorDataKalman.readingsDataframe, self.__kalmanFileName, self.__values)
            return True
        return False


