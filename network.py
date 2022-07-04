import socket
import threading
import time

def simulate_lag(ms,fn,args):
    time.sleep(ms/1000)
    fn(args)

class Server:
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #
        self.socket.bind((ip,port))
        self.addr = self.socket.getsockname()
        self.socket.listen(4)
        #
        self.clients = [] ## List of sockets that this server is listening to.  Not to be confused with Network.clients
        self.clients_ips = []
        self.threaded_connection = False

    def start(self):
        t = threading.Thread(daemon=True, target=self.thread_connection)
        self.threaded_connection = True
        t.start()

    def thread_client(self, conn, addr):
        print('### Waiting for client',id,'data')
        while(1):
            data = conn.recv(2048).decode()
            if data:
                data = data.split('\0')[:-1]
                for d in data:
                    t = threading.Thread(daemon=True, target=simulate_lag, args=(300, Network.on_message, d))
                    t.start()
                    # Network.on_message(d)

    def thread_connection(self):
        print("\n### Server.thread_connection()")
        print('### Waiting on other clients requests')
        while(self.threaded_connection):
            conn, addr = self.socket.accept() ## Waiting for others to connect.
            self.clients.append(conn) ## Saves socket addr
            self.clients_ips.append(addr)
            print('### Recived client request to connect',addr)


            ## Gives them an Id and the ip of everyone else. These ips should be used with cascade_connect
            id = str(len(Network.other_servers_ips) + 2)
            ips = [c[0]+':'+str(c[1]) for c in Network.other_servers_ips]
            ips = ';'.join(ips)
            print("### Asnwering client request with",[id],[ips],'\n')
            conn.send((id+'-'+ips).encode())
            ##
            ## Waits for their server ip
            data = conn.recv(2048).decode()
            print("### Received their server ip:port",data)
            ip,port = data.split(':')
            port = int(port)
            Network.connect_to(ip,port,first_connection=0) ## This is a connection back, which implies this guy is already in a room, thus first_connection=0
            ##

            t = threading.Thread(daemon=True, target=self.thread_client, args=(conn, addr))
            t.start()

    def stop_waiting_connection(self):
        self.threaded_connection = False

class Client:
    def __init__(self, ip, port,first_connection=1):
        self.addr = (ip,port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #
        self.connection_id = self.connect(first_connection)

    def __repr__(self) -> str:
        return str(self.addr)

    def send(self,string):
        self.socket.send((string + '\0').encode())

    def connect(self, first_connection=1):
        ##
        self.socket.connect(self.addr)
        self.addr = self.socket.getsockname()

        data = self.socket.recv(2048).decode() ## str(Int-Ip;Ip;Ip;...)
        ids,cascade_ips = data.split('-')
        print('## Id and cascade recived',cascade_ips)
        ##
        print('## Sending back own server ip',Network.server.addr)
        self.socket.send(Network.addr_string().encode())
        ##
        if first_connection:
            print("## Cascade connection [",cascade_ips,']')
            Network.cascade_connect(cascade_ips)
        else:
            print("## Skipping cascade connection")
        return int(ids)

class Network:
    connection_id = 0 # 0 means no server setted up. 1 Means pseudo-host (first of the room). Any other including 1 represents their player number
    server = None
    clients = [] ## List of sockets connected to other servers. Not to be confused with Server.clients
    other_servers_ips = []
    game_started = 0

    ## Obj recived/sent format
    ## Packet-Type(str) + '/' + Args (Str.join(;))
    ## Pakcet-type -> PKT_mode_name
    ## mode can be U (update), S (Spawn), R (remove)
    # PKT_U_Ball # Update ball, calls Ball.update_network
    # PKT_S_Ball # Spawn new ball, calls Ball.spawn_network
    # PKT_U_Player # Update player
    # ...

    classes = {'Ball':'Ball', 'Player':'Player', 'Network':"Network", 'Goal':"Goal"}
    modes = {'S':'spawn_network','U':'update_network','R':'remove_network',"C":"cascade_connect",'I':'initialize_game'}

    def does_connection_exists(ip,port):
        for c in Network.other_servers_ips:
            if c == (ip,port):
                return True
        return False

    def addr_string():
        addr = Network.server.addr
        return addr[0] + ':' + str(addr[1])

    def start(ip,port):
        print("\n### Network.start()")
        print('### Initating own server')
        Network.server = Server(ip,port)
        Network.server.start()
        Network.connection_id = 1
        print('### Server initated')
        print("###")

    def start_game():
        Network.server.stop_waiting_connection()
        Network.send("PKT_I_Network/")

    def initialize_game(args):
        Network.game_started = 1

    def connect_to(ip,port,first_connection=1):
        if Network.does_connection_exists(ip,port):
            return
        
        print("\n### Network.connect_to()")
        ip = socket.gethostbyname(ip)
        Network.other_servers_ips.append((ip,port))
        ## creates a Client, connects and saves
        print("### Trying to connect to server",ip,port)
        c = Client(ip,port,first_connection)
        Network.add_client(c)
        if first_connection:
            Network.connection_id = c.connection_id
            print('### My id',Network.connection_id)
        print("### Connected")
        print("### End of Network.connect_to()")
        

    def cascade_connect(args): ## Connection due to spread_client(). Args = "ip:port;ip:port;..."
        if args == '':
            return
        addrs = args.split(';')
        for addr in addrs:
            addr = addr.split(':')
            ip = addr[0]
            port = int(addr[1])
            Network.add_client(Client(ip,port,0))

    def add_client(client):
        Network.clients.append(client)

    def send(obj): ## Obj is a string
        for c in Network.clients:
            c.send(obj)

    def on_message(message):
        from objects.player import Player # "Not used", but used with eval
        from objects.ball import Ball # "Not used", but used with eval
        from objects.goal import Goal # "Not used", but used with eval
        pkt,args = message.split('/')

        try:
            _,m,classt = pkt.split('_')
            class_type = Network.classes[classt]
            mode = Network.modes[m]
        except:
            print('Invalid Packet recived')
            return

        # print(f">>> Pkt - {class_type}.{mode} with args {args} {' '*30}",end='\r')
        ## Using dictionary and variable fn to avoid code injection
        fn = lambda : None
        _locals = locals()
        exec('fn = '+class_type+'.'+mode, globals(), _locals)
        _locals['fn'](args)

        return
