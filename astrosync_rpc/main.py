

from astrosync_rpc.rpc_client import RPC_Client

def on_status_changed(status):
    print(f'status changed: {status}')

def on_recieve(data):
    print(f'recieve data: {data}')

if __name__ == '__main__':
    client = RPC_Client('astrosync.ru', 'c0833966-ae6d-4034-b74a-c0ee9424df5d', 'NSU')
    client.on_status_changed(on_status_changed)
    client.on_receive(on_recieve)
    print(client.echo())
    print(client.rotator_get_position())