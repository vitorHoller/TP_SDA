import numpy as np
import matplotlib.pyplot as plt
from opcua import Client, ua
import time
import multiprocessing
import signal
import sys
from config import TEMPERATURA_ATUAL_NS, TEMPERATURA_REFERENCIA_NS, CALOR_NS, TEMPERATURA_ATUAL_I, TEMPERATURA_REFERENCIA_I, CALOR_I

C_m = 1000 # Capacidade termica (J/K)
T_amb = 25 # Temperatura ambiente (°C)
R = 50 # Resistencia termica (K/W)

def derivada_temperatura(T, Q):
    dTdt = (Q / C_m) - ((T - T_amb) / R)
    return dTdt

def integracao_runge_kutta(T, dt, Q):
    k1 = derivada_temperatura(T, Q)
    k2 = derivada_temperatura(T + 0.5 * dt * k1, Q)
    k3 = derivada_temperatura(T + 0.5 * dt * k2, Q)
    k4 = derivada_temperatura(T + dt * k3, Q)
    return T + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

def auto_forno(opcua_url, period=1):

    client = Client(opcua_url)
    client.connect()
    temp_atual = client.get_node(f"ns={TEMPERATURA_ATUAL_NS};i={TEMPERATURA_ATUAL_I}")
    calor_node = client.get_node(f"ns={CALOR_NS};i={CALOR_I}")

    try:
        while True:
            calor = calor_node.get_value()
            T_atual = temp_atual.get_value()
            T = integracao_runge_kutta(T_atual, period, calor)      
            temp_atual.set_value(ua.Variant(T, ua.VariantType.Float))
            print(f"Temperatura atual do forno: {T}, Temperatura no t anterior: {T_atual}, Calor inserido no sistema: {calor}")
            time.sleep(period)
            pass
    except KeyboardInterrupt:
        client.disconnect()
        print("Auto forno interrompido pelo usuario!")


def controle(opcua_url, period=0.5):
    running = True

    client = Client(opcua_url)
    client.connect()
    temp_atual = client.get_node(f"ns={TEMPERATURA_ATUAL_NS};i={TEMPERATURA_ATUAL_I}")
    temp_ref = client.get_node(f"ns={TEMPERATURA_REFERENCIA_NS};i={TEMPERATURA_REFERENCIA_I}")
    calor = client.get_node(f"ns={CALOR_NS};i={CALOR_I}")


    try:
        while True:
            T_atual = temp_atual.get_value() 
            T_ref = temp_ref.get_value()
            if T_atual < T_ref:
                Q = 100000  # Liga
            else:
                Q = 0  # Desliga
            
            calor.set_value(ua.Variant(Q, ua.VariantType.Int32))
            print(f"Controle on-off, temperatura atual: {T_atual}, temperatura referencia: {T_ref}, calor inserido no sistema: {Q}")
            time.sleep(period)
            pass
    except KeyboardInterrupt:
        client.disconnect()
        print("Controle interrompido pelo usuario!")

    client.disconnect()


def handle_sigint(signum, frame):
    print("Interrupção por Control+C detectada. Encerrando...")
    sys.exit(0)

if __name__ == "__main__":
    ##################
    # cria o client
    client_url =  "opc.tcp://localhost:53530/OPCUA/SimulationServer"
    process_controle = multiprocessing.Process(target=controle, args=(client_url,))
    process_auto_forno = multiprocessing.Process(target=auto_forno, args=(client_url,))
    signal.signal(signal.SIGINT, handle_sigint)
    
    subprocesses = [process_controle, process_auto_forno]
    for p in subprocesses:
        p.start()
    try:
        for p in subprocesses:
            p.join()
    except KeyboardInterrupt:
        print("Main process interrupted. Terminating all workers...")
        for p in subprocesses:
            p.terminate()
        for p in subprocesses:
            p.join()
