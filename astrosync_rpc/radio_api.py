from astrosync_rpc.naku_enums import NAKU_Methods
from astrosync_rpc.sx127x_registers_and_params import SX127x_BW, SX127x_CR, SX127x_HeaderMode, SX127x_Modulation
from astrosync_rpc.websocket_client import WebSocketClient


class RadioAPI:
    def __init__(self, client: WebSocketClient) -> None:
        self._client: WebSocketClient = client

        # self._modulation: SX127x_Modulation | None = None
        # self._coding_rate: SX127x_CR | None = None
        # self._bandwidth: SX127x_BW | None = None
        # self._spread_factor: int | None = None
        # self._frequency: int | None = None
        # self._crc_mode: bool | None = None
        # self._tx_power: int | None = None
        # self._sync_word: int | None = None
        # self._preamble_length: int | None = None
        # self._auto_gain_control: bool | None = None
        # self._payload_length: int | None = None
        # self._low_noize_amplifier: int | None = None
        # self._lna_boost: bool | None = None
        # self._header_mode: SX127x_HeaderMode | None = None
        # self._low_data_rate_optimize: bool | None = None

    def _set_property(self, prop, new_prop) -> None:
        return self._client.call(prop, {'method': 'set', 'new_prop': new_prop})

    def _get_property(self, prop) -> dict:
        return self._client.call_answer(prop, {'method': 'get', 'new_prop': None})

    def init(self) -> None:
        self._client.call(NAKU_Methods.RADIO_INIT)

    def send(self, data: bytes | list[int]) -> None:
        self._client.call(NAKU_Methods.RADIO_SEND, {'data': data})

    def send_repeat(self, data: list[int] | bytes, period_sec: float, max_retries: int = 100,
                          untill_answer: bool = True):
        return self._client.call_answer(NAKU_Methods.RADIO_SEND_REPEAT,
                                          {'data': data, 'period_sec': period_sec, 'max_retries': max_retries,
                                           'untill_answer': untill_answer},
                                          answer_timeout=period_sec * max_retries + 0.3)

    def wait_rx(self, timeout_sec: float | None = None):
        return self._client.call_answer(NAKU_Methods.RADIO_WAIT_RX, answer_timeout=timeout_sec or 2)

    def read_config(self) -> dict:
        return self._client.call_answer(NAKU_Methods.RADIO_READ_CONFIG)

    @property
    def modulation(self) -> dict | None:
        return self._get_property(NAKU_Methods.RADIO_MODULATION)

    @modulation.setter
    def modulation(self, modulation: SX127x_Modulation) -> None:
        return self._set_property(NAKU_Methods.RADIO_MODULATION, modulation.name)

    @property
    def frequency(self) -> dict | None:
        return self._get_property(NAKU_Methods.RADIO_FREQUENCY)

    @frequency.setter
    def frequency(self, frequency_hz: int) -> None:
        return self._set_property(NAKU_Methods.RADIO_FREQUENCY, frequency_hz)

    @property
    def header_mode(self) -> dict | None:
        return self._get_property(NAKU_Methods.RADIO_HEADER_MODE)

    @header_mode.setter
    def header_mode(self, header_mode: SX127x_HeaderMode) -> None:
        return self._set_property(NAKU_Methods.RADIO_HEADER_MODE, header_mode.name)

    @property
    def bandwidth(self) -> dict | None:
        return self._get_property(NAKU_Methods.RADIO_BANDWIDTH)

    @bandwidth.setter
    def bandwidth(self, bandwidth: SX127x_BW) -> None:
        return self._set_property(NAKU_Methods.RADIO_BANDWIDTH, bandwidth.name)

    @property
    def payload_length(self) -> dict | None:
        return self._get_property(NAKU_Methods.RADIO_PAYLOAD_LENGTH)

    @payload_length.setter
    def payload_length(self, payload_length: int) -> None:
        return self._set_property(NAKU_Methods.RADIO_PAYLOAD_LENGTH, payload_length)

    @property
    def coding_rate(self) -> dict | None:
        return self._get_property(NAKU_Methods.RADIO_CODING_RATE)

    @coding_rate.setter
    def coding_rate(self, coding_rate: SX127x_CR) -> None:
        return self._set_property(NAKU_Methods.RADIO_CODING_RATE, coding_rate.name)

    @property
    def crc_mode(self) -> dict | None:
        return self._get_property(NAKU_Methods.RADIO_CRC_MODE)

    @crc_mode.setter
    def crc_mode(self, crc_mode: bool) -> None:
        return self._set_property(NAKU_Methods.RADIO_CRC_MODE, crc_mode)

    @property
    def ldro(self) -> dict | None:
        return self._get_property(NAKU_Methods.RADIO_LOW_DATA_RATE_OPTIMIZE)

    @ldro.setter
    def ldro(self, ldro: bool) -> None:
        return self._set_property(NAKU_Methods.RADIO_LOW_DATA_RATE_OPTIMIZE, ldro)

    @property
    def preamble_length(self) -> dict | None:
        return self._get_property(NAKU_Methods.RADIO_PREAMBLE_LENGTH)

    @preamble_length.setter
    def preamble_length(self, preamble_length: int) -> None:
        return self._set_property(NAKU_Methods.RADIO_PREAMBLE_LENGTH, preamble_length)

    @property
    def spreading_factor(self) -> dict | None:
        return self._get_property(NAKU_Methods.RADIO_SPREADING_FACTOR)

    @spreading_factor.setter
    def spreading_factor(self, spreading_factor: int) -> None:
        return self._set_property(NAKU_Methods.RADIO_SPREADING_FACTOR, spreading_factor)

    @property
    def tx_power(self) -> dict | None:
        return self._get_property(NAKU_Methods.RADIO_TX_POWER)

    @tx_power.setter
    def tx_power(self, tx_power: int) -> None:
        return self._set_property(NAKU_Methods.RADIO_TX_POWER, tx_power)

    @property
    def sync_word(self) -> dict | None:
        return self._get_property(NAKU_Methods.RADIO_SYNC_WORD)

    @sync_word.setter
    def sync_word(self, sync_word: int) -> None:
        return self._set_property(NAKU_Methods.RADIO_SYNC_WORD, sync_word)

    @property
    def auto_gain_control(self) -> dict | None:
        return self._get_property(NAKU_Methods.RADIO_AUTO_GAIN_CONTROL)

    @auto_gain_control.setter
    def auto_gain_control(self, auto_gain_control: bool) -> None:
        return self._set_property(NAKU_Methods.RADIO_AUTO_GAIN_CONTROL, auto_gain_control)

    @property
    def lna_gain(self) -> dict | None:
        return self._get_property(NAKU_Methods.RADIO_LOW_NOIZE_AMPLIFIER)

    @lna_gain.setter
    def lna_gain(self, lna_gain: int) -> None:
        return self._set_property(NAKU_Methods.RADIO_LOW_NOIZE_AMPLIFIER, lna_gain)
