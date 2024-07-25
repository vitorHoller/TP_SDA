import numpy as np
import matplotlib.pyplot as plt
from opcua import Client, ua
import signal
import sys
import multiprocessing

def client_opc_ua(opcua_url, filename):
    running = True

    client = Client(opcua_url)
    client.connect()
    temp_atual = client.get_node("ns=3;i=1009")
    temp_referencia = client.get_node("ns=3;i=1010")
    calor_node = client.get_node("ns=3;i=1011")

    while running:
        try:
            T_atual = temp_atual.get_value()   
            T_referencia = temp_referencia.get_value()
            calor = calor_node.get_value()

            data = f"Temperatura atual: {T_atual}, Temperatura referencia: {T_referencia}, Calor: {calor}"

            try:
                with open("mex.txt", 'a') as f:
                    f.write(data + '\n')
            except Exception as e:
                print(f"Erro ao tentar criar ou escrever no arquivo: {e}")


        except KeyboardInterrupt:
            client.disconnect()
            running = False

def handle_sigint(signum, frame):
    print("Interrupção por Control+C detectada. Encerrando...")
    sys.exit(0)

if __name__ == "__main__":
    client_url =  "opc.tcp://localhost:53530/OPCUA/SimulationServer"
    filename = "mex.txt"

    signal.signal(signal.SIGINT, handle_sigint)

    
    client_opc_process = multiprocessing.Process(target=client_opc_ua, args=(client_url, filename))

    try:
        client_opc_process.start()
        

    except KeyboardInterrupt:
        print("Main process is shutting down...")
        client_opc_process.terminate()
        client_opc_process.join()
        print("Main process has shut down.")