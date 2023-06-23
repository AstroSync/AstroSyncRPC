import time
from astrosync_rpc.rpc_client import RPC_Client

def on_status_changed(status):
    print(f'status changed: {status}')

def on_recieve(data: str) -> None:
    print(f'recieve data: {data}')

if __name__ == '__main__':
    client = RPC_Client('NSU')
    client.on_status_changed(on_status_changed)
    client.on_receive(on_recieve)
    print(client.echo())
    # print(client.radio_send_repeat([14, 10, 6, 1, 251, 1, 1, 1, 1, 0, 2, 0, 0, 0, 1], 2, 10, False))
    print(client.rotator_get_position())
    # client.rotator_set_position(40, 0)
    # print(client.rotator_get_position())
    # client.rotator_set_position(40, 0)
    # time.sleep(10)
    # print(client.rotator_get_position())

    # print(client.rotator_get_position())
    # print(client.echo())
    client.run_script_path('Norbi/Parser/parser_test.py', timeout=15)
    # time.sleep(2)
    # client.radio_tx('hello')