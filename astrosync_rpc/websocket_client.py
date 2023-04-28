
from __future__ import annotations
from enum import Enum
import json
from queue import Queue, Empty
from threading import Thread
import time
from dataclasses import dataclass
from typing import Callable
from uuid import UUID, uuid4
from pydantic import BaseModel
import websocket
from websocket import WebSocketApp, WebSocket


def on_error(_, error) -> None:
    print('socket error:', error)
    # ws.keep_running = False
    # ws.close()

def on_close(_, close_status_code, close_msg) -> None:
    print(f"### closed {close_status_code} {close_msg}###")

@dataclass
class WaitingMsg:
    timestamp: float
    message: Msg


class Msg(BaseModel):
    src: str
    dst: str
    method: str
    params: dict | list
    message_id: UUID = uuid4()


class WebSocketClient:
    def __init__(self, server_addr: str, user_id: str, ground_station: str, headers: dict | None = None) -> None:
        websocket.enableTrace(False)
        self.ground_station: str = ground_station
        self.user_id: str = user_id
        self.ws: WebSocketApp = WebSocketApp(f"'ws://{server_addr}/ws'", header=headers, on_open=self.on_open,
                                             on_message=self.on_message, on_error=on_error, on_close=on_close)
        self.reconnect_period: int = 15
        self.waiting_queue: Queue = Queue()
        self.message_spoil_time: int = 60
        self.handlers: dict = {}
        self._waiting_answer: bool = False
        self._last_msg: Msg
        self._thread: Thread
        self._connect()

    def register_event(self, method: str | Enum, handler: Callable) -> None:
        if isinstance(method, Enum):
            method = method.name
        self.handlers.update({method: handler})

    def on_message(self, _: WebSocket, data: str) -> None:
        self._last_msg = Msg.parse_obj(json.loads(data))
        print(f'get msg: {self._last_msg}')
        handler: Callable | None = self.handlers.get(self._last_msg.method, None)
        if handler is not None:
            handler(**self._last_msg.params)
        elif '_ANSWER' in self._last_msg.method:
            self._waiting_answer = False
        else:
            print(f'unsubscribed method: {data}')

    def on_open(self, _) -> None:
        print('connected')
        try:
            while True:
                msg: WaitingMsg = self.waiting_queue.get_nowait()
                if time.time() - msg.timestamp < self.message_spoil_time:
                    self.ws.send(msg.message.json())
        except Empty:
            pass

    def _connect(self) -> None:
        if self._thread.is_alive():
            return
        self._thread: Thread = Thread(target=self.ws.run_forever, kwargs={'reconnect': 15}, daemon=True)
        self._thread.start()

    def is_connected(self) -> bool:
        if self.ws.sock is not None:
            return self.ws.sock.connected
        return False

    def call(self, method: str, params: dict | None = None) -> None:
        msg = Msg(src=self.user_id, dst=self.ground_station, method=method, params=params if params else {})
        if not self.is_connected():
            print('no connection')
            self.waiting_queue.put(WaitingMsg(timestamp=time.time(), message=msg))
            return None
        self.ws.send(msg.json())


    def call_answer(self, method: str, params: dict | None = None, answer_timeout: float = 2):
        self.call(method, params)
        if not (answer := self._answer_waiting(answer_timeout)):
            raise TimeoutError(f'RPC {method} answer timeout')
        return answer

    def _answer_waiting(self, answer_timeout: float) -> dict | list | None:
        while answer_timeout or self._waiting_answer:
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