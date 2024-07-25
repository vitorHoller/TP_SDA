import numpy as np
import matplotlib.pyplot as plt
from opcua import Client, ua
import time
import socket
import multiprocessing
import sys
import signal

def client_opc_ua(opcua_url, queue_calor, queue_temperatura, queue_referencia):
    running = True

    client = Client(opcua_url)
    client.connect()
    temp_atual = client.get_node("ns=3;i=1009")
    temp_referencia = client.get_node("ns=3;i=1010")
    calor_node = client.get_node("ns=3;i=1011")

    while running:
        try:
            if not queue_referencia.empty():
                T_referencia = queue_referencia.get()
                temp_referencia.set_value(ua.Variant(float(T_referencia), ua.VariantType.Float))

            calor = calor_node.get_value()
            T_atual = temp_atual.get_value()   
            queue_calor.put(calor)
            queue_temperatura.put(T_atual)
            time.sleep(1)

            
        except KeyboardInterrupt:
            client.disconnect()
            running = False

def receive_messages(client_socket, queue_referencia):    
    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                try:
                    if message == b'__EXIT__':
                        print("Client asked for disconnection")
                        client_socket.close()
                        break
                    queue_referencia.put(message.decode('utf-8'), timeout=1)
                except queue_referencia.Full:
                    print("queue_referencia is full. Failed to put message.")
                client_socket.sendall(b"Nova temperatura de referencia obtida")
        except ConnectionResetError:
            print("Client disconnected")
            break


def send_messages(client_socket, queue_calor, queue_temperatura):
    while True:
        try:
            if not queue_calor.empty() and not queue_temperatura.empty():
                calor_message = queue_calor.get()
                temperatura_message = queue_temperatura.get()
                
                combined_message = f"Calor: {calor_message}; Temperatura: {temperatura_message}"
                client_socket.send(combined_message.encode('utf-8'))

            time.sleep(0.5)  # Aguarde 0.5 segundos entre os envios

        except ConnectionResetError:
            print("Client disconnected")
            break

        except BrokenPipeError:
            print("Client disconnected")
            break

def server_tcp_ip(queue_calor, queue_temperatura, queue_referencia, client_url):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    HOST = '127.0.0.1'  # Localhost
    PORT = 65432        # Port to listen on
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)  # Permitir até 10 conexões pendentes
    
    print(f"Server listening on {HOST}:{PORT}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")

            client_opc_process = multiprocessing.Process(target=client_opc_ua, args=(client_url, queue_calor, queue_temperatura, queue_referencia))
            client_opc_process.start()
            send_messages_process = multiprocessing.Process(target=send_messages, args=(client_socket, queue_calor, queue_temperatura))
            send_messages_process.start()
            receive_messages_process = multiprocessing.Process(target=receive_messages, args=(client_socket, queue_referencia))
            receive_messages_process.start()       

            while receive_messages_process.is_alive():
                pass

            client_opc_process.terminate()
            client_opc_process.join()

            receive_messages_process.join()
            
            send_messages_process.terminate()
            send_messages_process.join()

    except KeyboardInterrupt:
        print("Server is shutting down...")
    
    finally:
        server_socket.close()
        print("Server has shut down.")

def handle_sigint(signum, frame):
    print("Interrupção por Control+C detectada. Encerrando...")
    sys.exit(0)

if __name__ == "__main__":
    queue_calor = multiprocessing.Queue()
    queue_temperatura = multiprocessing.Queue()
    queue_referencia = multiprocessing.Queue()
    client_url =  "opc.tcp://localhost:53530/OPCUA/SimulationServer"

    server_process = multiprocessing.Process(target=server_tcp_ip, args=(queue_calor, queue_temperatura, queue_referencia, client_url))
    signal.signal(signal.SIGINT, handle_sigint)

    try:
        server_process.start()
        

    except KeyboardInterrupt:
        print("Main process is shutting down...")
        server_process.terminate()
        server_process.join()
        print("Main process has shut down.")