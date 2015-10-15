#!/usr/bin/env python3

import sys
import json
import ntpath
import os
import os.path
from lxml import etree

# Config File Name
config_fname = "config.json"

# App Name
app_name = sys.argv[0]

# Errors Msg
ErrMsgConf = "Erreur avec le fichier de configuration."
ErrMsgParse = "Une erreur est survenu pendant le parsing."
ErrNotFound = " n'a pas ete trouve !"
ErrSplittFailed = "ERREUR : Une erreur est survenue lors du partitionnement des fichiers osm. [FIN]"
ErrMsgListFile = "Une erreur est survenuem, aucun fichier partitionne trouve."

# Files format format
osm_extension = ".osm"
osm_gz_extension = ".osm.gz"
prefix_output = "light_"

# Messages
MsgDelNodes = "Supression des noeuds non utilises (peut prendre quelque minutes)..."
MsgDelMember = "Supression des membres non utilises..."
MsgDelRelation = "Supression des relations non utilises..."
MsgGetNodes = "Recuperation des noeuds... "
MsgAskConf = "Voulez vous lancer le choix des options ? (o/n default : n) : "
MsgAskConfFName = "Quelle configuration souhaitez-vous lancer ? "

# Xml tag name
t_tag = "tag"
t_bounds = "bounds"
t_node = "node"
t_nd = "nd"
t_member = "member"
t_way = "way"
t_relation = "relation"

# Tag attributes
t_attr_key = "k"
t_attr_value = "v"

# Splitter Options
s_max_nodes = 100000
s_limit_memory = "256m"  # Default JVM /!\

# Important Files Path
path_areas_list = "./splitter/res/areas.list"
path_split_res = "./splitter/res/"


def export_osm(tree, fname):
    fout = get_fout_name(fname)
    print("Export to \"" + fout + "\".")

    fo = open(fout, "wb")
    fo.write(etree.tostring(tree.getroot()))
    fo.close()
    return fout


def del_all(tree, expr):
    for elem in tree.xpath(expr):
        elem.getparent().remove(elem)
    return tree


# Check si le tag est dans la conf
def tag_is_needed(tag, cfg):
    if t_attr_key in tag.attrib:
        if t_attr_value in tag.attrib:
            key = tag.xpath(".//@" + t_attr_key)
            key = "" if len(key) == 0 else key[0]
            value = tag.xpath(".//@" + t_attr_value)
            value = "" if len(value) == 0 else value[0]
            # Check avec une valeur de type "valeur=qqchse"
            if "=" in value:
                tmp = value.split("=", 1)
                if len(tmp) > 0:
                    value = tmp[0]
            if t_tag in cfg:
                if key in cfg[t_tag]:
                    if "*" in cfg[t_tag][key]:
                        return True
                    if value in cfg[t_tag][key]:
                        return True
    return False


# Check si le tag est un tag de type "name"
def check_tag_is_name(tag):
    if t_attr_key in tag.attrib:
        key = tag.xpath(".//@" + t_attr_key)
        key = "" if len(key) == 0 else key[0]
        if key == "name":
            return True
    return False


# Check si un way contient un tag needed
# Supprimme les tags qui ne sont pas dans le fichier de conf
def check_way_needed(way, cfg):
    tags = way.xpath(".//" + t_tag)

    way.set("version", "1")
    way.set("timestamp", "1-04-13T13:23:55Z")
    way.set("changeset", "1")
    way.set("uid", "1")
    way.set("user", "W")

    for tag in tags:
        if not tag_is_needed(tag, cfg):
            tag.getparent().remove(tag)

    tags = way.xpath(".//" + t_tag)
    if len(tags) == 0:
        return False
    if len(tags) == 1:
        if check_tag_is_name(tags[0]):
            # est un name ratache a rien -> non important
            return False
    return True


# Recupere les noeuds necessaires pour les WAY
def get_needed_nodes_way(tree, cfg):
    print(MsgGetNodes)
    nodes = []

    ways = tree.xpath("//" + t_way)

    for w in ways:
        if not check_way_needed(w, cfg):
            w.getparent().remove(w)

    ways = tree.xpath("//" + t_way)

    for w in ways:
        refs = w.xpath(".//" + t_nd + "/@ref")
        for ref in refs:
            if not ref in nodes:
                nodes.append(ref)
    return nodes


# Check si le node contient des tags importants
def check_node_important(node, cfg):
    tags = node.xpath(".//" + t_tag)

    for tag in tags:
        if not tag_is_needed(tag, cfg):
            tag.getparent().remove(tag)

    tags = node.xpath(".//" + t_tag)

    if len(tags) > 0:
        if len(tags) == 1:
            if check_tag_is_name(tags[0]):
                # est un name ratache a rien -> non important
                return False
        # est important
        return True
    # est a supprimmer
    return False


# Supprimmer tous les nodes non utilises
def del_node_exclude(tree, nodes_list, cfg):
    print(MsgDelNodes)
    nodes = tree.xpath("//" + t_node)

    for node in nodes:
        nid = node.xpath(".//@id")
        nid = "" if len(nid) == 0 else nid[0]
        node.set("version", "1")
        node.set("timestamp", "1-04-13T13:23:55Z")
        node.set("changeset", "1")
        node.set("uid", "1")
        node.set("user", "W")
        if not nid in nodes_list:
            if not check_node_important(node, cfg):
                node.getparent().remove(node)


def parse_osm(fname, cfg):
    tree = etree.parse(fname)
    if cfg is False:
        print(ErrMsgConf)
        return False

    minlat = tree.xpath("//" + t_bounds + "/@minlat")
    minlat = "" if len(minlat) == 0 else minlat[0]
    maxlat = tree.xpath("//" + t_bounds + "/@maxlat")
    maxlat = "" if len(maxlat) == 0 else maxlat[0]
    minlon = tree.xpath("//" + t_bounds + "/@minlon")
    minlon = "" if len(minlon) == 0 else minlon[0]
    maxlon = tree.xpath("//" + t_bounds + "/@maxlon")
    maxlon = "" if len(maxlon) == 0 else maxlon[0]

    # Liste des noeuds a ne pas supprimer
    n_needed = []
    n_needed.extend(get_needed_nodes_way(tree, cfg))

    osm = tree.xpath("//osm")
    if len(osm) > 0:
        osm[0].set("version", "0.6")
        osm[0].set("timestamp", "2015-10-02T21:23:01Z")

    print(MsgDelMember)
    del_all(tree, t_member)
    print(MsgDelRelation)
    del_all(tree, t_relation)
    del_node_exclude(tree, n_needed, cfg)

    print("===[END]===")

    if len(minlat) == 0:
        print("minlat " + ErrNotFound)
        export_osm(tree, fname)
        return False
    if len(maxlat) == 0:
        print("maxlat " + ErrNotFound)
        export_osm(tree, fname)
        return False
    if len(minlon) == 0:
        print("minlon " + ErrNotFound)
        export_osm(tree, fname)
        return False
    if len(maxlon) == 0:
        print("maxlon " + ErrNotFound)
        export_osm(tree, fname)
        return False

    print("Latitude Min: " + minlat + ", Max :" + maxlat)
    print("Longitude Min: " + minlon + ", Max :" + maxlon)
    fout = export_osm(tree, fname)
    fout_name =fout[:-3]
    fout_name += 'map'
    size = fout_name.rfind('/')
    if size != -1:
        fout_name = fout_name[size + 1:]
    print(fout_name)
    os.system("cd converter/bin && ./osmosis --rx file=../../" + fout +
              " --mapfile-writer file=../../map_file/" + fout_name + " bbox=" + minlat + "," + minlon + "," + maxlat + "," + maxlon)
    return True


def check_if_fexist(fname):
    if not os.path.isfile(fname):
        return 1
    if not os.path.isfile(config_fname):
        return 2
    return 0


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


# Genere le nom de fichier de sortie
def get_fout_name(fname):
    i = 1

    filename = path_leaf(fname)
    res = fname.replace(filename, str(prefix_output + filename))
    tmp = res
    while os.path.isfile(tmp):
        tmp = fname.replace(filename, str(
            prefix_output + filename + "_" + str(i)).replace(osm_extension, ""))
        tmp = tmp + osm_extension
        if not os.path.isfile(tmp):
            return tmp
        i += 1
        pass
    return tmp


def ask_for_conf_fname():
    global config_fname
    sys.stdout.write(MsgAskConfFName)
    sys.stdout.write("(default: \"" + config_fname + "\") : ")
    res = raw_input()
    if len(res) == 0:
        return True
    config_fname = res


def ask_for_conf():
    sys.stdout.write(MsgAskConf)
    res = raw_input()
    if len(res) == 0 or res == "n":
        ask_for_conf_fname()
        return True
    if res == "o":
        os.system("./generatorConf.py")
        ask_for_conf_fname()
    else:
        ask_for_conf()


def get_list_files(fname):
    if not os.path.isfile(path_areas_list):
        return False
    flist = []
    filename = path_leaf(fname)
    prefix = filename.replace(osm_extension, "") + "_"
    with open(path_areas_list) as f:
        content = f.read()
        content = content.split("\n")
        for line in content:
            line = line.strip()
            if len(line) > 0:
                if line[0] != "#":
                    line = line.split(":")
                    if len(line) > 0:
                        flist.append(line[0] + osm_extension)
    print(str(len(flist)) + " fichiers generes.")
    for fl in flist:
        print("Extraction de \"" +
              fl.replace(osm_extension, osm_gz_extension) + "\"...")
        ret = os.system("cd " + path_split_res + "; mv " + fl.replace(osm_extension, osm_gz_extension) + " " +
                        prefix + fl.replace(osm_extension, osm_gz_extension) +
                        "; gunzip " + prefix +
                        fl.replace(osm_extension, osm_gz_extension))
        if ret != 0:
            return False
        fl = prefix + fl.replace(osm_gz_extension, osm_extension)
        if os.path.isfile(path_split_res + fl):
            print("Fichier \"" + fl + "\" genere.")
    res_list = []
    for fl in flist:
        fl = prefix + fl.replace(osm_gz_extension, osm_extension)
        res_list.append(fl)
    return res_list


def main():
    if len(sys.argv) < 2:
        print("Usage: ./" + sys.argv[0] + " [OSM FILE]")
        return False
    fname = sys.argv[1]
    e = check_if_fexist(sys.argv[1])
    ask_for_conf()
    if e != 0:
        print(app_name + " : Erreur, le fichier \"" +
              (fname if e == 1 else config_fname) +
              "\" n'existe pas ou vous n'avez pas les permissions requises.")
        return False
    cfg = False
    with open(config_fname) as f:
        cfg = json.load(f)
    print(app_name + " : Parsing du fichier \"" + fname + "\"...")

    ret = os.system("cd splitter; java " +
                    " -jar splitter.jar --max-nodes=" + str(s_max_nodes) +
                    " --output=xml --output-dir=./res ../" + fname)
    if ret != 0:
        print(ErrSplittFailed)
        return False

    f_list = get_list_files(fname)
    if f_list == False or len(f_list) == 0:
        print(ErrMsgListFile)
        return False

    i = 0
    for fl in f_list:
        i += 1
        print("Generation fichier " + fl +
              " (" + str(i) + "/" + str(len(f_list)) + "):")
        if not parse_osm(path_split_res + fl, cfg):
            print(ErrMsgParse)
            return False
    print("==============================[FIN]==============================")
    return True

main()
