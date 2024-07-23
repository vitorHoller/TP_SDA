import time
from opcua import Client, ua


def controle(opcua_url, period=0.5):
    running = True

    client = Client(opcua_url)
    client.connect()
    temp_atual = client.get_node("ns=3;i=1009")
    temp_ref = client.get_node("ns=3;i=1010")
    control_node = client.get_node("ns=3;i=1011")

    while running:
        try:
            T_atual = temp_atual.get_value() 
            T_ref = temp_ref.get_value()
            if T_atual < T_ref:
                Q = 5000  # Liga
            else:
                Q = 0  # Desliga
            
            control_node.set_value(ua.Variant(Q, ua.VariantType.Int32))
            print(f"Controle on-off, temperatura atual: {T_atual}, temperatura referencia: {T_ref}, calor inserido no sistema: {Q}")
            time.sleep(period)
        except KeyboardInterrupt:
            client.disconnect()
            running = False

    client.disconnect()

if __name__ == "__main__":
    ##################
    # cria o client
    client_url =  "opc.tcp://localhost:53530/OPCUA/SimulationServer"

    controle(client_url)