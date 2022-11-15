import Data
from enum import Enum
from utils import *
from utils import get_covered_cells


class Action(Enum):
    LEFT = (0, -1)
    RIGHT = (0, 1)
    UP = (-1, 0)
    DOWN = (1, 0)

class Policy(Enum):
    GREEDY = 1
    BEST = 2

def move(router: list,
         action: Action):
    """
    moves a router in the direction requested
    no check in the boundary, since routers are generated inside interested point,
    and those are not on borders

    Args:
        router (list): the router coordinate
        action (Action): action taken from Action

    Returns:
        _type_: new coordinate for router
    """
    router[0] = router[0] + action.value[0]
    router[1] = router[1] + action.value[1]
    return router
    
def greedy_move(actual_score, map_mask, building_matrix, router_list):
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
    for i, router in enumerate(router_list):
        start_coord = [router[0], router[1]]
        map_mask[start_coord[0], start_coord[1]] = 0
        for action in Action:
            move(router, action)
            map_mask[router[0], router[1]] = 1
            temp_score = get_covered_cells(map_mask, building_matrix, range)
            map_mask[router[0], router[1]] = 0
            router = [start_coord[0], start_coord[1]]
            if temp_score > actual_score:
                greedy_move_set = (i, action, temp_score)
                map_mask[start_coord[0], start_coord[1]] = 1
                return greedy_move_set
                
        map_mask[start_coord[0], start_coord[1]] = 1
    
    return greedy_move_set

def best_move(actual_score, map_mask, building_matrix, router_list):
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
    per_action_score = {}
    best_move_set = ()
    best_score = actual_score
    for i, router in enumerate(router_list):
        start_coord = [router[0], router[1]]
        map_mask[start_coord[0], start_coord[1]] = 0
        for action in Action:
            move(router, action)
            map_mask[router[0], router[1]] = 1
            temp_score = get_covered_cells(map_mask, building_matrix, range)
            per_action_score[str((router,action))] = temp_score
            map_mask[router[0], router[1]] = 0
            router = [start_coord[0], start_coord[1]]
            if temp_score > best_score:
                best_move_set = (i, action, temp_score)
        map_mask[start_coord[0], start_coord[1]] = 1
    return best_move_set
    
def optimization_step(map_mask, building_matrix, router_list, range, policy):
    """
    first stupid implementation
    Args:
        map_mask (np.array): the mask of routers in the matrix
        building_matrix (np.array): the matrix representation of the building
        router_list (list): the list of router coordinates
        range (int): the router coverage range
        policy (Policy): the applied policy to find the move

    Returns:
        _type_: new coordinate for router
    """
    score = get_covered_cells(map_mask, building_matrix, range)
    # per_action_score = {}
    # for router in router_list:
    #     start_coord = [router[0], router[1]]
    #     map_mask[start_coord[0], start_coord[1]] = 0
    #     for action in Action:
    #         move(router, action)
    #         map_mask[router[0], router[1]] = 1
    #         temp_score = get_covered_cells(map_mask, building_matrix, range)
    #         per_action_score[str((router,action))] = temp_score
    #         map_mask[router[0], router[1]] = 0
    #         router = [start_coord[0], start_coord[1]]
    #     map_mask[start_coord[0], start_coord[1]] = 1
    
    if policy == Policy.BEST:
        move = best_move(score, map_mask, building_matrix, router_list, range)
    elif policy == Policy.GREEDY:
        move = greedy_move(score, map_mask, building_matrix, router_list, range)
    chosen_router = router_list[move[0]]
    
    map_mask[chosen_router[0], chosen_router[1]] = 0
    move(chosen_router, move[1])
    map_mask[chosen_router[0], chosen_router[1]] = 1
        
def optimization_step_2(routers, map_mask, range):
    """
    second stupid implementation
    
    Args:
        map_mask (np.array): the mask of routers in the matrix
        building_matrix (np.array): the matrix representation of the building
        router_list (list): the list of router coordinates
        range (int): the router coverage range

    Returns:
        _type_: new coordinate for router
    """
    
    score = get_covered_cells(routers, map_mask, range)
    per_action_score = {}
    # todo
    return per_action_score
        