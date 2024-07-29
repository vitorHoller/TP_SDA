from opcua import Client
import signal
import sys
import multiprocessing
from config import TEMPERATURA_ATUAL_NS, TEMPERATURA_REFERENCIA_NS, CALOR_NS, TEMPERATURA_ATUAL_I, TEMPERATURA_REFERENCIA_I, CALOR_I

def client_opc_ua(opcua_url, filename):
    running = True

    client = Client(opcua_url)
    client.connect()
    temp_atual = client.get_node(f"ns={TEMPERATURA_ATUAL_NS};i={TEMPERATURA_ATUAL_I}")
    temp_referencia = client.get_node(f"ns={TEMPERATURA_REFERENCIA_NS};i={TEMPERATURA_REFERENCIA_I}")
    calor_node = client.get_node(f"ns={CALOR_NS};i={CALOR_I}")

    while running:
        try:
            T_atual = temp_atual.get_value()   
            T_referencia = temp_referencia.get_value()
            calor = calor_node.get_value()

            data = f"Temperatura atual: {T_atual}, Temperatura referencia: {T_referencia}, Calor: {calor}"

            try:
                with open(filename, 'a') as f:
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
    filename = "mes.txt"

    signal.signal(signal.SIGINT, handle_sigint)

    
    client_opc_process = multiprocessing.Process(target=client_opc_ua, args=(client_url, filename))

    try:
        client_opc_process.start()
        

    except KeyboardInterrupt:
        print("Main process is shutting down...")
        client_opc_process.terminate()
        client_opc_process.join()
        print("Main process has shut down.")