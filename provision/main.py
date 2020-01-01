#!/usr/bin/python3

import os
import apt
import secrets, string

def installIfMissing(cmd, packages, apt_cache):
    is_installed = os.system("which {}".format(cmd))
    if is_installed is not 0:
        for package in packages:
            apt_cache[package].mark_install()
        apt_cache.commit()

def install_dependencies():
    apt_cache = apt.Cache()
    apt_cache.update()
    apt_cache.open()

    packages = {
        "php": ["php-fpm", "php-mysql"],
        "mysql": ["mysql-server"],
        "nginx": ["nginx"]
    }

    for cmd in packages.keys():
        installIfMissing(cmd, packages[cmd], apt_cache)

def create_nginx_config(domain):
    pass

def insert_hosts_domain(host_ip, domain):
    pass

def download_wordpress(wordpress_path):
    pass

def create_mysql_db(db_user, db_host, password, domain):
    pass

def create_wp_config(db_name, db_user, password, wordpress_path):
    pass

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

    print("All done! Congrats! Go ahead and open up http://{} in a browser.".format(domain))

if "__main__" == __name__:
    main()

