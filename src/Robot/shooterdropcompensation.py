import math

"""
the goal of this file is to use the shooter pitch auto with the limelight and adding on to that angle with the compensation of the notes downward trajectory and we use that to
get the right angle needed for the shooter
"""

# Keys are distance in meters, values are degrees of compensation needed
# These values are filled in from testing on robot
# left side is distance in m and the right side is compensation value
compensation_table = {
    0 : 0,
    1 : 0,
    6 : 4,
    10 : 12
}

def closest_keys_to_current_distance(keys, current_distance):
    low = 0
    for high in keys:
        if high >= current_distance :
            return (low, high)
        else:
            low = high
    return (low, high)

def degrees_for_ranges(compensation_table, low_distance, high_distance):
    low_degrees = compensation_table[low_distance]
    high_degrees = compensation_table[high_distance]
    return (low_degrees, high_degrees)


def compensation(compensation_table, current_distance):
    low_key_distance, high_key_distance = closest_keys_to_current_distance(compensation_table.keys(),current_distance)
    low_value_degrees, high_value_degrees = degrees_for_ranges(compensation_table, low_key_distance, high_key_distance)
    delta_degrees = high_value_degrees - low_value_degrees
    if high_key_distance - low_key_distance != 0:
        percent_current_distance_between_low_distance_and_high_distance = (current_distance - low_key_distance) / (high_key_distance - low_key_distance)
    else:
        percent_current_distance_between_low_distance_and_high_distance = 0.0
    correction_for_lower_distance = low_value_degrees
    linear_interpolation = percent_current_distance_between_low_distance_and_high_distance * delta_degrees
    return correction_for_lower_distance + linear_interpolation

# def test_compensation(distance_in_m, desired_angle_in_degrees):
#     compensation_degrees = compensation(compensation_table, distance_in_m)
#     print(f"Given {distance_in_m}, I think compensation is {compensation_degrees} while desired is {desired_angle_in_degrees}")
#     assert compensation_degrees == desired_angle_in_degrees

# if __name__ == '__main__':
#     test_compensation(1,0) ==0
#     test_compensation(6,4) == 4
#     test_compensation(3.5,2) == 2
#     test_compensation(10,12) == 12