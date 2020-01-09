#!/usr/bin/python3

import apt
import shlex
import tarfile
import os, errno
import configparser
import secrets, string
import sys, subprocess
import urllib.request, shutil

def installIfMissing(cmd, packages, apt_cache):
    is_installed = os.system(f"which {shlex.quote(cmd)}")
    if is_installed is not 0:
        for package in packages:
            apt_cache[package].mark_install()
        apt_cache.commit()

def install_dependencies():
    apt_cache = apt.Cache()
    apt_cache.update()
    apt_cache.open()

    packages = {
        "php"  : ["php-fpm", "php-mysql"],
        "mysql": ["mysql-server"],
        "nginx": ["nginx"],
        "pip"  : ["python3-pip"]
    }

    for cmd in packages.keys():
        installIfMissing(cmd, packages[cmd], apt_cache)

    subprocess.check_call([sys.executable, "-m", "pip", "install", "mysql-connector-python"])

def create_nginx_config(domain):

    conf_available = "/etc/nginx/sites-available/wp.conf"
    conf_enabled = "/etc/nginx/sites-enabled/wp.conf"

    with open(f"{os.path.dirname(os.path.realpath(__file__))}/nginx-wp.conf", 'r') as template, open(conf_available, 'w') as conf_file:
        for line in template:
            conf_file.write(line.replace("domain.tld", domain))
    try:
        os.symlink(conf_available, conf_enabled)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(conf_enabled)
            os.symlink(conf_available, conf_enabled)

    os.system("systemctl reload nginx")

def insert_hosts_domain(host_ip, domain):
    with open("/etc/hosts", 'a') as hosts_file:
        hosts_file.write(f"{host_ip}       {domain}\n")

def download_wordpress(wordpress_path):

    wp_tgz = f"{wordpress_path}/latest.tar.gz"

    with urllib.request.urlopen("https://wordpress.org/latest.tar.gz") as response, open(wp_tgz, 'wb') as downloaded_file:
        shutil.copyfileobj(response, downloaded_file)

    f = tarfile.open(wp_tgz, 'r:gz')
    f.extractall(wordpress_path)
    f.close()

    os.remove(wp_tgz)

    for root, dirs, files in os.walk(f"{wordpress_path}/wordpress"):
        shutil.chown(root, "www-data", "www-data")
        for d in dirs:
            shutil.chown(f"{root}/{d}", "www-data", "www-data")
        for f in files:
            shutil.chown(f"{root}/{f}", "www-data", "www-data")

def create_mysql_db(db_user, db_host, password, domain):

    import mysql.connector

    config = configparser.ConfigParser()
    config.read_file(open('/etc/mysql/debian.cnf'))

    db_conn = mysql.connector.connect(
        host=db_host,
        user=config.get('client', 'user'),
        password=config.get('client', 'password'),
    )

    try:
         cursor = db_conn.cursor(prepared=True)
         cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{domain}_db`;")
         cursor.execute(f"CREATE USER IF NOT EXISTS '{db_user}'@'{db_host}' IDENTIFIED BY '{password}';")
         cursor.execute(f"GRANT ALL ON `{domain}_db`.* TO '{db_user}'@'{db_host}';")
         db_conn.commit()
    except mysql.connector.Error as err:
        print(err)
    finally:
        db_conn.close()

def create_wp_config(db_name, db_user, password, wordpress_path):

    wp_sample = f"{wordpress_path}/wordpress/wp-config-sample.php"
    wp_config = f"{wordpress_path}/wordpress/wp-config.php"

    with open(wp_sample, 'r') as template, open(wp_config, 'w') as conf_file:
        for line in template:
            conf_file.write(
                line.replace("database_name_here", db_name)
                    .replace("username_here", db_user)
                    .replace("password_here", password)
            )

def main():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(32))

    # TODO: Read domain from commandline?
    domain = input("Please enter a domain: ")

    install_dependencies()
    # TODO: Translate these above:
    create_nginx_config(domain)
    insert_hosts_domain("127.0.0.1", domain)
    download_wordpress("/var/www/html")
    create_mysql_db("wpuser", "localhost", password, domain)
    create_wp_config(domain + "_db", "wpuser", password, "/var/www/html")

    print(f"All done! Congrats! Go ahead and open up http://{domain} in a browser.")

if "__main__" == __name__:
    main()

