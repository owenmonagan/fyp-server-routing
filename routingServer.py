import random
import SocketServer
import os
import socket
import logging
from poolRequest.poolRequest import handlePoolRequest
from testclient import testClient
import thread
import threading
port =random.randint(4000, 9999)

apiKey ='AIzaSyAoUGzwRMXGeO9X8_QApT6cB85FOV2ec9Y'


if os.name != "nt":
    import fcntl
    import struct

    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                                ifname[:15]))[20:24])

def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = [
            "eth0",
            "eth1",
            "eth2",
            "wlan0",
            "wlan1",
            "wifi0",
            "ath0",
            "ath1",
            "ppp0",
            ]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip

class ThreadedTCPHandler (SocketServer.BaseRequestHandler):

    def handle(self):
        requestMessage=self.request.recv(1024)
        print"Request Message:"
        print(requestMessage)
        if("PoolRequest" in requestMessage):
            response=handlePoolRequest(requestMessage)
            self.request.sendall(response)
        elif("Update" in requestMessage):
            pass


class ThreadedDirectionsTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__== "__main__":
    logging.basicConfig(filename='logging.log',level=logging.DEBUG)

    HOST, PORT = "localhost", port
    HOST= my_ip = get_lan_ip()
    server = ThreadedDirectionsTCPServer((HOST, PORT), ThreadedTCPHandler)
    print ("Receive")
    ip, port = server.server_address
    server.server_alive=True
    print  server.server_address
    print ("reced")
    try:
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        #print("About to launch test")
        #thread.start_new_thread(testClient,(HOST,PORT))
        #print("test launched")

        while(server.server_alive==True):
            pass

        server.shutdown()
        server.server_close()
        exit()

    except KeyboardInterrupt:
        print("Key board interrupt \nServer Shutting Down")
        server.shutdown()
        server.server_close()
        exit()
    server.serve_forever()


