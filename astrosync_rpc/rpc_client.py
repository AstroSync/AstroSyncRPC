
from queue import Empty
import time
from typing import Any, Callable
from astrosync_rpc.auth_client import AstroSyncAuthClient
from astrosync_rpc.websocket_client import WebSocketClient, WaitingMsg, Msg


class RPC_Client:

    def __init__(self, ground_station: str, server_addr: str = 'astrosync.ru/api') -> None:
        self.auth_client = AstroSyncAuthClient()
        self.user = self.auth_client.userinfo()
        self.ws_client = WebSocketClient(server_addr, self.user['sub'], ground_station, {})
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
            self.ws_client.call('CONNECT')

    def _auth(self) -> None:
        self.ws_client.ws.send(Msg(src=self.user['sub'], dst='COORDINATOR', method='AUTH',
                         params={'token': self.auth_client.token.access_token}).json())

    def radio_tx(self, data: bytes | list[int]) -> None:
        self.ws_client.call('SEND', {'data': data})

    def radio_wait_rx(self, timeout_sec: float | None = None):
        self.ws_client.call_answer('WAIT_RX', answer_timeout=timeout_sec or 2)

    def run_script(self, script_id: str, timeout: int = 2) -> None:
        print(f'{self.user["sub"]=}')
        self.ws_client.call('RUN_SCRIPT', {'user_id': self.user['sub'], 'script_id': str(script_id), 'timeout': timeout})

    def radio_init(self):
        self.ws_client.call('INIT_RADIO')

    def rotator_set_position(self, az: float, el: float) -> None:
        return self.ws_client.call('SET_POSITION', {'az': az, 'el': el})

    def rotator_get_position(self):
        return self.ws_client.call_answer('GET_POSITION')

    def rotator_get_position_error(self):
        return self.ws_client.call_answer('GET_POSITION_ERROR')

    def get_remaining_session_time(self):
        return self.ws_client.call_answer('GET_REMAINING_SESSION_TIME')

    def echo(self):
        timestamp = time.time()
        answer = self.ws_client.call_answer("ECHO")

        return answer, time.time() - timestamp

    def on_aborted(self, handler: Callable[[None], Any]):
        self.ws_client.register_event('ON_ABORTED', handler)

    def on_session_started(self, handler: Callable[[None], Any]):
        self.ws_client.register_event('ON_SESSION_STARTED', handler)

    def on_session_finished(self, handler: Callable[[None], Any]):
        self.ws_client.register_event('ON_SESSION_FINISHED', handler)

    def on_receive(self, handler: Callable[[str], Any]):
        self.ws_client.register_event('ON_RECEIVE', handler)

    def on_status_changed(self, handler: Callable[[str], Any]):
        self.ws_client.register_event('ON_STATUS_CHANGED', handler)

if __name__ == '__main__':
    client = RPC_Client('NSU')
    client.radio_tx(b'hello world')
    print(client.rotator_get_position())