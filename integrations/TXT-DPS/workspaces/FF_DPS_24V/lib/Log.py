import logging
from lib.Axes1Ref import *
from lib.calibration_commands import *
from lib.Factory import *
from lib.GUI import *
from lib.Nfc import *
from lib.SSC_Publisher import *
from lib.VGR import *

lev = None


def initlib_log(lev):
    #TRACE0_A1R, TRACE_A1R, DEBUG_A1R
    initlog_A1R(1, 0, 21)
    #TRACE0_FSM, TRACE_FSM, DEBUG_FSM
    initlog_FSM(0, 0, 0)
    #TRACE0_GUI, TRACE_GUI, DEBUG_GUI
    initlog_GUI(5, 0, 0)
    #TRACE0_VGR, TRACE_VGR, DEBUG_VGR
    initlog_VGR(6, 16, 26)
    #TRACE0_NFC, TRACE_NFC, DEBUG_NFC
    initlog_NFC(8, 0, 38)
    #TRACE0_RGW, TRACE_RGW, DEBUG_RGW
    #TRACE0_FCL, TRACE_FCL, DEBUG_FCL
    initlog_FCL(9, 19, 29)
    initlog_VDACMD(4, 14, 24)
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


