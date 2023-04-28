from enum import Enum, auto


class NAKU_Modes(Enum):
    IDLE = auto()
    BUSY = auto()
    PAUSE = auto()
    CRITICAL_ERROR = auto()

class NAKU_Events(Enum):
    ON_RECEIVE = auto()
    ON_TRANSMIT = auto()
    ON_RX_TIMEOUT = auto()
    ON_TX_TIMEOUT = auto()
    ON_PRINT = auto()
    ON_SESSION_FINISHED = auto()
    ON_SESSION_STARTED = auto()
    ON_ABORTED = auto()
    ON_PAUSE = auto()
    ON_STATUS_CHANGED = auto()
    ON_RUNTIME_ERROR = auto()
    ON_ROTATOR_TURN_AWAY = auto()
    ON_ROTATOR_CRITICAL_ERROR = auto()
    ON_ROTATOR_AIMED = auto()
    ON_ROTATE = auto()

class NAKU_Methods(Enum):
    SEND = auto()
    WAIT_RX = auto()
    INIT_RADIO = auto()
    GET_POSITION = auto()
    GET_POSITION_ERROR = auto()
    SET_RX_TIMEOUT = auto()
    GET_RX_BUFFER = auto()
    GET_REMAINING_SESSION_TIME = auto()
    START_SESSION = auto()
    RUN_SCRIPT = auto()
    PAUSE_EXECUTOR = auto()
    NEXT_STEP = auto()
    ABORT_EXECUTOR = auto()
    CONTINUE_EXECUTOR = auto()
    GO_INTO = auto()
    GO_OUT = auto()
    HELP = auto()