
from __future__ import annotations
from enum import Enum
from queue import Queue
from threading import RLock, Thread
import time
from dataclasses import dataclass
from typing import Callable, Type
from uuid import UUID, uuid4
from loguru import logger
from pydantic import BaseModel, Field, ValidationError
import websocket
from websocket import WebSocketApp, WebSocket

from astrosync_rpc.naku_enums import NAKU_Methods


def on_error(_, error) -> None:
    print('socket error:', error)
    # ws.keep_running = False
    # ws.close()

def on_close(_, close_status_code, close_msg) -> None:
    print(f"### closed {close_status_code} {close_msg}###")

class Signal:

    lock: RLock = RLock()

    # def __init__(self, args: list[Type] | None = None):
    #     self.args: list[Type] | None = args
    def __init__(self, *args: Type) -> None:
        self.listeners: list[Callable] = []
        self.args: tuple[Type, ...] = args

    def connect(self, func: Callable) -> None:
        self.listeners.append(func)

    def disconnect(self, func: Callable) -> None:
        self.listeners.remove(func)

    def emit(self, *args) -> None:
        with self.lock:
            if len(args) == len(self.args):
                if any(not isinstance(arg, self_arg) for arg, self_arg in zip(args, self.args)):
                    raise TypeError(f'This signal should emit next types: {self.args}, but you try to emit {args}.')
            else:
                raise TypeError(f'This signal should emit next types: {self.args}, but you try to emit {args}.')
            _ = [callback(*args) for callback in self.listeners]

@dataclass
class WaitingMsg:
    timestamp: float
    message: Msg


class Msg(BaseModel):
    src: str
    dst: str
    method: str
    params: dict
    message_id: UUID = Field(default_factory=uuid4)


class WebSocketClient:

    on_open_event: Signal = Signal()
    on_close_event: Signal = Signal()

    def __init__(self, server_addr: str, user_id: str, ground_station: str, headers: dict | None = None,
                 ssl: bool = True) -> None:
        websocket.enableTrace(False)
        ws_headers: dict | list = headers or []
        self.ground_station: str = ground_station
        self.user_id: str = user_id
        self.__ssl: str = 'wss' if ssl else 'ws'
        self.ws: WebSocketApp = WebSocketApp(f"{self.__ssl}://{server_addr}/ws", header=ws_headers,
                                             on_open=self.on_open,  on_message=self.on_message,
                                             on_error=on_error, on_close=self.on_close)
        self.reconnect_period: int = 15
        self.waiting_queue: Queue = Queue()
        self.message_spoil_time: int = 60
        self.handlers: dict = {}
        self._waiting_answer: bool = False
        self._last_msg: Msg
        self._thread: Thread
        self.connection_status = False



    def register_event(self, method: str | Enum, handler: Callable) -> None:
        if isinstance(method, Enum):
            method = method.name
        self.handlers.update({method: handler})

    def on_message(self, _: WebSocket, data: str) -> None:
        try:
            self._last_msg = Msg.model_validate_json(data.lower())
        except ValidationError:
            logger.error('got incorrect message:', data)
            return None
        handler: Callable | None = self.handlers.get(self._last_msg.method.upper(), None)
        if handler is not None:
            handler(self._last_msg.params)
        elif '_answer' in self._last_msg.method:
            self._waiting_answer = False
        else:
            logger.warning(f'unsubscribed method: {data}')

    def on_close(self, _, close_status_code, close_msg) -> None:
        logger.debug(f'{close_status_code=}, {close_msg=}')
        self.connection_status = False
        self.on_close_event.emit()

    def on_open(self, _) -> None:
        logger.debug('connected')
        self.connection_status = True
        self.on_open_event.emit()

    def _connect(self) -> None:
        # if not self._thread:
        #     return
        # if self._thread.is_alive():
        #     return
        self._thread: Thread = Thread(name='ws_thread', target=self.ws.run_forever, kwargs={'reconnect': 15},
                                      daemon=True)
        self._thread.start()
        time.sleep(0.5)

    def is_connected(self) -> bool:
        if self.ws.sock is not None:
            return self.ws.sock.connected
        return False

    def call(self, method: NAKU_Methods, params: dict | None = None) -> None:
        if not self.connection_status:
            raise RuntimeError('Websocket is not connected. AstroSync api server is offline')
        msg = Msg(src=self.user_id, dst=self.ground_station, method=method.name.lower(), params=params or {})
        if not self.is_connected():
            logger.warning('no connection')
            self.waiting_queue.put(WaitingMsg(timestamp=time.time(), message=msg))
            return None
        self.ws.send(msg.model_dump_json())


    def call_answer(self, method: NAKU_Methods, params: dict| None = None, answer_timeout: float = 2) -> dict:
        if not self.connection_status:
            raise RuntimeError('Websocket is not connected')
        self._waiting_answer = True
        self.call(method, params)
        if not (answer := self._answer_waiting(answer_timeout)):
            raise TimeoutError(f'RPC {method.name.lower()} answer timeout')
        return answer

    def _answer_waiting(self, answer_timeout: float) -> dict | None:
        while answer_timeout > 0 and self._waiting_answer:
            time.sleep(0.05)
            answer_timeout -= 0.05
        if not self._waiting_answer:
            return self._last_msg.params


    def close(self) -> None:
        return self.ws.close()

    def set_reconnection_period(self, period_sec: int) -> None:
        self.reconnect_period = period_sec


if __name__ == "__main__":
    rpc = WebSocketClient('10.6.1.136:8086', 'c0833966-ae6d-4034-b74a-c0ee9424df5d', 'NSU')
    # pubsub.publish('NSU', )
    print('start')
    try:
        while True:
            d: str = input('>')
            # rpc.notify('message', {'data': d})
    except KeyboardInterrupt:
        print('Shutdown radio driver')