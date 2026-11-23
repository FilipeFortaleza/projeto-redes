import socket
import threading
import sys

# Configurações de rede
HOST = input("Digite o IP do servidor: ")
PORT = 5000

def receber_mensagens(sock):
    """Thread que fica infinitamente a receber dados do servidor."""
    while True:
        try:
            mensagem = sock.recv(2048).decode('utf-8')
            if not mensagem:
                print("Servidor fechou a ligação.")
                sock.close()
                sys.exit()
            # O uso do print primitivo exigido
            print(mensagem) 
        except:
            print("Erro de ligação.")
            sock.close()
            sys.exit()

def iniciar_cliente():
    # Criação do Socket primitivo TCP
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        cliente.connect((HOST, PORT))
    except Exception as e:
        print(f"Não foi possível ligar ao servidor: {e}")
        return

    # Inicia a Thread para receber atualizações do tabuleiro e mensagens
    thread_receber = threading.Thread(target=receber_mensagens, args=(cliente,))
    thread_receber.daemon = True 
    thread_receber.start()

    print("Ligado ao servidor de Damas! Aguarda o outro jogador.")
    print("Para jogar, digita a linha e coluna de origem e destino.")
    print("Exemplo: 5 0 4 1 (Move a peça da linha 5 coluna 0 para linha 4 coluna 1)")

    # Loop principal para enviar jogadas usando input primitivo
    while True:
        try:
            # Em Python 2 seria raw_input(), em Python 3 usamos input()
            jogada = input() 
            if jogada.lower() == 'sair':
                cliente.close()
                break
            cliente.send(jogada.encode('utf-8'))
        except:
            break

if __name__ == "__main__":
    iniciar_cliente()