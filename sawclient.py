#!/usr/bin/env python 
import socket
import sys
import time
import os
import hashlib
import pickle       #To store the data

recv_host='127.0.0.1'
#recv_host='10.221.112.108'
recv_port=9987
#recv_host=str(sys.argv[1])     #the address where you are going to send
#recv_port=int(sys.argv[2])     #you can type in the port you want

#create the socket
client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client.settimeout(0.001)

#takes the file name as command line arguments
#filename = ''.join(sys.argv[3])
filename='./alice.txt'

#initialize the variable
lar_num=1
seq_num=1

#SENDS DATA
fileOpen= open(filename, 'rb')  #read in binary
length=500
offset=500

data = fileOpen.read(length)       #each time read 500-bytes data
data_fin_state = False          #define whether the all the data are read
ada_timeout=0.01       #initailize the timeout as 1 second

while not data_fin_state:
    #we must read the data before the loop,or the first transmission wouldn't
    #know whether data_fin_state condition
    sndpkt=[]
    sndpkt.append(seq_num)
    sndpkt.append(data)

    md5 = hashlib.md5()  # define hash.md5 algorithm
    md5.update(pickle.dumps(sndpkt))
    sndpkt.append(md5.digest())

    pkt = pickle.dumps(sndpkt)
    #send data
    client.sendto(pkt, (recv_host, recv_port))
    last_ackrecv = time.time()      # timer start to calculate

    print("Sent data", seq_num,'offset',offset)

    if (not data):  # if data is empty,data=False
        data_fin_state = not data_fin_state  # set the statement flag be True

    # RECEIPT OF AN ACK
    try:
        packet,serverAddress = client.recvfrom(4096)
        recv_pkt = []
        recv_pkt = pickle.loads(packet)
        #check whether we received the right packet
        c=recv_pkt[-1]
        del recv_pkt[-1]
        md5rec = hashlib.md5()
        md5rec.update(pickle.dumps(recv_pkt))
        if c == md5rec.digest():   #if there is no error
            print("Received ack:",recv_pkt[0])
            #only after receiving the data,then we can transmit the next one
            seq_num = seq_num + 1
            offset = offset + length
            data = fileOpen.read(length)

            #use adaptive timeout
            time_recv = time.time()     #until we get the packet,we ensure it's a round
            newRTT=time_recv-last_ackrecv       #calculate the RTT
            ada_timeout=0.9*ada_timeout+0.1*newRTT
            print('ada-timeout:',ada_timeout)
            print('\n')

        else:   #if the packet number is incorresponding,didn't get the right packet
            print("error detected")

# TIMEOUT
    except: #if we can't get the revc,check if it has reach the timeout
        if (time.time() - last_ackrecv > ada_timeout):
            client.sendto(pkt, (recv_host, recv_port))
            print("Timeout")
            print("resent data", seq_num,'length',offset)

fileOpen.close()
print("connection closed")
client.close()
