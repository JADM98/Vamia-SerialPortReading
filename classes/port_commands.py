class PortCommands(): 

    #Static Constants
    END_OF_STRING = -1
    START_OF_STRING = 0

    @staticmethod
    def checkIfCommand(data:str) -> bool:
        if(data.find("Command >> ") == 0):
            return True
        return False

    @staticmethod
    def contains(data:str, textToFind:str) -> bool:
        if(data.find(textToFind)):
            return True
        return False

    @staticmethod
    def getPosition(data:str, textToFind:str) -> int|None:
        position = data.find(textToFind)
        if position == -1:
            position = None
        return position

    @staticmethod
    def getLastPosition(data:str, textToFind:str) -> int|None:
        position = PortCommands.getPosition(data, textToFind)
        if position is not None:
            position += len(textToFind)
        return position

    @staticmethod
    def getString(data:str, start:int, stop:int) -> str|None:
        if stop == PortCommands.END_OF_STRING:
            stop = len(data)
        if start is None:
            return None
        if start > len(data):
            return None
        try:
            myData = data[start:stop]
        except:
            myData = data[start:len(data)]
        return myData

    @staticmethod
    def getStringUntil(data:str, start:int, charToFind:str) -> str|None:
        try:
            position = data.index(charToFind, start)
            myData = PortCommands.getString(data, start, position)
            return myData
        except:
            return None


