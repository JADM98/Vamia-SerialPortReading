from abc import ABC, abstractmethod
from classes.port_commands import PortCommands

class Gateway(ABC):
    @abstractmethod
    def checkIfCommand(self, data:str) -> bool:
        pass
    @abstractmethod
    def contains(self, data:str, textToFind:str) -> bool:
        pass
    @abstractmethod
    def getValueOf(self, data:str, key:str) -> str|None:
        pass

class GatewayService:
    #static variables
    ESP32 = 0
    VAMIA_V0 = 1

    @staticmethod
    def create(gatewayConst:int) -> Gateway:
        if gatewayConst == GatewayService.ESP32:            return GatewayESP32()
        if gatewayConst == GatewayService.VAMIA_V0:         return GateWayVamiaV0()
        raise ValueError("Not appropiate value was pased in create method.")

class GatewayKeys:
    #static variables
    MAC = "mac:"
    AVERAGE = "average:"
    RSSI = "RSSI:"
    ADDRESS = "ADDR:"

    keys = [MAC, AVERAGE, RSSI, ADDRESS]

class GatewayESP32(Gateway):
    def checkIfCommand(self, data: str) -> bool:
        return PortCommands.contains(data, "Command >> ")
    def contains(self, data: str, textToFind: str) -> bool:
        return PortCommands.contains(data, textToFind)
    def getValueOf(self, data: str, key: str) -> str|None:
        position = PortCommands.getLastPosition(data, key)
        value = PortCommands.getStringUntil(data, position, ",")
        if value is None: 
            value = PortCommands.getString(data, position, PortCommands.END_OF_STRING)
        return value

class GateWayVamiaV0(Gateway):
    def checkIfCommand(self, data: str):
        return PortCommands.contains(data, "MQTT <<")
    def contains(self, data: str, textToFind: str):
        return PortCommands.contains(data, textToFind)
    def getValueOf(self, data: str, key: str) -> str|None:
        position = PortCommands.getLastPosition(data, key)
        value = PortCommands.getStringUntil(data, position, " ")
        if value is None: 
            value = PortCommands.getString(data, position, PortCommands.END_OF_STRING)
        return value
