import logging
from lib.RemoteGateway import *

lev = None


def initlib_log(lev):
    #TRACE0_FSM, TRACE_FSM, DEBUG_FSM
    #TRACE0_GUI, TRACE_GUI, DEBUG_GUI
    #TRACE0_RGW, TRACE_RGW, DEBUG_RGW
    initlog_RGW(7, 17, 27)
    # Logging levels already reserved:
    #  CRITICAL 50
    #  ERROR 40
    #  WARNING 30
    #  INFO 20
    #  DEBUG 10 (Debug all)
    #  #TRACE 9 (no loops)
    #  #TRACE0 1 (with loops)
    #  NOTSET 0

    logging.TRACE0 = 1
    logging.addLevelName(logging.TRACE0 , 'TRACE0')
    logging.TRACE = 9
    logging.addLevelName(logging.TRACE , 'TRACE')

    logging.basicConfig(\
    #filename='/opt/ft/workspaces/FactoryMain.log',\
    #filemode='w',\
    level=lev,\
    format="%(asctime)s [%(threadName)s] %(levelname)-10s %(funcName)3s %(message)s   #%(filename)3s:%(lineno)d"\
    )


