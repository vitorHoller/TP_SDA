import socket
import sys

def client_send(ipc_host, ipc_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ipc_s:
        ipc_s.connect((ipc_host, ipc_port))
        try:
            while True:
                message = input("Temperatura de Referencia (ou 'exit' para encerrar): ").strip()
                if message.lower() == 'exit':
                    ipc_s.sendall(b'__EXIT__')
                    ipc_s.close()
                    break
                if message:  # Verifica se a mensagem não está vazia
                    ipc_s.sendall(message.encode('utf-8'))
        except (ConnectionResetError, BrokenPipeError):
            print("Connection closed.")
        except KeyboardInterrupt:
            print("Client send process interrupted.")

if __name__ == "__main__":
    ipc_host = sys.argv[1]
    ipc_port = int(sys.argv[2])
    client_send(ipc_host, ipc_port)