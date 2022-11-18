import threading
import serial

from classes.sensor import Sensor
from classes.port_commands import PortCommands
from classes.dataframe_sensor import DataframeSensor
from classes.dataframe_operations import DataframeOperations
from classes.gateway import *

class PortController():

    def __init__(self, port:str, baudRate:int = 115200, numberOfTests:int = 10, measurementsPerTest:int = 10) -> None:
        self.__numberOfTests = numberOfTests
        self.__measurementsPerTest = measurementsPerTest
        self.__values = None
        self.port = port
        self.baudRate = baudRate

    def start(self, gateway:Gateway):
        self.portThread = threading.Thread(target=self._readPort, args= [gateway])
        self.portThread.start()

    def wait(self):
        self.portThread.join()

    def printAllData(self):
        self.portThread = threading.Thread(target=self._printAllData, args= [])
        self.portThread.start()

    def setTestValues(self, values:list[str]):
        if len(values) != self.__numberOfTests:
            raise ValueError("Exception in number of test values passed. Expected {}, but received {}.".format(self.__numberOfTests, len(values)))
        self.__values = values

    def _readPort(self, gateway:Gateway):
        serialPort = serial.Serial(port=self.port, baudrate=self.baudRate)
        mac = None
        rssi = None
        sensor = None
        counter = 0
        updateData = False
        sensorData = DataframeSensor(self.__measurementsPerTest)

        while(True):
            if( serialPort.inWaiting() > 0 ):
                data = serialPort.readline(None).decode('ascii')
                commandConfirmed = False
                mac:str= None
                rssi:str = None

                if gateway.checkIfCommand(data):
                    if gateway.contains(data, GatewayKeys.MAC):
                        mac = gateway.getValueOf(data, GatewayKeys.MAC)
                        rssi = gateway.getValueOf(data, GatewayKeys.AVERAGE)
                    elif gateway.contains(data, GatewayKeys.ADDRESS):
                        mac = gateway.getValueOf(data, GatewayKeys.ADDRESS)
                        rssi = gateway.getValueOf(data, GatewayKeys.RSSI)

                if (mac is not None) and (rssi is not None):
                    commandConfirmed = True

                if commandConfirmed:
                    if(mac is not None) and (rssi is not None):
                        if sensor is None:
                            sensor = Sensor(mac)
                            sensor.insertRSSI(int(rssi))
                            print(mac, rssi)
                        else:
                            if sensor.checkIMEI(mac):
                                print(mac, rssi)
                                sensor.insertRSSI(int(rssi))
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
                

    def _printAllData(self):
        serialPort = serial.Serial(port=self.port, baudrate=self.baudRate)

        while(True):
            if( serialPort.inWaiting() > 0 ):
                data = serialPort.readline(None).decode('ascii')
                print(data)