# ZarTek - DNS Cache DB / Z-DNS Cache DB

Z-DNS Cache DB est un serveur DNS personnalisé qui stocke les enregistrements DNS dans une base de données MySQL. Il a été créé pour résoudre un problème que l'on peut rencontrer avec les "DNS dynamiques gratuits" qui nécessitent une validation mensuelle. Si le propriétaire oublie ou ne réagit pas à temps, les enregistrements DNS peuvent expirer (TTL), empêchant l'accès au site web ou à l'IP correspondante.

## Avertisemment
Ce code ne respecte pas les standart du protocol DNS. Il a été créé pour un usage personnel et n'est pas destiné à être utilisé en production. Il est fourni tel quel, sans aucune garantie. L'utilisation de ce code est à vos risques et périls.
Le faite de contourner les TTL et de preserver les DNS expiré malgré tout est un mauvaise pratique qui va a contre sens du protocol DNS. Il est fortement déconseillé d'utiliser ce code en production. Alors vive l'opensource et vive le DIY mais pas n'importe comment.

## Comment ça fonctionne ?
Avant d'accéder à un site web ou à un autre protocole en utilisant un nom de domaine, le navigateur ou le client doit résoudre ce nom en une adresse IP. Pour cela, il interroge un serveur DNS qui lui retourne l'adresse IP du serveur ainsi qu'un TTL (Time To Live), qui correspond à la durée de validité de cette information. Si le TTL expire, le client doit interroger de nouveau le serveur DNS pour obtenir une nouvelle adresse IP.

Dans le cas où le propriétaire n'a pas réactivé son DNS dynamique gratuit, les serveurs DNS peuvent indiquer que le nom de domaine n'existe pas, alors que le DNS est toujours valide et que l'IP est en ligne. C'est là que Z-DNS Cache DB intervient. Il stocke les enregistrements DNS dans une base de données MySQL et met automatiquement à jour ceux qui ont été consultés. Si Z-DNS Cache DB est le dernier serveur DNS de votre liste, il retournera toujours l'adresse IP du serveur même si le TTL est expiré.

Z-DNS Cache DB est conçu pour fonctionner avec BIND9, mais peut être utilisé avec d'autres solutions DNS. Il dispose des fonctionnalités suivantes :

 - Stockage en cache des enregistrements DNS dans une base de données MySQL
 - Prise en charge de plusieurs types d'enregistrements DNS (A, AAAA, CNAME, MX, NS, PTR, SOA, SRV, TXT)
 - Mise à jour automatique des enregistrements DNS consultés
- Configuration facile via un fichier YAML

## Prérequis

- Python 3.6 ou ultérieur
- MySQL 5.6 ou ultérieur

## Installation

Clonez ce dépôt GitHub :

```shell
git clone https://github.com/user/z-dns-cache-db.git
cd z-dns-cache-db
```

Installez les dépendances Python :

```shell
pip install -r requirements.txt
```

Créez la base de données et la table en utilisant le fichier `zdns_cache_db_structure.sql` :

```shell
mysql -u <username> -p < zdns_cache_db_structure.sql
```
4. Configurez le serveur en modifiant le fichier `zdns_cache_config.yml` :
- Définissez les paramètres de connexion à la base de données MySQL
- Configurez l'adresse et le port du serveur DNS
- Ajustez les autres paramètres selon vos préférences
5. Exécutez le serveur DNS :

   ```shell
   python3 zdns_cache_server.py
   ```

6. Exécutez le script de mise à jour des enregistrements DNS :
7. ```
   python3 zdns_cache_updater.py
   ```

## Configuration de Z-DNS Cache DB
Renommer le fichier `zdns_cache_config.yml.example` en `zdns_cache_config.yml` et modifier les paramètres de configuration selon vos besoins.

Le fichier `zdns_cache_config.yml` contient les paramètres de configuration du serveur DNS et du script de mise à jour des enregistrements DNS. Vous pouvez ajuster ces paramètres selon vos besoins.

## Configuration de BIND9
Pour utiliser Z-DNS Cache DB avec BIND9, vous devez configurer BIND9 pour qu'il utilise Z-DNS Cache DB comme serveur DNS de cache. Pour ce faire, ajoutez la ligne suivante dans le fichier `named.conf.options` :


```proprieties
options {
	directory "/var/cache/bind";

   recursion yes;
    allow-recursion {
        127.0.0.1;
        116.202.156.128/26;
        172.31.0.0/16;
        172.17.0.0/16;
        192.168.240.0/20;
        192.168.96.0/20;
        172.16.238.0/24;
    };

    forwarders {
        8.8.8.8; 8.8.4.4;
        213.133.98.98; 213.133.99.99; 213.133.100.100;
        208.67.220.220; 208.67.222.222;
        1.1.1.1; 1.0.0.1;
        9.9.9.9; 149.112.112.112;
        156.154.70.1; 156.154.71.1;
        8.26.56.26; 8.20.247.20;
        84.200.69.80; 84.200.70.40;
        199.85.126.10; 199.85.127.10;
        77.88.8.8; 77.88.8.1;
        195.46.39.39; 195.46.39.40;
        9.9.9.10; 149.112.112.10;
        74.82.42.42;
        185.228.168.168; 185.228.169.168;
        156.154.70.22; 156.154.71.22;
    };
};
```
## Contribution

Les contributions sont les bienvenues ! Veuillez soumettre des pull requests pour les améliorations ou les corrections de bugs, ou créez des issues pour discuter des problèmes ou des suggestions.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
