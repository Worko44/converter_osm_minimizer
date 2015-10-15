REQUIREMENT:

- python2.7.8 (import xml)
- Lire le README.txt dans converter pour le fonctionnement de osmosis (le convertisseur)
- gunzip (pour décompresser un osm.bz2)

________________CONVERTISSEUR OSMOSIS MINIMIZER .osm->.map________________

- aller dans le dossier converter
- chmod +x converter (si les droits d'execution n'existe pas)
- executer ./converter
- si aucune erreur n'apparait, et qu'on obtient bien un fichier test.map dans "/map_file" le convertisseur est ok
- sinon lire le README.txt de converter



EXECUTION:

python OsmMinimizer.py osm_file/example.osm



Le programme procède a plusieurs étapes:
   
	- Demande la configuration du fichier osm réduit et génère un fichier de configuration ou il peut en utiliser un qui a déjà été généré. Cette configuration sert a alléger le fichier osm (exemple.osm) de certaines balises.
	- Découpe le fichier osm de départ (example.osm) en plusieurs sous fichier .osm dans "splitter/res". Cela sert a éviter de surchager la mémoire (pour les gros fichiers par exemple un fichier osm de 100Go).
	- Convertis tous ces sous fichiers en des .osm allégés dans "splitter/res". "light_example_6324000*.osm"
	- Convertis tous ces .osm allégés en des .map dans "map_file"






RESULTATS:

on obtient:
	- splitter/res/example_6324000*.osm			(le fichier example.osm découpé en plusieurs parties)
	- splitter/res/light_example_6324000*.osm		(le fichier léger en fonction de ce qu'on veut enlever du fichier example.osm de départ)
	- map_file/example_6324000*.map				(le fichier convertis en .map de light_example_6324000*.osm)

NETTOYAGE:

./clean

nettoies les fichiers temporaires stocker dans splitter/res
