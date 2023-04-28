
from typing import Callable
from astrosync_rpc.websocket_client import WebSocketClient


class RPC_Client:
    def __init__(self, server_addr: str, user_id: str, ground_station: str) -> None:
        self._ws = WebSocketClient(server_addr, user_id, ground_station, {})

    def radio_tx(self, data: str) -> None:
        self._ws.call('SEND', {'data': data})

    def radio_wait_rx(self):
        self._ws.call('WAIT_RX')

    def radio_init(self):
        self._ws.call('INIT_RADIO')

    def rotator_get_position(self):
        return self._ws.call_answer('GET_POSITION')

    def rotator_get_position_error(self):
        return self._ws.call_answer('GET_POSITION_ERROR')

    def get_remaining_session_time(self):
        return self._ws.call_answer('get_remaining_session_time')

    def echo(self):
        return self._ws.call_answer("ECHO")

    def on_aborted(self, handler: Callable):
        self._ws.register_event('ON_ABORTED', handler)

    def on_session_started(self, handler: Callable):
        self._ws.register_event('ON_SESSION_STARTED', handler)

    def on_session_finished(self, handler: Callable):
        self._ws.register_event('ON_SESSION_FINISHED', handler)

    def on_receive(self, handler: Callable):
        self._ws.register_event('ON_RECEIVE', handler)

    def on_status_changed(self, handler: Callable):
        self._ws.register_event('ON_STATUS_CHANGED', handler)