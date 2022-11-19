import Data
import random
from enum import Enum
from utils import get_covered_cells
from utils import print_routers
from utils import get_points_around_router
from utils import filter_non_target_points

class NotValidPolicyExcception(Exception):
    pass

class Action(Enum):
    LEFT = (0, -1)
    RIGHT = (0, 1)
    UP = (-1, 0)
    DOWN = (1, 0)

class Policy(Enum):
    GREEDY = 1
    BEST = 2

def move(router: list,
         action: Action)->list:
    """
    moves a router in the direction requested
    no check in the boundary, since routers are generated inside interested point,
    and those are not on borders

    Args:
        router (list): the router coordinate
        action (Action): action taken from Action

    Returns:
        list: new coordinate for router
    """
    router[0] = router[0] + action.value[0]
    router[1] = router[1] + action.value[1]
    return router

def restore_move(router: list,
                 action: Action) ->list:
    """restore the position of the router that have taken actio

    Args:
        router (list): the router coordinate
        action (Action): action taken from Action

    Returns:
        list: new coordinate for router
    """
    router[0] = router[0] - action.value[0]
    router[1] = router[1] - action.value[1]
    return router 
    
def greedy_move(actual_score, map_mask, building_matrix, router_list)->set:
    """
    return the first move set found that improves the overall score

    Args:
        actual_score (int): score achieved until the move
        map_mask (np.array): router mask in the building
        building_matrix (np.array): matrix representation of the building
        router_list (list): the list of router coordinates

    Returns:
        set: move set <router_idx, action, score_achieved>
    """
    greedy_move_set = ()
    boundary = map_mask.shape
    for i, router in enumerate(router_list):
        start_coord = [router[0], router[1]]
        map_mask[start_coord[0], start_coord[1]] = 0
        for action in Action:
            move(router, action)
            # violating the boundary, should be reset
            # print("check: router[0]: {} >= boundary[0]{} ? ".format(router[0], boundary[0]))
            if router[0] >= boundary[0] or router[0] < 0:
                restore_move(router, action)
                # router = [start_coord[0], start_coord[1]]
                continue
            # print("check: router[1]: {} >= boundary[1]{} ? ".format(router[1], boundary[1]))
            if router[1] >= boundary[1] or router[1] < 0:
                router = [start_coord[0], start_coord[1]]
                continue
            map_mask[router[0], router[1]] = 1
            temp_score = get_covered_cells(map_mask, building_matrix, range)
            map_mask[router[0], router[1]] = 0
            restore_move(router, action)
            # router = [start_coord[0], start_coord[1]]
            if temp_score > actual_score:
                greedy_move_set = (i, action, temp_score)
                map_mask[start_coord[0], start_coord[1]] = 1
                return greedy_move_set
                
        map_mask[start_coord[0], start_coord[1]] = 1
    
    return greedy_move_set

def best_move(actual_score, map_mask, building_matrix, router_list, range):
    """
    return the best move set of <router_idx, action, score> found

    Args:
        actual_score (int): score achieved until the move
        map_mask (np.array): router mask in the building
        building_matrix (np.array): matrix representation of the building
        router_list (list): the list of router coordinates

    Returns:
        set: move set <router_idx, action, score_achieved>
    """
    # per_action_score = {}
    best_move_set = ()
    best_score = actual_score
    
    boundary = map_mask.shape
    for i, router in enumerate(router_list):
        start_coord = [router[0], router[1]]
        map_mask[start_coord[0], start_coord[1]] = 0
        for action in Action:
            move(router, action)
            
            # violating the boundary, should be reset
            if (router[0] >= boundary[0] or router[0] < 0 or
                router[1] >= boundary[1] or router[1] < 0 or
                building_matrix[router[0]][router[1]] == '#' or
                building_matrix[router[0]][router[1]] == '-'
                ):
                restore_move(router, action)
                # router = [start_coord[0], start_coord[1]]
                continue

            map_mask[router[0], router[1]] = 1
            temp_score = get_covered_cells(map_mask, building_matrix, range)
            # per_action_score[str((router,action))] = temp_score
            map_mask[router[0], router[1]] = 0
            restore_move(router, action)
            # router = [start_coord[0], start_coord[1]]
            if temp_score > best_score:
                best_move_set = (i, action, temp_score)
        map_mask[start_coord[0], start_coord[1]] = 1
    return best_move_set
    
def add_router(map_mask, building_matrix, router_list)->list:
    """
    add a router in one of the target area still to be covered by routers


    Args:
        map_mask (np.array): the mask of routers in the matrix
        building_matrix (np.array): the matrix representation of the building
        router_list (list): the list of router coordinates

    Returns:
        list: router list
    """
    covered_cells = set()
    for router_coords in zip(*router_list.nonzero()):
        # compute points covered by the router
        points_covered_by_router = get_points_around_router(
            map_mask,
            router_coords,
            range
        )
        # filter points covered by walls and void cells
        points_covered_by_router = filter_non_target_points(
            building_matrix,
            router_coords,
            points_covered_by_router
        )
        for covered_cell in points_covered_by_router:
            covered_cells.add(covered_cell)
            
    target_coord = set()
    for i, row in enumerate(building_matrix):
        for j, item in enumerate(row):
            if item == '.':
                target_coord.add((i,j))
    
    to_cover = target_coord.difference(covered_cell)
    if len(to_cover) == 0:
        # no need to add router
        # since all cells are covered
        return router_list
    i = random.sample(range(0, len(to_cover)), 1)
    router_list.add(to_cover[i])
    return router_list
    
    
def optimization_step(map_mask, building_matrix, router_list, range, policy, verbose=True):
    """
    first stupid implementation
    
    Calculate the global score, and chose the action that improves the overall score
    
    Args:
        map_mask (np.array): the mask of routers in the matrix
        building_matrix (np.array): the matrix representation of the building
        router_list (list): the list of router coordinates
        range (int): the router coverage range
        policy (Policy): the applied policy to find the move
        verbose (str): if True, the move taken and the difference about the score achieved is displayed

    Raise:
        NotValidPolicyExcception if the policy chosen is not a valid one, an exception is raised
    Returns:
        int: improving score
    """
    score = get_covered_cells(map_mask, building_matrix, range)

    if policy == Policy.BEST:
        move_set = best_move(score, map_mask, building_matrix, router_list, range)
    elif policy == Policy.GREEDY:
        move_set = greedy_move(score, map_mask, building_matrix, router_list, range)
    else:
        raise NotValidPolicyExcception("Not a valid policy")
    if len(move_set) != 3:
        print("no improving action")
        return 0
    chosen_router = router_list[move_set[0]]

    map_mask[chosen_router[0], chosen_router[1]] = 0
    move(chosen_router, move_set[1])
    map_mask[chosen_router[0], chosen_router[1]] = 1
    improved = move_set[2] - score
    if(verbose):
        print("OPTIMIZATION STEP:")
        print("\tscore before: {}\n\tascore after: {}".format(score, move_set[2]))
        print("\trouter: {}\t action:{}\n\tscore improved by: {}".format(move_set[0], move_set[1], improved))
        print_routers(building_matrix, router_list)
    return improved
        
def optimization_step_2(map_mask, building_matrix, router_list, range, policy, verbose=True):
    """
    second stupid implementation
    
    Uses the same idea from the first implementation, but if the local score is improved,
    then also the global score is improved too.
    
    Args:
        map_mask (np.array): the mask of routers in the matrix
        building_matrix (np.array): the matrix representation of the building
        router_list (list): the list of router coordinates
        range (int): the router coverage range
        policy (Policy): the applied policy to find the move
        verbose (str): if True, the move taken and the difference about the score achieved is displayed

    Returns:
        int : improving score
    """
    
    score = get_covered_cells(router_list, map_mask, range)
    covered_dict = {}
    per_action_score = {}
    # todo
    
    for router_coords in zip(*router_list.nonzero()):
        # compute points covered by the router
        points_covered_by_router = get_points_around_router(
            map_mask,
            router_coords,
            range
        )
        # filter points covered by walls and void cells
        points_covered_by_router = filter_non_target_points(
            building_matrix,
            router_coords,
            points_covered_by_router
        )

        for covered_cell in points_covered_by_router:
            if covered_cell not in covered_dict:
                covered_dict[covered_cell] = 1
            else:
                covered_dict[covered_cell] += 1
    
    return per_action_score
        