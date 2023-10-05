
from queue import Empty
import time
from typing import Any, Callable, Literal
from astrosync_rpc.auth_client import AstroSyncAuthClient
from astrosync_rpc.naku_enums import NAKU_Methods, NAKU_Events
from astrosync_rpc.websocket_client import WebSocketClient, WaitingMsg, Msg


class RPC_Client:

    def __init__(self, ground_station: str, server_addr: str = 'astrosync.ru/api', ssl: bool = True) -> None:
        self.auth_client = AstroSyncAuthClient(server_addr=server_addr, ssl=ssl)
        self.user = self.auth_client.userinfo()
        self.ws_client = WebSocketClient(server_addr, self.user['sub'], ground_station, {}, ssl)
        self.ws_client.on_open_event.connect(self.on_connected)
        self.ws_client._connect()

    def on_connected(self) -> None:
        self._auth()
        try:
            while True:
                msg: WaitingMsg = self.ws_client.waiting_queue.get_nowait()
                if time.time() - msg.timestamp < self.ws_client.message_spoil_time:
                    self.ws_client.ws.send(msg.message.json())
        except Empty:
            pass
        finally:
            self.ws_client.call(NAKU_Methods.CONNECT)

    def _auth(self) -> None:
        self.ws_client.ws.send(Msg(src=self.user['sub'], dst='COORDINATOR', method='AUTH',
                         params={'token': self.auth_client.token.access_token}).json())

    def radio_send(self, data: bytes | list[int]) -> None:
        self.ws_client.call(NAKU_Methods.RADIO_SEND, {'data': data})

    def radio_send_repeat(self, data: list[int] | bytes, period_sec: float, max_retries: int = 100,
                          untill_answer: bool = True):
        return self.ws_client.call_answer(NAKU_Methods.RADIO_SEND_REPEAT,
                                          {'data': data, 'period_sec': period_sec, 'max_retries': max_retries,
                                           'untill_answer': untill_answer},
                                          answer_timeout=period_sec * max_retries + 0.3)

    def radio_wait_rx(self, timeout_sec: float | None = None):
        return self.ws_client.call_answer(NAKU_Methods.RADIO_WAIT_RX, answer_timeout=timeout_sec or 2)

    def run_script(self, script_id: str, timeout: int = 2):
        print(f'{self.user["sub"]=}')
        return self.ws_client.call_answer(NAKU_Methods.RUN_SCRIPT, {'script_id': str(script_id),
                                                                    'timeout': timeout,
                                                                    'need_result': True},
                                          answer_timeout=timeout + 2)

    def run_script_path(self, script_path: str, timeout: int = 2):
        if not script_path.startswith(f'{self.user["given_name"]}/'):
            script_path = f'{self.user["given_name"]}/{script_path}'
        return self.ws_client.call_answer(NAKU_Methods.RUN_SCRIPT_PATH, {'script_path': script_path,
                                                                         'timeout': timeout,
                                                                         'need_result': True},
                                          answer_timeout=timeout + 2)

    def radio_init(self) -> None:
        self.ws_client.call(NAKU_Methods.RADIO_INIT)

    def terminate_script(self):
        return self.ws_client.call_answer(NAKU_Methods.TERMINATE_SCRIPT)

    def rotator_set_position(self, az: float, el: float) -> None:
        return self.ws_client.call(NAKU_Methods.SET_POSITION, {'az': az, 'el': el})

    def rotator_get_position(self):
        return self.ws_client.call_answer(NAKU_Methods.GET_POSITION)

    def rotator_get_position_error(self):
        return self.ws_client.call_answer(NAKU_Methods.GET_POSITION_ERROR)

    def get_remaining_session_time(self):
        return self.ws_client.call_answer(NAKU_Methods.GET_REMAINING_SESSION_TIME)

    def _call_property(self, method: Literal['set', 'get'], prop, new_prop):
        handler = self.ws_client.call_answer
        if method == 'set':
            handler = self.ws_client.call
        return handler(prop, {'method': method, 'new_prop': new_prop})

    def radio_modulation(self, method: Literal['set', 'get'],
                         modulation: Literal['lora', 'fsk'] | None = None) -> dict | None:
        return self._call_property(method, NAKU_Methods.RADIO_MODULATION, modulation)

    def radio_frequency(self, method: Literal['set', 'get'], frequency_hz: int | None = None) -> dict | None:
        return self._call_property(method, NAKU_Methods.RADIO_FREQUENCY, frequency_hz)

    def radio_header_mode(self, method: Literal['set', 'get'], header_mode: str | None = None) -> dict | None:
        return self._call_property(method, NAKU_Methods.RADIO_HEADER_MODE, header_mode)

    def radio_bandwidth(self, method: Literal['set', 'get'], bandwidth: str | None = None) -> dict | None:
        return self._call_property(method, NAKU_Methods.RADIO_BANDWIDTH, bandwidth)

    def radio_payload_length(self, method: Literal['set', 'get'], payload_length: int | None = None) -> dict | None:
        return self._call_property(method, NAKU_Methods.RADIO_PAYLOAD_LENGTH, payload_length)

    def radio_coding_rate(self, method: Literal['set', 'get'], coding_rate: str | None = None) -> dict | None:
        return self._call_property(method, NAKU_Methods.RADIO_CODING_RATE, coding_rate)

    def radio_crc_mode(self, method: Literal['set', 'get'], crc_mode: bool | None = None) -> dict | None:
        return self._call_property(method, NAKU_Methods.RADIO_CRC_MODE, crc_mode)

    def radio_ldro(self, method: Literal['set', 'get'], ldro: bool | None = None) -> dict | None:
        return self._call_property(method, NAKU_Methods.RADIO_LOW_DATA_RATE_OPTIMIZE, ldro)

    def radio_preamble_length(self, method: Literal['set', 'get'], preamble_length: int | None = None) -> dict | None:
        return self._call_property(method, NAKU_Methods.RADIO_PREAMBLE_LENGTH, preamble_length)

    def radio_spreading_factor(self, method: Literal['set', 'get'], spreading_factor: str | None = None) -> dict | None:
        return self._call_property(method, NAKU_Methods.RADIO_SPREADING_FACTOR, spreading_factor)

    def radio_tx_power(self, method: Literal['set', 'get'], tx_power: int | None = None) -> dict | None:
        return self._call_property(method, NAKU_Methods.RADIO_TX_POWER, tx_power)

    def radio_sync_word(self, method: Literal['set', 'get'], sync_word: int | None = None) -> dict | None:
        return self._call_property(method, NAKU_Methods.RADIO_SYNC_WORD, sync_word)

    def radio_auto_gain_control(self, method: Literal['set', 'get'], auto_gain_control: bool | None = None) -> dict | None:
        return self._call_property(method, NAKU_Methods.RADIO_AUTO_GAIN_CONTROL, auto_gain_control)

    def radio_lna_gain(self, method: Literal['set', 'get'], lna_gain: int | None = None) -> dict | None:
        return self._call_property(method, NAKU_Methods.RADIO_LOW_NOIZE_AMPLIFIER, lna_gain)

    def radio_read_config(self) -> dict:
        return self.ws_client.call_answer(NAKU_Methods.RADIO_READ_CONFIG)

    def help(self, method_or_event: str = ''):
        return self.ws_client.call_answer(NAKU_Methods.HELP, {'method_or_event': method_or_event})

    def echo(self):
        timestamp = time.time()
        answer = self.ws_client.call_answer(NAKU_Methods.ECHO)
        return answer, time.time() - timestamp

    def on_aborted(self, handler: Callable[[None], Any]):
        self.ws_client.register_event(NAKU_Events.SESSION_ABORTED, handler)

    def on_session_started(self, handler: Callable[[None], Any]):
        self.ws_client.register_event(NAKU_Events.SESSION_STARTED, handler)

    def on_session_finished(self, handler: Callable[[None], Any]):
        self.ws_client.register_event(NAKU_Events.SESSION_FINISHED, handler)

    def on_receive(self, handler: Callable[[str], Any]):
        self.ws_client.register_event(NAKU_Events.RADIO_RECEIVED, handler)

if __name__ == '__main__':
    client = RPC_Client('NSU')
    client.radio_send(b'hello world')
    print(client.rotator_get_position())