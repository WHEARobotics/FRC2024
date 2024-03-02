
from pyfrc.tests import *
from shooterdropcompensation import compensation_table, compensation

def test_compensation():
    test_table = [
        (1, 0),
        (6,4),
        (3.5,2),
        (8,8),
        (10,12)
    ]
    for distance_in_m, desired_angle_in_degrees in test_table:
        compensation_degrees = compensation(compensation_table, distance_in_m)
        print(f"Given {distance_in_m}, I think compensation is {compensation_degrees} while desired is {desired_angle_in_degrees}")
        assert compensation_degrees == desired_angle_in_degrees
