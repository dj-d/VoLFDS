START_INDEX = 0

# Log Messages
MSG_SUC_SEQUENTIALIZATION = 'Sequentialization successfully completed'
MSG_LOW_OBJECT_BITS = 'too many addressed objects'
MSG_CONVERSION_ERROR = 'CONVERSION ERROR'

# PATHS
CBMC_PATH = '/path/to/cbmc/tool/'
LAZY_CSEQ_PATH = '/path/to/lazycseq/tool/'
MAIN_PATH = '/path/to/VoLFDS/project/'
VERSION_PATH = f'{MAIN_PATH}versions/'
SEQUENTIALIZATIONS_PATH = f'{MAIN_PATH}sequentializations/'
TMP_PATH = f'{MAIN_PATH}tmp/'
OUTPUT_PATH = f'{MAIN_PATH}outputs/'

NO_ATOMIC_VERSION_PATH = f'{MAIN_PATH}no_atomic_versions/'
NO_ATOMIC_SEQUENTIALIZATIONS_PATH = f'{MAIN_PATH}no_atomic_sequentializations/'
NO_ATOMIC_TMP_PATH = f'{MAIN_PATH}no_atomic_tmp/'
NO_ATOMIC_OUTPUT_PATH = f'{MAIN_PATH}no_atomic_outputs/'

# Telegram Message
TELEGRAM_MESSAGE = 'SS Script - Done'

# Analysis Parameters
N_OBJECT_BITS = 12
N_UNWIND = 8
N_ROUNDS = 3

# Analysis Limits
MAX_OBJECT_BITS = 15

# File Parameters
FILE_NAME = 'atomic_aio'
FILE_EXTENSION = 'c'
STUB_FILE_EXTENSION = 'stub'

# Telegram Parameters
TL_API_KEY = 'api_key'
TL_CHAT_ID = 'chat_id'