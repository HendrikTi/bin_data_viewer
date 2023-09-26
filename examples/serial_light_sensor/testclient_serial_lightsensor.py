import serial
import pandas as pd
import socket, time,random
from multiprocessing import Process, Queue
import json

# Dataformat used in this example
# (x1,x2,x3,x4,x5,x6,x7,x8)\r\n


PORT = "COM17"
BAUDRATE = "115200"
SENDCOUNTER = 1
NUMBER_OF_ELEMENTS = 8  # Number of elements each packet

dict = {
    "name": "Light",
    "legend": ["1","2","3","4","5","6","7","8"],
    "colors": ['b', 'g', 'r', 'c', 'm', 'y','k', 'w'],
    "len": 2000,
    "payload": [[0],[0],[0],[0],[0],[0],[0],[0]]
}

def do_serial(q):
    dev = serial.Serial()
    dev.baudrate = BAUDRATE
    dev.port = PORT
    dev.open()
    data = []           # Data elements extracted from UART transmission
    data_list = []      # List of data packet (nested list)
    cnt = 0             # Counts number of data packet received
    msg_decoded = ""
    # Read to flush current buffer to prevent missing data
    c = dev.read_until(b'\r\n')
   
    while True:
        
        # Read line
        msg_encoded = dev.read_until(b'\r\n')
        
        # Format message --------------------------- 
        msg_encoded = msg_encoded.replace(b'(', b'')
        msg_encoded = msg_encoded.replace(b')', b'')
        msg_decoded += msg_encoded.decode()
        # ------------------------------------------
        # Retrieve data
        data = msg_decoded.split(",")
        
        # Add data, when packet contains the correct number of elements
        if len(data) == NUMBER_OF_ELEMENTS:
            print(data)
            data_list = [[int(data[0])],[int(data[1])],[int(data[2])],[int(data[3])],[int(data[4])],[int(data[5])],[int(data[6])],[int(data[7])]]
            msg_decoded = ""
            cnt += 1
        # Number of packets == SENDCOUNTER
        if cnt == SENDCOUNTER:
            q.put(data_list)
            data_list = []
            cnt = 0
def main(q):

    print("main")



def start():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 7011))
    data_queue = Queue()
    p = Process(target=do_serial, args=(data_queue,))
    p.start()
    
    while True:
        # read queued data from serial port
        if not data_queue.empty():
            msg = data_queue.get()
            print(msg)
            dict["payload"][0] = msg[0]
            dict["payload"][1] = msg[1]
            dict["payload"][2] = msg[2]
            dict["payload"][3] = msg[3]
            dict["payload"][4] = msg[4]
            dict["payload"][5] = msg[5]
            dict["payload"][6] = msg[6]
            dict["payload"][7] = msg[7]
            print(dict)
            s.send(json.dumps(dict).encode())
    p.join()

if __name__ == '__main__':
    start()

