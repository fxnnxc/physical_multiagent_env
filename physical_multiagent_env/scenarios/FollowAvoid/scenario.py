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
        self.follow_intensity = 0.5
        self.avoid_intensity = 0.5 
        

    # Similar to the linear combination
    def set_phase(self, **kwargs):
        self.follow_intensity = kwargs.get("follow_intensity", 0.5)
        self.avoid_intensity = kwargs.get("avoid_intensity", 0.5)

    def step(self, agent_action):
        if self.timestep % 200 == 0:
            for object_type, object_list in self.objects.items():
                for obj in object_list:
                    obj.move_kind = random.choice(self.directions)
        if self.timestep % 50 == 0:
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
        # MAX : +10 (no collision and full target follwing)
        # MIN : -3 (collision at the last step)
        self.remove_candidates.clear()  
        reward = {a:0 for a  in agents}
        for a in agents:
            agent = self.objects['agent'][a]
            if p.getContactPoints(agent.pid):
                reward[a] -= 40/self.max_timestep * self.avoid_intensity
                self.remove_candidates.append(a)
            for target in self.objects['target']:
                distance = agent.distance(target)
                if 1 < distance < 1.2:
                    reward[a] +=20/self.max_timestep * self.follow_intensity 
                else:
                    reward[a] += -1/self.max_timestep
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
    config = {
        "connect" : p.GUI,
         "agent":{
            "globalScaling" : 1,
            "acc" : 2,
            "max_speed" : 5,
            "color" : [0,125,0,1]
        },
        "target":{
            "globalScaling" : 2,
            "acc" : 0.3,
            "max_speed" : 2,
            "color" : [0,0,125,1]
        },
        "obstacle":{
            "globalScaling" : 3,
            "color" : [125,125,125,1],
            "acc" : 0.0001,
            "max_speed" : 2
        },
        "num_agents" : 1,
        "num_obstacles" : 5,
        "num_targets" : 1,
        "map_size" : 2,
        "max_timestep" : 4000
    }

    env = FollowAvoid(config)
    
    for i in range(10):
        env.reset()
        for j in range(2000):
            alive_agents = []
            for index, agent in enumerate(env.objects['agent']):
                if agent.alive:
                    alive_agents.append(index)

            state, reward, done, info = env.step({i:0 for i in alive_agents})
            time.sleep(0.01)
            print(reward)