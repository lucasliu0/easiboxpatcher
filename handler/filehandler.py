
import subprocess
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
                        proc1 = subprocess.Popen(['sudo', 'mv', '-f', dir+file_name, file_path])
                        proc1.communicate()                           
                        proc2 = subprocess.Popen(['sudo', 'chown', '{}:{}'.format(user, group), file_path])
                        proc2.communicate()                         
                        proc3 = subprocess.Popen(['sudo', 'chmod', permission, file_path])
                        proc3.communicate() 

                    #usar ced para substituir text em config.txt                  
    def backup_files():
        EasiLogging.info("Backing up easicash...")
        proc1 = subprocess.Popen(["sudo","tar","-cf","easicash_backup.tar.gz","/mnt/easicash_test/"])
        proc1.communicate()

    def restore_files():
        proc1 = subprocess.Popen(['sudo', 'tar', '-xf', '/mnt/easiboxpatcher/easicash_backup.tar.gz', '/mnt/easiboxpatcher/backup_files'])
        proc1.communicate()
        proc2 = subprocess.Popen(['sudo', 'rm', '-r', '/mnt/easicash_test/'])
        proc2.communicate()
        proc3 = subprocess.Popen(['sudo', 'mv', '-F',  '/mnt/easiboxpatcher/backup_files/', '/mnt/easicash'])
        proc3.communicate()
        














































                    