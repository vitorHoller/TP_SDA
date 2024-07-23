import socket
import multiprocessing
import time
import subprocess

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

def write_to_file(filename, q, semaphore):
    with open(filename, 'a') as f:
        while True:
            data = q.get()
            with semaphore:
                f.write(data + '\n')

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
                    q.put(f"Temperatura de Referencia: {data}")
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
    semaphore = multiprocessing.Semaphore(1)

    writer_process = multiprocessing.Process(target=write_to_file, args=('historiador.txt', queue, semaphore))
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

if __name__ == "__main__":
    start_client()
