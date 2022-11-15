class Sensor():
    def __init__(self, imei:str) -> None:
        self.imei : str = imei
        self.readings : list[int] = []
        self.counter : int = 0

    def checkIMEI(self, imei:str) -> bool:
        return self.imei == imei

    def insertRSSI(self, rssi:int) -> None:
        self.readings.append(rssi)
        self.counter += 1

    def resetRSSI(self) -> None:
        self.readings:list[int] = []
        self.counter:int = 0

    def getReadingsLength(self) -> bool:
        return self.counter

    def checkReadingsLength(self, length:int) -> bool:
        return self.counter >= length