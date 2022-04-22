import socket
import threading

from cv2 import add
import player

class Server:
    def __init__(self, ip, port):
        self.addr = (ip,port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #
        self.socket.bind(self.addr)
        self.socket.listen(4)
        #
        self.clients = [] ## List of sockets that this server is listening to.  Not to be confused with Network.clients

    def start(self):
        t = threading.Thread(daemon=True, target=self.thread_connection)
        t.start()

    def thread_client(self, conn, addr):
        ## Gives them an Id and the ip of everyone else. These ips should be used with cascade_connect
        id = str(len(Network.clients) + 2)
        ips = [c.addr[0]+':'+str(c.addr[1]) for c in Network.clients]
        ips = ';'.join(ips)
        print("asnwering client request with",[id],[ips])
        conn.send((id+'-'+ips).encode())
        ##
        ## Waits for their server ip
        data = conn.recv(2048).decode()
        ip,port = data.split(':')
        port = int(port)
        Network.connect_to(ip,port,first_connection=0) ## This is a connection back, which implies this guy is already in a room, thus first_connection=0
        ##
        
        print('waiting for client',id,'data')
        while(1):
            data = conn.recv(2048).decode()
            if data:
                data = data.split('\0')[:-1]
                for d in data:
                    Network.on_message(d)

    def thread_connection(self):
        while(1):
            print('waiting on other clients requests')
            conn, addr = self.socket.accept() ## Waiting for others to connect.
            self.clients.append(conn) ## Saves socket addr
            print('recived client request to connect',addr)
            t = threading.Thread(daemon=True, target=self.thread_client, args=(conn, addr))
            t.start()

class Client:
    def __init__(self, ip, port,first_connection=1):
        self.addr = (ip,port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #
        self.connection_id = self.connect(first_connection)

    def send(self,data):
        self.socket.send(data + b'\0')

    def connect(self, first_connection=1):
        ##
        self.socket.connect(self.addr)
        data = self.socket.recv(2048).decode() ## str(Int-Ip;Ip;Ip;...)
        ids,cascade_ips = data.split('-')
        print('id and cascade recived',cascade_ips)
        ##
        print('sending back own server ip')
        self.socket.send(Network.addr_string().encode())
        ##
        if first_connection:
            print("cascade connection",cascade_ips)
            Network.cascade_connect(cascade_ips)
        return int(ids)

class Network:
    connection_id = 0 # 0 means no server setted up. 1 Means pseudo-host (first of the room). Any other including 1 represents their player number
    server = None
    clients = [] ## List of sockets connected to other servers. Not to be confused with Server.clients

    ## Obj recived/sent format
    ## Packet-Type(str) + '/' + Args (Str.join(;))
    ## Pakcet-type -> PKT_mode_name
    ## mode can be U (update), S (Spawn), R (remove)
    # PKT_U_Ball # Update ball, calls Ball.update_network
    # PKT_S_Ball # Spawn new ball, calls Ball.spawn_network
    # PKT_U_Player # Update player
    # ...

    classes = {}
    classes = {'Ball':'player.Ball', 'Player':'player.Player', 'Network':"Network"}
    modes = {'S':'spawn_network','U':'update_network','R':'remove_network',"C":"cascade_connect"}

    def does_connection_exists(ip,port):
        for c in Network.clients:
            if c.addr == (ip,port):
                return True
        return False

    def addr_string():
        addr = Network.server.addr
        return addr[0] + ':' + str(addr[1])

    def start(ip,port):
        print("###")
        print('Initating own server')
        Network.server = Server(ip,port)
        Network.server.start()
        Network.connection_id = 1
        print('Server initated')
        print("###")

    def connect_to(ip,port,first_connection=1):
        print('My id',Network.connection_id)
        if Network.does_connection_exists(ip,port):
            return
        ## creates a Client, connects and saves
        print("Connecting to server")
        c = Client(ip,port,first_connection)
        Network.add_client(c)
        if first_connection:
            Network.connection_id = c.connection_id
        print("Connected")

    def cascade_connect(args): ## Connection due to spread_client(). Args = "ip:port;ip:port;..."
        if args == '':
            return
        addrs = args.split(';')
        for addr in addrs:
            addr = addr.split(':')
            ip = addr[0]
            port = int(addr[1])
            Network.add_client(Client(ip,port,1))

    def add_client(client):
        Network.clients.append(client)

    def send(obj): ## Send obj encoded in the format listed in this class with comments
        for c in Network.clients:
            c.send(obj)

    def on_message(message):
        pkt,args = message.split('/')

        try:
            _,m,classt = pkt.split('_')
            class_type = Network.classes[classt]
            mode = Network.modes[m]
        except:
            print('Invalid Packet recived')
            return

        exec(class_type+'.'+mode+'("'+args+'")') ## TODO this opens up for code injection. exec() failed when trying something like 'fn = functioncall' as fn stayed as None.
        ## Tried this already
        # exec('fn = '+class_type+'.'+mode)
        # fn(args)
        ## Didnt work as fn was still not defined
        return # just so the comments are hidden inside the function (vscode thing)
