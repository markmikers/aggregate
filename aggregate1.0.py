import os
import openpyxl
import re

working_directory = os.getcwd()

directories = [x for x in os.listdir(working_directory) if (os.path.isdir(x)) and (x[0] != '.')]


def read_file(file_name):
    file_socket = open(file_name, 'r')
    data = file_socket.read()
    file_socket.close()
    return data


def get_atomic_properties():
    split_poscar = poscar.rstrip().split('\n')[7:]
    for atom in split_poscar:
        atom = atom.rstrip()
        if not(re.sub('[^a-zA-Z]+', '', atom) in atomic_sorts):
            atomic_sorts.append(re.sub('[^a-zA-Z]+', '', atom))
    poscar_string = '\n'.join(split_poscar)
    for sort in atomic_sorts:
        number_of_atoms.append(poscar_string.count(sort))
    for line in split_poscar:
        split_line = line.split()
        split_line[3] = re.sub('[^a-zA-Z]+', '', split_line[3])
        atomic_coordinates.append({'x': split_line[0], 'y': split_line[1], 'z': split_line[2], 'sort': split_line[3]})
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
    energy = outcar[outcar.rfind('free  energy   TOTEN  =')+29:outcar.rfind(' eV')].rstrip()
    return float(energy)


def get_volume():
    volume = outcar[outcar.rfind('volume of cell :')+23:outcar.rfind('direct lattice vectors')].rstrip()
    return float(volume)


def issue_results():
    #define all necessary results
    sys_name = []
    number_of_each_sort = []
    total_number_of_atoms = []
    magmom_by_sorts = []
    avg_magmom_by_sorts = []
    abs_magmom_by_sorts = []
    avg_abs_magmom_by_sorts = []

    def collect_results():
        for i in range(len(atomic_sorts)):
            number_of_each_sort.append({'sort': atomic_sorts[i], 'number': number_of_atoms[i]})
        for sort in number_of_each_sort:
            sys_name.append(sort['sort'] + str(sort['number']))
        sys_name.append('_' + directory)

        for atom in number_of_atoms:
            total_number_of_atoms.append(int(atom))

        for sort in atomic_sorts:
            magmom = 0
            n = 0
            for atom in magnetic_properties:
                if atom['sort'] == sort:
                    # print n
                    magmom += float(atom['magmom'])
                    n += 1
            magmom_by_sorts.append({'sort': sort, 'magmom': magmom})
            avg_magmom_by_sorts.append({'sort': sort, 'magmom': magmom / n})

        #for sort in atomic_sorts:
        #    magmom = 0
        #    n = 0
        #    for atom in magnetic_properties:
        #        if atom['sort'] == sort:
        #            magmom += abs(float(atom['magmom']))
        #            n += 1
        #    abs_magmom_by_sorts.append({'sort': sort, 'magmom': magmom})
        #    avg_abs_magmom_by_sorts.append({'sort': sort, 'magmom': magmom / n})
        return


    def produce_results():
        nat = ''
        for n in number_of_atoms:
            nat += str(n) + '\t'
        mag_avgs = ''
        for i in range(len(magmom_by_sorts)):
            mag_avgs += str(avg_magmom_by_sorts[i]['magmom']) + '\t'
            ### str(magmom_by_sorts[i]['magmom']) + '\t' + str(abs_magmom_by_sorts[i]['magmom']) + '\t' + str(avg_abs_magmom_by_sorts[i]['magmom'])
        line = sys_name + '\t' + str(total_number_of_atoms) + '\t' + nat + str(concentration_of_first_sort) + \
               '\t' + mag_tot + '\t' + str(mag_avg) + '\t' + mag_avgs + str(volume) + '\t' + str(volume_per_atom) + '\t' + \
               str(energy) + '\n' + assumed_mag_struct + '\n'
        return line

    collect_results()
    # easily calculated properties
    total_number_of_atoms = sum(total_number_of_atoms)
    sys_name = ''.join(sys_name)
    concentration_of_first_sort = float(number_of_atoms[0]) / float(total_number_of_atoms)
    mag_tot = total_magnetization['magmom']
    mag_avg = float(total_magnetization['magmom']) / float(total_number_of_atoms)
    volume_per_atom = volume / total_number_of_atoms

    return produce_results()

textfile = 'SysName\tNat\tN1\tN2\tC1\tMagMom\tMM_avg\tMM1avg\tMM2avg\tVolume\tV/at\tEnergy\tAssumedMS\n'
#textfile = 'SysName\tNat\tN1\tN2\tC1\tMagMom\tMM1\tMM1abs\tMM1avg\tMM1avgabs\tMM2\tMM2abs\tMM2avg\tMM2avgabs\tVolume\tV/at\tEnergy\n'


def create_newposcar(): # and assume magnetic structure
    newposcar = poscar.split('\n')[:7] #np
    np_atoms = []
    magmom_sorts = []
    magmom_sort_count = []
    for i in range(len(atomic_coordinates)):
        np_atoms.append([atomic_coordinates[i]['x'], atomic_coordinates[i]['y'], atomic_coordinates[i]['z'],
                         atomic_coordinates[i]['sort'], float(magnetic_properties[i]['magmom'])])
    np_atoms = sorted(np_atoms, key=lambda atom: atom[-1])

    against_z = any(atom[-1] < 0 for atom in np_atoms)
    along_z = any(atom[-1] > 0 for atom in np_atoms)
    assumed_mag_struct = ''
    if (along_z + against_z) == 0:
        assumed_mag_struct = 'NM'
    elif (along_z == 0) or (against_z == 0):
        assumed_mag_struct = 'FM'
    else:
        assumed_mag_struct = 'AFM/FiM'

    minuses = 0
    for atom in np_atoms:
        if not(atom[-1] in magmom_sorts):
            magmom_sorts.append(atom[-1])
            if atom[-1] < 0:
                minuses += 1
    for sort in magmom_sorts:
        count = 0
        for i in np_atoms:
            if i[-1] == sort:
                count += 1
        magmom_sort_count.append(count)
    for i in range(len(magmom_sort_count)):
        magmom_sort_count[i] = str(magmom_sort_count[i])

    magmom_sort_count = ' '.join(magmom_sort_count)
    newposcar[5] = magmom_sort_count

    for i in range(len(np_atoms)):
        np_atoms[i][-1] = str(np_atoms[i][-1])
        np_atoms[i] = ' '.join(np_atoms[i])[::-1].replace(' ', '', 1)[::-1]

    newposcar = newposcar + np_atoms
    newposcar = '\n'.join(newposcar)

    fsock = open('NEWPOSCAR-' + str(len(magmom_sorts)) + '-' + str(minuses) + '-' + str(len(magmom_sorts) - minuses), 'w').write(newposcar)
    return assumed_mag_struct

for directory in directories:
    atomic_coordinates = []
    atomic_sorts = []
    number_of_atoms = []
    magnetic_properties = []

    os.chdir('./' + directory)

    poscar = read_file('POSCAR')
    outcar = read_file('OUTCAR')

    get_atomic_properties()
    total_magnetization = get_magnetic_properties()
    volume = get_volume()
    energy = get_energy()

    assumed_mag_struct = create_newposcar()
    textfile += issue_results()
    os.chdir('../')

fsock = open('aggregated.txt', 'w').write(textfile)

# def produce_excel():
#     return
