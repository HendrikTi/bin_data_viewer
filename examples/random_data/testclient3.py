import socket, time,random
import json

dict = {
    "name": "Testsensor3",
    "legend": ["X", "Y", "Z"],
    "colors": ['b', 'g', 'r'],
    "len": 10000,
    "payload": [[0], [0], [0]]
}


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 7011))
while True:
    dict["payload"][0] = random.sample(range(-100, 95), 100)
    dict["payload"][1] = random.sample(range(-23, 110), 100)
    dict["payload"][2] = random.sample(range(-47, 160), 100)
    s.send(json.dumps(dict).encode())
    time.sleep(0.1)

s.sendall(b'Hello, world')