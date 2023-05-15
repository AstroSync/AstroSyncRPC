
from astrosync_rpc.rpc_client import RPC_Client

def on_status_changed(status):
    print(f'status changed: {status}')

def on_recieve(data: str) -> None:
    print(f'recieve data: {data}')

if __name__ == '__main__':
    client = RPC_Client('NSU')
    client.on_status_changed(on_status_changed)
    client.on_receive(on_recieve)
    print(client.rotator_get_position())
    print(client.echo())
    # client.radio_tx('hello')