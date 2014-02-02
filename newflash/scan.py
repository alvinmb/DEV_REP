#!/usr/bin/python
import sys
import socket
import time
import datetime
import serial
import uuid
import re

sys.path.insert(0, '/usr/lib/python2.7/bridge/')
from bridgeclient import BridgeClient as bridgeclient
# Program to control the outdoor flash reader.
# The reader will scan a card and remove value or entitlements

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
#Function to process the account pkt
def process_account_pkt(command_str):
    if ('[ACCT]' in command_str):
        tsocket.sendall('[EOTX]/r/n')
        #pass the account package

        #acct_header = command_str[0:6]
        command_str = command_str[7:length_command_str]
        second_index = command_str.find('.')
        acct_card_number = command_str[0:second_index]
        print 'acct_number is', acct_card_number
        command_str = command_str[second_index: (len(command_str))]
        #get the reason code
        acct_reason_code = command_str[1:3]
        acct_reason_code = acct_reason_code.strip()
        print 'Reason code is:', acct_reason_code

        # look at the reason codes and response

        if (acct_reason_code == '00'):
            print'Good Scan'
            #Need to set the light pattern
            value.put('LSTAT', '1')
            print 'value of LSTAT is', value.get('LSTAT')

        elif (acct_reason_code == '01'):
            print' Reason Code 01'
            #Need to set the light pattern
            value.put('LSTAT', '0')
            print 'value of LSTAT is', value.get('LSTAT')

        elif (acct_reason_code == '02'):
            print'Insufficient Funds'
            #Need to set the light pattern
            value.put('LSTAT', '0')
            print 'value of LSTAT is', value.get('LSTAT')

        else:
            print'Reason code is', acct_reason_code
            value.put('LSTAT', '0')
            #Need to set the light pattern
            print 'value of LSTAT is', value.get('LSTAT')

            acct_play_balance = command_str[4:16]
            acct_play_balance = acct_play_balance.strip()
            print 'play balance is', acct_play_balance

            acct_cash_balance = command_str[17:28]
            acct_cash_balance = acct_cash_balance.strip()
            print 'play cash is', acct_cash_balance

            acct_comp_balance = command_str[29:40]
            acct_comp_balance = acct_comp_balance.strip()
            print 'comp balance is', acct_comp_balance

            acct_ticket_balance = command_str[41:52]
            acct_ticket_balance = acct_ticket_balance.strip()
            print 'ticket balance is', acct_ticket_balance

            acct_dispense_actn = command_str[53]
            acct_dispense_actn = acct_dispense_actn.strip()
            print 'dispense actn is', acct_dispense_actn

            acct_approval_type = command_str[54:55]
            acct_approval_type = acct_approval_type.strip()
            print 'acct approval type is', acct_approval_type

            acct_total_balance = command_str[56:67]
            acct_total_balance = acct_total_balance.strip()
            print 'acct_total balance is', acct_total_balance

            acct_time_balance = command_str[68:79]
            acct_time_balance = acct_time_balance.strip()
            print 'acct_time_balance is', acct_time_balance

            acct_entitlement_balance = command_str[80:81]
            acct_entitlement_balance = acct_entitlement_balance.strip()
            print 'acct_entitlement_balance is', acct_entitlement_balance

            acct_output_signal = command_str[82:97]
            acct_output_signal = acct_output_signal.strip()
            print 'acct_output_signal is', acct_output_signal

#----------------------------------------------------------------------------------------
#Function to process the happy packet
def processhappypkt():
#if we have not communicated with the server in the last 240 sec we send a [HAPY] pkt
    if (lastHappyTime == 0):
        timeNow = datetime.datetime.now()
        lastHappyTime = timeNow
        print 'lastHappyTime is  %d', lastHappyTime
    else:
        timeNow = datetime.datetime.now()
        timeDiff = timeNow - lastHappyTime
        print timeDiff.seconds

        if (timeDiff.seconds > happyInterval):
            lastHappyTime = datetime.datetime.now()
            print 'Send Happy packet to server'
            playstate = '0'
            bufferTxns = '0'
            priceSelection = '1'
            #timeNOW =  datetime.datetime.now().time()
            dateNow = datetime.datetime.now().strftime("%Y%m%d")
            timeNow = datetime.datetime.now().strftime("%H%M%S")
            tmessage = '[HAPY].' + str(
                macAddress) + '.' + dateNow + timeNow + '.' + playstate + '.' + bufferTxns + '.' + priceSelection + '\r\n'
            print  tmessage

            try:
                tsocket.sendall(tmessage)
                command_str = tsocket.recv(1024)
                print command_str

            except socket.error:
                #Send failed
                print 'Scan Send failed' + str(socket.error)
                tmessage = ''
                command_str = ''
                stateMachine = stateMachineBoot

#----------------------------------------------------------------------------------------
#Function to process the [REBX] command
def processrebxkt(command_str):
    length_command_str = len(command_str)
    command_str = command_str[7:length_command_str]
    if (command_str == 0):
        #soft reset
        print 'Sytem Reset Requsted. System will now reboot'
        stateMachine = stateMachineIdle
    else
        #hard Reset
        pass

def main():
    macAddress = ''
    serverHost = ''
    serverPort = 1000
    snbbHost = ''
    snbbPort = 2030
    ipAddress = ''
    commandHost = ''
    commandPort = 2119
    commandBacklog = 5
    commandBufferSize = 4096
    stateMachineIdle = 10
    stateMachineBoot = 20
    stateMachineStart = 30
    stateMachineScan = 40
    stateMachine = 0
    happyInterval = 240
    transaction = ''

    lastHappyTime = 0
    server_address = ''
    hardWareVersion = '080000'
    softWareVersion = '080000'

    command_card_dict = ('reboot', '111111111111111120', 'diag', '111111111111111105')

    #Set the status of Pin 12 on the arduino side. We will use pin 12 to indicate the status of go or no go.
    #When pin 12 = 0 the we flash red, When pin 12 is 1 we flash green for 3 seconds

    value = bridgeclient()
    value.put('LSTAT', '2')
    print 'value of LSTAT is', value.get('LSTAT')


    #Setup phase before we try and connect to the snbb broardcast
    #Setup the serial scanner

    #Establish the Serial input for the scanner unit

    buffer = bytes()
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2)
    #Print the serial connection string for DEBUG
    #print ser

    #set the initial state of the state machine
    stateMachine = stateMachineIdle

    #Get the MAC address of the flash unit
    macAddress = getHwAddr()
    print 'My MAC Address is :', macAddress

    # Setup the socks we need to operate.
    # includes the command socket - cs
    # include the transaction socket ts
    # include snbb socket

    #this is the head of the state machine the BIG loop
    ###################################################
    while True:


    #we enter into the idel mode and listen for the snbb broardcast from the server
    #from the snbb broardcast we get the ip address and the port number to be used for all communications with ssrv

        while (stateMachine == stateMachineIdle):
        #############################################################
        # Listen for the SNBB broadcast to find the server IP Address
            # SNBB port address is 2030

            try:
                sb = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sb.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sb.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sb.bind((snbbHost, snbbPort))

                message = sb.recv(1024)

                if (message[0:6] == '[SNBB]'):
                    print "Got data: %s" % repr(message)
                    serverHost = message[36:51]
                    print 'IPaddress of Server: %s' % serverHost
                    serverPort = int(message[21:26])
                    print "Server Port: %d" % int(serverPort)
                    stateMachine = stateMachineBoot
                    print 'Going to Boot phase'
                    print 'stateMachine is', str(stateMachine)
                    message = ''
                    sb.close
                    stateMachine = stateMachineBoot
                else:
                    stateMachine = stateMachineIdle
                    print 'SNBB failed'

            except KeyboardInterrupt:

            # State machine is entering the boot phase
            # We connect to the serverHost and serverPort returned by the snbb message and we sent a boot packet and listen for a replay

                while (stateMachine == stateMachineBoot):
                    print 'Entered Boot Mode'

                    try:
                        cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        cs = ((commandHost, commandPort))
                        cs.bind(lserver_address)
                        cs.setblocking(0)
                        cs.listen(commandBacklog)
                        print 'Starting the command socket'
                    except:
                        pass

                try:
                    #Send the Boot message to ssrv
                    ts = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_address = ((serverHost, serverPort))
                    ts.connect(server_address)
                    print 'Starting the transaction socket'
                except:
                    pass

            while (stateMachine == stateMachineStart):

                # Construct the Boot message and send the boot message to ssrv
                tstring = '[BOOT].' + str(macAddress) + '.0.0.' + hardWareVersion + softWareVersion + '.0.1\r\n'
                ts.sendall(tstring)
                #set the initial happy time
                lastHappyTime = datetime.datetime.now()

                #wait for a reply and then process the reply
                tmessage = ts.recv(1024)
                print 'First String', tmessage
                length_tmessage = len(tmessage)

                if ('[DISP]' in tmessage):
                    transactionMessage = transactionMessage[7:length_tmessage]
                    print 'Message to Display' + tmessage

                elif ('[CRDS]' in tmessage):
                    tmessage = tmessage[7:length_tmessage]
                    print tmessage
                    ts.sendall('[EOTX]/r/n')
                    stateMachine = stateMachineRun

                elif ('[CNFG]' in tmessage):
                    print'CNFG message' + tmessage
                elif ('[CMSG]' in tmessage):
                    print'CCMSG message' + tmessage
                elif ('[MSSG]' in tmessage):
                    print'MSSG message' + tmessage
                elif ('[DEVC]' in tmessage):
                    print'DEVC message' + tmessage
                elif ('[IEVM]' in tmessage):
                    print'IEVM message' + tmessage
                elif ('[RELY]' in tmessage):
                    print'RELY message' + tmessage
                else:
                    stateMachine = stateMachineRun

                    #Open the command port for listening
                while 1:
                    cs, address = lsocket.accept()
                    command_message = cs.recv(commandBufferSize)
                    print 'Command Message' + command_message
                    if command_message:
                        cs.sendall('EOTX\r\n')

                        if command_message:
                            cs.sendall('EOTX\r\n')
                            if ('[PRCE]' in command_message):
                                print'PRCE Message found'
                                print command_message

                            elif ('[REBX]' in command_message):
                                print'REBX Message found'
                                print command_message
                                print 'Soft Reset'
                                stateMachine = stateMachineIdle

                            elif ('[DELY]' in command_message):
                                print'DELY Message found'
                                print command_message

                            elif ('[MSSG]' in command_message):
                                print'MSSG Message found'
                                print command_message

                            else:
                                break
                                #else:
                                #print'.'
                                #stateMachine = stateMachineStart

                                #StateMachine is now in start mode and ready to accept and send card scan data to ssrv
                                #we send a scan packet and we receive a acct pkt back
                                #########################################################
        while (stateMachine == stateMachineRun):

            processhappypkt()


        # Read the barcode from the scanner and process
        barcode = ser.readline()
        barcode.rstrip('\r\n')
        barcode_length = len(barcode)
        if (len(barcode) > 0):
            print 'Length of barcode is %d ', len(barcode)
            print 'barcode is' + barcode

        # build tne scan pkt and send to ssrv
        tstring = '[SCAN].' + str(macAddress) + '.' + barcode + '\r\n'

    try:
        #Send the Boot message to ssrv
        ts.sendall(tstring)
        #reset the happy time
        lastHappyTime = datetime.datetime.now()

        command_str = ts.recv(1024)
        print command_str

    except:
        pass

        #Process the ACCT packet and extract the data we need
        #####################################################
        process_account_pkt(command_str)

    else:
        print'.'
        #Reset the lights
        value.put('LSTAT', '2')
        print 'value of LSTAT is', value.get('LSTAT')
        stateMachine = stateMachineRun


if __name__ == '__main__':
    main()
