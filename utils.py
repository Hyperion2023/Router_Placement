import numpy as np
    
"""
calculate the fitness score of the router list
"""
def fitness(matrix, mask, router_pos, r):
    x,y = matrix.shape
    score = r * r
    start_x = 0
    end_x = x
    start_y = 0
    end_y = y 
    
    for router_x, router_y in router_pos:
        if router_x - r > 0:
            start_x = router_x - r
        if router_x + r +1 < x:
            end_x = router_x + r + 1
        if router_y - r > 0:
            start_y = router_y - r
        if router_y + r + 1 < y:
            end_y = router_y + r + 1 
            
        coverage_area = matrix[start_x:end_x, start_y:end_y]
        coverage_mask = mask[start_x:end_x, start_y:end_y]
    return coverage_area

    """
    scans each row of the matrix, should return how mush points it has covered
    """
def scan(matrix, dim , r):
    upper = 0
    lower = dim
    
    left = r - 1 
    right = r + 1
    
    upper, lower = closest_wall(matrix[r, upper:lower])
    
    while left > 0:
        if lower == r or upper == r:
            # non e' necessario continuare in quanto il muro 
            # e' allo stesso livello del router 
            # (se il muro ha una coordinata uguale al router
            # allora tutti i punti sopra/sotto/destra/sinistra,
            # non li copre)
            # stesso ragionamento va fatto per la parte destra
            break
        
            
        
    while right < len(dim): 
        if lower == r or upper == r:
            break
        
    
    # for row in enumerate(matrix[r:]):
        
    return

    """
    return the closest wall to the center of the line 
    (that's the a row of the matrix)
    """
def closest_wall(line, r):
    upper = 0
    lower = len(line)
    i = r
    while i < len(line):
        if line[i] == '#':
            lower = i-1
            break
        i += 1
    
    j = r
    while j > 0:
        if line[j] == '#':
            upper = j-1
            break
        j -= 1
    return (upper, lower)
        
    """
    the next step that would improve the fitness score
    """
def optimization_step():
    return 

    """
    utility function that prints the map
    """
def print_matrix(matrix):
    for row in matrix:
        for item in row:
            print(item, end='')
        print("")