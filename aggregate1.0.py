import os
import re

os.chdir('./1')

atomic_coordinates = []
atomic_sorts = []
number_of_atoms = []
magnetic_properties = []

def read_file(file_name):
    file_socket = open(file_name, 'r')
    data = file_socket.read()
    file_socket.close()
    return data


def get_atomic_properties():
    split_poscar = poscar.rstrip().split('\n')[7:]
    # for line in split_poscar:
    #     if len(line.split()) > 2:
    #         atomic_coordinates = split_poscar[split_poscar.index(line):]
    #         break
    # print atomic_coordinates
    # print split_poscar
    for atom in split_poscar:
        atom = atom.rstrip()
        if not(atom[-4:-2] in atomic_sorts):
            atomic_sorts.append(atom[-4:-2])
    poscar_string = '\n'.join(split_poscar)
    for sort in atomic_sorts:
        number_of_atoms.append(poscar_string.count(sort))
    for line in split_poscar:
        split_line = line.split()
        atomic_coordinates.append({'x': split_line[0], 'y': split_line[1], 'z': split_line[2], 'sort': split_line[3][:-2]})
    return


def get_magnetic_properties():
    magnetic_part = outcar[outcar.rfind('magnetization (x)')+20:outcar.rfind('total amount of memory used by VASP on root node')].rstrip()
    split_magnetic_part = magnetic_part.split('\n')
    total_magnetic_properties = split_magnetic_part[-1].rstrip().split()
    total_magnetization = {'s': total_magnetic_properties[1], 'p': total_magnetic_properties[2], 'd': total_magnetic_properties[3], 'magmom': total_magnetic_properties[4]}
    i = 0
    for atom in split_magnetic_part[2:-2]:
        atom = atom.rstrip().split()
        magnetic_properties.append({'sort': atomic_coordinates[i]['sort'], 's': atom[1], 'p': atom[2], 'd': atom[3], 'magmom': atom[4]})
        i += 1
    return total_magnetization


def get_energy():
    energy = outcar[outcar.rfind('free  energy   TOTEN  =')+30:outcar.rfind(' eV')].rstrip()
    return float(energy)


def get_volume():
    volume = outcar[outcar.rfind('volume of cell :')+23:outcar.rfind('direct lattice vectors')].rstrip()
    return float(volume)


def issue_results():
    sys_name = ''
    number_of_each_sort = []
    for i in range(len(atomic_sorts)):
        number_of_each_sort.append({'sort': atomic_sorts[i], 'number': number_of_atoms[i]})

    for sort in number_of_each_sort:
        sys_name += sort['sort'] + str(sort['number'])

    total_number_of_atoms = 0
    for atom in number_of_atoms:
        total_number_of_atoms += int(atom)

    concentration_of_first_sort = int(number_of_atoms[0]) / total_number_of_atoms

    mag_tot = total_magnetization['magmom']

    magmom_by_sorts = []
    avg_magmom_by_sorts = []
    for sort in atomic_sorts:
        magmom = 0
        n = 0
        for atom in magnetic_properties:
            if atom['sort'] == sort:
                magmom += float(atom['magmom'])
                n += 1
        magmom_by_sorts.append({'sort': sort, 'magmom': magmom})
        avg_magmom_by_sorts.append({'sort': sort, 'magmom': magmom / n})

    abs_magmom_by_sorts = []
    avg_abs_magmom_by_sorts = []
    for sort in atomic_sorts:
        magmom = 0
        n = 0
        for atom in magnetic_properties:
            if atom['sort'] == sort:
                magmom += abs(float(atom['magmom']))
                n += 1
        abs_magmom_by_sorts.append({'sort': sort, 'magmom': magmom})
        avg_abs_magmom_by_sorts.append({'sort': sort, 'magmom': magmom / n})

    volume_per_atom = volume / total_number_of_atoms

poscar = read_file('POSCAR')
outcar = read_file('OUTCAR')

get_atomic_properties()
total_magnetization = get_magnetic_properties()
volume = get_volume()
energy = get_energy()

issue_results()