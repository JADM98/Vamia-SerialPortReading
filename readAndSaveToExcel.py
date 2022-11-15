from classes import port_controller

myPort = port_controller.PortController(port="COM5", measurementsPerTest=3, numberOfTests=2)
myPort.setTestValues(["10", "20"])
myPort.start()
myPort.wait() 