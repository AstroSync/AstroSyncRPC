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
    client.radio_tx([14, 10, 6, 1, 251, 1, 1, 1, 1, 0, 1, 0, 0, 0, 9])
    print(client.radio_wait_rx(3))

    # print(client.rotator_get_position())
    # client.rotator_set_position(30, 0)
    # time.sleep(5)
    # print(client.rotator_get_position())
    # print(client.echo())
    # client.run_script('c04b0f66-33b1-4fd7-b949-e02f4152b6c8')
    # client.radio_tx('hello')