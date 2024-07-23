from opcua import Client
from opcua.ua import AttributeIds
import time

TEMP_ATUAL_INICIAL = 100
TEMP_REFERENCIA_INICIAL = 4000

##################
# cria o client
client = Client("opc.tcp://localhost:53530/OPCUA/SimulationServer")

try:
    client.connect()

    temp_atual = client.get_node("ns=3;i=1009")
    temp_ref = client.get_node("ns=3;i=1010")

    temp_atual.set_value(TEMP_ATUAL_INICIAL)
    temp_ref.set_value(TEMP_REFERENCIA_INICIAL)

    # Espera por 2 segundos
    time.sleep(2)

finally:
    client.disconnect()
    print("Client disconnected")

print("Script executed for 2 seconds.")
