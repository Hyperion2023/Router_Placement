import Data
import numpy as np
import random
from enum import Enum
from utils import get_number_covered_cells
from utils import get_points_around_router
from utils import filter_non_target_points
from utils import print_routers

class NotValidPolicyExcception(Exception):
    pass

class Action(Enum):
    LEFT = (0, -1)
    RIGHT = (0, 1)
    UP = (-1, 0)
    DOWN = (1, 0)
    ADD = (0, 0)

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
    
#region naive optimization move
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
            temp_score = get_number_covered_cells(map_mask, building_matrix, range)
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
            temp_score = get_number_covered_cells(map_mask, building_matrix, range)
            # per_action_score[str((router,action))] = temp_score
            map_mask[router[0], router[1]] = 0
            restore_move(router, action)
            # router = [start_coord[0], start_coord[1]]
            if temp_score > best_score:
                best_move_set = (i, action, temp_score)
        map_mask[start_coord[0], start_coord[1]] = 1
    return best_move_set
    
def add_router(map_mask, building_matrix, router_list, _range):
    """
    add a router in one of the target area still to be covered by routers


    Args:
        map_mask (np.array): the mask of routers in the matrix
        building_matrix (np.array): the matrix representation of the building
        router_list (list): the list of router coordinates
        _range (int): coverage range of the routers

    Returns:
        np.array, list: mask of routers and the new router list
    """
    covered_cells = set()
    for router_coords in zip(*map_mask.nonzero()):
        # compute points covered by the router
        points_covered_by_router = get_points_around_router(
            map_mask,
            router_coords,
            _range
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
    
    to_cover = target_coord-covered_cells
    # print("target_coord: {}".format(target_coord))
    # print("target_coord.type: {}".format(type(target_coord)))
    # print("covered_cells: {}".format(covered_cells))
    # print("covered_cells.type: {}".format(type(covered_cells)))
    # print("to_cover: {}".format(to_cover))
    if len(to_cover) == 0:
        # no need to add router
        # since all cells are covered
        return map_mask, router_list
    i = random.sample(range(len(to_cover)), 1)
    new_router = to_cover[i]
    router_list.add(new_router)
    map_mask[new_router[0], new_router[1]] = 1
    return map_mask, router_list
    
    
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
    score = get_number_covered_cells(map_mask, building_matrix, range)

    if policy == Policy.BEST:
        move_set = best_move(score, map_mask, building_matrix, router_list, range)
    elif policy == Policy.GREEDY:
        move_set = greedy_move(score, map_mask, building_matrix, router_list, range)
    else:
        raise NotValidPolicyExcception("Not a valid policy")
    if len(move_set) != 3:
        # try to add a new router
        print("trying to add new router...", end="")
        map_mask, router_list = add_router(map_mask, building_matrix, router_list, range)
        add_score = get_number_covered_cells(map_mask, building_matrix, range)
        if add_score == score:
            print("no improving action")
            return 0
        print("success")
        move_set = (len(router_list)-1, Action.ADD, add_score)
        
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

#endregion    
    

#region better implementation of the search algorithm
class Search:
    """
    the search class, based on the naive implementation but instead calculating each time the overall
    score, we calculate the score locally in the router coverage (it should be faster) 
    """
    def __init__(self, map_mask, building_matrix, router_list, target_coords, range) -> None:
        """Constructor
        initialize the coverage of each router in a dictionary form s.t. the pair <key, value> are defined as:
         - key is the coordinates the each covered cell
         - value is how many routers have covered that cell

        Args:
            map_mask (np.array): the mask that represents the router on the map (aka building_matrix)
            building_matrix (np.array): the representation of the building
            router_list (list): list of router coordinates
            range (int): the coverage range of the routers
        """
        self.covered_dict = {}
        self.map_mask = map_mask
        self.building_matrix = building_matrix
        self.router_list = router_list
        self.range = range
        self.target_coords = target_coords
        self.cached_move_set = None
        
        for router_coords in zip(*map_mask.nonzero()):
            points_covered_by_router = self.get_router_coverage(router_coords)
            for covered_cell in points_covered_by_router:
                if covered_cell not in self.covered_dict.keys():
                    self.covered_dict[covered_cell] = 1
                else:
                    self.covered_dict[covered_cell] += 1
                    
    def get_router_coverage(self, router_coords) -> list:
        """gets the local coverage of the router with coordinates router_coords

        Args:
            router_coords (list): the coordinate of the router

        Returns:
            list: the list of covered points
        """
        # compute points covered by the router
        points_covered_by_router = get_points_around_router(
        self.map_mask,
        router_coords,
        self.range
        )
        # filter points covered by walls and void cells
        points_covered_by_router = filter_non_target_points(
            self.building_matrix,
            router_coords,
            points_covered_by_router
        )
        return points_covered_by_router
    
    def calc_cost(self, new_pos, decreased) -> int:
        """calculate the improvement by moveing a router into new_pos

        Args:
            new_pos (list): the new coordinate of a router
            decreased (int): decreased coverage 

        Returns:
            int: improvement in term of coverage
        """
        new_pos_coverage = self.get_router_coverage(new_pos)
        increase = 0
        for new_cov in new_pos_coverage:
            # assert(self.covered_dict[new_cov] >= 0)
            if (new_cov not in self.covered_dict or
                self.covered_dict[new_cov] == 0):
                increase += 1
        return increase - decreased
    
    def update(self, moveset):
        """update the state by moving the router
        updates: 
        - the map mask of router
        - coverage dictionary
        
        Args:
            moveset (tuple): a triplet containing the router index, action and improving score (the last one not used in this function)
        """
        if len(moveset) != 3:
            return
        # print("router:{}, action:{}, improvement:{}".format(moveset[0], moveset[1], moveset[2]))
        router = self.router_list[moveset[0]]
        action = moveset[1]
        if action is not Action.ADD:
            self.map_mask[router[0], router[1]] = 0
            # -1 for all cell in the old position
            old_pos_coverage = self.get_router_coverage(router)
            for old_cov in old_pos_coverage:
                self.covered_dict[old_cov] -= 1
            
            # update for the new position
            # print("updating dict:")
            move(router, action)
        self.map_mask[router[0], router[1]] = 1
        new_pos_coverage = self.get_router_coverage(router)
        for new_cov in new_pos_coverage:
            # print(new_cov)
            if new_cov not in self.covered_dict:
                self.covered_dict[new_cov] = 1
            else:
                self.covered_dict[new_cov] += 1
                
    def do_cached(self):
        """caches the last action done
        in such way we can significantly improve each optimization step in terms of time
        we store the last router updated and try to push this router to its maximum coverage

        Returns:
            tuple: the triple of <router idx, action, improvement score>
        """
        router_idx = self.cached_move_set[0]
        action = self.cached_move_set[1]
        router = self.router_list[router_idx]
        boundary = self.map_mask.shape
        best_improve = 0
        best_move_set = ()
        start_coord = [router[0], router[1]]
        self.map_mask[start_coord[0], start_coord[1]] = 0
        old_pos_coverage = self.get_router_coverage(router)
        decreased = 0
        for old_cov in old_pos_coverage:
            # print("oldcov:{}".format(old_cov))
            assert old_cov in self.covered_dict, f"covered_dict:{self.covered_dict} \n old_cov:{old_cov}"
            self.covered_dict[old_cov] -= 1
            if self.covered_dict[old_cov] == 0:
                decreased += 1
        
        for action in Action:
            move(router, action)
            # violating the boundary, should be reset
            if ((router[0] >= boundary[0] or router[0] < 0) or 
                (router[1] >= boundary[1] or router[1] < 0)):
                restore_move(router, action)
                continue
            # checking if improved the fitness
            improvement = self.calc_cost(router, decreased)
            restore_move(router, action)
            if improvement > best_improve:
                best_move_set = (router_idx, action, improvement)
                best_improve = improvement
        for old_cov in old_pos_coverage:
                self.covered_dict[old_cov] += 1
        self.map_mask[start_coord[0], start_coord[1]] = 1
        return best_move_set
                
    def greedy_move(self):
        """the greedy move action, this retuns the first move triplet that improves the coverage

        Returns:
            tuple: the first triplet <router idx, action, improvement score> that improves the overall coverage
        """
        # see if can use cache
        greedy_move_set = ()
        if (self.cached_move_set is not None):
            greedy_move_set = self.do_cached()
            if greedy_move_set is not None:
                return greedy_move_set
        boundary = self.map_mask.shape
        for i, router in enumerate(self.router_list):
            # setting up the coverage and mask
            start_coord = [router[0], router[1]]
            self.map_mask[start_coord[0], start_coord[1]] = 0
            old_pos_coverage = self.get_router_coverage(router)
            decreased = 0
            for old_cov in old_pos_coverage:
                assert old_cov in self.covered_dict, f"old_cov:{old_cov}"
                self.covered_dict[old_cov] -= 1
                if self.covered_dict[old_cov] == 0:
                    decreased += 1
            
            for action in Action:
                move(router, action)
                # violating the boundary, should be reset
                if ((router[0] >= boundary[0] or router[0] < 0) or 
                    (router[1] >= boundary[1] or router[1] < 0)):
                    restore_move(router, action)
                    continue
                # checking if improved the fitness
                improvement = self.calc_cost(router, decreased)
                restore_move(router, action)
                if improvement > 0:
                    greedy_move_set = (i, action, improvement)
                    self.map_mask[start_coord[0], start_coord[1]] = 1
                    # self.update(greedy_move_set)
                    for old_cov in old_pos_coverage:
                        self.covered_dict[old_cov] += 1
                    return greedy_move_set
                
            # restore of the coverage and mask
            for old_cov in old_pos_coverage:
                self.covered_dict[old_cov] += 1
            self.map_mask[start_coord[0], start_coord[1]] = 1
        return greedy_move_set
    
    def best_move(self):
        """the best move action, this retuns the best move triplet that improves the coverage

        Returns:
            tuple: the best triplet <router idx, action, improvement score> that improves the overall coverage
        """
        best_move_set = ()
        best_improve = 0
        if (self.cached_move_set is not None):
            best_move_set = self.do_cached()
            if best_move_set is not None:
                return best_move_set                
        
        boundary = self.map_mask.shape
        for i, router in enumerate(self.router_list):
            # setting up the coverage and mask
            start_coord = [router[0], router[1]]
            self.map_mask[start_coord[0], start_coord[1]] = 0
            old_pos_coverage = self.get_router_coverage(router)
            decreased = 0
            for old_cov in old_pos_coverage:
                # print("oldcov:{}".format(old_cov))
                assert old_cov in self.covered_dict, f"covered_dict:{self.covered_dict} \n old_cov:{old_cov}"
                self.covered_dict[old_cov] -= 1
                if self.covered_dict[old_cov] == 0:
                    decreased += 1
            
            for action in Action:
                move(router, action)
                # violating the boundary, should be reset
                if ((router[0] >= boundary[0] or router[0] < 0) or 
                    (router[1] >= boundary[1] or router[1] < 0)):
                    restore_move(router, action)
                    continue
                # checking if improved the fitness
                improvement = self.calc_cost(router, decreased)
                restore_move(router, action)
                if improvement > best_improve:
                    best_move_set = (i, action, improvement)
                    best_improve = improvement
                
            # restore of the coverage and mask
            for old_cov in old_pos_coverage:
                self.covered_dict[old_cov] += 1
            self.map_mask[start_coord[0], start_coord[1]] = 1
        return best_move_set
    
    def add_router(self, patient = 5):
        """tries to add a new router in the map with some patience
        if after patient pass in a row I can't find an improvement

        Args:
            patient (int, optional): an interger, greater it is, slower the algorithm is. Defaults to 5.

        Returns:
            np.array, int: the coordinate for the new router and how much new points is possibile to cover
        """
        covered_cells = set(self.covered_dict.keys())
        target_coord = set(self.target_coords)
        # for i, row in enumerate(self.building_matrix):
        #     for j, item in enumerate(row):
        #         if item == '.':
        #             target_coord.add((i,j))
        
        to_cover = target_coord-covered_cells
        if len(to_cover) == 0:
            return
        # test where placing the router maximizes the coverage
        max_increment_coord = None
        max_increment = 0
        increment = 0
        wait = 0
        for coord in to_cover:
            # print(f"testing: {i}-coord")
            increment = self.calc_cost(coord, 0)
            if increment > max_increment:
                max_increment = increment
                max_increment_coord = np.reshape(np.array(coord), (1,2))# forcing the dimension of the new coordinates
                wait = 0
            else:
                wait+=1
            if max_increment == (self.range*2 + 1)**2 or wait == patient:
                return max_increment_coord, max_increment
        return max_increment_coord, max_increment
    def remove_router(self):
        # todo 
        # here should test if removing a router we loses score and how much we loose
        # how can we test if removing a router is worth?
        pass
    
    def optimization_step(self, policy, verbose=0):
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
        
        if policy == Policy.BEST:
            move_set = self.best_move()
        elif policy == Policy.GREEDY:
            move_set = self.greedy_move()
        else:
            raise NotValidPolicyExcception("Not a valid policy")
        
        if len(move_set) != 3:
            print("no improving action...", end="")
            print("trying to add a new router ", end="")
            pair = self.add_router()
            if  pair is not None:
                print("success")
                # print("-"*50)
                # print(f"coords: {pair[0]}")
                # print(f"type of pair[0]: {type(pair[0])}")
                # print(f"pair[0] shape: {pair[0].shape}")
                # print(f"router list shape: {self.router_list.shape}")
                # print(f"router list before inserting: {[item for item in self.router_list]}")
                # print(f"router len before inserting: {len(self.router_list)}")
                self.router_list = np.append(self.router_list, pair[0], axis=0)
                # print(f"router list after inserting: {[item for item in self.router_list]}")
                # print(f"router len after inserting: {len(self.router_list)}")
                # print("-"*50) 
                move_set = (len(self.router_list)-1, Action.ADD, pair[1])
                print(f"number of router: {len(self.router_list)}")
            else:
                print("fail")
                return 0
        self.update(move_set)
        self.cached_move_set = move_set

        if(verbose < 2):
            print("\trouter: {}\t action:{}\n\tscore improved by: {}".format(move_set[0], move_set[1], move_set[2]))
        if verbose >= 2:
            print_routers(self.building_matrix, self.router_list)

        return move_set[2]
#endregion