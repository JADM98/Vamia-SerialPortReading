from abc import ABC, abstractmethod
import serial

from classes.sensor import Sensor
from classes.dataframe_sensor import DataframeSensor
from classes.dataframe_operations import DataframeOperations
from classes.kalman import KalmanFilter

class processDataStrategy(ABC):

    @abstractmethod
    def setNumberOfMeasurements(self, numberOfMeasurements:int) -> None:
        pass

    @abstractmethod
    def setNumberOfTest(self, numberOfTests:int) -> None:
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
    def processData(self, data) -> bool:
        pass

    @abstractmethod
    def saveData(self)-> bool:
        pass

class DefaultStrategy(processDataStrategy):

    def __init__(self) -> None:
        self.__canMeasure = True
        self.__measurementsCounter = 0
        self.__testsCounter = 0
        self.__sensor = None

    def setNumberOfMeasurements(self, numberOfMeasurements:int) -> None:
        self.__numberOfMeasurements = numberOfMeasurements
        df = DataframeSensor(self.__numberOfMeasurements)
        self.__sensorData = df
    def setIndexValues(self, values: list[str]):
        self.__values = values
    def setMainFileName(self, name: str):
        self.__mainFileName = name
    def setNumberOfTest(self, numberOfTests: int) -> None:
        self.__numberOfTests = numberOfTests
    def setStatisticsFileName(self, name: str):
        self.__statisticsFileName = name

    def confirmTest(self) -> bool:
        if(not self.__canMeasure and self.__measurementsCounter == self.__numberOfMeasurements):
            self.__canMeasure = True
            self.__measurementsCounter = 0
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
                            self.__testsCounter = self.__sensorData.insertMeasurements(self.__sensor.readings)
                            print("Number of rows: {}".format(self.__testsCounter))
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

    def __init__(self) -> None:
        self.__canMeasure = True
        self.__measurementsCounter = 0
        self.__testsCounter = 0
        self.__sensor = None
        self.__kalman = KalmanFilter(includeVelocity=False)

    def setNumberOfMeasurements(self, numberOfMeasurements:int) -> None:
        self.__numberOfMeasurements = numberOfMeasurements
        df = DataframeSensor(self.__numberOfMeasurements)
        self.__sensorData = df
    def setIndexValues(self, values: list[str]):
        self.__values = values
    def setMainFileName(self, name: str):
        self.__mainFileName = name
    def setNumberOfTest(self, numberOfTests: int) -> None:
        self.__numberOfTests = numberOfTests
    def setStatisticsFileName(self, name: str):
        self.__statisticsFileName = name

    def confirmTest(self) -> bool:
        if(not self.__canMeasure and self.__measurementsCounter == self.__numberOfMeasurements):
            self.__canMeasure = True
            self.__measurementsCounter = 0
            return True
        return False

    def processData(self, mac:str, rssi:int) -> bool:
        if(self.__testsCounter < self.__numberOfTests):
            if(self.__canMeasure):
                if self.__sensor is None:
                    self.__sensor = Sensor(mac)
                    # self.__sensor.insertRSSI(int(rssi))
                    self.__measurementsCounter += 1
                    self.__kalman.predict()
                    kalmanRssi = self.__kalman.update(float(rssi))[0]
                    self.__sensor.insertRSSI(int(kalmanRssi))
                    print(mac, rssi, kalmanRssi)
                    return True
                else:
                    if self.__sensor.checkIMEI(mac):
                        
                        # self.__sensor.insertRSSI(int(rssi))

                        self.__kalman.predict()
                        kalmanRssi = self.__kalman.update(float(rssi))[0]
                        self.__sensor.insertRSSI(int(kalmanRssi))

                        print(mac, rssi, kalmanRssi)

                        self.__measurementsCounter += 1

                        if( self.__sensor.checkReadingsLength(self.__numberOfMeasurements) ):
                            self.__testsCounter = self.__sensorData.insertMeasurements(self.__sensor.readings)
                            print("Number of rows: {}".format(self.__testsCounter))
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


