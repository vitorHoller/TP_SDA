import socket
import multiprocessing
import os
import subprocess
import signal
import sys

def client_receive(s, q):
    while True:
        try:
            combined_message = s.recv(1024)
            if not combined_message:
                break
            decoded_message = combined_message.decode('utf-8')
            print(f"Recebido: {decoded_message}")
            q.put(f"Recebido: {decoded_message}")
        except ConnectionResetError:
            break

def write_to_file(filename, q):
    while True: 
        try:
            with open(filename, 'a') as f:
                if not q.empty():
                    data = q.get()
                    f.write(data + '\n')
        except Exception as e:
            print(f"Erro ao tentar criar ou escrever no arquivo: {e}")



        

def ipc_server(s, ipc_host, ipc_port, q, q_kill):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_ipc:
        s_ipc.bind((ipc_host, ipc_port))
        s_ipc.listen(1)
        conn, addr = s_ipc.accept()
        with conn:
            while True:
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    if data == b'__EXIT__':
                        print("Client requested to close the connection.")
                        s.sendall(b'__EXIT__')
                        s.close()
                        conn.close()
                        q_kill.put("kill")
                        break
                    s.sendall(data)
                    q.put(f"Temperatura de Referencia: {data.decode('utf-8')}")
                except (ConnectionResetError, BrokenPipeError):
                    print("Connection closed.")
                    conn.close()
                    break
                except KeyboardInterrupt:
                    print("IPC server process interrupted.")
                    conn.close()
                    break
          


def start_client(host='127.0.0.1', port=65432, ipc_host='127.0.0.1', ipc_port=65433):
    queue = multiprocessing.Queue()
    queue_kill = multiprocessing.Queue()

    writer_process = multiprocessing.Process(target=write_to_file, args=('historiador.txt', queue))
    writer_process.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        receive_process = multiprocessing.Process(target=client_receive, args=(s, queue))
        receive_process.start()

        ipc_process = multiprocessing.Process(target=ipc_server, args=(s, ipc_host, ipc_port, queue, queue_kill))
        ipc_process.start()



        # Iniciar client_send.py em um novo terminal e passar a fila send_queue
        subprocess.Popen(['gnome-terminal', '--', 'python3', 'client_send.py', ipc_host, str(ipc_port)])

        try:
            while True:
                if not queue_kill.empty():
                    receive_process.terminate()
                    receive_process.join()
                    writer_process.terminate()
                    writer_process.join()
                    ipc_process.terminate()
                    ipc_process.join()
                    break

        except KeyboardInterrupt:
            receive_process.terminate()
            writer_process.terminate()
            ipc_process.terminate()
            receive_process.join()
            writer_process.join()
            ipc_process.join()

def handle_sigint(signum, frame):
    print("Interrupção por Control+C detectada. Encerrando...")
    sys.exit(0)

if __name__ == "__main__":
    start_client()
    signal.signal(signal.SIGINT, handle_sigint)

