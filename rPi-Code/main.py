"""
Title: Augmented Warfighter Awareness System Main
Author: Bryan Ritchie
Team: UCCS Senior Design "Heads Up" 2020

Purpose: This file is intended to run a Raspberry Pi 4 (or other submodels),
         a 2.8" TFT display, a TCP Server, and mock sensor data intended to
         simulate real-time battlefield data to be displayed holographically
         on a Microsoft HoloLens (Gen 1). 

"""

import socket
from threading import Thread
from multiprocessing import Value
import display
from display import MessagePrintService, ConnectionStatus
import time
import subprocess
import platform
import os

RUN =  0
DEMO = 1

RUNMODE = RUN

HOST = "10.0.0.204"
PORT = "9501"

# Demo Sensor Data
SAMPLES = 3

ID = [1, 2, 3]
# ammo_count = [265, 200, 20]
# water_level = [3, 2, 1]
# vitals = [ [84, 99, 98.6, 15], [90, 95, 99.2, 8], [120, 87, 90.1, 30] ]
# weapon_status = [0, 1, 12]
# sensorData =\
# [\
#     [ID[0], ammo_count[0], water_level[0], vitals[0], weapon_status[0] ],\
#     [ID[1], ammo_count[1], water_level[1], vitals[1], weapon_status[1]],\
#     [ID[2], ammo_count[2], water_level[2], vitals[2], weapon_status[2]]\
# ]

ammo_count_packages =\
[\
    [265, 200, 20],\
    [245, 185, 160],\
    [200, 270, 200]\
]

water_level_packages =\
[\
    [3, 2, 1],\
    [4, 1, 0],\
    [2, 0, 1]\
]

vitals_packages =\
[\
    [\
        [ 84, 99, 98.6, 15  ],\
        [ 90, 95, 99.2, 8   ],\
        [ 120, 87, 90.1, 30 ]\
    ],\

    [\
        [ 82, 98, 98.4, 14 ],\
        [ 92, 96, 99.4, 9  ],\
        [ 135, 81, 87.8, 45 ]\
    ],\

    [ 
        [ 80, 99, 98.5, 15 ],\
        [ 108, 98, 99.3, 12 ],\
        [ 160, 65, 83.4, 60 ]\
    ]\
]

weapon_status_packages =\
[\
    [0, 1, 12],\
    [0, 1, 12],\
    [0, 1, 12]\
]

sensorData_packages =\
[\
    [\
        [ID[0], ammo_count_packages[0][0], water_level_packages[0][0], vitals_packages[0][0], weapon_status_packages[0][0] ],\
        [ID[1], ammo_count_packages[0][1], water_level_packages[0][1], vitals_packages[0][1], weapon_status_packages[0][1]],\
        [ID[2], ammo_count_packages[0][2], water_level_packages[0][2], vitals_packages[0][2], weapon_status_packages[0][2]]\
    ],\

    [\
        [ID[0], ammo_count_packages[1][0], water_level_packages[1][0], vitals_packages[1][0], weapon_status_packages[1][0] ],\
        [ID[1], ammo_count_packages[1][1], water_level_packages[1][1], vitals_packages[1][1], weapon_status_packages[1][1]],\
        [ID[2], ammo_count_packages[1][2], water_level_packages[1][2], vitals_packages[1][2], weapon_status_packages[1][2]]\
    ],\

    [\
        [ID[0], ammo_count_packages[2][0], water_level_packages[2][0], vitals_packages[2][0], weapon_status_packages[2][0] ],\
        [ID[1], ammo_count_packages[2][1], water_level_packages[2][1], vitals_packages[2][1], weapon_status_packages[2][1]],\
        [ID[2], ammo_count_packages[2][2], water_level_packages[2][2], vitals_packages[2][2], weapon_status_packages[2][2]]\
    ]\
]

def ServerHost():
    exit = 0

    # Blocking statement to wait for a connection
    time.sleep(2)
    messagePrintService.printClientMessage("Waiting for connection")
    
    # accept connection
    (clientsocket, address) = serversocket.accept()
    time.sleep(2)

    # Reply to connection
    messagePrintService.printClientMessage("Connection Success with {}:{}".format(str(address[0]), str(address[1])))
    clientsocket.send("Welcome to the Augmented Warfighter Awareness System\r\n".encode("utf-8"))
    clientsocket.send("Connection from {}:{} to {}:{}".format(str(address[0]), str(address[1]), HOST, PORT).encode("utf-8"))

    while not exit:

        try:    
            # Display valid commands to client
            clientsocket.send("\r\n\r\nValid Commands: \r\nPing\r\nPoll\r\nShutdown\r\nCommand: ".encode())
            
            # Receive and decode clients message
            data = clientsocket.recv(1024).decode("utf-8")

        except BrokenPipeError as e: #< Unexpected disconnection
            # Print exception
            messagePrintService.printClientMessage(str(e))
            messagePrintService.printClientMessage("Attempting to reconnect")
            
            # Attempt to reconnect
            serversocket.listen(requestAttempts)
            (clientsocket, address) = serversocket.accept()

            # Did we find a client?
            if(clientsocket is not None and address is not None):
                messagePrintService.printClientMessage("Reconnection Success with " + str(address))
                clientsocket.send("Welcome to the Augmented Warfighter Awareness System\r\n".encode("utf-8"))
            
                # Display valid commands to client
                clientsocket.send("\r\n\r\nValid Commands: \r\nPing\r\nPoll\r\nShutdown\r\nCommand: ".encode())
                
                # Receive and decode clients message
                data = clientsocket.recv(1024).decode("utf-8")

            else:
                messagePrintService.printClientMessage("Client disconnected")
                exit = 1
            
        if(data is not None):

            if data == "Ping" or data == 'ping':
                # Acknowledge command
                messagePrintService.printClientMessage("Ping request from " + str(address[0]))
                
                # Send a response to client
                clientsocket.send("\n{}: ".format(HOST).encode())
                clientsocket.send("Pong\r\n".encode())

            elif data == "Poll" or data == 'poll':
                # Acknowledge command
                messagePrintService.printClientMessage("Poll request from " + str(address[0]))

                # Send a response to client
                clientsocket.send("\n{}: ".format(HOST).encode())
                for i in range(3):
                    clientsocket.send(str(sensorData_packages[messagePrintService.sample_counter][i]).encode() + "\r\n".encode())

            elif data == "Shutdown" or data == 'shutdown':
                # Acknowledge command
                messagePrintService.printClientMessage("Shutdown commanded from " + str(address))
                exit = 1

    clientsocket.close()
    return

if __name__ == '__main__':

    if(RUNMODE == RUN):
        # Setup Display
        display.clearScreen()
        display.hideCursor()

        # Turn on message print service
        messagePrintService = MessagePrintService()

        # Display AWAS Structure
        messagePrintService.displayStructure()

        # Set up a connection status object (not used)
        connectionStatus = ConnectionStatus()
        
        # Set up the socket object
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        host = "10.0.0.204"
        #host = socket.gethostname() # localhost 
        port = 9501
        requestAttempts = 5

        try:
            # Bind the socket object and listen for incoming connections
            serversocket.bind((host,port))
            serversocket.listen(requestAttempts)
            
            messagePrintService.printClientMessage("Server started; Listening for connections on " + str(host) + \
                ":" + str(port))

            # Create a new thread to listen for incoming connections
            t2 = Thread(target=ServerHost)
            t2.start()

        except OSError as e: #< Connection attempt failed
            messagePrintService.printClientMessage(str(e))

            # Wait and try again
            time.sleep(10)
            try:
                serversocket.bind((host,port))
                serversocket.listen(requestAttempts)
                
                messagePrintService.printClientMessage("Server started; Listening for connections on " + str(host) + \
                    ":" + str(port))

                # Create a new thread to listen for incoming connections
                t2 = Thread(target=ServerHost)
                t2.start()
            
            except OSError as e: #< Second connection attempt failed
                messagePrintService.printClientMessage(str(e))
                messagePrintService.printClientMessage("ServerHost unable to start. Power cycle system and try again")

        t1 = Thread(target=messagePrintService.displayData, args=(connectionStatus, sensorData_packages,))
        t1.start()

    elif(RUNMODE == DEMO): # Print out sensorData_packages
        for sample in range(3):
            print("Sample " + str(sample))
            for warrior in range(3):
                print(" -Warrior " + str(warrior))
                for sensor in range(5):
                    print("   -Sensor " + str(sensor))
                    if(sensor == 3): # vitals
                        for vital in range(4):
                            print("     -Vital " + str(vital) + ":   " + str(sensorData_packages[sample][warrior][sensor][vital]))
                    else:        
                        print("                 " + str(sensorData_packages[sample][warrior][sensor]))
