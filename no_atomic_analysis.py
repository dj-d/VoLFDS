import os
import re

import constant
from utility import telegram_notification, generate_instance, run_cbmc, get_solution, move, create_folder, purge_folder

def prepare_folder_env():
    """
    Create the folders needed to run the tool.
    """
    
    if not os.path.exists(path=constant.NO_ATOMIC_VERSION_PATH):
        print('Create no_atomic_versions folder')
        create_folder(folder_path=constant.NO_ATOMIC_VERSION_PATH)
    
    if not os.path.exists(path=constant.NO_ATOMIC_SEQUENTIALIZATIONS_PATH):
        print('Create no_atomic_sequentializations folder')
        create_folder(folder_path=constant.NO_ATOMIC_SEQUENTIALIZATIONS_PATH)
    
    if not os.path.exists(path=constant.NO_ATOMIC_OUTPUT_PATH):
        print('Create no_atomic_outputs folder')
        create_folder(folder_path=constant.NO_ATOMIC_OUTPUT_PATH)
    
    if not os.path.exists(path=constant.NO_ATOMIC_TMP_PATH):
        print('Create no_atomic_tmp folder')
        create_folder(folder_path=constant.NO_ATOMIC_TMP_PATH)

def clean_folders():
    """
    Clean the folder.
    """

    purge_folder(folder_path=constant.NO_ATOMIC_VERSION_PATH)
    purge_folder(folder_path=constant.NO_ATOMIC_SEQUENTIALIZATIONS_PATH)
    purge_folder(folder_path=constant.NO_ATOMIC_OUTPUT_PATH)
    purge_folder(folder_path=constant.NO_ATOMIC_TMP_PATH)

def get_name_last_file(dir_path: str) -> str:
    """
    Get the name of the last file in the folder.
    """

    files = os.listdir(dir_path)
    paths = [os.path.join(dir_path, basename) for basename in files]

    paths.sort(key=lambda f: int(re.sub('\D', '', f)))

    return paths[-1].split('/')[-1]

def remove_atomic(file_name: str):
    """
    Remove the atomic from the file.
    """

    _file = open(f'{constant.VERSION_PATH}{file_name}', 'r')
    model = _file.read()
    _file.close()

    file_name = f'no_{file_name}'

    _file = open(f'{constant.NO_ATOMIC_VERSION_PATH}{file_name}', 'w')

    model = model.replace('__VERIFIER_atomic_enq', '_enq')
    model = model.replace('__VERIFIER_atomic_deq', '_deq')
    
    _file.write(model)
    _file.close()

    return file_name


if __name__ == '__main__':
    clean_folders()

    prepare_folder_env()

    file_name = get_name_last_file(dir_path=constant.VERSION_PATH)

    no_atomic_file_name = remove_atomic(file_name=file_name)

    output, error = generate_instance(
            tool_path=constant.LAZY_CSEQ_PATH,
            file_path=f'{constant.NO_ATOMIC_VERSION_PATH}{no_atomic_file_name}',
            unwind=constant.N_UNWIND, 
            rounds=constant.N_ROUNDS
            )

    print(error)

    print(f'Move {no_atomic_file_name} to {constant.NO_ATOMIC_SEQUENTIALIZATIONS_PATH}')
    
    os.chdir(path=constant.NO_ATOMIC_VERSION_PATH)

    move(
        _from=f'_cs_{no_atomic_file_name}', 
        _to=f'{constant.NO_ATOMIC_SEQUENTIALIZATIONS_PATH}_cs_{no_atomic_file_name}'
        )

    print(f'Move .json.tmp to {constant.NO_ATOMIC_TMP_PATH}')

    move(
        _from=f'{constant.NO_ATOMIC_VERSION_PATH}*.json.tmp', 
        _to=f'{constant.NO_ATOMIC_TMP_PATH}.'
        )

    output, error = run_cbmc(
            tool_path=constant.CBMC_PATH,
            file_path=f'{constant.NO_ATOMIC_SEQUENTIALIZATIONS_PATH}_cs_{no_atomic_file_name}',
            unwind=constant.N_UNWIND,
            object_bits=constant.N_OBJECT_BITS
            )
    
    print(error)

    with(open(f'{constant.NO_ATOMIC_OUTPUT_PATH}_cs_{no_atomic_file_name}.log', 'w')) as f:
        f.write(output)

    print(get_solution(file_path=f'{constant.NO_ATOMIC_OUTPUT_PATH}_cs_{no_atomic_file_name}.log'))

    telegram_notification(message='SS - No_atomic finished')
