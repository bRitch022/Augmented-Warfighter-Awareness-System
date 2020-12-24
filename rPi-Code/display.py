"""
Title: Augmented Warfighter Awareness System Display
Author: Bryan Ritchie
Team: UCCS Senior Design "Heads Up" 2020

Purpose: This file is intended as a driver for the 2.8" TFT display,
         to display the "real-time" simulated sensor data.       

"""
import time
from multiprocessing import Value
import os
#from main import sensorData

RUN = 0
DEMO = 1

# Change this runmode to run as a standalone demo
# This is useful when modifying the layout of the display
RUNMODE = RUN

### <<< SCREEN LAYOUT >>> ###
#< COLUMNS >#
TITLE_START             =   10
SAMPLE_START            =   4
WARRIOR_NAME_START      =   14
WARRIOR_NAME_SPACING    =   13
DATA_NAME_START         =   4
DATA_START              =   WARRIOR_NAME_START + 3
DATA_SPACING            =   WARRIOR_NAME_SPACING
CONNECTION_STATUS_START =   4
CLIENT_MESSAGE_START    =   3

#< ROWS >#
TITLE_ROW               =   3
SAMPLE_ROW              =   TITLE_ROW + 1
WARRIOR_NAME_ROW        =   TITLE_ROW + 2
AMMO_ROW                =   TITLE_ROW + 3
WATER_ROW               =   TITLE_ROW + 4
HR_ROW                  =   TITLE_ROW + 5
SPO2_ROW                =   TITLE_ROW + 6
TEMP_ROW                =   TITLE_ROW + 7
RESP_ROW                =   TITLE_ROW + 8
WEAPON_ROW              =   TITLE_ROW + 9
CONNECTION_STATUS_ROW   =   3
CLIENT_MESSAGE_ROW      =   WEAPON_ROW + 2

#< CLIENT MESSAGE >#
MAX_MESSAGE_LENGTH      =   49
MAX_MESSAGE_LINES       =   5

### <<< SENSOR DATA >>> ###
#< SENSOR DATA ELEMENTS>#
WARRIOR_TOTAL           =   3
HIGH                    =   1
LOW                     =   0

ID_DATA                 =   0
AMMO_DATA               =   1
WATER_DATA              =   2
VITALS_DATA             =   3
HR_DATA                 =   0
SPO2_DATA               =   1
TEMP_DATA               =   2
RESP_DATA               =   3
WEAPON_DATA             =   4

# AMMO COLOR STATUS >#
# Units are in Rounds of Ammunition
AMMO_GREEN              =   270
AMMO_AMBER              =   202
AMMO_RED                =   135
AMMO_BLACK              =   68   # Black doesn't show up well, so it will be blue

# WATER COLOR STATUS >#
# Units are in Quarts
WATER_GREEN             =   3
WATER_AMBER             =   2
WATER_RED               =   1
WATER_BLACK             =   0

#< VITALS COLOR STATUS >#
#<< HR >>#
# Units: Beats per Minute   [LOW, HIGH]
HR_GREEN                =   [60, 100]
HR_AMBER                =   [50, 120]
HR_RED                  =   [40, 160]
HR_BLACK                =   [30, 200]

#<< SPO2 >>#
SPO2_GREEN              =   100
SPO2_AMBER              =   92
SPO2_RED                =   85
SPO2_BLACK              =   80

#<< RESPIRATIONS >>#
# Units: Breaths per min    [LOW, HIGH]
RESP_GREEN              =   [12, 15]
RESP_AMBER              =   [10, 18]
RESP_RED                =   [8, 21]
RESP_BLACK              =   [0, 25]

#<< TEMP >>#
# Units: Degrees F          [LOW, HIGH]
TEMP_GREEN              =   [96, 99]
TEMP_AMBER              =   [93, 101]
TEMP_RED                =   [85, 103]
TEMP_BLACK              =   [80, 104]

#< WEAPON COLOR STATUS >#
# WEAPON ON SAFE: Even Number
# WEAPON ON FIRE: Odd Number
# [SECONDS SINCE FIRING + SAFETY]
WEAPON_GREEN            = 0         # Has not fired, weapon on safe
WEAPON_AMBER            = 1         # Has not fired, weapon on fire
WEAPON_RED              = 11        # Been at least 10 seconds since last firing (weapon on safe or fire)
WEAPON_BLACK            = [2, 11]   # Been 2 - 10 just a short time since firing (weapon on safe or fire)

### <<< TFT NAVIGATION >>> ###
def moveCursor(row, col):
    print(chr(27) + "[" + str(row) + ";" + str(col) + "f")

def clearScreen():
    moveCursor(1,1)
    print(chr(27) + "[2J")

def hideCursor():
    print("\033[?25h")

# Print at a certain location on the TFT Screen
def print_at(row, col, message):
    print(chr(27) + "[" + str(row) + ";" + str(col) + "f" + message)

### <<< HANDLE TFT MESSAGE PRINTING >>> ###
class MessagePrintService(object):
    def __init__(self):
        self.messageLines = [None] * MAX_MESSAGE_LINES

        self.colorText_Mutex = Value("i", 0)

        self.messageColor   = "red"
        self.warriorColor   = "white"
        self.dataNameColor  = "white"
        self.dataColor      = "white"
        self.titleColor     = "green"
        self.borderColor    = "white"

        self.sample_counter = 0
        self.delay_counter   = 0

    def displayStructure(self):
        #< BORDER >#
        moveCursor(1,1)
        self.colorText(self.borderColor)
        print("*****************************************************")
        print("*                                                   *")
        print("*                                                   *")
        print("*                                                   *")
        print("*                                                   *")
        print("*                                                   *")
        print("*                                                   *")
        print("*                                                   *")
        print("*                                                   *")
        print("*                                                   *")
        print("*                                                   *")
        print("*                                                   *")
        print("*                                                   *")
        print("*                                                   *")
        print("*                                                   *")
        print("*                                                   *")
        print("*                                                   *")
        print("*                                                   *")
        print("*****************************************************")

        #< TITLE >#
        self.colorText(self.titleColor)
        print_at(TITLE_ROW, TITLE_START, "AUGMENTED WARFIGHTER AWARENESS SYSTEM")        

        #< WARRIOR LABELS >#
        self.colorText(self.warriorColor)
        print_at(WARRIOR_NAME_ROW, WARRIOR_NAME_START,  "Warrior 1")
        print_at(WARRIOR_NAME_ROW, WARRIOR_NAME_START + WARRIOR_NAME_SPACING,  "Warrior 2")
        print_at(WARRIOR_NAME_ROW, WARRIOR_NAME_START + WARRIOR_NAME_SPACING * 2,  "Warrior 3")

        #< SENSOR LABELS >#
        self.colorText(self.dataNameColor)
        print_at(AMMO_ROW, DATA_NAME_START,     "Ammo   :")
        print_at(WATER_ROW, DATA_NAME_START,    "Water  :")
        print_at(HR_ROW, DATA_NAME_START,       "HR     :")
        print_at(SPO2_ROW, DATA_NAME_START,     "SPO2   :")
        print_at(TEMP_ROW, DATA_NAME_START,     "Temp   :")
        print_at(RESP_ROW, DATA_NAME_START,     "Resp   :")
        print_at(WEAPON_ROW, DATA_NAME_START,   "Weapon :")
    
    def clearMessagePane(self):
        self.colorText(self.borderColor)
        print_at(CLIENT_MESSAGE_ROW, CLIENT_MESSAGE_START, "                                                   ")
        self.colorText(self.borderColor)
        print_at(CLIENT_MESSAGE_ROW + 1, 1,                "*                                                   *")
        self.colorText(self.borderColor)
        print_at(CLIENT_MESSAGE_ROW + 2, 1,                "*                                                   *")
        self.colorText(self.borderColor)
        print_at(CLIENT_MESSAGE_ROW + 3, 1,                "*                                                   *")
        self.colorText(self.borderColor)
        print_at(CLIENT_MESSAGE_ROW + 4, 1,                "*                                                   *")
    
    def shiftMessagePane(self, numLines):

        # Shift Messages 
        for i in range(numLines):
            for j in range(MAX_MESSAGE_LINES - 1, 0, -1):
                self.messageLines[j] = self.messageLines[j - 1]
        
        # Re-print messages 
        for k in range(MAX_MESSAGE_LINES):
            if(self.messageLines[k] is not None):
                self.colorText(self.borderColor)
                print_at(CLIENT_MESSAGE_ROW + k, CLIENT_MESSAGE_START, "                                                  *")
                self.colorText(self.messageColor)
                print_at(CLIENT_MESSAGE_ROW + k, CLIENT_MESSAGE_START, self.messageLines[k])

    def printClientMessage(self, message):
        # Add concatenated timestamp to message
        message = "[" + str(int(time.time()) & 0xFFF) + "]: " + str(message)

        # Check length of message
        messageLength = len(message)
        messagesRequired = 1
        
        # If message is too long, count how many messages will be needed?
        while(messageLength > MAX_MESSAGE_LENGTH):
            messagesRequired += 1
            messageLength -= MAX_MESSAGE_LENGTH

        # Shift the message pane to make room for new messages
        self.shiftMessagePane(messagesRequired)

        # Clear the first message row (Bugfix)
        self.colorText(self.borderColor)
        print_at(CLIENT_MESSAGE_ROW, CLIENT_MESSAGE_START, "                                                  *")
        
        # Change the pen color to messageColor
        self.colorText(self.messageColor)

        # Create a messages list to split the messages into
        if(messagesRequired > 1):
            # Re-discover message length
            messageLength = len(message)

            # Track how many messages have been parsed
            messagesParsed = 0

            while(messagesParsed < messagesRequired and messageLength > MAX_MESSAGE_LENGTH) and messagesParsed < MAX_MESSAGE_LINES:
                
                # Store message to messageLines (for shifting purposes)
                self.messageLines[messagesParsed] = str(message[ messagesParsed*MAX_MESSAGE_LENGTH : (messagesParsed + 1)*MAX_MESSAGE_LENGTH ])

                # Print the message that was stored
                print_at(CLIENT_MESSAGE_ROW + messagesParsed, CLIENT_MESSAGE_START, self.messageLines[messagesParsed])

                # Iterate how many messages have been parsed
                messagesParsed += 1

                # Reduce remaining message length to be parsed
                messageLength -= MAX_MESSAGE_LENGTH

            # Check if there is any leftover message
            if(messageLength > 0 and messagesParsed < MAX_MESSAGE_LINES):
                # Store the message to messageLines (for shifting purposes)
                self.messageLines[messagesParsed] = str(message[ messagesParsed*MAX_MESSAGE_LENGTH : len(message) ])
                
                # Print the message that was stored
                print_at(CLIENT_MESSAGE_ROW + messagesParsed, CLIENT_MESSAGE_START, self.messageLines[messagesParsed])
            
        else:
            # Just print the single message
            self.messageLines[0] = str(message)
            print_at(CLIENT_MESSAGE_ROW, CLIENT_MESSAGE_START, self.messageLines[0])

    def displayData(self, connectionStatus, sensorData_packages):
        while(1):
            # Iterate through the sample data
            if(self.sample_counter < 3):

                # Apply a delay to make the changing data observable
                if(self.delay_counter >= 2000):
                    self.sample_counter += 1
                    self.delay_counter = 0 # cyclic reset
                else:
                    self.delay_counter += 1
            else:
                self.sample_counter = 0 # cyclic reset
            
            # redundant check (Bugfix)
            if(self.sample_counter == 3):
                self.sample_counter = 0

            # Select the current sample data
            sensorData = sensorData_packages[self.sample_counter]

            #< AMMO >#
            # Determine Color Status
            for i in range(WARRIOR_TOTAL):
                if(sensorData[i][AMMO_DATA] > AMMO_AMBER and sensorData[i][AMMO_DATA] <= AMMO_GREEN):
                    self.colorText("green")
                elif(sensorData[i][AMMO_DATA] > AMMO_RED and sensorData[i][AMMO_DATA] <= AMMO_AMBER):
                    self.colorText("yellow")
                elif(sensorData[i][AMMO_DATA] > AMMO_BLACK and sensorData[i][AMMO_DATA] <= AMMO_RED):
                    self.colorText("red")
                elif(sensorData[i][AMMO_DATA] <= AMMO_BLACK):
                    self.colorText("blue")

                # Print Data
                print_at(AMMO_ROW, DATA_START + (DATA_SPACING * i), str(sensorData[i][AMMO_DATA]) + "   ") 

            #< WATER >#
            for i in range(WARRIOR_TOTAL):
                # Determine Color Status
                if(sensorData[i][WATER_DATA] > WATER_AMBER):
                    self.colorText("green")
                elif(sensorData[i][WATER_DATA] > WATER_RED and sensorData[i][WATER_DATA] <= WATER_AMBER):
                    self.colorText("yellow")
                elif(sensorData[i][WATER_DATA] > WATER_BLACK and sensorData[i][WATER_DATA] <= WATER_RED):
                    self.colorText("red")
                elif(sensorData[i][WATER_DATA] <= WATER_BLACK):
                    self.colorText("blue")

                # Print Data
                print_at(WATER_ROW, DATA_START + (DATA_SPACING * i), str(sensorData[i][WATER_DATA]) + "   ") 

            #< HR >#
            for i in range(WARRIOR_TOTAL):
                # Determine Color Status
                if(sensorData[i][VITALS_DATA][HR_DATA] >= HR_GREEN[LOW] and sensorData[i][VITALS_DATA][HR_DATA] <= HR_GREEN[HIGH]):
                    self.colorText("green")
                elif((sensorData[i][VITALS_DATA][HR_DATA] >= HR_AMBER[LOW] and sensorData[i][VITALS_DATA][HR_DATA] < HR_GREEN[LOW]) or \
                    (sensorData[i][VITALS_DATA][HR_DATA] > HR_GREEN[HIGH] and sensorData[i][VITALS_DATA][HR_DATA] <= HR_AMBER[HIGH])):
                    self.colorText("yellow")
                elif((sensorData[i][VITALS_DATA][HR_DATA] >= HR_RED[LOW] and sensorData[i][VITALS_DATA][HR_DATA] < HR_AMBER[LOW]) or \
                    (sensorData[i][VITALS_DATA][HR_DATA] > HR_AMBER[HIGH] and sensorData[i][VITALS_DATA][HR_DATA] <= HR_RED[HIGH])):
                    self.colorText("red")
                elif(sensorData[i][VITALS_DATA][HR_DATA] <= HR_BLACK[LOW] or sensorData[i][VITALS_DATA][HR_DATA] >= HR_BLACK[HIGH]):
                    self.colorText("blue")

                # Print Data
                print_at(HR_ROW, DATA_START + (DATA_SPACING * i), str(sensorData[i][VITALS_DATA][HR_DATA]) + "   ") 

            #< SPO2 >#
            for i in range(WARRIOR_TOTAL):
                # Determine Color Status
                if(sensorData[i][VITALS_DATA][SPO2_DATA] > SPO2_AMBER and sensorData[i][VITALS_DATA][SPO2_DATA] <= SPO2_GREEN):
                    self.colorText("green")
                elif(sensorData[i][VITALS_DATA][SPO2_DATA] > SPO2_RED and sensorData[i][VITALS_DATA][SPO2_DATA] <= SPO2_AMBER):
                    self.colorText("yellow")
                elif(sensorData[i][VITALS_DATA][SPO2_DATA] > SPO2_BLACK and sensorData[i][VITALS_DATA][SPO2_DATA] <= SPO2_RED):
                    self.colorText("red")
                elif(sensorData[i][VITALS_DATA][SPO2_DATA] <= SPO2_BLACK):
                    self.colorText("blue")

                # Print Data
                print_at(SPO2_ROW, DATA_START + (DATA_SPACING * i), str(sensorData[i][VITALS_DATA][SPO2_DATA]) + "   ")

            #< RESP >#
            for i in range(WARRIOR_TOTAL):
                # Determine Color Status
                if(sensorData[i][VITALS_DATA][RESP_DATA] >= RESP_GREEN[LOW] and sensorData[i][VITALS_DATA][RESP_DATA] <= RESP_GREEN[HIGH]):
                    self.colorText("green")
                elif((sensorData[i][VITALS_DATA][RESP_DATA] >= RESP_AMBER[LOW] and sensorData[i][VITALS_DATA][RESP_DATA] < RESP_GREEN[LOW]) or \
                    (sensorData[i][VITALS_DATA][RESP_DATA] > RESP_GREEN[HIGH] and sensorData[i][VITALS_DATA][RESP_DATA] <= RESP_AMBER[HIGH])):
                    self.colorText("yellow")
                elif((sensorData[i][VITALS_DATA][RESP_DATA] >= RESP_RED[LOW] and sensorData[i][VITALS_DATA][RESP_DATA] < RESP_AMBER[LOW]) or \
                    (sensorData[i][VITALS_DATA][RESP_DATA] > RESP_AMBER[HIGH] and sensorData[i][VITALS_DATA][RESP_DATA] <= RESP_RED[HIGH])):
                    self.colorText("red")
                elif(sensorData[i][VITALS_DATA][RESP_DATA] <= RESP_BLACK[LOW] or sensorData[i][VITALS_DATA][RESP_DATA] >= RESP_BLACK[HIGH]):
                    self.colorText("blue")

                # Print Data
                print_at(RESP_ROW, DATA_START + (DATA_SPACING * i), str(sensorData[i][VITALS_DATA][RESP_DATA]) + "   ") 

            #< TEMP >#
            for i in range(WARRIOR_TOTAL):
                # Determine Color Status
                if(sensorData[i][VITALS_DATA][TEMP_DATA] >= TEMP_GREEN[LOW] and sensorData[i][VITALS_DATA][TEMP_DATA] <= TEMP_GREEN[HIGH]):
                    self.colorText("green")
                elif((sensorData[i][VITALS_DATA][TEMP_DATA] >= TEMP_AMBER[LOW] and sensorData[i][VITALS_DATA][TEMP_DATA] < TEMP_GREEN[LOW]) or \
                    (sensorData[i][VITALS_DATA][TEMP_DATA] > TEMP_GREEN[HIGH] and sensorData[i][VITALS_DATA][TEMP_DATA] <= TEMP_AMBER[HIGH])):
                    self.colorText("yellow")
                elif((sensorData[i][VITALS_DATA][TEMP_DATA] >= TEMP_RED[LOW] and sensorData[i][VITALS_DATA][TEMP_DATA] < TEMP_AMBER[LOW]) or \
                    (sensorData[i][VITALS_DATA][TEMP_DATA] > TEMP_AMBER[HIGH] and sensorData[i][VITALS_DATA][TEMP_DATA] <= TEMP_RED[HIGH])):
                    self.colorText("red")
                elif(sensorData[i][VITALS_DATA][TEMP_DATA] <= TEMP_BLACK[LOW] or sensorData[i][VITALS_DATA][TEMP_DATA] >= TEMP_BLACK[HIGH]):
                    self.colorText("blue")

                # Print Data
                print_at(TEMP_ROW, DATA_START + (DATA_SPACING * i), str(sensorData[i][VITALS_DATA][TEMP_DATA]) + "   ") 

            #< WEAPON >#
            for i in range(WARRIOR_TOTAL):
                if(sensorData[i][WEAPON_DATA] == WEAPON_GREEN):
                    self.colorText("green")
                elif(sensorData[i][WEAPON_DATA] == WEAPON_AMBER):
                    self.colorText("yellow")
                elif(sensorData[i][WEAPON_DATA] > WEAPON_RED):
                    self.colorText("red")
                elif(sensorData[i][WEAPON_DATA] >= WEAPON_BLACK[LOW] or sensorData[i][WEAPON_DATA] <= WEAPON_BLACK[HIGH]):
                    self.colorText("blue")

                # Print Data
                print_at(WEAPON_ROW, DATA_START + (DATA_SPACING * i), str(sensorData[i][WEAPON_DATA]) + "   ") 


    def colorText(self, color):
        # lock the colorText if it is in use by another process
        while(self.colorText_Mutex.value == 1):
            pass 
        
        # lock mutex
        self.colorText_Mutex.value = 1
        if(color == "red"):
            print(chr(27) + "[31m" + chr(27) + "[033F")
        elif(color == "green"):
            print(chr(27) + "[32m" + chr(27) + "[033F")
        elif(color == "yellow"):
            print(chr(27) + "[33m" + chr(27) + "[033F")
        elif(color == "blue"):
            print(chr(27) + "[34m" + chr(27) + "[033F")
        elif(color == "magenta"):
            print(chr(27) + "[35m" + chr(27) + "[033F")
        elif(color == "cyan"):
            print(chr(27) + "[36m" + chr(27) + "[033F")
        elif(color == "white"):
            print(chr(27) + "[37m" + chr(27) + "[033F")
        
        #unlock mutex
        self.colorText_Mutex.value = 0

    def hideCursor(self):
        print("\033[?25h")

        


class ConnectionStatus(object):

    def __init__(self):
        self.stateIndicatorTable = ["|", "/", "-", "\\"]
        self.errorIndicator = "0"
        self.errorState = 0
        self.stateIndicator = 0

    """ Cyclic Incrementing """
    def incrementStateIndicator(self):
        if(self.stateIndicator < len(self.stateIndicatorTable) - 1):
            self.stateIndicator += 1

        else:
            self.stateIndicator = 0
    
    def getStateIndicator(self):
        return self.stateIndicatorTable[self.stateIndicator]

    def displayConnectionStatus(self):
        while(1):
            time.sleep(1)
            if(not self.errorState):
                print_at(CONNECTION_STATUS_ROW, CONNECTION_STATUS_START, str(self.getStateIndicator()))
            else:
                print_at(CONNECTION_STATUS_ROW, CONNECTION_STATUS_START, str(self.errorIndicator))

# Depricated, but still might be useful
if(RUNMODE is DEMO):
    # Setup
    connectionStatus = ConnectionStatus()
    messagePrintService = MessagePrintService()

    clearScreen()
    messagePrintService.displayStructure()

    counter = 0

    # Loop
    while(1):
        #messagePrintService.displayData() #< to run this, pass in sample data
        if(not(counter % 200)):
            connectionStatus.incrementStateIndicator()
            counter += 1

        elif(counter is 1000):
            clearScreen()
            messagePrintService.displayStructure()
            counter = 0
            
        else:
            counter += 1

        connectionStatus.displayConnectionStatus()
