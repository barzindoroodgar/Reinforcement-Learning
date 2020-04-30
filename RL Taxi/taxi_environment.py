import tkinter as tk
import copy
import reinforcement_learning as rl
    
class Environment:

    def __init__(self, gui, grid=None, 
                 taxi_i=None, taxi_j=None, 
                 pass_i=None, pass_j=None, 
                 dest_i=None, dest_j=None):
        
        self.pass_picked = False    # passenger picked up by taxi
        self.task_complete = False  # passenger dropped off at destination
        
        # values of various cell types in grid
        self.space_value = 0
        self.obstacle_value = 1
        self.taxi_value = 2
        self.pass_value = 3
        self.dest_value = 4
        
        # what the environemnt looks like at t = 0      
        self.grid_rows = 10
        self.grid_cols = 10
        
        if grid is None or len(grid) < self.grid_rows or len(grid[0]) < self.grid_cols:
            self.grid = [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 1, 0, 0, 0, 1, 1, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0, 0, 0, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 1, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 1, 0, 0, 0]]           
        else:
            self.grid = copy.deepcopy(grid)
            self.grid_rows = len(grid)
            self.grid_cols = len(grid[0])
            # assign taxi, passenger and destination locations from grid
            # if they have not been provided
            for r in range(self.grid_rows):
                for c in range(self.grid_cols):
                    if self.grid[r][c] == self.taxi_value:
                        if taxi_i is None:
                            taxi_i = r
                        if taxi_j is None:
                            taxi_j = c
                    elif self.grid[r][c] == self.pass_value:
                        if pass_i is None:
                            pass_i = r
                        if pass_j is None:
                            pass_j = c
                    elif self.grid[r][c] == self.dest_value:
                        if dest_i is None:
                            dest_i = r
                        if dest_j is None:
                            dest_j = c
            
        self.grid_width = 400
        self.grid_height = 400
        self.cell_width = self.grid_width / self.grid_cols
        self.cell_height = self.grid_height / self.grid_rows
        
        # determine initial taxi, passenge and destination locations in grid
        if taxi_i is None:
            self.taxi_i = 0
        else:           
            self.taxi_i = taxi_i
        if taxi_j is None:
            self.taxi_j = 0
        else:
            self.taxi_j = taxi_j
        if pass_i is None:
            self.pass_i = 9
        else:
            self.pass_i = pass_i
        if pass_j is None:
            self.pass_j = 4
        else:
            self.pass_j = pass_j
        if dest_i is None:
            self.dest_i = 9
        else:
            self.dest_i = dest_i
        if dest_j is None:
            self.dest_j = 9
        else:
            self.dest_j= dest_j
            
        self.grid[self.taxi_i][self.taxi_j] = self.taxi_value
        self.grid[self.pass_i][self.pass_j] = self.pass_value
        self.grid[self.dest_i][self.dest_j] = self.dest_value
        
        # colors of various types of cells
        self.space_color = "white"
        self.obstacle_color = "black"
        self.taxi_color = "yellow"
        self.pass_color = "blue"
        self.dest_color = "red"
        
        # canvas for drawing the environment
        self.center_gui(gui, windowWidth=self.grid_width, windowHeight=self.grid_height)
        self.canvas = tk.Canvas(gui, width=self.grid_width, height=self.grid_height)
        self.canvas.pack()
        self.draw_env()
    
    def center_gui(self, gui, windowWidth=None, windowHeight=None):
        
        # Gets the requested values of the height and width.
        if windowWidth == None or windowHeight == None:         
            windowWidth = gui.winfo_reqwidth()
            windowHeight = gui.winfo_reqheight()      
 
        # Gets both half the screen width/height and window width/height
        positionRight = int(gui.winfo_screenwidth()/2 - windowWidth/2)
        positionDown = int(gui.winfo_screenheight()/2 - windowHeight/2)
 
        # Positions the window in the center of the page.
        gui.geometry("+{}+{}".format(positionRight, positionDown))
    
    # draw the environment for the first time
    def draw_env(self):

        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):              
                if self.grid[i][j] == self.obstacle_value:
                    self.draw_obstacle(i, j)
                else:
                    self.draw_space(i, j)
        
        self.draw_taxi() 
        self.draw_pass() 
        self.draw_dest()
    
    # get a list of allowed actions based on state and environment
    def get_allowed_actions(self):
        actions = list()
        
        left_i = self.taxi_i - 1
        left_j = self.taxi_j
        right_i = self.taxi_i + 1
        right_j = self.taxi_j
        up_i = self.taxi_i
        up_j = self.taxi_j - 1
        down_i = self.taxi_i
        down_j = self.taxi_j + 1
        
        # left move allowed if no obstacles and within grid boundaries
        if self.cell_inbound(left_i, left_j) and self.grid[left_i][left_j] != self.obstacle_value:
            actions.append('w')
        # right move allowed if no obstacles and within grid boundaries
        if self.cell_inbound(right_i, right_j) and self.grid[right_i][right_j] != self.obstacle_value:
            actions.append('e')
        # up move allowed if no obstacles and within grid boundaries
        if self.cell_inbound(up_i, up_j) and self.grid[up_i][up_j] != self.obstacle_value:
            actions.append('n')
        # down move allowed if no obstacles and within grid boundaries
        if self.cell_inbound(down_i, down_j) and self.grid[down_i][down_j] != self.obstacle_value:
            actions.append('s')
        # dropping passenger allowed anywhere if passenger is picked up
        if self.pass_picked:        
            actions.append('d')
        # picking up passenger allowed only if taxi is at same locations
        elif self.taxi_i == self.pass_i and self.taxi_j == self.pass_j:           
            actions.append('p')
            
        return actions

    # execute the given action and return an immediate reward based on the current state
    def execute_action(self, a):
        # reward
        r = 0
        # moving west, east, north, south
        if a == 'w' or a == 'e' or a =='n' or a == 's':
            if a == 'w':
                next_i = self.taxi_i - 1
                next_j = self.taxi_j
            elif a == 'e':
                next_i = self.taxi_i + 1
                next_j = self.taxi_j
            elif a == 'n':
                next_i = self.taxi_i
                next_j = self.taxi_j - 1
            elif a == 's':
                next_i = self.taxi_i
                next_j = self.taxi_j + 1  
                
            self.updateEnv(next_i, next_j)
            
            if self.cell_inbound(next_i, next_j) and self.grid[next_i][next_j] != self.obstacle_value:
                r = -1
            else:
                r = -2
        # pick up
        elif a == 'p':
            # taxi has not picked up passenger yet
            if not self.pass_picked:
                # picking up passenger at the right location
                if self.taxi_i == self.pass_i and self.taxi_j == self.pass_j:
                    r = 0
                    self.draw_taxi() 
                    self.pass_picked = True
                # picking up passenger somewhere else
                else:
                    r = -2
            # passneger is already in taxi!
            else:
                r = -1
        # drop off
        elif a == 'd':
            # taxi has picked up passenger
            if self.pass_picked:
                # dropping passenger at destination
                if self.taxi_i == self.dest_i and self.taxi_j == self.dest_j:
                    r = 100
                    self.task_complete = True
                # dropping passenger somewhere else
                else:
                    r = -2
                self.draw_taxi() 
                self.pass_picked = False
            # passneger is not in taxi!
            else:
                r = -2
                
        return r
    
    # convert i, j oof environment grid to x,y for canvas
    def get_xy(self, i, j):
        return i*self.cell_width, j*self.cell_height  
    def taxi_xy(self):
        return self.taxi_i*self.cell_width, self.taxi_j*self.cell_height   
    def pass_xy(self):
        return self.pass_i*self.cell_width, self.pass_j*self.cell_height
    
    # drawing various types of cells in canvas
    # draw obstacle cell
    def draw_obstacle(self, i, j):
        x, y = self.get_xy(i, j)
        self.canvas.create_rectangle(x, y, x+self.cell_width, y+self.cell_height, fill=self.obstacle_color)
        
    # draw open space cell
    def draw_space(self, i, j):
        x, y = self.get_xy(i, j)
        self.canvas.create_rectangle(x, y, x+self.cell_width, y+self.cell_height, fill=self.space_color)
        
    # taxi cell
    def draw_taxi(self):
        x, y = self.get_xy(self.taxi_i, self.taxi_j)
        self.canvas.create_rectangle(x, y, x+self.cell_width, y+self.cell_height, fill=self.taxi_color)
        
        if self.pass_picked:
            self.draw_pass()
            
    # delete taxi from cell (make open space as it moves)
    def del_taxi(self):
        x, y = self.get_xy(self.taxi_i, self.taxi_j)
        self.canvas.create_rectangle(x, y, x+self.cell_width, y+self.cell_height, fill=self.space_color)
        
    # draw passenger
    def draw_pass(self):
        x, y = self.get_xy(self.pass_i, self.pass_j)
        self.canvas.create_rectangle(x+self.cell_width*0.25, y+self.cell_height*0.25, 
                                     x+self.cell_width*0.75, y+self.cell_height*0.75, fill=self.pass_color)
        
    # delete star (for destination)
    def polygon_star_points(self, x, y):
        p=self.cell_width/2
        t=self.cell_width/10
        points = []
        for i in (1,-1):
            points.extend((x, y + i*p))
            points.extend((x + i*t, y + i*t))
            points.extend((x + i*p, y))
            points.extend((x + i*t, y - i * t))
        return points  
    
    # draw destination
    def draw_dest(self):
        x, y = self.get_xy(self.dest_i, self.dest_j)
        points = self.polygon_star_points(x + self.cell_width/2, y+self.cell_height/2)
        self.canvas.create_polygon(points, outline=self.dest_color, fill=self.dest_color, width=1)
        
    # check if given cell coordiantes are in environment boundaries
    def cell_inbound(self, i, j):
        if i >= 0 and i < self.grid_rows and j >= 0 and j < self.grid_cols:
            return True
        else:
            return False
        
    # update the environemnt as the taxi moves (based on next position)
    def updateEnv(self, next_i, next_j):
        if self.cell_inbound(next_i, next_j) and self.grid[next_i][next_j] != self.obstacle_value:
            
            self.del_taxi()
            # if current position is passenger or destination
            # redraw passenger when taxi leaves
            if self.taxi_i == self.pass_i and self.taxi_j == self.pass_j and not self.pass_picked:
                self.grid[self.pass_i][self.pass_j] = self.pass_value             
                self.draw_pass()
            # redraw destination when taxi leaves
            elif self.taxi_i == self.dest_i and self.taxi_j == self.dest_j:
                self.grid[self.dest_i][self.dest_j] = self.dest_value
                self.draw_dest()
            # else make previous position an open space
            else:
                self.grid[self.taxi_i][self.taxi_j] = self.space_value
                
            # update taxi position
            self.taxi_i = next_i
            self.taxi_j = next_j
            if self.pass_picked:
                self.pass_i = next_i
                self.pass_j = next_j
                
            # move taxi to new position
            self.grid[self.taxi_i][self.taxi_j] = self.taxi_value
            self.draw_taxi()
    
    #def __del__(self): 
            
    ### ----- for manual movements ----- ###
    def moveLeft(self, event): 
        next_i = self.taxi_i - 1
        next_j = self.taxi_j
        self.updateEnv(next_i, next_j)
    
    def moveRight(self, event): 
        next_i = self.taxi_i + 1
        next_j = self.taxi_j
        self.updateEnv(next_i, next_j)
        
    def moveUp(self, event): 
        next_i = self.taxi_i
        next_j = self.taxi_j - 1
        self.updateEnv(next_i, next_j)
        
    def moveDown(self, event): 
        next_i = self.taxi_i
        next_j = self.taxi_j + 1
        self.updateEnv(next_i, next_j)
        
    def passActions(self, event): 
        if (self.taxi_i == self.pass_i and self.taxi_j == self.pass_j):
            self.pass_picked = not self.pass_picked
            next_i = self.taxi_i
            next_j = self.taxi_j
            self.draw_taxi() 
    ### ------------------------------- ###

def get_state(env, taxi_i=None, taxi_j=None, pass_i=None, pass_j=None, dest_i=None, dest_j=None, pass_picked=None):
    
    # give default values to parameters
    if taxi_i == None:
        taxi_i = env.taxi_i
    if taxi_j == None:
        taxi_j = env.taxi_j
    if pass_i == None:
        pass_i = env.pass_i
    if pass_j == None:
        pass_j = env.pass_j
    if dest_i == None:
        dest_i = env.dest_i
    if dest_j == None:
        dest_j = env.dest_j
    if pass_picked == None:
        pass_picked = env.pass_picked

    # figure out cell values surrounding the taxi for state definition
    north_i = taxi_i
    north_j = taxi_j - 1
    north_cell = env.obstacle_value
    if env.cell_inbound(north_i, north_j) and env.grid[north_i][north_j] != env.obstacle_value:
        north_cell = env.grid[north_i][north_j]

    east_i = taxi_i + 1
    east_j = taxi_j   
    east_cell = env.obstacle_value
    if env.cell_inbound(east_i, east_j) and env.grid[east_i][east_j] != env.obstacle_value:
        north_cell = env.grid[east_i][east_j]

    south_i = taxi_i
    south_j = taxi_j + 1
    south_cell = env.obstacle_value
    if env.cell_inbound(south_i, south_j) and env.grid[south_i][south_j] != env.obstacle_value:
        north_cell = env.grid[south_i][south_j]

    west_i = taxi_i - 1
    west_j = taxi_j
    west_cell = env.obstacle_value
    if env.cell_inbound(west_i, west_j) and env.grid[west_i][west_j] != env.obstacle_value:
        north_cell = env.grid[west_i][west_j]

    # create state object
    s = rl.state(taxi_i=taxi_i, taxi_j=taxi_j, 
                 pass_i=pass_i, pass_j=pass_j, 
                 dest_i=dest_i, dest_j=dest_j, 
                 north_cell=north_cell, east_cell=east_cell,
                 south_cell=south_cell, west_cell=west_cell,
                 pass_picked=pass_picked)
    return s

small_grid = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 1, 0, 1],
    [2, 0, 0, 0, 0, 0, 0, 0, 3, 1],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
    [4, 0, 0, 1, 0, 0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0]]  

big_grid = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 3, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0],
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 2, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 4]]

huge_grid = [
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0], 
    [0, 0, 0, 3, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0],
    [0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0],
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 2, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 4, 1, 0, 0, 0, 0]]
