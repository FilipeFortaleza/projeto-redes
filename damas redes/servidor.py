import socket
import threading

# Configurações de rede
HOST = '0.0.0.0'
PORT = 5000        # Porta de comunicação

# Estado do Jogo
clientes = []
jogadores = {} # Mapeia o socket para a cor da peça ('b' ou 'w')
turno_atual = 'b' # 'b' (Brancas) começam sempre

# Tabuleiro inicial (8x8) - 'b'=brancas, 'p'=pretas, ' '=vazio
tabuleiro = [
    [' ', 'p', ' ', 'p', ' ', 'p', ' ', 'p'],
    ['p', ' ', 'p', ' ', 'p', ' ', 'p', ' '],
    [' ', 'p', ' ', 'p', ' ', 'p', ' ', 'p'],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    ['b', ' ', 'b', ' ', 'b', ' ', 'b', ' '],
    [' ', 'b', ' ', 'b', ' ', 'b', ' ', 'b'],
    ['b', ' ', 'b', ' ', 'b', ' ', 'b', ' ']
]

def formatar_tabuleiro():
    """Converte a matriz do tabuleiro numa string para enviar aos clientes."""
    res = "\n  0 1 2 3 4 5 6 7\n"
    for i, linha in enumerate(tabuleiro):
        res += str(i) + " " + " ".join(linha) + "\n"
    return res

def broadcast(mensagem):
    """Envia uma mensagem para todos os clientes ligados."""
    for cliente in clientes:
        try:
            cliente.send(mensagem.encode('utf-8'))
        except:
            pass

def alternar_turno():
    global turno_atual
    turno_atual = 'p' if turno_atual == 'b' else 'b'

def processar_jogada(jogada_str, cor_jogador):
    """Lógica simplificada de movimento (não valida capturas complexas por simplicidade)"""
    try:
        # Espera formato: "linha_origem col_origem linha_destino col_destino" (ex: "5 0 4 1")
        partes = jogada_str.split()
        if len(partes) != 4:
            return False, "Formato inválido. Usa: L_orig C_orig L_dest C_dest (ex: 5 0 4 1)"
        
        lo, co, ld, cd = map(int, partes)
        
        if tabuleiro[lo][co] != cor_jogador:
            return False, "Não podes mover essa peça!"
        if tabuleiro[ld][cd] != ' ':
            return False, "Casa de destino ocupada!"
        
        # Move a peça
        tabuleiro[lo][co] = ' '
        tabuleiro[ld][cd] = cor_jogador
        return True, "Jogada efetuada!"
    except Exception as e:
        return False, "Erro ao processar a jogada."

def lidar_com_cliente(conn, endereco, cor):
    """Função executada numa Thread para cada cliente."""
    global turno_atual
    conn.send(f"Bem-vindo! Tu és as peças: {cor}\n".encode('utf-8'))
    
    if len(clientes) == 2:
        broadcast("Jogo Iniciado!\n" + formatar_tabuleiro())
        broadcast(f"Turno do jogador: {turno_atual}")

    while True:
        try:
            mensagem = conn.recv(1024).decode('utf-8')
            if not mensagem:
                break
            
            if turno_atual != cor:
                conn.send("Não é o teu turno!\n".encode('utf-8'))
                continue
            
            valida, msg = processar_jogada(mensagem, cor)
            if valida:
                alternar_turno()
                broadcast("\n" + formatar_tabuleiro())
                broadcast(f"Turno do jogador: {turno_atual}")
            else:
                conn.send((msg + "\nTenta novamente.\n").encode('utf-8'))
                
        except:
            break
            
    print(f"Jogador {cor} ({endereco}) desligou-se.")
    clientes.remove(conn)
    conn.close()

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen(2)
    print(f"Servidor a escutar em {HOST}:{PORT}...")

    cores = ['b', 'p']
    
    while len(clientes) < 2:
        conn, endereco = servidor.accept()
        clientes.append(conn)
        cor = cores[len(clientes) - 1]
        jogadores[conn] = cor
        print(f"Conexão estabelecida com {endereco}. Peças: {cor}")
        
        # Cria a THREAD OBRIGATÓRIA para o cliente
        thread = threading.Thread(target=lidar_com_cliente, args=(conn, endereco, cor))
        thread.start()

if __name__ == "__main__":
    iniciar_servidor()