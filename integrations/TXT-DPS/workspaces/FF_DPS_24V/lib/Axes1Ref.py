# This file is probably not needed for the 24V version
import logging
import math
import os
import sys
import time
from fischertechnik.controller.Motor import Motor
from lib.controller import *

_tr0 = None
_tr = None
_dg = None
num = None
msg = None
rv = None
av = None
abspos = None
ABSLIMIT = None
_b_exit = None
tsdiff = None
_ref_valid = None
SPEED = None
ts0 = None
temp = None
_ref_last = None
SPEED_REF = None
TIMEOUT_S = None
def _update_abspos(num, rv):
    global _tr0, _tr, _dg, msg, av, abspos, ABSLIMIT, _b_exit, tsdiff, _ref_valid, SPEED, ts0, temp, _ref_last, SPEED_REF, TIMEOUT_S
    logging.log(logging.TRACE0_A1R, num)
    if num < 1 or num > len(ABSLIMIT):
        logging.error('A1R: num out of bounds: %d', num)
        return
    if abspos[int(num - 1)] == None:
        logging.error('A1R: abspos[num]=None')
        return
    logging.log(logging.DEBUG_A1R, 'num=%d, rv=%d abspos[num]=%d' , num, rv, abspos[num-1])
    temp = None
    if num == 1:
        temp = (temp if isinstance(temp, (int, float)) else 0) + (TXT_M_C1_motor_step_counter.get_count())
    elif num == 2:
        temp = (temp if isinstance(temp, (int, float)) else 0) + (TXT_M_C1_motor_step_counter.get_count())
    elif num == 3:
        temp = (temp if isinstance(temp, (int, float)) else 0) + (TXT_M_C1_motor_step_counter.get_count())
    elif num == 4:
        temp = (temp if isinstance(temp, (int, float)) else 0) + (TXT_M_C1_motor_step_counter.get_count())
    elif num == 5:
        temp = (temp if isinstance(temp, (int, float)) else 0) + (TXT_M_C1_motor_step_counter.get_count())
    if rv > 0:
        abspos[int(num - 1)] = abspos[int(num - 1)] + temp
        logging.log(logging.DEBUG_A1R, 'set abspos[%d]+=%d', num, abspos[num-1])
    elif rv < 0:
        abspos[int(num - 1)] = abspos[int(num - 1)] - temp
        logging.log(logging.DEBUG_A1R, 'set abspos[%d]-=%d', num, abspos[num-1])



def initlog_A1R(_tr0, _tr, _dg):
    global num, msg, rv, av, abspos, ABSLIMIT, _b_exit, tsdiff, _ref_valid, SPEED, ts0, temp, _ref_last, SPEED_REF, TIMEOUT_S
    logging.TRACE0_A1R = _tr0
    logging.addLevelName(logging.TRACE0_A1R , 'TRACE0_A1R')
    logging.TRACE_A1R = _tr
    logging.addLevelName(logging.TRACE_A1R , 'TRACE_A1R')
    logging.DEBUG_A1R = _dg
    logging.addLevelName(logging.DEBUG_A1R, 'DEBUG_A1R')


def initlib_Axes1Ref():
    global _tr0, _tr, _dg, num, msg, rv, av, abspos, ABSLIMIT, _b_exit, tsdiff, _ref_valid, SPEED, ts0, temp, _ref_last, SPEED_REF, TIMEOUT_S
    __version__ = '2022-07-25' #Axes1Ref (A1R)
    logging.log(logging.TRACE_A1R, '-')
    logging.log(logging.DEBUG_A1R, 'Axes1Ref (A1R) %s', __version__)
    # num: #MX, IX, CX
    # 1: VGR x  # VGR_M_M1, VGR_M_I1, VGR_M_C1
    # 2: VGR y  # VGR_M_M2, VGR_M_I2, VGR_M_C2
    # 3: VGR z  # VGR_M_M3, VGR_M_I3, VGR_M_C3
    # 4: SSC pan # SSC_E1_M1, SSC_E1_I1, SSC_E1_C1
    # 5: SSC tilt # SSC_E1_M2, SSC_E1_I2, SSC_E1_C2
    ABSLIMIT = [1500, 900, 1100, 1550, 700]
    abspos = [None] * len(ABSLIMIT)
    SPEED = 512
    SPEED_REF = 200
    TIMEOUT_S = [10.9, 7, 7.3, 10.5, 6.6]
    ts0 = [0] * len(ABSLIMIT)
    tsdiff = [0] * len(ABSLIMIT)
    _b_exit = False
    _ref_valid = [False] * len(ABSLIMIT)
    _ref_last = [False] * len(ABSLIMIT)


def get_abspos():
    global _tr0, _tr, _dg, num, msg, rv, av, abspos, ABSLIMIT, _b_exit, tsdiff, _ref_valid, SPEED, ts0, temp, _ref_last, SPEED_REF, TIMEOUT_S
    logging.log(logging.TRACE_A1R, abspos)
    return abspos


def get_ABSLIMIT():
    global _tr0, _tr, _dg, num, msg, rv, av, abspos, ABSLIMIT, _b_exit, tsdiff, _ref_valid, SPEED, ts0, temp, _ref_last, SPEED_REF, TIMEOUT_S
    logging.log(logging.TRACE_A1R, abspos)
    return ABSLIMIT


def _check_timeout_exit(num):
    global _tr0, _tr, _dg, msg, rv, av, abspos, ABSLIMIT, _b_exit, tsdiff, _ref_valid, SPEED, ts0, temp, _ref_last, SPEED_REF, TIMEOUT_S
    logging.log(logging.TRACE0_A1R, num)
    tsdiff[int(num - 1)] = time.time() - ts0[int(num - 1)]
    if tsdiff[int(num - 1)] > TIMEOUT_S[int(num - 1)]:
        logging.warning('A1R: timeout[%d] %.1f (%.1f), exit program', num, tsdiff[num-1], TIMEOUT_S[num-1])
        _exit_Axes1Ref('timeout {}s (max: {}s)'.format(round(tsdiff[int(num - 1)], 1), TIMEOUT_S[int(num - 1)]))
    time.sleep(0.001)


def _exit_Axes1Ref(msg):
    global _tr0, _tr, _dg, num, rv, av, abspos, ABSLIMIT, _b_exit, tsdiff, _ref_valid, SPEED, ts0, temp, _ref_last, SPEED_REF, TIMEOUT_S
    logging.log(logging.TRACE_A1R, '-')
    _b_exit = True
    _ref_valid = [False] * len(ABSLIMIT)
    msg = 'error in Axes1Ref: {}'.format(msg)
    #thread.interrupt_main()
    #raise SystemExit(msg) #not for threads!
    #sys.exit(msg) #not for threads!

    logging.error('A1R: ', msg)
    os._exit(os.EX_OK)


def moveRef(num):
    global _tr0, _tr, _dg, msg, rv, av, abspos, ABSLIMIT, _b_exit, tsdiff, _ref_valid, SPEED, ts0, temp, _ref_last, SPEED_REF, TIMEOUT_S
    logging.log(logging.TRACE_A1R, num)
    if num < 1 or num > len(ABSLIMIT):
        logging.error('A1R: num out of bounds: %d', num)
        return
    if _ref_last[int(num - 1)]:
        logging.log(logging.DEBUG_A1R, 'ref already done. ignore command')
        return
    ts0[int(num - 1)] = time.time()
    if num == 1:
        TXT_M_M1_encodermotor.set_speed(int(SPEED), Motor.CCW)
        TXT_M_M1_encodermotor.start_sync()
        while not ((TXT_M_I1_mini_switch.is_closed()) or _b_exit):
            _check_timeout_exit(num)
        TXT_M_M1_encodermotor.stop_sync()
        TXT_M_M1_encodermotor.set_speed(int(SPEED_REF), Motor.CW)
        TXT_M_M1_encodermotor.start_sync()
        while not ((TXT_M_I1_mini_switch.is_open()) or _b_exit):
            _check_timeout_exit(num)
        TXT_M_M1_encodermotor.stop_sync()
    elif num == 2:
        TXT_M_M1_encodermotor.set_speed(int(SPEED), Motor.CCW)
        TXT_M_M1_encodermotor.start_sync()
        while not ((TXT_M_I1_mini_switch.is_closed()) or _b_exit):
            _check_timeout_exit(num)
        TXT_M_M1_encodermotor.stop_sync()
        TXT_M_M1_encodermotor.set_speed(int(SPEED_REF), Motor.CW)
        TXT_M_M1_encodermotor.start_sync()
        while not ((TXT_M_I1_mini_switch.is_open()) or _b_exit):
            _check_timeout_exit(num)
        TXT_M_M1_encodermotor.stop_sync()
    elif num == 3:
        TXT_M_M1_encodermotor.set_speed(int(SPEED), Motor.CCW)
        TXT_M_M1_encodermotor.start_sync()
        while not ((TXT_M_I1_mini_switch.is_closed()) or _b_exit):
            _check_timeout_exit(num)
        TXT_M_M1_encodermotor.stop_sync()
        TXT_M_M1_encodermotor.set_speed(int(SPEED_REF), Motor.CW)
        TXT_M_M1_encodermotor.start_sync()
        while not ((TXT_M_I1_mini_switch.is_open()) or _b_exit):
            _check_timeout_exit(num)
        TXT_M_M1_encodermotor.stop_sync()
    elif num == 4:
        TXT_M_M1_encodermotor.set_speed(int(SPEED), Motor.CCW)
        TXT_M_M1_encodermotor.start_sync()
        while not ((TXT_M_I1_mini_switch.is_closed()) or _b_exit):
            _check_timeout_exit(num)
        TXT_M_M1_encodermotor.stop_sync()
        TXT_M_M1_encodermotor.set_speed(int(SPEED_REF), Motor.CW)
        TXT_M_M1_encodermotor.start_sync()
        while not ((TXT_M_I1_mini_switch.is_open()) or _b_exit):
            _check_timeout_exit(num)
        TXT_M_M1_encodermotor.stop_sync()
    elif num == 5:
        TXT_M_M1_encodermotor.set_speed(int(SPEED), Motor.CCW)
        TXT_M_M1_encodermotor.start_sync()
        while not ((TXT_M_I1_mini_switch.is_closed()) or _b_exit):
            _check_timeout_exit(num)
        TXT_M_M1_encodermotor.stop_sync()
        TXT_M_M1_encodermotor.set_speed(int(SPEED_REF), Motor.CW)
        TXT_M_M1_encodermotor.start_sync()
        while not ((TXT_M_I1_mini_switch.is_open()) or _b_exit):
            _check_timeout_exit(num)
        TXT_M_M1_encodermotor.stop_sync()
    abspos[int(num - 1)] = 0
    _ref_valid[int(num - 1)] = True
    _ref_last[int(num - 1)] = True
    logging.log(logging.DEBUG_A1R, 'stop')


def moveRel(num, rv):
    global _tr0, _tr, _dg, msg, av, abspos, ABSLIMIT, _b_exit, tsdiff, _ref_valid, SPEED, ts0, temp, _ref_last, SPEED_REF, TIMEOUT_S
    logging.log(logging.TRACE_A1R, num)
    if num < 1 or num > len(ABSLIMIT):
        logging.error('A1R: num out of bounds: %d', num)
        return
    if not _ref_valid[int(num - 1)]:
        logging.error('A1R: ref not valid')
        return
    if abspos[int(num - 1)] == None:
        logging.error('A1R: abspos[num]=None')
        return
    logging.log(logging.DEBUG_A1R, 'num=%d, rv=%d, abspos[num]=%d, ABSLIMIT[num]=%d', num, rv, abspos[num-1], ABSLIMIT[num-1])
    ts0[int(num - 1)] = time.time()
    temp = abspos[int(num - 1)] + rv
    if rv > 0:
        if temp <= ABSLIMIT[int(num - 1)]:
            if num == 1:
                TXT_M_M1_encodermotor.set_speed(int(SPEED), Motor.CW)
                TXT_M_M1_encodermotor.set_distance(int(math.fabs(rv)))
            elif num == 2:
                TXT_M_M1_encodermotor.set_speed(int(SPEED), Motor.CW)
                TXT_M_M1_encodermotor.set_distance(int(math.fabs(rv)))
            elif num == 3:
                TXT_M_M1_encodermotor.set_speed(int(SPEED), Motor.CW)
                TXT_M_M1_encodermotor.set_distance(int(math.fabs(rv)))
            elif num == 4:
                TXT_M_M1_encodermotor.set_speed(int(SPEED), Motor.CW)
                TXT_M_M1_encodermotor.set_distance(int(math.fabs(rv)))
            elif num == 5:
                TXT_M_M1_encodermotor.set_speed(int(SPEED), Motor.CW)
                TXT_M_M1_encodermotor.set_distance(int(math.fabs(rv)))
        else:
            _exit_Axes1Ref('num {} out of bounds {} > {}'.format(num, temp, ABSLIMIT[int(num - 1)]))
            return
    elif rv < 0:
        if temp >= 0:
            if num == 1:
                TXT_M_M1_encodermotor.set_speed(int(SPEED), Motor.CCW)
                TXT_M_M1_encodermotor.set_distance(int(math.fabs(rv)))
            elif num == 2:
                TXT_M_M1_encodermotor.set_speed(int(SPEED), Motor.CCW)
                TXT_M_M1_encodermotor.set_distance(int(math.fabs(rv)))
            elif num == 3:
                TXT_M_M1_encodermotor.set_speed(int(SPEED), Motor.CCW)
                TXT_M_M1_encodermotor.set_distance(int(math.fabs(rv)))
            elif num == 4:
                TXT_M_M1_encodermotor.set_speed(int(SPEED), Motor.CCW)
                TXT_M_M1_encodermotor.set_distance(int(math.fabs(rv)))
            elif num == 5:
                TXT_M_M1_encodermotor.set_speed(int(SPEED), Motor.CCW)
                TXT_M_M1_encodermotor.set_distance(int(math.fabs(rv)))
        elif temp == 0:
            logging.log(logging.DEBUG_A1R, 'temp==0')
        else:
            _exit_Axes1Ref('num {} out of bounds {} > {}'.format(num, temp, ABSLIMIT[int(num - 1)]))
            return
    elif rv == 0:
        logging.log(logging.DEBUG_A1R, 'rv==0')
    if num == 1:
        while not ((not TXT_M_M1_encodermotor.is_running()) or _b_exit):
            _check_timeout_exit(num)
    elif num == 2:
        while not ((not TXT_M_M1_encodermotor.is_running()) or _b_exit):
            _check_timeout_exit(num)
    elif num == 3:
        while not ((not TXT_M_M1_encodermotor.is_running()) or _b_exit):
            _check_timeout_exit(num)
    elif num == 4:
        while not ((not TXT_M_M1_encodermotor.is_running()) or _b_exit):
            _check_timeout_exit(num)
    elif num == 5:
        while not ((not TXT_M_M1_encodermotor.is_running()) or _b_exit):
            _check_timeout_exit(num)
    _update_abspos(num, rv)
    _ref_last[int(num - 1)] = False


def moveAbs(num, av):
    global _tr0, _tr, _dg, msg, rv, abspos, ABSLIMIT, _b_exit, tsdiff, _ref_valid, SPEED, ts0, temp, _ref_last, SPEED_REF, TIMEOUT_S
    if num < 1 or num > len(ABSLIMIT):
        logging.error('A1R: num out of bounds: %d', num)
        return
    if not _ref_valid[int(num - 1)]:
        logging.error('A1R: ref not valid')
        return
    logging.log(logging.DEBUG_A1R, 'num=%d, av=%d, abspos[num]=%d, ABSLIMIT[num]=%d', num, av, abspos[num-1], ABSLIMIT[num-1])
    if abspos[int(num - 1)] == None:
        _exit_Axes1Ref('num {} no ref, abspos not valid {}'.format(num, abspos[int(num - 1)]))
        return
    else:
        temp = av - abspos[int(num - 1)]
        moveRel(num, temp)


