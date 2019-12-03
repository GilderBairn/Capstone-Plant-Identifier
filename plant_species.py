import os
from bs4 import BeautifulSoup
import json


def find_species(xml, directory, structure):
    with open(os.path.join(directory, xml), 'r') as fp:
        bs = BeautifulSoup(fp.read(), features='html.parser')
    label = bs.classid.get_text()
    species = bs.species.get_text()
    genus = bs.genus.get_text()
    family = bs.family.get_text()
    try:
        if structure[label]['Species'] != species:
            print('Oh no! there is a duplicate species!')
    except KeyError:
        structure[label] = {}
        structure[label]['Species'] = species
        structure[label]['Genus'] = genus
        structure[label]['Family'] = family


main_dir = '/media/ben/DATA/plantdata'
dirs = ['test', 'train']
data = {}
counter = 0
for folder in dirs:
    for file in os.listdir(os.path.join(main_dir, folder)):
        if file.endswith('.xml'):
            if counter % 100 == 0:
                print(counter)
            find_species(file, os.path.join(main_dir, folder), data)
            counter += 1
with open('Class_species_mapping.json', 'w') as fp:
    json.dump(data, fp)

