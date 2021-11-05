
import subprocess
from config import *
import re
from easilogging import EasiLogging
import pymysql



LOGGING = 1
class SqlHandler():
    
    def getVersion():
        return Config.get("_CURRENT_SQL_VERSION")
    
    def setVersion(new_version):
        Config.set("_CURRENT_SQL_VERSION", new_version)

    def check_update(version):

        #request com versao atual para o servidor
        #do request with current major minor build > em string "x.x.x"
        #request deve retornar array de jsons com "version" [numero da versao] e um "file_url" para download do arquivo. Esses arquivos deverao ser salvos em pasta [./data]
        #ao final do request, caso tenha algum update pendente, retornar essa informação ao usuario
        pass
        
    def backup_sql():
        #Acessa o backup na pasta data/dump/, deleta o banco inteiro e executa o backup

        pass
    

    def create_dump_sql(user, password, database):
        args = ["mysqldump","--user="+user,"--password="+password, database]
        file = open("EASI_DUMP.sql", 'w')
        proc = subprocess.Popen(args, stdout=file)
        proc.communicate()
        file.close()
        EasiLogging.info("Dump of version {} made".format(Config.get("VERSION")))
 
    def downgradeSQL(version):
        user='easi'
        password='$easi$'
        database='easi'
        pass
        
    def sql_update(file, conn, dir):       
        try:
            with conn.cursor() as cur:
                EasiLogging.debugc(LOGGING, "cursor created") 
                EasiLogging.debugc(LOGGING, "checking file: {}".format(str(file)))
                result = SqlHandler.exec_sql_file(cur, dir + str(file), conn)
                if not result:
                    conn.rollback()
                    conn.close()
                    return False
        
            conn.commit()
            EasiLogging.debugc(LOGGING, "commit")
            conn.close()
            return True
        except pymysql.Error as e:
            EasiLogging.error("Update could not be completed: {}".format(str(e)))
            conn.close()
            return False
    
    def exec_sql_file(cursor, sql_file, connection):
        EasiLogging.info(" Executing SQL script file: '%s'" % (sql_file)) 
        statement = ""

        for line in open(sql_file):
            if re.match(r'--', line):  # ignore sql comment lines
                continue
            if not re.search(r';$', line):  # keep appending lines that don't end in ';'
                statement = statement + line
            else:  # when you get a line ending in ';' then exec statement and reset for next statement
                statement = statement + line
                #print "\n\n[DEBUG] Executing SQL statement:\n%s" % (statement)
                try:
                    cursor.execute(statement)
                except Exception as e:
                    EasiLogging.error("MySQLError in file '%s' during execute statement \n\tArgs: '%s'" % (str(sql_file),str(e.args)))
                    connection.rollback()
                    return False

                statement = ""
        return True

    def restore_sql(conn):
        try:
            with conn.cursor() as cur:
                file = '/mnt/easiboxpatcher/EASI_BACKUP.sql'
                response = SqlHandler.exec_sql_file(cur, file, conn)
                if response:
                    EasiLogging.debugc(LOGGING, "SQL reverted")
                    conn.commit()
                else:
                    conn.rollback()
                    EasiLogging.critical("-------------------------------------------------------------")
                    EasiLogging.critical("REVERT ERROR, CHECK DUMP")
                    EasiLogging.critical("-------------------------------------------------------------")
        except Exception as e:
            EasiLogging.error("Revert could not be completed: {}".format(str(e)))