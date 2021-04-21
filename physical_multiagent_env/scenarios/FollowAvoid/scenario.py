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
        self.follow_intensity = 1
        self.avoid_intensity = 1
        p.setTimeStep(0.01)
        

    # Similar to the linear combination
    def set_phase(self, **kwargs):
        self.follow_intensity = kwargs.get("follow_intensity", 0.5)
        self.avoid_intensity = kwargs.get("avoid_intensity", 0.5)
        self.num_obstacles = kwargs.get("num_obstacles", 10)

    def step(self, agent_action):
        if self.timestep % 200 == 0:
            for object_type, object_list in self.objects.items():
                for obj in object_list:
                    obj.move_kind = random.choice(self.directions)
        if self.timestep % 200 == 0:
            for target in self.objects['target']:
                target.move_kind = random.choice(self.directions)

        for agent, action in agent_action.items():
            self.objects['agent'][agent].take_action(action, bound=self.map_size)
        for target in self.objects['target']:
            target.move(target.move_kind, bound=self.map_size)
        for obstacle in self.objects['obstacle']:
            obstacle.move(obstacle.move_kind, bound=self.map_size)
        
        p.stepSimulation()

        for object_type, object_list in self.objects.items():
            for obj in object_list:
                if obj.alive:
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
        self.remove_candidates.clear()  
        reward = {a:0 for a  in agents}
        for a in agents:
            agent = self.objects['agent'][a]
            if p.getContactPoints(agent.pid):
                reward[a] -= 10/self.max_timestep * self.avoid_intensity
                self.remove_candidates.append(a)
            for target in self.objects['target']:
                distance = agent.distance(target)
                if 8 < distance < 1:
                    reward[a] += 1/self.max_timestep * self.follow_intensity 
                else:
                    reward[a] += -1/self.max_timestep * self.follow_intensity 
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
import json 
if __name__ == "__main__":
    with open("../../reinforcement_learning/FollowAvoid/version1.json") as f :
        config = json.load(f)

    config = config['env_config']
    config['connect'] = p.GUI

    env = FollowAvoid(config)
    
    for i in range(10):
        env.reset()
        for j in range(2000):
            alive_agents = []
            for index, agent in enumerate(env.objects['agent']):
                if agent.alive:
                    alive_agents.append(index)

            state, reward, done, info = env.step({i:1 for i in alive_agents})
            time.sleep(0.01)
            print(reward)