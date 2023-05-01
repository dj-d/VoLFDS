import os

import constant
from utility import telegram_notification, generate_instance, run_cbmc, get_solution, move, copy, create_folder, purge_folder

def prepare_folder_env():
    """
    Create the folders needed to run the tool.
    """
    
    if not os.path.exists(path=constant.VERSION_PATH):
        print('Create versions folder')
        create_folder(folder_path=constant.VERSION_PATH)
    
    if not os.path.exists(path=constant.SEQUENTIALIZATIONS_PATH):
        print('Create sequentializations folder')
        create_folder(folder_path=constant.SEQUENTIALIZATIONS_PATH)
    
    if not os.path.exists(path=constant.OUTPUT_PATH):
        print('Create outputs folder')
        create_folder(folder_path=constant.OUTPUT_PATH)
    
    if not os.path.exists(path=constant.TMP_PATH):
        print('Create tmp folder')
        create_folder(folder_path=constant.TMP_PATH)
    
def clean_folders():
    """
    Clean the folders needed to run the tool.
    """

    purge_folder(folder_path=constant.VERSION_PATH)
    purge_folder(folder_path=constant.SEQUENTIALIZATIONS_PATH)
    purge_folder(folder_path=constant.OUTPUT_PATH)
    purge_folder(folder_path=constant.TMP_PATH)

def get_assert(_solutions: list):
    """
    Create the assert to be added to the next file.

    :param _solutions: The solutions found by the tool.

    :return: The assert to be added to the next file.
    """

    _assert = ''
    _array = list()

    for i in range(len(_solutions)):
        _array.append(f'var_to_get[{i}] == {_solutions[i]}')

    _assert = f'__VERIFIER_assume(!({" && ".join(_array)}));'

    print(f'Assert: {_assert}')

    return _assert

def append_assert(file_name: str, cs_assert: str):
    """
    Append the assert to the file.

    :param file_name: The name of the file to append the assert.
    :param cs_assert: The assert to append.

    :return: None
    """

    _file = open(f'{constant.VERSION_PATH}{file_name}', 'r')
    model = _file.read()
    _file.close()

    _file = open(f'{constant.VERSION_PATH}{file_name}', 'w')
    model = model.replace('//CS_ASSUME', f'{cs_assert}\n\t//CS_ASSUME')
    
    _file.write(model)
    _file.close()


if __name__ == '__main__':
    if constant.START_INDEX == 0:
        print('Clean folders')
        clean_folders()
    
        print('\n')

        print('Prepare folders')
        prepare_folder_env()

    index = constant.START_INDEX

    if index == 0:
        solution = list()
    else:
        solution = get_solution(file_path=f'{constant.OUTPUT_PATH}_cs_{constant.FILE_NAME}_{index - 1}.log')
        
    while True:
        print('\n')
        
        if index == 0:
            os.chdir(path=constant.MAIN_PATH)

            copy(
                _from=f'{constant.FILE_NAME}.{constant.STUB_FILE_EXTENSION}',
                _to=f'versions/{constant.FILE_NAME}_{index}.{constant.FILE_EXTENSION}'
            )
        else:
            os.chdir(constant.VERSION_PATH)

            copy(
                _from=f'{constant.FILE_NAME}_{index - 1}.{constant.FILE_EXTENSION}',
                _to=f'{constant.FILE_NAME}_{index}.{constant.FILE_EXTENSION}'
            )

            print(f'Solution: {solution}')

            append_assert(
                file_name=f'{constant.FILE_NAME}_{index}.{constant.FILE_EXTENSION}', 
                cs_assert=get_assert(_solutions=solution)
            )

        print(f'Instance generation for: {constant.FILE_NAME}_{index}.{constant.FILE_EXTENSION}')

        output, error = generate_instance(
            tool_path=constant.LAZY_CSEQ_PATH,
            file_path=f'{constant.VERSION_PATH}{constant.FILE_NAME}_{index}.{constant.FILE_EXTENSION}', 
            unwind=constant.N_UNWIND, 
            rounds=constant.N_ROUNDS
        )

        print(f'Move {constant.FILE_NAME}_{index}.{constant.FILE_EXTENSION} to {constant.SEQUENTIALIZATIONS_PATH}')
        os.chdir(constant.VERSION_PATH)

        move(
            _from=f'_cs_{constant.FILE_NAME}_{index}.{constant.FILE_EXTENSION}', 
            _to=f'{constant.SEQUENTIALIZATIONS_PATH}_cs_{constant.FILE_NAME}_{index}.{constant.FILE_EXTENSION}'
            )

        if constant.MSG_SUC_SEQUENTIALIZATION not in output:
            print('No sequenzialization')
            print(output)

            exit(1)
        else:
            print(f'Move .json.tmp to {constant.TMP_PATH}')

            move(
                _from=f'{constant.VERSION_PATH}*.json.tmp', 
                _to=f'{constant.TMP_PATH}.'
                )

            obj_bits = constant.N_OBJECT_BITS
            while True:
                print(f'CBMC analysis for: {constant.FILE_NAME}_{index}.{constant.FILE_EXTENSION} with {obj_bits} object bits')

                output, error = run_cbmc(
                    tool_path=constant.CBMC_PATH,
                    file_path=f'{constant.SEQUENTIALIZATIONS_PATH}_cs_{constant.FILE_NAME}_{index}.{constant.FILE_EXTENSION}', 
                    unwind=constant.N_UNWIND, 
                    object_bits=obj_bits
                )

                if len(error) > 0:
                    print(f'\ncbmc_error: {error}')

                if constant.MSG_LOW_OBJECT_BITS in error and obj_bits < constant.MAX_OBJECT_BITS:
                    print('Too many addressed objects')
                    
                    obj_bits += 1
                elif obj_bits == constant.MAX_OBJECT_BITS:
                    print('Object bits limit reached')

                    exit(2)
                elif constant.MSG_CONVERSION_ERROR in error:
                    print('Conversion error')

                    exit(3)
                else:
                    print(f'Save output of: _cs_{constant.FILE_NAME}_{index}.{constant.FILE_EXTENSION}')

                    with(open(f'{constant.OUTPUT_PATH}_cs_{constant.FILE_NAME}_{index}.log', 'w')) as f:
                        f.write(output)

                    break

        solution = get_solution(file_path=f'{constant.OUTPUT_PATH}_cs_{constant.FILE_NAME}_{index}.log')

        print(f'Solution: {solution}')

        index += 1

        telegram_notification(constant.TELEGRAM_MESSAGE)

        if len(solution) == 0:
            print(f'Solution: {solution}')

            exit(0)