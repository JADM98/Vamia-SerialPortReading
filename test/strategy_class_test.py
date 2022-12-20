import sys
sys.path.append("")

from classes.strategy import DefaultStrategy, KalmanStrategy

strat = KalmanStrategy()

strat.setIndexValues(None)
strat.setMainFileName('Test_1.xlsx')
strat.setStatisticsFileName('Stats_Test_1.xlsx')
strat.setNumberOfMeasurements(5)
strat.setNumberOfTest(2)

for i in range(3):
    for j in range(6):
        strat.processData("123", i*j + 5)
        strat.processData("xxx", -1)
    
    strat.confirmTest()

if(strat.saveData()):
    print("Success")

