from opcua import Client
from opcua.ua import AttributeIds
import time
from config import TEMPERATURA_ATUAL_NS, TEMPERATURA_REFERENCIA_NS, CALOR_NS, TEMPERATURA_ATUAL_I, TEMPERATURA_REFERENCIA_I, CALOR_I


TEMP_ATUAL_INICIAL = 100
TEMP_REFERENCIA_INICIAL = 4000
CALOR_INICIAL = 0

##################
# cria o client
client = Client("opc.tcp://localhost:53530/OPCUA/SimulationServer")

try:
    client.connect()

    temp_atual = client.get_node(f"ns={TEMPERATURA_ATUAL_NS};i={TEMPERATURA_ATUAL_I}")
    temp_ref = client.get_node(f"ns={TEMPERATURA_REFERENCIA_NS};i={TEMPERATURA_REFERENCIA_I}")
    calor = client.get_node(f"ns={CALOR_NS};i={CALOR_I}")

    temp_atual.set_value(TEMP_ATUAL_INICIAL)
    temp_ref.set_value(TEMP_REFERENCIA_INICIAL)
    calor.set_value(CALOR_INICIAL)

    # Espera por 2 segundos
    time.sleep(2)

finally:
    client.disconnect()
    print("Client disconnected")

print("Script executed for 2 seconds.")
