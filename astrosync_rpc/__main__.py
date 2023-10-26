import time
from astrosync_rpc.rpc_client import RPC_Client


def on_recieve(data: str) -> None:
    print(f'recieve data: {data}')

def on_finished(data):
    print(f'script finished: {data}')

if __name__ == '__main__':
    ground_station = RPC_Client('NSU')
    # print(ground_station.auth_client.userinfo())
    ground_station.on_receive(on_recieve)
    ground_station.on_transmited(lambda data: print(data))
    ground_station.on_script_finished(on_finished)
    print(f'echo time: {ground_station.echo()[1]}')
    # client.radio_modulation('set', 'lora')
    print(ground_station.radio.frequency)
    print(ground_station.radio.bandwidth)
    print(ground_station.run_script_path('Norbi/test2.py', 5))
    # client.radio_header_mode('set', 'implicit')
    # client.radio_bandwidth('set', 'bw125')
    # client.radio_ldro('set', False)
    # client.radio_coding_rate('set', 'CR6')
    # client.radio_crc_mode('set', False)
    # client.radio_payload_length('set', 102)
    # client.radio_preamble_length('set', 10)
    # client.radio_sync_word('set', 10)
    # client.radio_tx_power('set', 5)
    # print(client.radio_read_config())
    # ground_station.radio.init()
    # print(ground_station.radio.read_config())
    # print(ground_station.radio.send_repeat(bytes.fromhex('0E 0A 06 01 CF 05 00 00 01 00 01 00 00 00 01'), 3, 10))

    # print(client.help('get_sat_name'))
    # print(client.radio_send_repeat([14, 10, 6, 1, 251, 1, 1, 1, 1, 0, 2, 0, 0, 0, 1], 2, 10, False))
    # client.rotator_set_position(40, 0)
    # time.sleep(20)
    # print(client.rotator_get_position())
    # client.rotator_set_position(140, 0)
    # time.sleep(10)
    # print(client.rotator_get_position())
    # print(client.rotator_get_position())

    # print(client.rotator_get_position())
    # print(client.echo())
    # client.radio_tx(b'hello')
    # client.radio_tx([1, 2, 3, 43])
    # print(client.run_script_path('Norbi/test.py', timeout=30))
    # time.sleep(6)
    # print(client.terminate_script())

    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass