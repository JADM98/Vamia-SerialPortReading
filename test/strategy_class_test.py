import sys
sys.path.append("")

from classes.strategy import DefaultStrategy, KalmanStrategy

strat = KalmanStrategy(numberOfMeasurements=5, numberOfTests=2)
# strat = DefaultStrategy()

# strat.setIndexValues(None)
# strat.setMainFileName('Test_1.xlsx')
# strat.setStatisticsFileName('Stats_Test_1.xlsx')

for i in range(9):
    for j in range(10):
        if strat.canProcess():
            if strat.matchIdentifier("123"):
                strat.processData("123", i*j + 5)
            if strat.matchIdentifier("xxx"):
                strat.processData("xxx", -1)

    strat.confirmTest()
    if strat.hasFinished():
        break


if(strat.hasFinished()):
    strat.saveData()
    print("Success")

