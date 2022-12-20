import threading
import serial

from classes.sensor import Sensor
from classes.port_commands import PortCommands
from classes.dataframe_sensor import DataframeSensor
from classes.dataframe_operations import DataframeOperations
from classes.gateway import *
from classes import strategy

class PortController():

    def __init__(self, port:str,  baudRate:int = 115200, processDataStrategy:strategy.processDataStrategy  = strategy.DefaultStrategy()) -> None:
        self.__dataStrategy = processDataStrategy
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


    def _readPort(self, gateway:Gateway):
        serialPort = serial.Serial(port=self.port, baudrate=self.baudRate)
        mac = None
        rssi = None
        counter = 0

        while(True):
            if( serialPort.inWaiting() > 0 ):
                data = serialPort.readline(None).decode('ascii')
                # commandConfirmed = False
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
                    if self.__dataStrategy.canProcess():
                        if self.__dataStrategy.matchIdentifier(mac):
                            self.__dataStrategy.processData(mac=mac, rssi=int(rssi))

                if self.__dataStrategy.isTestCompleted():
                    self.__dataStrategy.confirmTest()
                    if self.__dataStrategy.hasFinished():
                        self.__dataStrategy.saveData()
                        break
                    else:
                        input("Press Enter to continue for test number {}".format(self.__dataStrategy.getTestCounter() + 1))
                        serialPort.read(serialPort.inWaiting())

                # if self.__dataStrategy.hasFinished():
                #     self.__dataStrategy.saveData()
                #     break

                # if not self.__dataStrategy.canProcess():
                #     input("Press Enter to continue for test number {}".format(self.__dataStrategy.getTestCounter() + 1))
                #     serialPort.read(serialPort.inWaiting())
                

    def _printAllData(self):
        serialPort = serial.Serial(port=self.port, baudrate=self.baudRate)

        while(True):
            if( serialPort.inWaiting() > 0 ):
                data = serialPort.readline(None).decode('ascii')
                print(data)