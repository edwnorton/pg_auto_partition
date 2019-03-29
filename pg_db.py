# -*- coding: utf-8  -*-
import psycopg2
from psycopg2 import pool
from psycopg2.extras import execute_values
import configparser
import logging
import time, os, re, datetime
import multiprocessing
from subprocess import Popen,PIPE

srcpath = os.path.dirname(os.path.realpath(__file__))
conf = configparser.ConfigParser()
confile = os.path.join(srcpath, 'conf.ini')
conf.read(confile)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
dbname = conf.get("db", "dbname")
port = conf.get("db", "port")
user = conf.get("db", "user")
password = conf.get("db", "password")
host = conf.get("db", "host")

class pgproces():
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        #self.pg_conn = False
        self.connect()

    def connect(self):
        try:
            self.dbpool = psycopg2.pool.SimpleConnectionPool(1, 20, dbname=self.dbname, user=self.user, \
                password=self.password, host=self.host, port=self.port)
            self.connectstat = True
            self.pg_conn = self.dbpool.getconn()
            self._cur = self.pg_conn.cursor()
            logger.info('connect ok')
        except:
            self.connectstat = False
            logger.error('connect failed')

    #def reconnect(self):
    #    try:
    #        self.dbpool.drop(self._oraconn)
    #        self._oraconn = self.dbpool.acquire()
    #        self._oraconn.autocommit = True
    #        self._cur = self._oraconn.cursor()
    #        self.connectstat = True
    #        logger.info('reconnect sucess')
    #    except:
    #        logger.error('reconnect failed ')

    def dbexec_values(self, commd, value):
        try:
            execute_values(self._cur, commd, value)
            self.pg_conn.commit()
            if commd.strip().lower().startswith('select'):
                return self._cur.fetchall()
        except Exception as e:
            logger.error('commd:{0},[{1}]'.format(commd, e))


    def dbexec(self, commd, value):
        try:
            if value == None:
                self._cur.execute(commd)
                self.pg_conn.commit()
            else:
                self._cur.execute(commd, value)
                self.pg_conn.commit()
            if commd.strip().lower().startswith('select'):
                return self._cur.fetchall()
        #except cx_Oracle.DatabaseError as exc:
        #    error, = exc.args
        #    if int(error.code) == 3114 or int(error.code) == 3113:
        #        while self.connectstat:
        #            self.connectstat = False
        #            logger.error('reconnect retry ')
        #            self.reconnect()
        #            if self.connectstat:
        #                if value == None:
        #                    self._cur.execute(commd)
        #                    self._oraconn.commit()
        #                else:
        #                    self._cur.execute(commd, value)
        #                    self._oraconn.commit()
        #                return self._cur.fetchall()
        #            time.sleep(3)
        except Exception as e:
            logger.error('commd:{0},[{1}]'.format(commd, e))
    #def dbexecmany(self, sql, valuelist):
    #    try:
    #        self.valuelist = valuelist
    #        self._cur.prepare(sql)
    #        self._cur.executemany(sql, valuelist)
    #        self._oraconn.commit()
    #        #self._cur.close()
    #        logger.debug('inert urs_event count {0}'.format(len(self.valuelist)))
    #        return True
    #        #if commd.strip().lower().startswith('select'):
    #        #    return self._cur.fetchall()
    #    except cx_Oracle.DatabaseError as exc:
    #        error, = exc.args
    #        if int(error.code) == 3114 or int(error.code) == 3113:
    #            while self.connectstat:
    #                self.connectstat = False
    #                logger.error('reconnect retry ')
    #                self.reconnect()
    #                if self.connectstat:
    #                    self.valuelist = valuelist
    #                    self._cur.prepare(sql)
    #                    self._cur.executemany(sql, valuelist)
    #                    self._oraconn.commit()
    #                    return True
    #                time.sleep(3)
    #    except Exception as e:
    #        logger.error(e)
    #        return False



if __name__ == "__main__":
    srcpath = os.path.dirname(os.path.realpath(__file__))
    conf = configparser.ConfigParser()
    confile = os.path.join(srcpath, 'conf.ini')
    conf.read(confile)
    dbname = conf.get("db", "dbname")
    port = int(conf.get("db", "port"))
    user = conf.get("db", "user")
    password = conf.get("db", "password")
    host = conf.get("db", "host")

    db = pgproces(dbname, user, password, host, port)
    #sqllist = []
    rtpsql_sel = 'SELECT * from t_rtp_report;'
    rtpsql = "INSERT into t_rtp_report(pcap_time,srcip) VALUES (to_date(:1,\'YYYYMMDDHH24MISS\',:2)"
    #a = db.dbexec(rtpsql, None)
    #print(a)

    def run():
        sqllist = []
        try:
            testfile = os.path.join(srcpath, 'test.txt')
            with open(testfile) as f:
                slist = f.read()
            dlist = slist.strip().split("\n")
            for i in dlist:
                a = i.split(",")
                b = tuple(a)
                sqllist.append(b)
            print(sqllist)
            db.dbexec_values(rtpsql, sqllist)
            a = db.dbexec(rtpsql_sel)
            print(a)
            #sqllist = []
            #cmd = ("move {0} {1}".format(sfile, bak_dir_day))
            #print(cmd)
            #a = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
            #stdout, stderr = a.communicate()
            ##a.wait()
        except Exception as e:
            logger.error(e)

    run()
