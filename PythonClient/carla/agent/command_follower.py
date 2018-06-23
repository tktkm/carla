


from carla.agent.agent import Agent
from carla.agent.modules import ObstacleAvoidance, Controller
from carla.agent.modules.utils import get_angle, get_vec_dist



class CommandFollower(Agent):
    """
    The Command Follower agent. It follows the high level commands proposed by the player.
    """
    def __init__(self):

        self.wp_num_steer = 0.8  # Select WP - Reverse Order: 1 - closest, 0 - furthest
        self.wp_num_speed = 0.5  # Select WP - Reverse Order: 1 - closest, 0 - furthest
        self.obstacle_avoider = ObstacleAvoidance()
        self.controller = Controller()



    def run_step(self, measurements, sensor_data, waypoints, target):
        """

        Args:
            measurements: carla measurements for all vehicles
            sensor_data: the sensor that attached to this vehicle
            waypoints: waypoints produced by the local planner
            target: the transform of the target.

        Returns:

        """

        player = measurements.player_measurements
        agents = measurements.non_player_agents
        # print ' it has  ',len(agents),' agents'
        loc_x_player = player.transform.location.x
        loc_y_player = player.transform.location.y
        ori_x_player = player.transform.orientation.x
        ori_y_player = player.transform.orientation.y

        self.wp = [waypoints[int(self.wp_num_steer * len(waypoints))][0],
                   waypoints[int(self.wp_num_steer * len(waypoints))][1]]

        wp_vector, wp_mag = get_vec_dist(self.wp[0], self.wp[1], loc_x_player, loc_y_player)

        if wp_mag > 0:
            wp_angle = get_angle(wp_vector, [ori_x_player, ori_y_player])
        else:
            wp_angle = 0

        # WP Look Ahead for steering
        self.wp_speed = [waypoints[int(self.wp_num_speed * len(waypoints))][0],
                         waypoints[int(self.wp_num_speed * len(waypoints))][1]]
        wp_vector_speed, wp_mag_speed = get_vec_dist(self.wp_speed[0], self.wp_speed[1],
                                                     loc_x_player,
                                                     loc_y_player)
        wp_angle_speed = get_angle(wp_vector_speed, [ori_x_player, ori_y_player])

        # print ('Next Waypoint (Steer): ', waypoints[self.wp_num_steer][0], waypoints[self.wp_num_steer][1])
        # print ('Car Position: ', player.transform.location.x, player.transform.location.y)
        # print ('Waypoint Vector: ', wp_vector[0]/wp_mag, wp_vector[1]/wp_mag)
        # print ('Car Vector: ', player.transform.orientation.x, player.transform.orientation.y)
        # print ('Waypoint Angle: ', wp_angle, ' Magnitude: ', wp_mag)

        speed_factor = self.obstacle_avoider.stop_for_agents(player.transform.location, wp_angle,
                                                             wp_vector, agents)



        # We should run some state machine around here
        control = self.controller.get_control(wp_angle, wp_angle_speed, speed_factor,
                                              player.forward_speed*3.6)

        return control