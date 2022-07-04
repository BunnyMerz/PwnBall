from network import *
from main import main as start


def main():
    ## Iniciar um servidor ou connectar a alguém
    mode = input("Start server or connect to another player? [S/P]: ")
    mode = mode.lower()
    while mode not in ['s','p','server','player']:
        print("Invalid option.")
        mode = input("Start server or connect to another player? [S/P]: ")
        mode = mode.lower()
    ###

    if mode == 's':
        ## Cria server
        while(1):
            try:
                port = input("Choose your port (blank for default 111): ")
                if port == '':
                    port = '111'
                Network.start('localhost',int(port))
                break
            except Exception as e:
                print(e)

        print("Waiting for other players...")
        print("----- Press Enter to start the match -----")
        input()
        while(len(Network.clients) < 1):
            input("No players have connected yet. Wait until at least one has and press enter.\n")

        Network.start_game()
        start()

    elif mode == 'p':
        Network.start('localhost',0)
        while(1):
            try:
                ip = input("Choose their ip (default to local host):")
                port = input("Choose their port (blank for default 111): ")

                if ip == '':
                    ip = 'localhost'
                if port == '':
                    port = '111'

                Network.connect_to('localhost',int(port))
                break
            except Exception as e:
                print(e)

        print("Waiting for the host to start the game...")
        while(Network.game_started == 0):
            pass

        start()

if __name__ == "__main__":
    main()

