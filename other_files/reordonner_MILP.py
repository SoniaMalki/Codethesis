import re


def reorder_constraints(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    minimize_section = re.search(
        r'MINIMIZE\n(.*?)\nSUBJECT TO', content, re.DOTALL).group(1)
    subject_to_section = re.search(
        r'SUBJECT TO\n(.*?)\nVARIABLES', content, re.DOTALL).group(1)
    variables_section = re.search(
        r'VARIABLES\n(.*)', content, re.DOTALL).group(1)

    constraints = re.findall(r'_(.*?): (.*?)\n', subject_to_section, re.DOTALL)

    constraints.sort(key=lambda x: x[1])

    reordered_subject_to_section = 'SUBJECT TO\n'
    for i, (name, constraint) in enumerate(constraints, start=1):
        reordered_subject_to_section += f'_C{i}: {constraint}\n'

    reordered_content = f'MINIMIZE\n{minimize_section}\n{reordered_subject_to_section}\nVARIABLES\n{variables_section}'
    return reordered_content


def main():

    file1_path = 'prob1.txt'
    file2_path = 'prob2.txt'

    reordered_file1 = reorder_constraints(file1_path)
    reordered_file2 = reorder_constraints(file2_path)

    with open(f'reordered_{file1_path}', 'w') as f:
        f.write(reordered_file1)

    with open(f'reordered_{file2_path}.txt', 'w') as f:
        f.write(reordered_file2)

    print("Les fichiers réordonnés ont été enregistrés.")


if __name__ == '__main__':
    main()
