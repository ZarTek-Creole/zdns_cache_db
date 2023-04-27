# -*- coding: utf-8 -*-
# Path: zdns_cache_server.py
# Ce fichier fait partie du projet Z-DNS Cache  (ZarTek - DNS Cache)
# Installation:
# - Copier le fichier dns_cache_updater.py dans le répertoire /root/_dns_cache_zartek
# Les packages suivants doivent être installés:
# - pip3 install mysql-connector-python
# - pip3 install dnslib
# - socketserver est un module standard de Python 3
# - logging est un module standard de Python 3
# - yaml est un module standard de Python 3
# Le fichier de configuration zdns_cache_config.yml doit être créé dans le répertoire /root/_dns_cache_zartek

import argparse
import mysql.connector
import socketserver
import logging
import yaml
from dnslib import A, DNSHeader, DNSRecord, QTYPE, RCODE, RR

# Charger les paramètres de configuration à partir du fichier YAML
def load_config(config_file):
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    return config

# Fonction pour gérer les requêtes DNS
class DnsCacheRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0]
        socket = self.request[1]

        # Analyser la requête DNS
        request = DNSRecord.parse(data)

        # Extraire le nom de domaine de la requête
        domain_name = str(request.q.qname).rstrip('.')

        # Log de la requête DNS
        logging.info(f"Received DNS request for {domain_name}")

        # Recherche de l'enregistrement A dans la base de données
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            query = "SELECT ip_address, search_count FROM dns_records WHERE domain_name = %s AND record_type = 'A'"
            logging.info(f"Executing SQL query: {query} with domain_name = {domain_name}")
            cursor.execute(query, (domain_name,))
            result = cursor.fetchone()
            logging.info(f"Query result: {result}")

            if result:
                search_count = result[1] + 1
                cursor.execute("UPDATE dns_records SET search_count = %s WHERE domain_name = %s AND record_type = 'A'",
                               (search_count, domain_name))
                conn.commit()

                response = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
                response.add_answer(RR(f"{domain_name}.", rdata=A(result[0]), ttl=config['dns_server']['ttl']))
                socket.sendto(response.pack(), self.client_address)
                logging.info(f"Resolved {domain_name} to {result[0]}")

            else:
                response = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, rcode=RCODE.NXDOMAIN), q=request.q)
                socket.sendto(response.pack(), self.client_address)
                logging.info(f"Unable to resolve {domain_name}")

        except Exception as e:
            response = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, rcode=RCODE.SERVFAIL), q=request.q)
            socket.sendto(response.pack(), self.client_address)
            logging.error(f"Failed to resolve {domain_name}: {e}")

        finally:
            # Fermer la connexion à la base de données
            if cursor:
                cursor.close()
            if conn:
                conn.close()


# Fonction principale
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ZarTek - DNS Cache Updater")
    parser.add_argument("-c", "--config", help="Path to the configuration file", default="zdns_cache_config.yml")
    args = parser.parse_args()

    config = load_config(args.config)

    db_config = config["db_settings"]
    logging.basicConfig(level=config['logging']['level'], format=config['logging']['format'])

    server_address = (config["dns_server"]["host"], config["dns_server"]["port"])
    server = socketserver.UDPServer(server_address, DnsCacheRequestHandler)
    logging.info(f"Starting DNS server on {server_address[0]}:{server_address[1]}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Shutting down DNS server")
        server.shutdown()
        server.server_close()
