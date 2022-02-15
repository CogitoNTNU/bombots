from bombots.environment import Bombots, Upgrade
import numpy as np
import random
import sys
explosions = []
for i in range(15):
    explosions.append(np.zeros((i * 2 + 1, i * 2 + 1), dtype=bool))
    explosions[-1][i, :] = True
    explosions[-1][:, i] = True

BOMB_TIME_TO_EXPLODE = 30
BOMB_EXPLOSION_DURATION = 5
N = 11


def find_connected_bombs(bombs):
    connections = np.zeros((len(bombs), len(bombs)), dtype=bool)
    for i, bomb in enumerate(bombs):
        x, y = bomb.pos_x, bomb.pos_y
        strength = bomb.str
        for j, sec_bomb in enumerate(bombs):
            x_2, y_2 = sec_bomb.pos_x, sec_bomb.pos_y
            strength_2 = sec_bomb.str
            if (y == y_2 and abs(x - x_2) <= max(strength, strength_2)) or \
                    (x == x_2 and abs(y - y_2) <= max(strength, strength_2)):
                connections[i, j] = True
    np.fill_diagonal(connections, False)
    return connections


def apply_explostion(wall_matrix, explosion_pos, strength, inverse=False):
    x, y = explosion_pos

    out_of_bounds_left = min(x - strength, 0)
    out_of_bounds_right = min(N - (x + strength + 1), 0)
    out_of_bounds_top = min(y - strength, 0)
    out_of_bounds_bottom = min(N - (y + strength + 1), 0)

    x_left, x_right = x - strength - out_of_bounds_left, x + strength + out_of_bounds_right + 1
    y_left, y_right = y - strength - out_of_bounds_top, y + strength + out_of_bounds_bottom + 1

    explosion = explosions[strength][
                -out_of_bounds_left:explosions[strength].shape[
                                        0] + out_of_bounds_right,
                -out_of_bounds_top:explosions[strength].shape[
                                       1] + out_of_bounds_bottom]
    if inverse:
        explosion = np.logical_not(explosion)
        wall_matrix[:, x_left:x_right,
        y_left:y_right] = \
            np.logical_and(
                wall_matrix[:, x_left:x_right,
                y_left:y_right],
                explosion)
    else:
        wall_matrix[:, x_left:x_right,
        y_left:y_right] = \
            np.logical_or(
                wall_matrix[:, x_left:x_right,
                y_left:y_right],
            explosion)


def rec_check(bomb_matrix, bombs, connected_bombs, fuse, index):
    for j, connected_bool in enumerate(connected_bombs[index]):
        if connected_bool:
            connected_bomb = bombs[j]
            strength = connected_bomb.str
            pos = connected_bomb.pos_x, connected_bomb.pos_y
            apply_explostion(
                bomb_matrix[fuse:fuse + BOMB_EXPLOSION_DURATION], pos,
                strength)
            connected_bombs[index][j] = False
            connected_bombs[j][index] = False
            rec_check(bomb_matrix, bombs, connected_bombs, fuse, j)


def find_bomb_matrix(bombs, connected_bombs):
    """ Returns a matrix with all future bomb explosions """
    bomb_matrix = np.zeros(
        (BOMB_TIME_TO_EXPLODE + BOMB_EXPLOSION_DURATION, N, N), dtype=bool)
    for i, bomb in enumerate(bombs):
        fuse = bomb.fuse
        strength = bomb.str

        pos = bomb.pos_x, bomb.pos_y
        apply_explostion(bomb_matrix[fuse - 1:fuse-1 + BOMB_EXPLOSION_DURATION],
                         pos, strength)

        rec_check(bomb_matrix, bombs, connected_bombs, fuse, i)

    return bomb_matrix


def find_fire_matrix(fires):
    fire_matrix = np.zeros((BOMB_EXPLOSION_DURATION, N, N), dtype=bool)

    for fire in fires:
        fuse = fire.life
        strength = fire.size
        pos = fire.pos_x, fire.pos_y
        apply_explostion(fire_matrix[:fuse], pos,
                         strength)

    return fire_matrix


def evaluate_pos(position, traveled, walls):
    """ Evaluates if a position is safe """
    if not 0 <= position[0] < walls.shape[0]:
        return False

    if not 0 <= position[1] < walls.shape[1]:
        return False

    if not walls[position]:
        return False

    if traveled[position] != -1:
        return False

    return True


def find_distance_matrix(position, walls_and_boxes, bomb_matrix, fire_matrix,
                         offset=0):
    """ Finds distance to and directions to all non-lethal squares """
    directions = -np.ones(
        walls_and_boxes.shape)  # 1 right, 2 left, 3 up, 4 down
    travel_time = -np.ones(walls_and_boxes.shape)

    positions = [position]

    travel_time[position] = 0

    while len(positions) > 0:
        current_position = positions.pop(0)
        current_value = int(travel_time[current_position]) + 1
        if current_value < BOMB_TIME_TO_EXPLODE + BOMB_EXPLOSION_DURATION - offset:
            bomb_walls = np.logical_and(walls_and_boxes,
                                        np.logical_not(
                                            bomb_matrix[
                                                current_value + offset]))
            if current_value < 5 - offset:
                bomb_walls = np.logical_and(bomb_walls,
                                            np.logical_not(fire_matrix[
                                                               current_value + offset]))
        else:
            bomb_walls = walls_and_boxes

        # if (bomb_matrix[current_value].any()):
        #     print(current_value)
        #     print(bomb_matrix[current_value])
        left_right_down_up = [(current_position[0] - 1, current_position[1]),
                              (current_position[0] + 1, current_position[1]),
                              (current_position[0], current_position[1] + 1),
                              (current_position[0], current_position[1] - 1)]
        for i, pos in enumerate(left_right_down_up):
            if evaluate_pos(pos, travel_time, bomb_walls):
                positions.append(pos)
                if travel_time[pos] == -1:
                    travel_time[pos] = current_value
                    directions[pos] = i + 1
                else:
                    if current_value < travel_time[pos]:
                        travel_time[pos] = current_value
                        directions[pos] = i + 1

    return travel_time, directions


def find_path(directions, target):
    path = []
    current_position = [target[0], target[1]]
    while True:
        direction = directions[current_position[0], current_position[1]]
        if direction == -1:
            return path
        elif direction == 1:
            path.append(Bombots.LEFT)
            current_position[0] += 1
        elif direction == 2:
            path.append(Bombots.RIGHT)
            current_position[0] -= 1
        elif direction == 3:
            path.append(Bombots.DOWN)
            current_position[1] -= 1
        elif direction == 4:
            path.append(Bombots.UP)
            current_position[1] += 1


def find_bomb_potential(travel_time, boxes, strength, bombs):
    direction_vectors = np.array([[1, 0], [-1, 0], [0, 1], [0, -1]])
    scores = np.zeros(travel_time.shape)
    for y, column in enumerate(travel_time):
        for x, row in enumerate(column):
            pos = np.array([x, y])
            if travel_time[x, y] == -1:
                continue
            score = 0
            for direction in direction_vectors:
                multiplier = 1
                while True:
                    try:
                        vector = pos + direction * multiplier
                        if vector[0] < 0 or vector[0] >= travel_time.shape[0] or \
                                vector[1] < 0 or vector[1] >= travel_time.shape[
                            1]:
                            break
                        if travel_time[vector[0], vector[1]] == -1:
                            if boxes[vector[0], vector[1]] == 1:
                                score += 1
                            break
                        multiplier += 1
                        if multiplier > strength:
                            break
                    except Exception as e:
                        break
            scores[x, y] = score
    for bomb in bombs:
        scores[bomb.pos_x, bomb.pos_y] = 0
    return scores


# TODO fix self bombing
def is_bomb_safe(bomb_pos, strength, travel_time, walls_and_boxes, bomb_matrix,
                 fire_matrix):
    bomb_travel_time, bomb_directions = find_distance_matrix(bomb_pos,
                                                             walls_and_boxes,
                                                             bomb_matrix,
                                                             fire_matrix,
                                                             offset=int(travel_time[
                                                                 bomb_pos])+1)
    allowed_positions = bomb_travel_time.reshape((-1, *travel_time.shape))
    allowed_positions[allowed_positions > -1] = True
    allowed_positions[allowed_positions == -1] = False
    apply_explostion(allowed_positions, bomb_pos, strength, inverse=True)
    if allowed_positions.any():
        return True

    #print("unsafe")
    return False


class SmartAgent:
    def __init__(self, env):
        self.env = env
        self.has_updated = False
        self.ammo = 1
        self.path = []
        self.bomb_strength = 1
        self.bombing = False
        self.target = ()

    def update_state(self, position):
        walls_and_boxes = np.logical_not(
            np.logical_or(self.env.wall_map,
                          self.env.box_map))
        connected_bombs = find_connected_bombs(self.env.bombs)

        bomb_matrix = find_bomb_matrix(self.env.bombs, connected_bombs)
        fire_matrix = find_fire_matrix(self.env.fires)
        travel_time, directions = find_distance_matrix(position,
                                                       walls_and_boxes,
                                                       bomb_matrix, fire_matrix)

        if travel_time.max() == 0:
            #print("nowhere to go")
            self.path = []
            return
        if travel_time.max() == -1:
            print("how")
            self.path = []
            return
        # print(bomb_potential)

        best_position = position

        upgrade_travel_times = []
        upgrade_positions = []
        upgrade_types = []
        for upper in self.env.upers:
            upgrade_travel_time = travel_time[upper.pos_x, upper.pos_y]
            if upgrade_travel_time != -1:
                upgrade_travel_times.append(upgrade_travel_time)
                upgrade_positions.append((upper.pos_x, upper.pos_y))
                upgrade_types.append(upper.upgrade_type)
        if len(upgrade_travel_times):
            index = np.argmin(upgrade_travel_times)
            shortest_position = upgrade_positions[index]

            self.path = find_path(directions, shortest_position)
            if (len(self.path) == 1):
                if (upgrade_types[index] == Upgrade.STR):
                    self.bomb_strength += 1
            return
        self.bombing = False
        if self.ammo > 0:
            # TODO make this a function
            bomb_potential = find_bomb_potential(travel_time,
                                                 self.env.box_map,
                                                 self.bomb_strength,
                                                 self.env.bombs)
            current_bomb_potential = bomb_potential[position]
            best_potential = np.max(bomb_potential)

            if best_potential != 0:
                if current_bomb_potential == best_potential and \
                        is_bomb_safe(position, self.bomb_strength,
                                     travel_time, walls_and_boxes,
                                     bomb_matrix, fire_matrix):
                    self.bombing = True
                else:
                    unsafe = True
                    best_positions = np.argsort(-bomb_potential, axis=None)
                    best_positions_coords = []
                    bomb_distances = []
                    for i,best_position in enumerate(best_positions):

                        best_positions_coords.append(np.unravel_index(best_position,
                                                         travel_time.shape))
                        bomb_distances.append(travel_time[best_positions_coords[i]])

                    bomb_potential = bomb_potential.flatten()
                    bomb_potential = np.sort(bomb_potential)
                    bomb_potential = np.flip(bomb_potential)

                    ind = np.lexsort((-np.array(bomb_distances), bomb_potential))
                    ind = np.flip(ind)


                    for best_position in np.array(best_positions_coords)[ind]:
                        best_position = tuple(best_position)

                        if not is_bomb_safe(best_position, self.bomb_strength,
                                            travel_time, walls_and_boxes,
                                            bomb_matrix, fire_matrix):
                            #print("not safe")
                            continue
                        else:
                            unsafe = False
                            break
                    if unsafe:
                        print("no valid bomb spots")
                        best_position = np.argmax(travel_time)
                        best_position = np.unravel_index(best_position,
                                                         travel_time.shape)

            else:
                if position == self.target or self.target == ():
                    self.target = tuple(
                        random.choice(np.argwhere(travel_time > 0)))
                    self.path = find_path(directions, self.target)
                else:
                    if travel_time[self.target] != -1:
                        self.path = find_path(directions, self.target)
                        return
                    else:
                        best_position = np.argmax(travel_time)
                        best_position = np.unravel_index(best_position,
                                                         travel_time.shape)
                        self.path = find_path(directions, best_position)
                        return
                if not self.env.box_map.any():
                    if is_bomb_safe(position, self.bomb_strength, travel_time,
                                    walls_and_boxes,
                                         bomb_matrix, fire_matrix):
                        self.bombing = True
                return



        else:
            if self.env.box_map.any():
                best_position = np.argmax(travel_time)
                best_position = np.unravel_index(best_position,
                                                 travel_time.shape)
            else:
                if position == self.target or self.target == ():
                    self.target = tuple(
                        random.choice(np.argwhere(travel_time > 0)))
                    self.path = find_path(directions, self.target)
                else:
                    if travel_time[self.target] != -1:
                        self.path = find_path(directions, self.target)
                        return
                    else:
                        best_position = np.argmax(travel_time)
                        best_position = np.unravel_index(best_position,
                                                         travel_time.shape)
        self.path = find_path(directions, best_position)

    def act(self, env_state):
        self.path = []
        self.ammo = env_state["ammo"]

        self.update_state(env_state["self_pos"])



        if len(self.path):
            return self.path.pop()
        if self.ammo >= 1 and self.bombing and not env_state['self_pos'] in \
                                                   env_state['bomb_pos']:
            return Bombots.BOMB

        return Bombots.NOP

    def reset(self):
        self.__init__(self.env)
