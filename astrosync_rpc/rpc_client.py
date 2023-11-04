
import time
from queue import Empty
from typing import Any, Callable

from loguru import logger
import requests
from astrosync_rpc.auth_client import AstroSyncAuthClient
from astrosync_rpc.naku_enums import NAKU_Methods, NAKU_Events
from astrosync_rpc.radio_api import RadioAPI
from astrosync_rpc.rotator_api import RotatorAPI
from astrosync_rpc.websocket_client import WebSocketClient, WaitingMsg, Msg


class RPC_Client:

    def __init__(self, ground_station: str, server_addr: str = 'astrosync.ru', api_path: str = 'api',
                 ssl: bool = True) -> None:
        self._server_addr: str = ('https' if ssl else 'http') + f'://{server_addr}/{api_path}/'
        self.auth_client = AstroSyncAuthClient(server_addr=server_addr, ssl=ssl)
        self.user = self.auth_client.userinfo()
        self.ws_client = WebSocketClient(f'{server_addr}/{api_path}', self.user['sub'], ground_station, {}, ssl)
        self.ws_client.on_open_event.connect(self._on_connected)
        self.ws_client._connect()
        self.radio = RadioAPI(self.ws_client)
        self.rotator = RotatorAPI(self.ws_client)

    def _on_connected(self) -> None:
        self._auth()
        try:
            while True:
                msg: WaitingMsg = self.ws_client.waiting_queue.get_nowait()
                if time.time() - msg.timestamp < self.ws_client.message_spoil_time:
                    self.ws_client.ws.send(msg.message.model_dump_json())
        except Empty:
            pass
        finally:
            self.ws_client.call(NAKU_Methods.CONNECT)

    def _auth(self) -> None:
        msg = Msg(src=self.user['sub'], dst='COORDINATOR', method='AUTH',
                         params={'token': self.auth_client.token.access_token})
        self.ws_client.ws.send(msg.model_dump_json())

    def run_script(self, script_id: str, timeout: int = 2):
        logger.debug(f'{self.user["sub"]=}')
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

    def terminate_script(self):
        return self.ws_client.call_answer(NAKU_Methods.TERMINATE_SCRIPT)

    def get_remaining_session_time(self):
        return self.ws_client.call_answer(NAKU_Methods.GET_REMAINING_SESSION_TIME)

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

    def on_transmited(self, handler: Callable[[str], Any]):
        self.ws_client.register_event(NAKU_Events.RADIO_TRANSMITED, handler)

    def on_script_finished(self, handler: Callable[[str], Any]):
        self.ws_client.register_event(NAKU_Events.SCRIPT_FINISHED, handler)

    def get_file_by_path(self, file_path: str):
        querry_str: str = self._server_addr + f'get_file_by_path?file_path={file_path}'
        access_token = self.auth_client.token.access_token
        resp: requests.Response = requests.get(querry_str, headers={'Authorization': 'Bearer ' + access_token})
        return resp.content.decode('utf-8')

if __name__ == '__main__':
    client = RPC_Client('NSU')
    print(client.get_file_by_path('test/Norbi/NORBI2/Scripts/wr_ft_pl_sol.json'))
    # client.radio_send(b'hello world')
    # print(client.rotator_get_position())