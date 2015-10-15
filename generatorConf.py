#!/usr/bin/env python3

import json
import os.path

with open("./data/data_key.json") as f:
    all_key = json.load(f)
cur_key = 0

def recup_choice(elem, insert, default):
    if (len(default) == 0):
        print(" (o/n) : ", end='')
    else:
        print(" (o/n default : " + default + ") : ", end='')
    rslt = input()
    if (len(default) != 0 and len(rslt) == 0):
        rslt = default
    if (rslt == 'o'):
        if (type(elem) == list):
            elem.append(insert)
    elif (rslt != 'n'):
        print("'o' pour oui, 'n' pour non")
    return (rslt, elem)

def recup_valdefault(tab_sous_key):
    choice_default = 'o'
    if (type(tab_sous_key) == list):
        if (len(tab_sous_key) > 0):
            sous_key = tab_sous_key[0]
            if (len(tab_sous_key) > 1):
                choice_default = tab_sous_key[1]
    else:
        sous_key = tab_sous_key
    return sous_key, choice_default


def parcourt_all_key():
    dic = {}
    
    for key in all_key:
        rslt = ''
        key_list = list(key.keys())
        for elem in key_list:
            if (elem != 'Type'):
                key_fr = elem
                break
        while (rslt != 'o' and rslt != 'n'):
            print("Voulez vous afficher l'élément " + key_fr, end='')
            rslt, dic = recup_choice(dic, '', '')
        if (rslt == 'o'):
            dic_sous_key = key['Type']
            rslt_tab = []
            for sous_key_fr, tab_sous_key in dic_sous_key.items():
                rslt = ""
                sous_key, choice_default = recup_valdefault(tab_sous_key)
                while (rslt != 'o' and rslt != 'n'):
                    print("Voulez vous afficher l'élément " + key_fr + " de type " + sous_key_fr, end='')
                    rslt, rslt_tab = recup_choice(rslt_tab, sous_key, choice_default)
            if (len(rslt_tab) != 0):
                dic[key[key_fr]] = rslt_tab

    return dic

def recup_name_conffile():
    
    rslt = ''
    while (rslt != "o"):
        print("Nom du fichier de config (default config.json) : ", end="")
        name_file_conf = input()
        if (len(name_file_conf) == 0):
            name_file_conf = "config.json"
        if (name_file_conf[-5:] != ".json"):
            name_file_conf += ".json"
        if (os.path.isfile(name_file_conf)):
            print("Le fichier " + name_file_conf + " existe déja voulez vous l'écraser ? ", end='')
            rslt, none = recup_choice(rslt, rslt, 'n')
        else:
            rslt = 'o'
    return name_file_conf


name_file_conf = recup_name_conffile()
print("Suivez les instructions pour creer votre fichier de conf nommé : " + name_file_conf)

config = parcourt_all_key()
final_config = {"tag":config}

with open(name_file_conf, 'w') as outfile:
    json.dump(final_config, outfile)
    print("Votre fichier de config " + name_file_conf + " a bien été créé.")
