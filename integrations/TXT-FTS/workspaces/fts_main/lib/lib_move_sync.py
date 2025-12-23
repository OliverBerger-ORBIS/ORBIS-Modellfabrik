from lib.lib_move_async import *

v = None
dist = None
rot = None


def move_forward_distance(v, dist):
    global rot
    move_async_distance_fwd(v, dist)
    move_async_wait()


def move_backward_distance(v, dist):
    global rot
    move_async_distance_backwd(v, dist)
    move_async_wait()


def move_left_distance(v, dist):
    global rot
    move_async_distance_left(v, dist)
    move_async_wait()


def move_right_distance(v, dist):
    global rot
    move_async_distance_right(v, dist)
    move_async_wait()


def move_rotate_left(v, rot):
    global dist
    move_async_rotate_left(v, rot)
    move_async_wait()


def move_rotate_right(v, rot):
    global dist
    move_async_rotate_right(v, rot)
    move_async_wait()


