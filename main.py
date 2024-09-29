#!/usr/bin/env python3
import os
import argparse
import subprocess

PATH_SITES = '/Users/jmarreros/Sites/public_html/'
VHOST_FILE = '/opt/homebrew/etc/httpd/extra/httpd-vhosts.conf'
TEMPLATE = '''\n
#{NAME_HOST}
<VirtualHost *:80>
    DocumentRoot "{PATH_HOST}"
    ServerName {NAME_HOST}.local
    ErrorLog "{PATH_HOST}/error_log"
</VirtualHost>
'''

def remove_virtual_host(basename):
    # Remove virtual host entry from httpd-vhosts.conf
    with open(VHOST_FILE, 'r') as file:
        lines = file.readlines()
    with open(VHOST_FILE, 'w') as file:
        skip = False
        for line in lines:
            if f'#{basename}' in line:
                skip = True
            if skip and '</VirtualHost>' in line:
                skip = False
                continue
            if not skip:
                file.write(line)
    # Remove virtual host from host file
    command = f"sudo sed -i '' '/{basename}.local/d' /etc/hosts"
    subprocess.run(command, shell=True, check=True)
    # Restart apache server
    os.system('brew services restart httpd')
    print('Virtual host removed successfully')

def create_virtual_host(directories, basename):
    path_site = PATH_SITES + directories
    # Create directory
    os.makedirs(path_site, exist_ok=False)
    # Create virtual host file called httpd-vhost.conf
    with open(VHOST_FILE, 'a') as file:
        file.write(TEMPLATE.format(PATH_HOST=path_site, NAME_HOST=basename))
    # Add virtual host to host file
    command = f'echo "\n127.0.0.1    {basename}.local" | sudo tee -a /etc/hosts'
    subprocess.run(command, shell=True, check=True)
    # Restart apache server
    os.system('brew services restart httpd')
    print('Virtual host created successfully')


def install_wordpress(directories, basename):
    path_site = PATH_SITES + directories
    os.chdir(path_site)
    # Download WordPress
    os.system('wp core download')
    # Create wp-config.php
    os.system(f'wp config create --dbname=wp_{basename} --dbuser=root --dbpass=root')
    # Create database
    os.system('wp db create')
    # Install WordPress
    os.system(f'wp core install --url={basename}.local --title={basename} --admin_user=admin --admin_password=admin --admin_email=admin@admin.com')
    # Install remote Plugin
    os.system('wp plugin install all-in-one-wp-migration --activate')
    # Install local Plugin
    os.system('wp plugin install "/Users/jmarreros/Documents/Plugins Interesantes/all-in-one-wp-migration-unlimited-extension.zip" --activate')


# Main function
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add the path to create the virtual host.')
    parser.add_argument('-r', '--remove', type=str, help='The path of the virtual host to remove')
    parser.add_argument('-w', '--wordpress', type=str, help='Create a virtual host for a wordpress project')
    parser.add_argument('path', type=str, nargs='?', help='The path to create the virtual host')

    args = parser.parse_args()

    if args.remove:
        virtual_host_name = os.path.basename(args.remove)
        remove_virtual_host(virtual_host_name)
    elif args.path or args.wordpress:
        virtual_host_path = args.path or args.wordpress
        virtual_host_name = os.path.basename(virtual_host_path)

        if virtual_host_path == '' or virtual_host_name == virtual_host_path:
            print('Ingresa una ruta correcta con el nombre del host y la carpeta')
            exit()

        # If virtual_host_name has the text '.local' remove it
        if '.local' in virtual_host_name:
            virtual_host_name = virtual_host_name.replace('.local', '')

        create_virtual_host(virtual_host_path, virtual_host_name)
        if args.wordpress:
           install_wordpress(virtual_host_path, virtual_host_name)
    else:
        print('Debes proporcionar una ruta para crear o eliminar un virtual host')

