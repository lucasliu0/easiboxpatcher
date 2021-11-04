
import subprocess
from config import *
import os
import re
from easilogging import EasiLogging
import pymysql

LOGGING = 1
class FileHandler():

    def file_update(files, dir):
        if('config.txt') in files:
            with open(dir + 'config.txt') as file:
                for line in file:
                    file_path, hash, permission, user, group = line.split(' ')
                    #fazer check de hash para substituir arquivos
                    EasiLogging.debugc(LOGGING, str(hash))
                    if(hash):
                        file_name = file_path.split("/")[-1]
                        subprocess.call('sudo mv -f {} {}'.format(dir+file_name, file_path))
                        subprocess.call('sudo chown {}:{} {}'.format(user, group, file_path))
                        subprocess.call('sudo chmod {} {}'.format(permission, file_path))
                    
                    #usar ced para substituir text em config.txt                  
    def backup_files():
        subprocess.call("sudo tar -cf easicash_backup.tar.gz /mnt/easicash/")
        subprocess.call("sudo mv easicash_backup.tar.gz /mnt/easicash_backup/")

    def restore_files():
        #remove all easicash, extract tar to mnt/easicash
        subprocess.call("")
        














































                    