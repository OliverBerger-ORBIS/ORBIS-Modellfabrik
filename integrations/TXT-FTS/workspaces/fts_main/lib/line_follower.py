import math
import time
from fischertechnik.controller.Motor import Motor
from lib.collision import *
from lib.controller import *
from lib.display import *
from lib.lib_move_async import *
from lib.util import *
from lib.vda5050 import *

v_standard_forwards = None
v_slow_backwards = None
v_slow_forward = None
distance = None
velocity = None
velocity_left = None
velocity_right = None
amount = None
previous_distance = None
range2 = None
deg = None
collision_relax_range = None
previous_distance_left = None
temp = None
collision_slow_range = None
previous_distance_right = None
on_line = None
v_line_speed_standard = None
collision_trigger_range = None
state_prev = None
v_line_speed = None
v_line_backwards_slow = None
collision_accuracy = None
line_left = None
state = None
line_right = None
v_line_forward_slow = None
counter_accu = None
collisionCounter = None
enc_pulses = None
distance_left = None
distance_right = None


def line_init(v_standard_forwards, v_slow_backwards, v_slow_forward):
    global distance, velocity, velocity_left, velocity_right, amount, previous_distance, range2, deg, collision_relax_range, previous_distance_left, temp, collision_slow_range, previous_distance_right, on_line, v_line_speed_standard, collision_trigger_range, state_prev, v_line_speed, v_line_backwards_slow, collision_accuracy, line_left, state, line_right, v_line_forward_slow, counter_accu, collisionCounter, enc_pulses, distance_left, distance_right
    collision_relax_range = 8
    collision_slow_range = 15
    collision_trigger_range = 6
    collision_accuracy = 5
    line_left = 1
    line_right = 2
    on_line = 0
    v_line_speed = v_standard_forwards
    v_line_forward_slow = v_slow_forward
    v_line_speed_standard = v_standard_forwards
    v_line_backwards_slow = v_slow_backwards


def line_follow_for_distance(distance):
    global v_standard_forwards, v_slow_backwards, v_slow_forward, velocity, velocity_left, velocity_right, amount, previous_distance, range2, deg, collision_relax_range, previous_distance_left, temp, collision_slow_range, previous_distance_right, on_line, v_line_speed_standard, collision_trigger_range, state_prev, v_line_speed, v_line_backwards_slow, collision_accuracy, line_left, state, line_right, v_line_forward_slow, counter_accu, collisionCounter, enc_pulses, distance_left, distance_right
    previous_distance_left = 0
    previous_distance_right = 0
    # Try to find the line if the FTS is off by a few degrees
    if not line_find_rotate():
        return False
    util_stop_driving()
    TXT_M_C1_motor_step_counter.reset()
    TXT_M_C2_motor_step_counter.reset()
    TXT_M_C3_motor_step_counter.reset()
    TXT_M_C4_motor_step_counter.reset()
    # Changing speed or direction resets the motor counters.
    # To calculate the correct distance, the previous
    # value has to be added to the current counter.
    counter_accu = 0
    collisionCounter = 0
    time.sleep(0.1)
    state_prev = -1
    enc_pulses = util_mm_to_enc_pulses(distance, v_line_speed)
    while not _line_at_least_encoder_pulses(enc_pulses, counter_accu):
        display.set_attr("label_status.text", str('Driving ...'))
        distance_left = TXT_M_I7_ultrasonic_distance_meter.get_distance()
        distance_right = TXT_M_I8_ultrasonic_distance_meter.get_distance()
        if counter_accu < enc_pulses * 0.8:
            if math.fabs(distance_left - previous_distance_left) <= 10 or math.fabs(distance_right - previous_distance_right) <= 10:
                if distance_left <= collision_slow_range or distance_right <= collision_slow_range:
                    v_line_speed = v_line_forward_slow
                    if distance_left <= collision_trigger_range or distance_right <= collision_trigger_range:
                        collisionCounter = (collisionCounter if isinstance(collisionCounter, (int, float)) else 0) + 1
                else:
                    collisionCounter = 0
                    v_line_speed = v_line_speed_standard
                state_prev = -1
        previous_distance_left = distance_left
        previous_distance_right = distance_right
        time.sleep(0.01)
        state = (1 if (TXT_M_I5_trail_follower.get_state() == 1) else 0) + (2 if (TXT_M_I6_trail_follower.get_state() == 1) else 0)
        if collisionCounter >= collision_accuracy:
            util_stop_driving()
            if collision_in_range(collision_relax_range):
                TXT_M.get_loudspeaker().play("06_Car_horn_short.wav", False)
                print('Collision Warning')
                display.set_attr("label_status.text", str('COLLISION WARNING'))
                vda_set_warning('COLLISION')
                vda_publish_status()
                while not ((TXT_M_I7_ultrasonic_distance_meter.get_distance() > collision_relax_range) and (TXT_M_I8_ultrasonic_distance_meter.get_distance() > collision_relax_range)):
                    time.sleep(1)
                vda_remove_warning('COLLISION')
                vda_publish_status()
                print('Line Free')
                time.sleep(1)
                print('No Collision Warning, continuing navigation')
            counter_accu = (counter_accu if isinstance(counter_accu, (int, float)) else 0) + _line_get_encoder_pulses()
            line_forward(v_line_speed)
            collisionCounter = 0
        else:
            if state == state_prev:
                pass
            elif state == line_left:
                counter_accu = (counter_accu if isinstance(counter_accu, (int, float)) else 0) + _line_get_encoder_pulses()
                line_turn(v_line_backwards_slow, v_line_speed_standard)
            elif state == line_right:
                counter_accu = (counter_accu if isinstance(counter_accu, (int, float)) else 0) + _line_get_encoder_pulses()
                line_turn(v_line_speed_standard, v_line_backwards_slow)
            elif state == on_line:
                counter_accu = (counter_accu if isinstance(counter_accu, (int, float)) else 0) + _line_get_encoder_pulses()
                line_forward(v_line_speed)
            else:
                print('Assuming line is lost, both sensors are white, trying to find line ...')
                util_stop_driving()
                counter_accu = (counter_accu if isinstance(counter_accu, (int, float)) else 0) + _line_get_encoder_pulses()
                if line_find_left_right():
                    print('Re-found line, continuing navigation')
                    # restart line following after line has been found.
                    line_forward(v_line_speed)
                else:
                    print('Line could not be found, stopping FTS ...')
                    return False
        time.sleep(0.01)
        state_prev = state
    util_stop_driving()
    print('Drive End')
    time.sleep(0.1)
    return True


def line_pivot_left(velocity):
    global v_standard_forwards, v_slow_backwards, v_slow_forward, distance, velocity_left, velocity_right, amount, previous_distance, range2, deg, collision_relax_range, previous_distance_left, temp, collision_slow_range, previous_distance_right, on_line, v_line_speed_standard, collision_trigger_range, state_prev, v_line_speed, v_line_backwards_slow, collision_accuracy, line_left, state, line_right, v_line_forward_slow, counter_accu, collisionCounter, enc_pulses, distance_left, distance_right
    TXT_M_M2_encodermotor.set_speed(int(velocity), Motor.CW)
    TXT_M_M2_encodermotor.set_speed(int(velocity), Motor.CCW)
    TXT_M_M3_encodermotor.set_speed(int(velocity), Motor.CW)
    TXT_M_M4_encodermotor.set_speed(int(velocity), Motor.CCW)
    TXT_M_M2_encodermotor.start_sync(TXT_M_M2_encodermotor, TXT_M_M3_encodermotor, TXT_M_M4_encodermotor)


def line_turn(velocity_left, velocity_right):
    global v_standard_forwards, v_slow_backwards, v_slow_forward, distance, velocity, amount, previous_distance, range2, deg, collision_relax_range, previous_distance_left, temp, collision_slow_range, previous_distance_right, on_line, v_line_speed_standard, collision_trigger_range, state_prev, v_line_speed, v_line_backwards_slow, collision_accuracy, line_left, state, line_right, v_line_forward_slow, counter_accu, collisionCounter, enc_pulses, distance_left, distance_right
    TXT_M_M3_encodermotor.set_speed(int(velocity_left), Motor.CCW)
    TXT_M_M1_encodermotor.set_speed(int(velocity_left), Motor.CCW)
    TXT_M_M3_encodermotor.start_sync(TXT_M_M1_encodermotor)
    TXT_M_M2_encodermotor.set_speed(int(velocity_right), Motor.CCW)
    TXT_M_M4_encodermotor.set_speed(int(velocity_right), Motor.CCW)
    TXT_M_M2_encodermotor.start_sync(TXT_M_M4_encodermotor)


def line_forward(velocity):
    global v_standard_forwards, v_slow_backwards, v_slow_forward, distance, velocity_left, velocity_right, amount, previous_distance, range2, deg, collision_relax_range, previous_distance_left, temp, collision_slow_range, previous_distance_right, on_line, v_line_speed_standard, collision_trigger_range, state_prev, v_line_speed, v_line_backwards_slow, collision_accuracy, line_left, state, line_right, v_line_forward_slow, counter_accu, collisionCounter, enc_pulses, distance_left, distance_right
    TXT_M_M2_encodermotor.set_speed(int(velocity), Motor.CCW)
    TXT_M_M1_encodermotor.set_speed(int(velocity), Motor.CCW)
    TXT_M_M3_encodermotor.set_speed(int(velocity), Motor.CCW)
    TXT_M_M4_encodermotor.set_speed(int(velocity), Motor.CCW)
    TXT_M_M2_encodermotor.start_sync(TXT_M_M1_encodermotor, TXT_M_M3_encodermotor, TXT_M_M4_encodermotor)


# Changing speed or direction resets the motor counters. To calculate the correct distance, the previous value has to be added to the current counter.
def _line_at_least_encoder_pulses(amount, previous_distance):
    global v_standard_forwards, v_slow_backwards, v_slow_forward, distance, velocity, velocity_left, velocity_right, range2, deg, collision_relax_range, previous_distance_left, temp, collision_slow_range, previous_distance_right, on_line, v_line_speed_standard, collision_trigger_range, state_prev, v_line_speed, v_line_backwards_slow, collision_accuracy, line_left, state, line_right, v_line_forward_slow, counter_accu, collisionCounter, enc_pulses, distance_left, distance_right
    temp = _line_get_encoder_pulses()
    temp = (temp if isinstance(temp, (int, float)) else 0) + previous_distance
    return temp >= amount


def _line_get_encoder_pulses():
    global v_standard_forwards, v_slow_backwards, v_slow_forward, distance, velocity, velocity_left, velocity_right, amount, previous_distance, range2, deg, collision_relax_range, previous_distance_left, temp, collision_slow_range, previous_distance_right, on_line, v_line_speed_standard, collision_trigger_range, state_prev, v_line_speed, v_line_backwards_slow, collision_accuracy, line_left, state, line_right, v_line_forward_slow, counter_accu, collisionCounter, enc_pulses, distance_left, distance_right
    return math_mean([TXT_M_C1_motor_step_counter.get_count(), TXT_M_C2_motor_step_counter.get_count(), TXT_M_C3_motor_step_counter.get_count(), TXT_M_C4_motor_step_counter.get_count()])


def _line_is_both_sensors_dark():
    global v_standard_forwards, v_slow_backwards, v_slow_forward, distance, velocity, velocity_left, velocity_right, amount, previous_distance, range2, deg, collision_relax_range, previous_distance_left, temp, collision_slow_range, previous_distance_right, on_line, v_line_speed_standard, collision_trigger_range, state_prev, v_line_speed, v_line_backwards_slow, collision_accuracy, line_left, state, line_right, v_line_forward_slow, counter_accu, collisionCounter, enc_pulses, distance_left, distance_right
    return (TXT_M_I5_trail_follower.get_state() == 0) and (TXT_M_I6_trail_follower.get_state() == 0)


def _line_stop_driving_success():
    global v_standard_forwards, v_slow_backwards, v_slow_forward, distance, velocity, velocity_left, velocity_right, amount, previous_distance, range2, deg, collision_relax_range, previous_distance_left, temp, collision_slow_range, previous_distance_right, on_line, v_line_speed_standard, collision_trigger_range, state_prev, v_line_speed, v_line_backwards_slow, collision_accuracy, line_left, state, line_right, v_line_forward_slow, counter_accu, collisionCounter, enc_pulses, distance_left, distance_right
    util_stop_driving()
    return True


def follow_until_range(range2):
    global v_standard_forwards, v_slow_backwards, v_slow_forward, distance, velocity, velocity_left, velocity_right, amount, previous_distance, deg, collision_relax_range, previous_distance_left, temp, collision_slow_range, previous_distance_right, on_line, v_line_speed_standard, collision_trigger_range, state_prev, v_line_speed, v_line_backwards_slow, collision_accuracy, line_left, state, line_right, v_line_forward_slow, counter_accu, collisionCounter, enc_pulses, distance_left, distance_right
    util_stop_driving()
    on_line = 0
    state_prev = -1
    while not (util_module_in_range(range2)):
        state = (1 if (TXT_M_I5_trail_follower.get_state() == 1) else 0) + (2 if (TXT_M_I6_trail_follower.get_state() == 1) else 0)
        if state == state_prev:
            pass
        elif state == line_left:
            line_turn(v_line_backwards_slow, v_line_speed)
        elif state == line_right:
            line_turn(v_line_speed, v_line_backwards_slow)
        elif state == on_line:
            line_forward(v_line_speed)
        else:
            util_stop_driving()
            return False
        time.sleep(0.01)
        state_prev = state
    util_stop_driving()
    return True


def line_find_rotate():
    global v_standard_forwards, v_slow_backwards, v_slow_forward, distance, velocity, velocity_left, velocity_right, amount, previous_distance, range2, deg, collision_relax_range, previous_distance_left, temp, collision_slow_range, previous_distance_right, on_line, v_line_speed_standard, collision_trigger_range, state_prev, v_line_speed, v_line_backwards_slow, collision_accuracy, line_left, state, line_right, v_line_forward_slow, counter_accu, collisionCounter, enc_pulses, distance_left, distance_right
    if _line_is_both_sensors_dark():
        return _line_stop_driving_success()
    move_async_rotate_left(v_line_speed, 10)
    while not (move_asnyc_done()):
        if _line_is_both_sensors_dark():
            return _line_stop_driving_success()
    move_async_rotate_right(v_line_speed, 20)
    while not (move_asnyc_done()):
        if _line_is_both_sensors_dark():
            return _line_stop_driving_success()
    move_async_rotate_left(v_line_speed, 10)
    while not (move_asnyc_done()):
        if _line_is_both_sensors_dark():
            return _line_stop_driving_success()
    return False


def line_rotate_left_and_find(deg):
    global v_standard_forwards, v_slow_backwards, v_slow_forward, distance, velocity, velocity_left, velocity_right, amount, previous_distance, range2, collision_relax_range, previous_distance_left, temp, collision_slow_range, previous_distance_right, on_line, v_line_speed_standard, collision_trigger_range, state_prev, v_line_speed, v_line_backwards_slow, collision_accuracy, line_left, state, line_right, v_line_forward_slow, counter_accu, collisionCounter, enc_pulses, distance_left, distance_right
    move_async_rotate_left(v_line_speed_standard, deg)
    move_async_wait()
    if _line_is_both_sensors_dark():
        return _line_stop_driving_success()
    if line_find_left_right():
        return _line_stop_driving_success()
    return False


def line_find_left_right():
    global v_standard_forwards, v_slow_backwards, v_slow_forward, distance, velocity, velocity_left, velocity_right, amount, previous_distance, range2, deg, collision_relax_range, previous_distance_left, temp, collision_slow_range, previous_distance_right, on_line, v_line_speed_standard, collision_trigger_range, state_prev, v_line_speed, v_line_backwards_slow, collision_accuracy, line_left, state, line_right, v_line_forward_slow, counter_accu, collisionCounter, enc_pulses, distance_left, distance_right
    if _line_is_both_sensors_dark():
        return _line_stop_driving_success()
    move_async_distance_left(v_line_backwards_slow, 30)
    while not (move_asnyc_done()):
        if _line_is_both_sensors_dark():
            return _line_stop_driving_success()
    move_async_distance_right(v_line_backwards_slow, 60)
    while not (move_asnyc_done()):
        if _line_is_both_sensors_dark():
            return _line_stop_driving_success()
    move_async_distance_left(v_line_backwards_slow, 30)
    while not (move_asnyc_done()):
        if _line_is_both_sensors_dark():
            return _line_stop_driving_success()
    return False


def line_rotate_right_and_find(deg):
    global v_standard_forwards, v_slow_backwards, v_slow_forward, distance, velocity, velocity_left, velocity_right, amount, previous_distance, range2, collision_relax_range, previous_distance_left, temp, collision_slow_range, previous_distance_right, on_line, v_line_speed_standard, collision_trigger_range, state_prev, v_line_speed, v_line_backwards_slow, collision_accuracy, line_left, state, line_right, v_line_forward_slow, counter_accu, collisionCounter, enc_pulses, distance_left, distance_right
    move_async_rotate_right(v_line_speed_standard, deg)
    move_async_wait()
    if _line_is_both_sensors_dark():
        return _line_stop_driving_success()
    if line_find_left_right():
        return _line_stop_driving_success()
    return False


def math_mean(myList):
        localList = [e for e in myList if isinstance(e, (float, int))]
        if not localList: return
        return float(sum(localList)) / len(localList)
