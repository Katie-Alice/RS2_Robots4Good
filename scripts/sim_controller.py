# sim_controller.py

# Main outer controller script for the RS2 Robots for Good demo.
# This script is intended to manage:
# - keyboard control for the robot in simulation
# - checking whether the robot is near a person
# - triggering the webcam emotion demo when allowed
# - printing the returned emotion result and robot dialogue
# - moving the robot backward after a successful interaction
#
# Current version:
# - hardcoded people positions
# - simple internal robot pose estimate
# - placeholder Gazebo command publishing function
# - ready to integrate with Gazebo Fortress transport next

import math
import sys
import time
import tty
import termios
import select
from typing import Optional, Dict, List

from emotion_demo import run_emotion_demo


# -----------------------------------
# Configuration
# -----------------------------------

# Hardcoded people in the world for version 1
PEOPLE = [
    {"name": "Person 1", "x": 2.0, "y": 1.0},
    {"name": "Person 2", "x": 4.0, "y": -1.5},
    {"name": "Person 3", "x": 6.0, "y": 0.5},
    {"name": "Person 4", "x": 3.5, "y": 2.0},
]

NEAR_PERSON_THRESHOLD = 1.5

# Movement settings
LINEAR_SPEED = 0.6      # m/s
ANGULAR_SPEED = 1.0     # rad/s
COMMAND_DURATION = 0.2  # seconds per keypress step

# After successful emotion interaction
BACKUP_SPEED = -0.4
BACKUP_DURATION = 1.0

# Update period for idle loop
IDLE_SLEEP = 0.05

# Standard cmd_vel topic name
CMD_VEL_TOPIC = "/cmd_vel"


# -----------------------------------
# Terminal keyboard helpers
# -----------------------------------

def get_key(timeout: float = 0.05) -> Optional[str]:
    """
    Read one key from terminal without requiring Enter.
    Returns None if no key was pressed within timeout.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            return sys.stdin.read(1)
        return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


# -----------------------------------
# Robot state
# -----------------------------------

class RobotState:
    """
    Internal estimate of robot position and heading.
    For version 1 this is updated from the commands we send.
    Later this can be replaced with true pose feedback from Gazebo.
    """
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0  # radians

    def update_from_command(self, linear_x: float, angular_z: float, dt: float) -> None:
        """
        Dead-reckoning style pose update based on commanded motion.
        Good enough for version 1 controller structure.
        """
        self.yaw += angular_z * dt

        # Keep yaw in [-pi, pi]
        self.yaw = math.atan2(math.sin(self.yaw), math.cos(self.yaw))

        self.x += linear_x * math.cos(self.yaw) * dt
        self.y += linear_x * math.sin(self.yaw) * dt


# -----------------------------------
# World helpers
# -----------------------------------

def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.hypot(x2 - x1, y2 - y1)


def find_nearby_person(robot_x: float, robot_y: float, threshold: float) -> Optional[Dict]:
    """
    Return the nearest person within threshold, otherwise None.
    """
    nearest_person = None
    nearest_distance = None

    for person in PEOPLE:
        d = distance(robot_x, robot_y, person["x"], person["y"])
        if d <= threshold:
            if nearest_distance is None or d < nearest_distance:
                nearest_person = person
                nearest_distance = d

    return nearest_person


# -----------------------------------
# Gazebo command layer
# -----------------------------------

def send_velocity_command(linear_x: float, angular_z: float, duration: float) -> None:
    """
    Placeholder for Gazebo movement command publishing.

    Right now this just prints the intended command.
    In the Gazebo-integrated version, this function should publish a Twist-like
    command to the robot's DiffDrive topic (for example cmd_vel).
    """
    print(
        f"[SIM CMD] topic={CMD_VEL_TOPIC} "
        f"linear_x={linear_x:.2f}, angular_z={angular_z:.2f}, duration={duration:.2f}"
    )


def stop_robot() -> None:
    send_velocity_command(0.0, 0.0, 0.0)


# -----------------------------------
# Controller actions
# -----------------------------------

def move_forward(robot_state: RobotState) -> None:
    send_velocity_command(LINEAR_SPEED, 0.0, COMMAND_DURATION)
    robot_state.update_from_command(LINEAR_SPEED, 0.0, COMMAND_DURATION)


def move_backward(robot_state: RobotState) -> None:
    send_velocity_command(-LINEAR_SPEED, 0.0, COMMAND_DURATION)
    robot_state.update_from_command(-LINEAR_SPEED, 0.0, COMMAND_DURATION)


def turn_left(robot_state: RobotState) -> None:
    send_velocity_command(0.0, ANGULAR_SPEED, COMMAND_DURATION)
    robot_state.update_from_command(0.0, ANGULAR_SPEED, COMMAND_DURATION)


def turn_right(robot_state: RobotState) -> None:
    send_velocity_command(0.0, -ANGULAR_SPEED, COMMAND_DURATION)
    robot_state.update_from_command(0.0, -ANGULAR_SPEED, COMMAND_DURATION)


def back_away(robot_state: RobotState) -> None:
    print("Backing away...")
    send_velocity_command(BACKUP_SPEED, 0.0, BACKUP_DURATION)
    robot_state.update_from_command(BACKUP_SPEED, 0.0, BACKUP_DURATION)
    stop_robot()


# -----------------------------------
# Printing helpers
# -----------------------------------

def print_controls() -> None:
    print("\n" + "=" * 50)
    print("Robots for Good - Simulation Controller")
    print("Controls:")
    print("  W = move forward")
    print("  S = move backward")
    print("  A = turn left")
    print("  D = turn right")
    print("  E = start emotion check (only when near a person)")
    print("  Q = quit")
    print("=" * 50 + "\n")


def print_robot_pose(robot_state: RobotState) -> None:
    print(
        f"Robot pose estimate -> "
        f"x: {robot_state.x:.2f}, y: {robot_state.y:.2f}, yaw(rad): {robot_state.yaw:.2f}"
    )


# -----------------------------------
# Main controller
# -----------------------------------

def main():
    robot_state = RobotState()
    print_controls()

    running = True

    while running:
        nearby_person = find_nearby_person(
            robot_state.x,
            robot_state.y,
            NEAR_PERSON_THRESHOLD
        )

        if nearby_person is not None:
            d = distance(
                robot_state.x,
                robot_state.y,
                nearby_person["x"],
                nearby_person["y"]
            )
            print(
                f"Near {nearby_person['name']} "
                f"(distance {d:.2f} m). Press E to start emotion check."
            )

        key = get_key(IDLE_SLEEP)

        if key is None:
            continue

        key = key.lower()

        if key == "q":
            print("Quit requested.")
            stop_robot()
            running = False

        elif key == "w":
            move_forward(robot_state)
            print_robot_pose(robot_state)

        elif key == "s":
            move_backward(robot_state)
            print_robot_pose(robot_state)

        elif key == "a":
            turn_left(robot_state)
            print_robot_pose(robot_state)

        elif key == "d":
            turn_right(robot_state)
            print_robot_pose(robot_state)

        elif key == "e":
            if nearby_person is None:
                print("Emotion check unavailable. Move closer to a person.")
                continue

            print(f"Starting emotion check for {nearby_person['name']}...")
            result = run_emotion_demo()

            if result["success"]:
                print("\n" + "=" * 50)
                print("Emotion detection complete.")
                print(f"Detected emotion: {result['emotion']}")
                print(f"Confidence score: {result['score']:.2f}")
                print(f"Robot says: {result['dialogue']}")
                print("=" * 50 + "\n")

                back_away(robot_state)
                print("Ready to find the next person.\n")

            elif result["quit_requested"]:
                print("Emotion demo was cancelled by the user.\n")

            else:
                print("Emotion demo ended without a valid result.\n")

        else:
            print("Unknown key. Use W/A/S/D, E, or Q.")

    print("Simulation controller ended.")


if __name__ == "__main__":
    main()
