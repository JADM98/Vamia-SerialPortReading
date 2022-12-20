from classes import port_controller
from classes import strategy
from classes.gateway import GatewayService

gateway = GatewayService.create(GatewayService.ESP32)

strat = strategy.KalmanStrategy(numberOfMeasurements=3, numberOfTests=3)
# strat = strategy.DefaultStrategy(numberOfMeasurements=10, numberOfTests=3)
# strat.setIndexValues(["1", "2", "3"])
# strat.setMainFileName("Test_2.xlsx")
# strat.setKalmanFileName("Test_2_kalman.xlsx")
# strat.setStatisticsFileName("Stats_Test_2.xlsx")
strat.setMeasurementStdDev(3.0)

myPort = port_controller.PortController(port="COM5", processDataStrategy=strat)

myPort.start(gateway=gateway)
myPort.wait()
