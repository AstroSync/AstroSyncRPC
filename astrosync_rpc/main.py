import time
from astrosync_rpc.rpc_client import RPC_Client

def on_status_changed(status):
    print(f'status changed: {status}')

def on_recieve(data: str) -> None:
    print(f'recieve data: {data}')

if __name__ == '__main__':
    client = RPC_Client('NSU', '10.8.2.2', False)
    print(client.auth_client.userinfo())
    client.on_receive(on_recieve)
    print(client.echo()[1])
    client.rotator_set_position(40, 0)
    # client.radio_modulation('set', 'lora')
    client.radio_frequency('set', 436_700_000)
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
    client.radio_init()
    print(client.radio_read_config())
    print(client.radio_send_repeat(bytes.fromhex('0E 0A 06 01 CF 05 00 00 01 00 01 00 00 00 01'), 3, 10))

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

    # try:
    #     while True:
    #         pass
    # except KeyboardInterrupt:
    #     pass