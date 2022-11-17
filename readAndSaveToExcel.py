from classes import port_controller

myPort = port_controller.PortController(port="COM7", measurementsPerTest=5, numberOfTests=20)
# list1 = ["{}".format(i*20) for i in range(11)]
# list2 = ["{}".format(i*40+240) for i in range(9)]
# myPort.setTestValues(list1+list2)
# myPort.start()
# myPort.wait() 

# myPort.printAllData()

myPort.start(port_controller.PortController.GATEWAY_VAMIA_V0)
myPort.wait()
