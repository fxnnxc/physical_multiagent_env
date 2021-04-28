from physical_multiagent_env.scenarios.FollowTemplate.scenario import *
from physical_multiagent_env.reinforcement_learning.utils.observation_functions import *


import time
import json 


transform = Observation_CNN.observation_fn_1


if __name__ == "__main__":
    with open("../../reinforcement_learning/FollowTemplate/version1.json") as f :
        config = json.load(f)

    config = config['env_config']
    config['connect'] = p.GUI

    env = FollowTemplate(config)
    
    for i in range(10):
        env.set_phase(phase=6)
        state = env.reset()
        
        for j in range(2000):
            alive_agents = []
            for index, agent in enumerate(env.objects['agent']):
                if agent.alive:
                    alive_agents.append(index)
            print(transform(state))
            if j%30==0:
                action = np.random.randint(5)

            state, reward, done, info = env.step({i:action for i in alive_agents})
            time.sleep(0.01)