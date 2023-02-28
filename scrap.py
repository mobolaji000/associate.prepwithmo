

requirements_venv_file = open('requirements_venv.txt', 'r')
requirements_venv_list = requirements_venv_file.readlines()
requirements_venv_file.close()

requirements_file = open('requirements.txt', 'r')
requirements_list = requirements_file.readlines()
requirements_file.close()

merged_requirements_file = open('merged_requirements.txt', 'a')
# merged_requirements_list = merged_requirements_file.readlines()
# merged_requirements_file.close()

found = False
for requirements_line in requirements_list:
    for requirements_venv_line in requirements_venv_list:
        if requirements_venv_line.lower().startswith(requirements_line.lower().split('==')[0]):
            merged_requirements_file.write(requirements_venv_line)
            found = True
            break
    if not found:
        merged_requirements_file.write(requirements_line)
    found = False


