import sys
sys.path.append("")


from classes.dataframe_sensor import DataframeSensor
from classes.dataframe_operations import DataframeOperations

lenght = 10

dfSensor = DataframeSensor(numberOfMeasurements=lenght)

dfSensor.insertMeasurements([i for i in range(lenght)])
dfSensor.insertMeasurements([i*2 for i in range(lenght)])
dfSensor.insertMeasurements([i*3 for i in range(lenght)])
dfSensor.insertMeasurements([i*4 for i in range(lenght)])
dfSensor.insertMeasurements([i*5 for i in range(lenght)])
dfSensor.insertMeasurements([i*6 for i in range(lenght)])
dfSensor.insertMeasurements([i*7 for i in range(lenght)])
dfSensor.insertMeasurements([i*8 for i in range(lenght)])

dfStats = DataframeOperations.getStatisticDataframe(dfSensor.readingsList)

DataframeOperations.writeToCsv(dfStats, "Statistics.xlsx", index=["{}".format(i) for i in range(8)])
DataframeOperations.writeToCsv(dfSensor.readingsDataframe, "Measurements.xlsx", index=["{}".format(i) for i in range(8)])
