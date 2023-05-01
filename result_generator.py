import os
import re

def get_data(file_path: str) -> dict:
    data = dict()
    c = True

    try:
        log_file = open(file_path, 'r')
        lines = log_file.readlines()
        log_file.close()
    except IOError as e:
        print(f'File {file_path} not found')
        print(f'Error: {e}')
    
    for line in lines:
        if 'Runtime Symex' in line:
            data['r_symex'] = line.split(':')[1].strip()
        elif 'Runtime Convert SSA' in line:
            data['r_convert_ssa'] = line.split(':')[1].strip()
        elif 'variables' in line and 'clauses' in line:
            line = line.split(',')
            data['variables'] = line[0].replace('variables', '').strip()
            data['clauses'] = line[1].replace('clauses', '').strip()
        elif 'Runtime Solver' in line:
            data['r_solver'] = line.split(':')[1].strip()
        elif 'Runtime decision procedure' in line:
            data['r_decision'] = line.split(':')[1].strip()
            c = False
        else:
            if not c:
                break
    
    data['variables'] = data.pop('variables')
    data['clauses'] = data.pop('clauses')

    data['tot'] = str(float(data['r_symex'].replace('s', '')) + float(data['r_convert_ssa'].replace('s', '')) + float(data['r_solver'].replace('s', '')) + float(data['r_decision'].replace('s', '')))

    return data

def format_table(index: int, data: dict) -> str:
    table = list()

    for value in data.values():
        table.append(f'{value}')

    return f'\#{index} & ' + ' & '.join(table)

def get_files(path: str) -> list:
    files = list()

    for file in os.listdir(path):
        if '.log' in file:
            files.append(file)

    files.sort(key=lambda f: int(re.sub('\D', '', f)))

    return files

if __name__ == '__main__':
    table = list()
    tot = 0.0
    files = get_files('/home/dj-d/Repositories/GitHub/proposal/outputs/')

    for index, file in enumerate(files):
        data = get_data(f'/home/dj-d/Repositories/GitHub/proposal/outputs/{file}')
        table.append(format_table(index + 1, data))
        tot += float(data['tot'])
    
    # print(' \\\\\n'.join(table))

    print(f'Total: {(tot/60)/60}h')
    print(f'Mean: {(tot/60)/len(files)}m')

    # Table for LaTeX
    print('The table to be imported to latex was saved in the table.txt file in the root directory of the project.')
    with open('/home/dj-d/Repositories/GitHub/proposal/table.txt', 'w') as file:
        file.write(' \\\\\n'.join(table))