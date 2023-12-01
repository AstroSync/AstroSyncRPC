# AstroSyncRPC

## Installation

`pip install git+https://github.com/AstroSync/AstroSyncRPC.git`

## Using

```python
from astrosync_rpc.rpc_client import RPC_Client


def on_recieve(data: str) -> None:
    print(f'receive data: {data}')

def on_finished(data):
    print(f'script finished: {data}')

if __name__ == '__main__':
    ground_station = RPC_Client('NSU')
    # print(ground_station.auth_client.userinfo())
    ground_station.on_receive(on_recieve)
    ground_station.on_transmited(lambda data: print(data))
    ground_station.on_script_finished(on_finished)
    print(f'echo time: {ground_station.echo()[1]}')

    # reading actual radio parameters
    print(ground_station.radio.frequency)
    print(ground_station.radio.bandwidth)
    print(ground_station.radio.tx_power)

    # sending data over radio with current settings
    ground_station.radio.send([1, 2, 3])

    # running script from DB file system
    ground_station.run_script_path('Norbi/NORBI2/N2_wr_ft.py')
```