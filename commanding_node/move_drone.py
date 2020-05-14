import rospy
from mavros_msgs.srv import CommandBool, CommandTOL, SetMode
from mavros_msgs.msg import GlobalPositionTarget, State, PositionTarget
from geometry_msgs.msg import PoseStamped
import time
import yaml
from gpio_diptera import Rpi_gpio_comm as Gpio_start
from gpio_clean import Rpi_gpio_comm_off as Gpio_stop


class Move_Drone():

    def __init__(self):
        rospy.init_node("Move_drone_node")

        self.local_pose_sub = rospy.Subscriber("/mavros/local_position/pose", PoseStamped, self.local_pose_callback)
        self.imu_sub = rospy.Subscriber("/mavros/imu/data", Imu, self.imu_callback)
        self.local_target_pub = rospy.Publisher('mavros/setpoint_raw/local', PositionTarget, queue_size=10)


    def construct_target(self, x, y, z, yaw, yaw_rate=1):
        target_raw_pose = PositionTarget()  # We will fill the following message with our values: http://docs.ros.org/api/mavros_msgs/html/msg/PositionTarget.html
        target_raw_pose.header.stamp = rospy.Time.now()

        target_raw_pose.coordinate_frame = 9

        target_raw_pose.position.x = x
        target_raw_pose.position.y = y
        target_raw_pose.position.z = z

        target_raw_pose.type_mask = PositionTarget.IGNORE_VX + PositionTarget.IGNORE_VY + PositionTarget.IGNORE_VZ \
                                    + PositionTarget.IGNORE_AFX + PositionTarget.IGNORE_AFY + PositionTarget.IGNORE_AFZ \
                                    + PositionTarget.FORCE

        target_raw_pose.yaw = yaw
        target_raw_pose.yaw_rate = yaw_rate

        return target_raw_pose

    def local_pose_callback(self, msg): 
        self.local_pose = msg
        self.local_enu_position = msg


    def imu_callback(self, msg):

        self.imu = msg

        self.current_heading = self.q2yaw(self.imu.orientation) # Transforms q into degrees of yaw

        self.received_imu = True

    def q2yaw(self, q):
        if isinstance(q, Quaternion): # Checks if the variable is of the type Quaternion
            rotate_z_rad = q.yaw_pitch_roll[0]
        else:
            q_ = Quaternion(q.w, q.x, q.y, q.z) # Converts into Quaternion
            rotate_z_rad = q_.yaw_pitch_roll[0]

        return rotate_z_rad

    def waiting_initialization(self):

        for i in range(10): # Waits 5 seconds for initialization
            if self.current_heading is not None:
                break
            else:
                print("Waiting for initialization.")
                time.sleep(0.5)

    def start(self, x, y, z, yaw, yaw_rate = 1):
        self.waiting_initialization()
        self.cur_target_pose = self.construct_target(x, y, z, yaw, yaw_rate)
        self.local_target_pub.publish(self.cur_target_pose) 

    def move_in_x(self, distance):
        self.waiting_initialization()
        self.cur_target_pose = self.construct_target(self.local_pose.pose.position.x + distance, self.local_pose.pose.position.y, self.local_pose.pose.position.z, self.current_heading)
        self.local_target_pub.publish(self.cur_target_pose) 

    def move_in_y(self, distance):
        self.waiting_initialization()
        self.cur_target_pose = self.construct_target(self.local_pose.pose.position.x, self.local_pose.pose.position.y + distance, self.local_pose.pose.position.z, self.current_heading)
        self.local_target_pub.publish(self.cur_target_pose) 

    def move_in_z(self, distance):
        self.waiting_initialization()
        self.cur_target_pose = self.construct_target(self.local_pose.pose.position.x, self.local_pose.pose.position.y, self.local_pose.pose.position.z + distance, self.current_heading)
        self.local_target_pub.publish(self.cur_target_pose) 
            
    def moving_forward(self, distance):
        self.move_in_x(distance)

    def moving_back(self, distance):
        self.move_in_x(distance)

    def moving_left(self, distance):
        self.move_in_y(-distance)

    def moving_right(self, distance):
        self.move_in_y(-distance)

    def moving_up(self, distance):
        self.move_in_z(distance)

    def moving_down(self, distance):
        self.move_in_z(-distance)




