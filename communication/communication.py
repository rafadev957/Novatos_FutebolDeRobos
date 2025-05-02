import socket
import sys
import os
import threading
sys.path.append(os.path.join(os.path.dirname(__file__), '../pb'))
from pb import packet_pb2, command_pb2, replacement_pb2, common_pb2

class Communication:

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
            
            self.env = packet_pb2.Environment()
            self.frame = common_pb2.Frame()

        except Exception as ex:
            print("Connection failed", ex)

    def startServer(self):
        listener_thread = threading.Thread(target=simState, args=(self, ), daemon=True)
        listener_thread.start()


    def sendOne(self, id, wl, wr, teamYellow = True):
        cmd = command_pb2.Command()
        cmd.id = id
        cmd.yellowteam = teamYellow
        cmd.wheel_left = wl
        cmd.wheel_right = wr

        commands = command_pb2.Commands()
        commands.robot_commands.append(cmd)

        packet = packet_pb2.Packet()
        packet.cmd.CopyFrom(commands)
        packet.replace.CopyFrom(replacement_pb2.Replacement())

        packet_bytes = packet.SerializeToString()
        self.sock_command.sendto(packet_bytes, (self.ip_send, self.port_send))

def simState(con):

    try:
        while True:
            data, server = con.sock_receive.recvfrom(4096)  # tamanho do buffer
            con.env.ParseFromString(data)
            con.frame.CopyFrom(con.env.frame)
            
    except Exception as ex:
        print("Falha na comunicação com o servidor!", ex)