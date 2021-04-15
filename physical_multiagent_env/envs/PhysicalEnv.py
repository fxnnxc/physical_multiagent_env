from physical_multiagent_env.envs.PhysicalObjects import PhysicalObjects, Agent
import pybullet as p 
import numpy as np 
import time 
import pybullet_data 
import gym 
from gym.spaces import Dict


generate_random_position = lambda x : np.array([np.random.uniform(-x.map_size, x.map_size),
                                                    np.random.uniform(-x.map_size, x.map_size), 
                                                    0])

class PhysicalEnv(gym.Env):
    def __init__(self, config={}):
        super().__init__()
        p.connect(config.get("connect", p.DIRECT))
        p.setAdditionalSearchPath(pybullet_data.getDataPath())

        self.num_targets = config.get("num_targets", 1)
        self.num_agents = config.get("num_agents", 5)
        self.num_obstacles = config.get("num_obstacles", 5)
        self.map_size = config.get("map_size", 10)

        self.objects = {'target':[],
                        'agent':[], 
                        'obstacle':[]}


    def build_position(self, obj_type, position=None):
        if position is None:
            while True:
                conflict = False 
                position = generate_random_position(self)
                for object_type, object_list in self.objects.items():
                    for obj in object_list: 
                        if np.linalg.norm(np.array(position)- np.array(obj.position)) < 0.2:
                            conflict = True 
                            break 
                    if conflict:
                        break 
                if not conflict:
                    break 
        if obj_type == "target":
            obj = PhysicalObjects(position, "cube_small.urdf", scaling=2, color=[125,0,0,1])
        elif obj_type == "agent":
            obj = Agent(position, "cube_small.urdf", 6,  scaling=2, color=[0,125,0,1])
        elif obj_type == "obstacle":
            obj = PhysicalObjects(position, "cube_small.urdf" , scaling=2, color=[0,0,0,1])
        self.objects[obj_type].append(obj)

    # === simulation ===
    def reset(self):
        if self.objects:
            for object_type, object_list in self.objects.items():
                for obj in object_list:
                    obj.remove()
                object_list.clear()
             
        for _ in range(self.num_targets):
            self.build_position("target")
        for _ in range(self.num_agents):
            self.build_position("agent")
        for _ in range(self.num_obstacles):
            self.build_position("obstacle")

        self.observation_space = Dict({
            i: agent.observation_space for i, agent in enumerate(self.objects['agent'])
        })
        self.action_space = Dict({
            i : agent.action_space for i, agent in enumerate(self.objects['agent'])    
        })
        self.done = {i:False for i in range(len(self.objects['agent']))}
        self.done['__all__'] = False
        self.timestep = 0
        return {i : np.hstack([agent.position,
                               agent.velocity])
                for i, agent in enumerate(self.objects['agent'])}
        
    def step(self, agent_action):
        for agent, action in agent_action.items():
            self.objects['agent'][agent].take_action(action, bound=self.map_size)
        for target in self.objects['target']:
            target.move(target.move_kind, bound=self.map_size)
        for obstacle in self.objects['obstacle']:
            obstacle.move(obstacle.move_kind, bound=self.map_size)
        
        p.stepSimulation()

        for object_type, object_list in self.objects.items():
            for obj in object_list:
                obj.update()
                obj.decrease_velocity()
                obj.clip_velocity()

        state ={i : np.hstack([agent.position,
                               agent.velocity])
                for i, agent in enumerate(self.objects['agent'])}

        reward = self._reward(agent_action.keys())
        done = self._done(agent_action.keys())
        info = self._info()
        self.timestep +=1

        return state, reward, done, info

    def _reward(self, agents):
        raise NotImplementedError()
    
    def _done(self, agents):
        raise NotImplementedError()
    
    def _info(self):
        raise NotImplementedError()
    

# === Not working because reward, done, info are not implemented here ===
import time 
if __name__ == "__main__":
    env = PhysicalEnv({'connect':p.GUI})
    for i in range(10):
        env.reset()
        for i in range(1000):
            print(env.step({}))
            time.sleep(0.01)
