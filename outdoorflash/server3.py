#!/usr/bin/python
import sys
import socket
import time
import datetime
import serial
import uuid
import re
from thread import *

sys.path.insert(0, '/usr/lib/python2.7/bridge/')
from bridgeclient import BridgeClient as bridgeclient

#----------------------------------------------------------------------------------------
#Function to get the IP address of the interface
def getip():
    global ipAddress
    hostname = socket.gethostname()
    ipAddress = socket.gethostbyname(hostname)
    return (ipAddress)

#----------------------------------------------------------------------------------------
#Function to return the MAC address of the interface
def getHwAddr():
    global macAddress
    macAddress = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    return macAddress

#----------------------------------------------------------------------------------------
#Function to send aa message to the ssrv after a command has been received
def clientthread(conn):
    #Sending message to connected client
    conn.send('[EOTX]\r\n')

#----------------------------------------------------------------------------------------
#Function to read a line from the socket data and process it
def readlines(sock, recv_buffer=4096, delim='\r\n'):
    buffer = ''
    data = True
    while data:
        data = sock.recv(recv_buffer)
        buffer += data

        while buffer.find(delim) != -1:
            line, buffer = buffer.split('\r\n', 1)
            yield line
    return


def main():
    serverHost = ''
    macAddress = ''
    serverPort = 1000
    snbbHost = ''
    snbbPort = 2030
    ipAddress = ''

    stateMachineIdle = 10
    stateMachineBoot = 20
    stateMachineStart = 30
    stateMachineScan = 40
    stateMachine = 0
    HeartbeatFrq = 240
    HeartbeatTime = 0
    server_address = ''
    ledontime = 2 #the one time for good / bad card read
    VSET = 0 # Volume of Speaker
    ColorOne = ''
    ColorTwo = ''

    #Send the status to the arduino side. We will use pin a variable LSTAT (LED Status) to indicate the status of go or no go.
    #When LSTAT = 0 the we flash red, When LSTAT is 1 we flash green and when LSTAT = 2 we flash blue (standby)

    value = bridgeclient()
    value.put('LSTAT', '0')
    print 'value of LSTAT is', value.get('LSTAT')
    ledtime = datetime.datetime.now()

    #Setup phase before we try and connect to the snbb broardcast
    #Setup the serial scanner

    #Establish the Serial input for the scanner unit

    buffer = bytes()
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2)
    #Print the serial connection string for DEBUG
    #print ser

    #set the initial state of the state machine
    stateMachine = stateMachineIdle

    macAddress = getHwAddr()
    print 'Mac Address is :', macAddress

    #this is the head of the state machine the BIG loop
    while True:


    #we enter into the idel mode and listen for the snbb broardcast from the server
    #from the snbb broardcast we get the ip address and the port number to be used for all communications with ssrv

        while (stateMachine == stateMachineIdle):
        # Listen for the SNBB broadcast to find the server IP Address
            # SNBB port address is 2030
            snbbPort = 2030

            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.bind((snbbHost, snbbPort))

            try:
                message = s.recv(1024)

                if (message[0:6] == '[SNBB]'):
                    print "Got data: %s" % repr(message)
                    serverHost = message[36:51]
                    print 'IPaddress of Server: %s' % serverHost
                    serverPort = int(message[21:26])
                    print "Server Port: %d" % int(serverPort)
                    stateMachine = stateMachineBoot
                    print 'Going to Boot phase'
                    print 'stateMachine is', str(stateMachine)
                    s.close

                else:
                    stateMachine = stateMachineIdle
                    print ' SNBB failed'

            except KeyboardInterrupt:
                break


            # State machine is entering the boot phase
            # We connect to the serverHost and serverPort returned by the snbb message and we sent a boot packet and listen for a replay

            while (stateMachine == stateMachineBoot):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_address = ((serverHost, serverPort))
                    s.connect(server_address)
                    message = '[BOOT].' + str(macAddress) + '.0.0.061008060200.0.0\r\n'
                    print  message
                    #Set the whole string
                    s.sendall(message)

                except socket.error:
                    print 'Failed to create socket'
                    stateMachine = stateMachineIdle
                    print 'Soft Reset started'

                for line in readlines(s):
                    # Do something with a line of data
                    if ('[CRDS]' in line):
                        print line
                    #s.sendall('[EOTX]/r/n')
                    elif ('[CMSG]' in line):
                        print line
                    #s.sendall('[EOTX]/r/n')
                    elif ('[MSSG]' in line):
                        print line
                    #s.sendall('[EOTX]/r/n')
                    elif ('[DEVC]' in line):
                        print line
                    #s.sendall('[EOTX]/r/n')
                    elif ('[DIOP]' in line):
                        print line
                    #s.sendall('[EOTX]/r/n')
                    elif ('[VSET]' in line):
                        print line
                    #s.sendall('[EOTX]/r/n')
                    elif ('[COLO]' in line):
                        print line
                    #s.sendall('[EOTX]/r/n')
                    elif ('[CNFG]' in line):
                        print line
                    #s.sendall('[EOTX]/r/n')
                    else:
                        stateMachine = stateMachineStart
                        s.close

                cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    cs.bind((serverHost, serverPort))
                except socket.error, msg:
                print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
                stateMachine = stateMachineIdle

                print 'Command Socket bind complete'
                cs.listen(1)
                print'Socket is now listening
            ################################
            #Set up the listening port

#StateMachine is now in start mode and ready to accept and send card scan data to ssrv
#we send a scan packet and we receive a acct pkt back


while (stateMachine == stateMachineStart):


    print 'Soft Reset started'

    for command in readlines(s):
        if ('[PRCE]' in command):
            print command
            clientthread(cs)
        elif ('[DELY]' in command):
            print command
            clientthread(cs)
        elif ('[REVX]' in command:
            print command
        clientthread(cs)
        elif ('[MSSG]' in command:
        print command
        clientthread(cs)


        #if we have not communicated with the server in the last 60 sec we send a [HAPY] pkt
        if (HeartbeatTime == 0):
        timeNow = datetime.datetime.now()
        HeartbeatTime = timeNow
        print 'HeartbeatTime is  %d', HeartbeatTime
        else:
        timeNow = datetime.datetime.now()
        timeDiff = timeNow - HeartbeatTime
        print timeDiff.seconds

        if (timeDiff.seconds > HeartbeatFrq):
        HeartbeatTime = datetime.datetime.now()
        print 'Send Happy packet to server'
        playstate = '0'
        bufferTxns = '0'
        priceSelection = '1'
        #timeNOW =  datetime.datetime.now().time()
        dateNow = datetime.datetime.now().strftime("%Y%m%d")
        timeNow = datetime.datetime.now().strftime("%H%M%S")

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ((serverHost, serverPort))
            s.connect(server_address)
            message = '[HAPY].' + str(
                macAddress) + '.' + dateNow + timeNow + '.' + playstate + '.' + bufferTxns + '.' + priceSelection + '\r\n'
            print  message
            s.sendall(message)
        except socket.error:
            print 'Failed to create socket'
            stateMachine = stateMachineIdle
            print 'Soft Reset started'

        # try:
        # 				command_str = s.recv(4096)
        # 				print command_str
        # 				print 'Length of return is ;', len(command_str)
        # 				print command_str
        #
        # 			except socket.error:
        # 				#Send failed
        # 				print 'Scan Send failed' + str(socket.error)
        # 				message = ''
        # 				command_str = ''
        # 				statemachine = stateMachinStart

        # Read the barcode from the scanner and process

    barcode = ser.readline()
    barcode.rstrip('\r\n')
    barcode_length = len(barcode)
    if (len(barcode) > 0):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ((serverHost, serverPort))
            s.connect(server_address)
            message = message = '[SCAN].' + str(macAddress) + '.' + barcode + '\r\n'
            print  message
            #Set the whole string
            s.sendall(message)

        except socket.error:
            print 'Failed to create socket'
            stateMachine = stateMachineIdle
            print 'Soft Reset started'

        for line in readlines(s):
        # Do something with a line of data
            if ('[ACCT]' in line):
                acct_header = line[0:6]
                line = line[7:len(line)]
                second_index = line.find('.')
                acct_card_number = line[0:second_index]
                print 'acct_number is', acct_card_number
                line = line[second_index: (len(line))]
                #get the reason code

                acct_reason_code = line[1:3]
                acct_reason_code = acct_reason_code.strip()
                print 'Reason code is:', acct_reason_code
                # look at the reason codes

                if (acct_reason_code == '00'):
                    print'Good Scan'
                    #Need to set the light patter
                    #Need to set the light pattern
                    value.put('LSTAT', '1')
                    print 'value of LSTAT is', value.get('LSTAT')
                    ledtime = datetime.datetime.now()
                elif (acct_reason_code == '01'):
                    print' Reason Code 01'
                    #Need to set the light pattern
                    value.put('LSTAT', '0')
                    print 'value of LSTAT is', value.get('LSTAT')
                    ledtime = datetime.datetime.now()
                elif (acct_reason_code == '02'):
                    print'Insufficient Funds'
                    #Need to set the light pattern
                    value.put('LSTAT', '0')
                    print 'value of LSTAT is', value.get('LSTAT')
                    ledtime = datetime.datetime.now()
                else:
                    print'Reason code is', acct_reason_code

                acct_play_balance = line[4:16]
                acct_play_balance = acct_play_balance.strip()
                print 'play balance is', acct_play_balance

                acct_cash_balance = line[17:28]
                acct_cash_balance = acct_cash_balance.strip()
                print 'play cash is', acct_cash_balance

                acct_comp_balance = line[29:40]
                acct_comp_balance = acct_comp_balance.strip()
                print 'comp balance is', acct_comp_balance

                acct_ticket_balance = line[41:52]
                acct_ticket_balance = acct_ticket_balance.strip()
                print 'ticket balance is', acct_ticket_balance

                acct_dispense_actn = line[53]
                acct_dispense_actn = acct_dispense_actn.strip()
                print 'dispense actn is', acct_dispense_actn

                acct_approval_type = line[54:55]
                acct_approval_type = acct_approval_type.strip()
                print 'acct approval type is', acct_approval_type

                acct_total_balance = line[56:67]
                acct_total_balance = acct_total_balance.strip()
                print 'acct_total balance is', acct_total_balance

                acct_time_balance = line[68:79]
                acct_time_balance = acct_time_balance.strip()
                print 'acct_time_balance is', acct_time_balance

                acct_entitlement_balance = line[80:81]
                acct_entitlement_balance = acct_entitlement_balance.strip()
                print 'acct_entitlement_balance is', acct_entitlement_balance

                acct_output_signal = line[82:97]
                acct_output_signal = acct_output_signal.strip()
                print 'acct_output_signal is', acct_output_signal
            else:
                print 'No Account pkt received back'

        print'.'
    #Reset the lights
    timeNow = datetime.datetime.now()
    timeDiff = timeNow - ledtime
    if (timeDiff.seconds > ledontime):
        value.put('LSTAT', '2')
        print 'value of LSTAT is', value.get('LSTAT')

    stateMachine = stateMachineStart
    s.close

if __name__ == '__main__':
    main()
