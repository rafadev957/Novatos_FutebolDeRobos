import socket
import sys
import os
import threading
sys.path.append(os.path.join(os.path.dirname(__file__), '../pb'))
from pb import vssref_command_pb2, vssref_common_pb2, vssref_placement_pb2

class Referee:

    def __init__(self, ip_send, ip_receive):
        try:
            self.ip_send   = ip_send.strip().split(":")[0]
            self.port_send = int(ip_send.strip().split(":")[1])

            self.ip_recv   = ip_receive.strip().split(":")[0]
            self.port_recv = int(ip_receive.strip().split(":")[1])

            self.sock_command = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            self.sock_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock_receive.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock_receive.bind((self.ip_recv, self.port_recv)) 
            
            self.foul = vssref_common_pb2.Foul
            self.team = vssref_common_pb2.Color
            self.quadrant = vssref_common_pb2.Quadrant

        except Exception as ex:
            print("Connection failed", ex)

    def startServer(self):
        listener_thread = threading.Thread(target=simState, args=(self, ), daemon=True)
        listener_thread.start()

def simState(con):

    try:
        while True:
            data, server = con.sock_receive.recvfrom(4096)  # tamanho do buffer
            comm = vssref_command_pb2.VSSRef_Command()
            comm.ParseFromString(data)
            con.foul = comm.foul
            con.team = comm.teamcolor
            con.quadrant = comm.foulQuadrant
            
    except Exception as ex:
        print("Falha na comunicação com o servidor!", ex)