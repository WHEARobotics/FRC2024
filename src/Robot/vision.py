import math
import cscore
import ntcore

import time # Temporary for diagnostics

from wpimath.units import meters, degrees


class Vision:
                                                     
    
    def __init__(self, desired_auto_x, speaker_x) -> None:
        self.desired_x_for_autonomous_driving = desired_auto_x
        self.speaker_x = speaker_x

        self.networktables = ntcore.NetworkTableInstance.getDefault()
        self.limelight_table = self.networktables.getTable("limelight")
        self.botpose_subscription = self.limelight_table.getDoubleArrayTopic("botpose").subscribe([])
        self.botpose = [-1, -1, -1, -1, -1, -1]
        self.bot_x = self.botpose[0] 
        self.bot_y = self.botpose[1]

    def checkBotpose(self):
        botpose = self.botpose_subscription.get()
        # Only modify botpose if: it exists, it's the correct datastructure, and it's not all zeros
        if botpose is not None: # and len(botpose) > 3 and (abs(botpose[0]) + abs(botpose[1])) > 0:  #<- the code behind gives an error saying you cannot combine ints and lists
            self.botpose = botpose
        return self.botpose

    def calculate_desired_direction(self, desired_angle, current_angle):
        """
        this function calculates the direction to travel for the robots yaw by saying if the value is greater than 180 it returns a negative number in degrees needed to travel
        if it is less it returns a positive amount of degrees to travel to get to the desired position.
        """
        desired_direction = desired_angle - current_angle
        if desired_direction > 180:
            desired_direction -= 360
        if desired_direction < -180:
            desired_direction += 360
        return desired_direction
    
    def calculate_desired_pitch(self, speaker_distance : meters, target_height : meters) -> degrees:
        """
        this function calculates the desired angle for the shooter at different positions. its measured by getting the distance to speaker and the height of the target
        and dividing them and uses the arctan function to calculate the angle needed to shoot into the speaker.
        """
        desired_angle = math.atan2(target_height, speaker_distance)
        desired_angle_degrees = self.radians_to_degrees(desired_angle)
        print(desired_angle_degrees)
        return desired_angle_degrees
    
    def distance_to_speaker(self, bot_x, bot_y, speaker_x, speaker_y):
        '''
        distance to speaker calculates the distance from the robots pos to the speaker in meters. it uses the distance formula subtracting the desired x,y (the speaker)
        by our current x, y and square roots the awnser to get our distance to be used in our shooter angle calculations. returns the distance from the robot to the speaker
        '''
        distance = math.sqrt(pow(2, speaker_x - bot_x)) + (pow(2, speaker_y - bot_y))
        return distance
    def calculate_desired_yaw(self, distance_to_speaker_y, distance_to_wall):
        """
        This function calculates the desired angle for the robot's orientation at different positions. It's measured by getting the distance to speaker on the y axis and the distance to the wall using the x axis
        and dividing them and uses the arctan function to calculate the angle needed to for the robot to rotate to into the speaker angle. This function returns the robots needed orientation in degrees.
        distance to speakerY is the adjacent angle
        distance to wall is the opposite angle
        """
        desired_angle_rad = math.atan2(distance_to_speaker_y, distance_to_wall) 
        desired_angle = self.radians_to_degrees(desired_angle_rad)
        if desired_angle < 0:
            desired_angle += 360
        return desired_angle
    
    def radians_to_degrees(self, radians):
        '''
        calculates radians into degrees
        '''
        return radians * (180/math.pi)
    
    def get_rotation_autonomous_periodic_for_speaker_shot(self, botpose, current_yaw) -> float:
        """
        Returns a value between -1.0 and 1.0 that is the desired"bang bang" control amount
        """
        x = botpose[0]
        desired_x = self.desired_x_for_autonomous_driving
        y = botpose[1]
       

        speaker_y = 1.44 # 
        distance_to_wall = (self.speaker_x - x) #Ajd
        distance_to_speaker_y = (speaker_y - y) #Opp
        # speaker_distance = self.distance_to_speaker(x, y, speaker_x, speaker_y) #Hy

        desired_bot_angle = self.calculate_desired_yaw(distance_to_speaker_y, distance_to_wall)


        direction_to_travel = self.calculate_desired_direction(desired_bot_angle, current_yaw)
        # direction_to_travel = self.radians_to_degrees(direction_to_travel_rad)
        x_distance_to_travel = (desired_x - x)
        x_kp = 0.007
        x_max_speed = 0.2
        x_speed = x_kp * x_distance_to_travel

        yaw_kp = 0.02
        max_rot_value = 0.1
        rot = yaw_kp * direction_to_travel
        # this acts like the p value in a pid loop for the rotation action

        if x_speed > x_max_speed:
            x_speed = x_max_speed
        elif x_speed < -x_max_speed:
            x_speed = -x_max_speed

        if rot > max_rot_value:
            rot = max_rot_value
        elif rot < -max_rot_value: 
            rot = -max_rot_value
            # this sets makes sure that the rot value does not pass the maximum we give

        return -rot

    def auto_pitch(self, speaker_x, speaker_y, bot_x, bot_y):
    
        self.speaker_distance = self.distance_to_speaker(bot_x, bot_y, speaker_x, speaker_y)
        print(self.speaker_distance)
        return self.calculate_desired_pitch(self.speaker_distance, 2)
        

    

