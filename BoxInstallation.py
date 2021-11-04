
from datetime import datetime
from logging import FileHandler
import os
from sqlite3.dbapi2 import version
import subprocess

import aiohttp
from config import *
from .handler.sqlhandler import SqlHandler
from easilogging import EasiLogging
from util import *
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove

import zipfile
import signal
import requests
import sqlite3
import json

#Aqui vao conter todos os scripts/dependencias necessarias para instalar e configurar o box pela primeira vez 
#talvez trocar para varias subpastas com coisas especificas necessarias na instalacao e reinstalacao

LOGGING = 0
class BoxInstallation():

    """
    ********************************************************************************************************************************************************************
     update box functions
    """
    

    """
     Retorna uma lista dos nomes do arquivo do diretorio desejado
    """
    def get_files(dir):
        
        files = sorted(os.listdir(dir))
        return files
    

    """
     Inicia update no Box
    """
    
    def update_box():
        # Inicia parametros de mysql
        user='easi'
        password='$easi$'
        database='easi'
        connection = pymysql.connect(unix_socket='/var/run/mysqld/mysqld.sock',
                            user=user,
                            password=password,
                            database=database,
                            cursorclass=pymysql.cursors.DictCursor)
        
        #EasiMigrate.request_update_files() #implementar funcao q faz request para o servidor com numero de versao atual

        #Pega arquivos para update
        dir ='/mnt/easiboxpatcher/data/'
        files = BoxInstallation.get_files(dir)

        #cria dump de mysql
        SqlHandler.create_dump_sql(user, password, database)
        
        #para serviços < Trocar para script >
        BoxInstallation.stopServices()
        
        #Faz backup de arquivos
        FileHandler.backup_files()
        

        EasiLogging.debugc(LOGGING, "Connection made")
        try:
            #Percorre array de arquivos e descompacta em pasta temp
            for file in files:
                with zipfile.ZipFile(dir + str(file), 'r') as zip_ref:
                    version_dir = dir + 'temp/' + str(file)
                    zip_ref.extractall(dir + 'temp/' + str(file))
                    update_files = BoxInstallation.get_files(version_dir) # update files contem um arquivo txt com instrucoes para o update de arquivos
                                                                            # além de um arquivo script sql para executar no banco 
                    #Executa update no MySQL, retornando resposta de execução                                                                            
                    sql_update = SqlHandler.sql_update(update_files[1], connection, dir + 'temp/' + str(file))
                    if not sql_update:
                        #troca pro dump e restarta serviços
                        SqlHandler.restore_sql()
                        BoxInstallation.startServices()
                        return
                    #Executa update de Arquivos, retornando resposta de execução
                    file_update = FileHandler.file_update(update_files, dir + 'temp/' + str(file))
                    if not file_update:
                        #substitui tudo pelo backup e restarta serviços
                        FileHandler.restore_files()
                        BoxInstallation.startServices()
                        return
                    
        except Exception as e:
            pass

    """
     Para serviços baseado no tipo de system
    """
    def stopServices():
        EasiLogging.debugc(LOGGING, "stopping services")
        if(Config.get_bool("SYSTEM_IS_MIDDLEWARE")):
            p1 = subprocess.call("service easiboxmidsrv stop", shell=True)
            p2 = subprocess.call("service mosquitto stop", shell=True)

        if(Config.get_bool("SYSTEM_IS_CASH") or Config.get_bool("SYSTEM_IS_GUARD")):
            p1 = subprocess.call("service janus stop", shell=True)
            p2 = subprocess.call("service easiboxsrv stop", shell=True)
            
        EasiLogging.debugc(LOGGING, "services stopped")
    
    """
     Inicia serviços baseado no tipo de system
    """
    def startServices():
        EasiLogging.debugc(LOGGING, "starting services")
        if(Config.get_bool("SYSTEM_IS_MIDDLEWARE")):
            p1 = subprocess.call("service easiboxmidsrv start", shell=True)
            p2 = subprocess.call("service mosquitto start", shell=True)

        if(Config.get_bool("SYSTEM_IS_CASH") or Config.get_bool("SYSTEM_IS_GUARD")):
            p1 = subprocess.call("service janus start", shell=True)
            p2 = subprocess.call("service easiboxsrv start", shell=True)

        EasiLogging.debugc(LOGGING, "services started")
        
        EasiLogging.debugc(LOGGING, "started services")
