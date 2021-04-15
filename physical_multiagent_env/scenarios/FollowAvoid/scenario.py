from physical_multiagent_env.envs.PhysicalEnv import PhysicalEnv
import pybullet as p 
import numpy as np 
import random 

class FollowAvoid(PhysicalEnv):
    def __init__(self, config={}):
        super().__init__(config)
        self.max_timestep = config.get("max_timestep", 10000)
        self.remove_candidates =[]
        self.terminal_agent_num = np.clip(config.get("terminal_agent_num", 10), 1, self.num_agents)
        self.directions = ["x+", "x-", "y+", "y-"]    

    def step(self, agent_action):
        if self.timestep % 300 == 0:
            for object_type, object_list in self.objects.items():
                for obj in object_list:
                    obj.move_kind = random.choice(self.directions)

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

        state ={agent : np.hstack([self.objects['agent'][agent].position,
                                   self.objects['agent'][agent].velocity])
                    for agent in agent_action.keys()}

        reward = self._reward(agent_action.keys())
        done = self._done(agent_action.keys())
        info = self._info()
        self.timestep +=1
        return state, reward, done, info

    def _reward(self, agents): 
        # MAX : +10 (no collision and full target follwing)
        # MIN : -3 (collision at the last step)
        self.remove_candidates.clear()  
        reward = {a:-1/self.max_timestep for a  in agents}
        for a in agents:
            agent = self.objects['agent'][a]
            for obj_type, obj_list in self.objects.items():
                if obj_type != "agent":
                    for obj in obj_list:
                        distance = agent.distance(obj)
                        if (distance < agent.safe_boundary + obj.safe_boundary 
                                            and a not in self.remove_candidates):
                            reward[a] -= 2
                            self.remove_candidates.append(a)
            for target in self.objects['target']:
                distance = agent.distance(target)
                if 1 < distance < 1.2:
                    reward[a] +=20/self.max_timestep
        return reward 

    def _done(self, agents):
        for a in set(self.remove_candidates):
            self.done[a] = True 
            self.objects['agent'][a].remove()
        
        if (sum([v for v in self.done.values()]) >= self.terminal_agent_num):            
            self.done['__all__'] = True 
        if self.timestep > self.max_timestep:
            self.done['__all__'] = True 

        return self.done 
         
    def _info(self):
        return {}

import time 
if __name__ == "__main__":
    env = FollowAvoid({'connect':p.GUI})
    env.map_size = 5
    env.num_obstacles = 50
    env.num_agents = 1
    env.num_targets = 2
    for i in range(10):
        env.reset()
        for j in range(1000):
            state, reward, done, info = env.step({i:0 for i in range(env.num_agents)})
            time.sleep(0.01)