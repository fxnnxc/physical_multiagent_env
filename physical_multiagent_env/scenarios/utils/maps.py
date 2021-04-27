class GridMap1:
    def __init__(self):
        self.init_position = [5,5,0]
        self.target_position = [8,8,0]
        self.agent_position = [1,1,0]
        self.width = 10
        self.height = 10
        self.map1 = [[1,1,1,1,1, 1,1,1,1,1],      # 1
                    [1,0,0,0,0, 0,0,0,0,1],     
                    [1,0,0,0,0, 0,0,0,0,1],
                    [1,0,0,0,0, 0,0,0,0,1],
                    [1,0,0,0,0, 0,0,0,0,1],      # 5 
                    [1,0,0,0,0, 0,0,0,0,1],
                    [1,0,0,0,0, 0,0,0,0,1],
                    [1,0,0,0,0, 0,0,0,0,1],
                    [1,0,0,0,0, 0,0,0,0,1],
                    [1,1,1,1,1, 1,1,1,1,1],      # 10
        ]
        self.num_obstacles = sum([sum(b) for b in self.map1])

class GridMap2:
    def __init__(self):
        self.init_position = [5,5,0]
        self.target_position = [8,4,0]
        self.agent_position = [1,4,0]
        self.width = 10
        self.height = 10
        self.map1 = [[1,1,1,1,1, 1,1,1,1,1],      # 1
                    [1,0,0,0,0, 0,0,0,0,1],     
                    [1,0,0,0,0, 0,0,0,0,1],
                    [1,0,0,0,0, 0,0,0,0,1],
                    [1,0,0,0,1, 1,0,0,0,1],      # 5 
                    [1,0,1,1,0, 0,1,1,0,1],
                    [1,0,0,0,0, 0,0,0,0,1],
                    [1,0,0,0,0, 0,0,0,0,1],
                    [1,0,0,0,0, 0,0,0,0,1],
                    [1,1,1,1,1, 1,1,1,1,1],      # 10
        ]
        self.num_obstacles = sum([sum(b) for b in self.map1])

class GridMap3:
    def __init__(self):
        self.init_position = [5,5,0]
        self.target_position = [4,4,0]
        self.agent_position = [2,4,0]
        self.width = 10
        self.height = 10
        self.map1 = [[1,1,1,1,1, 1,1,1,1,1],      # 1
                    [1,0,0,0,0, 0,0,0,0,1],     
                    [1,0,1,1,0, 0,1,1,0,1],
                    [1,0,1,1,1, 1,1,1,0,1],
                    [1,0,1,1,0, 0,1,1,0,1],      # 5 
                    [1,0,1,1,0, 0,1,1,0,1],
                    [1,0,1,1,0, 0,1,1,0,1],
                    [1,0,0,0,0, 0,0,0,0,1],
                    [1,0,0,0,0, 0,0,0,0,1],
                    [1,1,1,1,1, 1,1,1,1,1],      # 10
        ]
        self.num_obstacles = sum([sum(b) for b in self.map1])

        

