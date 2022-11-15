import threading
import serial

from classes.sensor import Sensor
from classes.port_commands import PortCommands
from classes.dataframe_sensor import DataframeSensor
from classes.dataframe_operations import DataframeOperations

class PortController():
    def __init__(self, port:str, baudRate:int = 115200, numberOfTests:int = 10, measurementsPerTest:int = 10) -> None:
        self.__numberOfTests = numberOfTests
        self.__measurementsPerTest = measurementsPerTest
        self.__values = None
        self.port = port
        self.baudRate = baudRate

    def start(self):
        self.portThread = threading.Thread(target=self._readPort, args= [])
        self.portThread.start()

    def wait(self):
        self.portThread.join()

    def setTestValues(self, values:list[str]):
        if len(values) != self.__numberOfTests:
            raise ValueError("Exception in number of test values passed. Expected {}, but received {}.".format(self.__numberOfTests, len(values)))
        self.__values = values

    def _readPort(self):
        serialPort = serial.Serial(port=self.port, baudrate=self.baudRate)
        mac = None
        avg = None
        sensor = None
        counter = 0
        updateData = False
        sensorData = DataframeSensor(self.__measurementsPerTest)

        while(True):
            if( serialPort.inWaiting() > 0 ):
                data = serialPort.readline(None).decode('ascii')
                commandConfirmed = False

                if( PortCommands.checkIfCommand(data) ):
                    commandConfirmed = True
                    if( PortCommands.contains(data, "mac") ):
                        position = PortCommands.getLastPosition(data, "mac:")
                        mac = PortCommands.getStringUntil(data, position, ",")
                    if( PortCommands.contains(data, "average") ):
                        position = PortCommands.getLastPosition(data, "average:")
                        avg = PortCommands.getString(data, position, PortCommands.END_OF_STRING)
                
                if commandConfirmed:
                    if(mac is not None) and (avg is not None):

                        if sensor is None:
                            sensor = Sensor(mac)
                            sensor.insertRSSI(int(avg))
                            print(mac, avg)
                        else:
                            if sensor.checkIMEI(mac):
                                print(mac, avg)
                                sensor.insertRSSI(int(avg))
                                if( sensor.checkReadingsLength(self.__measurementsPerTest) ):
                                    counter = sensorData.insertMeasurements(sensor.readings)
                                    print("Number of rows: {}".format(counter))
                                    sensor.resetRSSI()
                                    updateData = True
                
                if counter == self.__numberOfTests:
                    stats = DataframeOperations.getStatisticDataframe(sensorData.readingsList)
                    DataframeOperations.writeToCsv(sensorData.readingsDataframe, "Measurements.xlsx", index=self.__values)
                    DataframeOperations.writeToCsv(stats, "Statistics.xlsx", index=self.__values)
                    break

                if updateData:
                    updateData = False
                    input("Press Enter to continue for test number {}".format(counter + 1))
                    serialPort.read(serialPort.inWaiting())