from classes import port_controller
from classes.gateway import GatewayService

myPort = port_controller.PortController(port="COM5", measurementsPerTest=5, numberOfTests=20)
gateway = GatewayService.create(GatewayService.VAMIA_V0)

myPort.establishFileNames(measurementFileName="Measuremets3.xlsx", statisticsFileName="Statistics3.xlsx")
list1 = [i*20 for i in range(11)]
list2 = [i*40+240 for i in range(9)]
myPort.setTestValues(list1+list2)

myPort.start(gateway=gateway)
myPort.wait()
