import socket
import threading
import player

class Server:
    def __init__(self, ip, port):
        self.addr = (ip,port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #
        self.socket.bind(self.addr)
        self.socket.listen(4)
        #
        self.clients = []

    def start(self):
        t = threading.Thread(daemon=True, target=self.thread_connection)
        t.start()

    def thread_client(self, conn, addr):
        conn.send(str(len(Network.clients) + 1).encode())
        Network.add_client

        while(1):
            data = conn.recv(2048).decode()
            if data:
                data = data.split('\0')[:-1]
                print(data)
                for d in data:
                    Network.on_message(d)

    def thread_connection(self):
        while(1):
            conn, addr = self.socket.accept()

            self.clients.append([conn, addr])
            t = threading.Thread(daemon=True, target=self.thread_client, args=(conn, addr))
            t.start()

class Client:
    def __init__(self, ip, port):
        self.addr = (ip,port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #
        self.connection_id = self.connect()

    def send(self,data):
        self.socket.send(data + b'\0')

    def connect(self):
        self.socket.connect(self.addr)
        return self.socket.recv(2048).decode()

class Network:
    connection_id = 0 # 0 means no connection. Any other number means your player number
    server = None
    clients = []

    ## Obj recived/sent format
    ## Packet-Type(str) + '/' + Args (Str.join(;))
    ## Pakcet-type -> PKT_mode_name
    ## mode can be U (update), S (Spawn), R (remove)
    # PKT_U_Ball # Update ball, calls Ball.update_network
    # PKT_S_Ball # Spawn new ball, calls Ball.spawn_network
    # PKT_U_Player # Update player
    # ...

    classes = {}
    classes = {'Ball':'player.Ball', 'Player':'player.Player'}
    modes = {'S':'spawn','U':'update','R':'remove'}

    def start(ip,port):
        Network.server = Server(ip,port)
    
    def connect_to(ip,port):
        ## creates a Client, connects and saves
        Network.add_client(Client(ip,port))

    def add_client(client):
        Network.clients.append(client)

    def send(obj): ## Send obj encoded in the format listed in this class with comments
        for c in Network.clients:
            c.send(obj)

    def on_message(message):
        print(message)
        pkt,args = message.split('/')

        try:
            _,m,classt = pkt.split('_')
            class_type = Network.classes[classt]
            mode = Network.modes[m]
        except:
            print('Invalid Packet recived')
            return

        exec(class_type+'.'+mode+'_network("'+str(args)+'")')
