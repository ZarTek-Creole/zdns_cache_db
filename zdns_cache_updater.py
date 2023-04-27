# -*- coding: utf-8 -*-
# Installation:
# - Copier le fichier dns_cache_updater.py dans le répertoire /root/_dns_cache_zartek
# Les packages suivants doivent être installés:
# - pip3 install mysql-connector-python
# Les crontabs suivants doivent être configurés:
# - 0 9,21 * * * python3 /root/_dns_cache_zartek/dns_cache_updater.py

import os
import subprocess
import re
import mysql.connector

# Configuration de la base de données MySQL
db_config = {
    'user': 'dns_cache_user',
    'password': 'aBcDeFgHiJkL123',
    'port': 10100,
    'host': 'localhost',
    'database': 'dns_cache_db'
}

# Exécuter la commande pour extraire les données du cache
subprocess.run(['rndc', 'dumpdb', '-cache'])

# Lire le fichier de sortie
with open('/var/cache/bind/named_dump.db', 'r') as f:
    cache_data = f.read()

# Trouver les enregistrements A et CNAME
a_records = re.findall(r'(\S+)\.\s+\d+\sA\s+(\d+\.\d+\.\d+\.\d+)', cache_data)
cname_records = re.findall(r'(\S+)\.\s+\d+\sCNAME\s+(\S+)\.', cache_data)

# Insérer ou mettre à jour les données dans la base de données MySQL
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

for domain_name, ip_address in a_records:
    # Vérifier si l'enregistrement A existe déjà
    cursor.execute("SELECT id FROM dns_records WHERE domain_name = %s AND record_type = 'A'", (domain_name,))
    result = cursor.fetchone()

    if result:
        # Mettre à jour l'enregistrement A existant
        cursor.execute("UPDATE dns_records SET ip_address = %s, last_updated = NOW() WHERE domain_name = %s AND record_type = 'A'",
                       (ip_address, domain_name))
    else:
        # Insérer un nouvel enregistrement A
        cursor.execute("INSERT INTO dns_records (domain_name, ip_address, record_type) VALUES (%s, %s, 'A')",
                       (domain_name, ip_address))

for domain_name, cname in cname_records:
    # Vérifier si l'enregistrement CNAME existe déjà
    cursor.execute("SELECT id FROM dns_records WHERE domain_name = %s AND record_type = 'CNAME'", (domain_name,))
    result = cursor.fetchone()

    if result:
        # Mettre à jour l'enregistrement CNAME existant
        cursor.execute("UPDATE dns_records SET ip_address = %s, last_updated = NOW() WHERE domain_name = %s AND record_type = 'CNAME'",
                       (cname, domain_name))
    else:
        # Insérer un nouvel enregistrement CNAME
        cursor.execute("INSERT INTO dns_records (domain_name, ip_address, record_type) VALUES (%s, %s, 'CNAME')",
                       (domain_name, cname))

# Recherche d'enregistrements A correspondants pour les enregistrements CNAME
for cname_record in cname_records:
    matching_a_records = [a_record for a_record in a_records if a_record[0] == cname_record[1]]
    if matching_a_records:
        for matching_a_record in matching_a_records:
            cursor.execute("UPDATE dns_records SET target_ip_address = %s WHERE domain_name = %s AND record_type = 'CNAME'",
                           (matching_a_record[1], cname_record[0]))

conn.commit()

# Fermer les connexions à la base de données
cursor.close()
conn.close()
