#!/usr/bin/env python
import socket
import pickle
import hashlib
import sys
import numpy as np
import time

#takes the port number as command line arguments and create server socket
serverIP="127.0.0.1"
#serverIP='10.221.112.108'
#serverPort=int(sys.argv[1])
serverPort=9987

server=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server.bind((serverIP,serverPort))
server.settimeout(3)
print("Ready to serve")

#initializes packet variables
expected_seqnum=1
ACK=1
ack = []

#RECEIVES DATA
f = open("output", "wb")
end_of_file = False		#checksum which defines whether finish reading
last_pkt_recv = time.time()		#Whether receive the pkt,timer start counting
starttime = time.time()

while True:
    try:
        recvpkt=[]

        packet,clientAddress= server.recvfrom(4096)
        recvpkt = pickle.loads(packet)

        #check whether the received checksum value are the same as its sequence number
        c = recvpkt[-1]	#the last part of the received packet
        del recvpkt[-1]            #recvpkt.append("it's a error")     #to test error

        md5 = hashlib.md5()
        md5.update(pickle.dumps(recvpkt))
        # check whether the received packet's sequence number is in order
        if c == md5.digest():   #No error happens
            # create ACK (seqnum,checksum)
            sndpkt = []
            sndpkt.append(recvpkt[0])
            md5send = hashlib.md5()
            md5send.update(pickle.dumps(sndpkt))
            sndpkt.append(md5send.digest())
            ack_pkt = pickle.dumps(sndpkt)
            #time.sleep(0.2)
            server.sendto(ack_pkt, (clientAddress[0], clientAddress[1]))
            print("New Ack", recvpkt[0])
            #then check if the packet is what we want
            if (recvpkt[0] == expected_seqnum):     #In order
                print("ACCEPT",recvpkt[0])
                if recvpkt[1]:  # the second part is the data,if it's not empty
                    f.write(recvpkt[1])
                else:  # if the data is empty,its bool value=False
                    end_of_file = True

                expected_seqnum = recvpkt[0] + 1    #update the expected number


            else: #Didn't get the right packet
                print('Out of Order')
                print('IGNORED')

        else:  #Not correspond
            print('Error detected')
            print('IGNORED')

    except:
        if end_of_file:  # If reach the end of the data
            if (time.time() - last_pkt_recv > 0.1):  # wait for more than a timeout period
                break

endtime = time.time()

f.close()
print('FILE TRANFER SUCCESSFUL')
print("TIME TAKEN "), str(endtime - starttime)
