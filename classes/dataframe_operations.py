import pandas as pd
import numpy as np

class DataframeOperations():

    @staticmethod
    def writeToCsv(dataframe:pd.DataFrame, name:str, index:list[str] = None) -> None:
        indexAvailable = index is not None
        if indexAvailable:
            dataframe.index = index
        dataframe.to_excel(name, index=indexAvailable)

    @staticmethod
    def getStatisticDataframe(data:list[list[float]]) -> pd.DataFrame:
        dataframeData = []
        for measurements in data:
            measurements = np.array(measurements)
            average = np.average(measurements)
            stdDev = np.std(measurements)
            dataframeData.append([average, stdDev])
        return pd.DataFrame(dataframeData, columns=["Average", "Standard Deviation"])
