import os
import subprocess
import constant


def telegram_notification(message: str):
    """
    Send a message to a Telegram chat using the Telegram API.

    :param message: The message to send.

    :return: None
    """
    
    API_KEY = constant.TL_API_KEY
    CHAT_ID = constant.TL_CHAT_ID
    _message = '%20'.join(message.split())

    cmd = f'curl -s "https://api.telegram.org/bot{API_KEY}/sendMessage?chat_id={CHAT_ID}&text={_message}"'

    subprocess.call(cmd, shell=True)

def generate_instance(tool_path: str, file_path: str, unwind: int, rounds: int) -> tuple:
    """
    Generate the instance to be solved by cbmc with lazycseq.

    :param tool_path: The path of tool 'lazycseq'.
    :param file_path: The path of the file to be solved.
    :param unwind: The number of times the loop must be unwinded.
    :param rounds: The number of rounds to be executed.

    :return: The stdout and the stderr of the execution.
    """

    os.chdir(tool_path)

    cmd = f'\
        ./lazycseq.py \
            -i {file_path} \
            --unwind {unwind} \
            --rounds {rounds} \
            --seq \
        '

    process = subprocess.Popen(
        cmd.split(), 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
        )

    process.wait()

    _output, _error = process.communicate()

    return _output.decode('utf-8'), _error.decode('utf-8')

def run_cbmc(tool_path: str, file_path: str, unwind: int, object_bits: int) -> tuple:
    """
    Run cbmc on the instance generated by lazycseq.

    :param file_path: The path of the file to be solved.
    :param unwind: The number of times the loop must be unwinded.
    :param object_bits: The number of bits of the object.

    :return: The stdout and the stderr of the execution.
    """

    os.chdir(tool_path)

    cmd = f'\
        ./cbmc \
            {file_path} \
            --unwind {unwind} \
            --stop-on-fail \
            --object-bits {object_bits} \
            --trace \
        '

    process = subprocess.Popen(
        cmd.split(), 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
        )
    
    _output, _error = process.communicate()

    return _output.decode('utf-8'), _error.decode('utf-8')

def get_solution(file_path: str) -> list:
    """
    Get the solution from the log file of cbmc (we find variable 'var_to_get').

    :param file_path: The path of the file to be solved.

    :return: The solution
    """

    _solution = list()

    try:
        log_file = open(file_path, 'r')
        lines = log_file.readlines()
        log_file.close()
    except IOError as e:
        print(f'File {file_path} not found')
        print(f'Error: {e}')

    if lines[-2] == 'VERIFICATION SUCCESSFUL':
        print('VERIFICATION SUCCESSFUL')
        
        return []

    for line in lines:
        if 'var_to_get' in line:
            line = line.replace(' ', '')
            line = line.replace('l', '')
            line = line.replace('var_to_get[', '')
            line = line.replace(']', '')
            line = line.replace(line[line.find('('):], '')
            line = line.split('=')

            try:
                index = int(line[0])
                value = int(line[1])
            except ValueError:
                index = -1
                value = -1

            if len(_solution) < index + 1:
                _solution.append(value)
            else:
                _solution[index] = value

    return _solution

def move(_from: str, _to: str) -> None:
    """
    Move a file from a path to another.

    :param _from: The path of the file to move.
    :param _to: The path where to move the file.

    :return: None
    """

    os.system(f'mv {_from} {_to}')

def copy(_from: str, _to: str) -> None:
    """
    Copy a file from a path to another.

    :param _from: The path of the file to copy.
    :param _to: The path where to copy the file.

    :return: None
    """

    os.system(f'cp {_from} {_to}')

def create_folder(folder_path: str) -> None:
    """
    Create a folder.

    :param folder_path: The path of the folder to create.

    :return: None
    """

    os.mkdir(folder_path)

def purge_folder(folder_path: str) -> None:
    """
    Delete all the files in a folder.

    :param folder_path: The path of the folder to purge.

    :return: None
    """

    os.system(f'rm -rf {folder_path}/*')