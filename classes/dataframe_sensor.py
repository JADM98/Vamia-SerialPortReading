import pandas as pd

class DataframeSensor():
    
    @property
    def readingsDataframe(self):
        return pd.DataFrame(data=self.__data, columns=self.__columns)

    @property
    def readingsList(self):
        return self.__data

    def __init__(self, numberOfMeasurements:int) -> None:
        self.__numOfMeasurements = numberOfMeasurements
        self.__columns = [f"measure {i+1}" for i in range(numberOfMeasurements)]
        self.__data:list[list[float]] = []
        self.__values = None
    
    def insertMeasurements(self, measurements:list[float]) -> int:
        if (len(measurements) != self.__numOfMeasurements):
            raise ValueError("Measurements list passed is not from correct size. Expected size is: {}, received: {}".format(self.__numOfMeasurements, len(measurements)))
        self.__data.append(measurements)
        return len(self.__data)

    def isEmpty(self) -> bool:
        return len(self.__data) == 0