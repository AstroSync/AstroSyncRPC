
from astrosync_rpc.naku_enums import NAKU_Methods
from astrosync_rpc.websocket_client import WebSocketClient


class RotatorAPI:
    def __init__(self, client: WebSocketClient) -> None:
        self._client: WebSocketClient = client

    def set_position(self, az: float, el: float) -> None:
        return self._client.call(NAKU_Methods.SET_POSITION, {'az': az, 'el': el})

    def get_position(self):
        return self._client.call_answer(NAKU_Methods.GET_POSITION)

    def get_position_error(self):
        return self._client.call_answer(NAKU_Methods.GET_POSITION_ERROR)
