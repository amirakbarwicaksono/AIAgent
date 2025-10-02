# mas_qlearning_shared_commQ.py
import random
import pickle
from collections import defaultdict

class MultiAgentEnv:
    def __init__(self, n_agents=3):
        self.rooms = ["room-A", "room-B", "room-C"]
        self.n_agents = n_agents
        self.reset()

    def reset(self):
        self.state = {room: "dirty" for room in self.rooms}
        self.locations = {f"agent{i}": random.choice(self.rooms) for i in range(self.n_agents)}
        return self.state, self.locations

    def step(self, actions):
        rewards = {agent: 0 for agent in actions}

        for agent, action in actions.items():
            loc = self.locations[agent]

            if action == "clean":
                if self.state[loc] == "dirty":
                    self.state[loc] = "clean"
                    rewards[agent] = 10
                else:
                    rewards[agent] = -2

            elif action.startswith("move"):
                target = "-".join(action.split("-")[1:])
                if target in self.rooms:
                    self.locations[agent] = target
                    rewards[agent] = -1
                else:
                    rewards[agent] = -5

        done = all(v == "clean" for v in self.state.values())
        return (self.state, self.locations, rewards), done

class QLearningAgent:
    def __init__(self, name, actions, alpha=0.1, gamma=0.9, epsilon=1.0):
        self.name = name
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        # gunakan fungsi bawaan, bukan lambda
        self.q_table = defaultdict(self._default_action_values)

    def _default_action_values(self):
        return {a: 0.0 for a in self.actions}

    def get_state_key(self, state, locs):
        return str(state) + "|" + str(locs[self.name])

    def choose_action(self, state, locs):
        state_key = self.get_state_key(state, locs)
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        return max(self.q_table[state_key], key=self.q_table[state_key].get, default=random.choice(self.actions))

    def learn(self, state, locs, action, reward, next_state, next_locs):
        state_key = self.get_state_key(state, locs)
        next_key = self.get_state_key(next_state, next_locs)

        q_predict = self.q_table[state_key][action]
        q_target = reward + self.gamma * max(self.q_table[next_key].values())
        self.q_table[state_key][action] += self.alpha * (q_target - q_predict)

    def export_q_table(self):
        """Convert ke dict biasa agar bisa di-pickle"""
        return dict(self.q_table)

def train(episodes=200, n_agents=3):
    env = MultiAgentEnv(n_agents=n_agents)
    actions = ["clean"] + [f"move-{room}" for room in env.rooms]
    agents = [QLearningAgent(f"agent{i}", actions) for i in range(n_agents)]

    comm_q = defaultdict(float)

    for ep in range(1, episodes + 1):
        state, locs = env.reset()
        total_rewards = {a.name: 0 for a in agents}
        done = False

        while not done:
            acts = {a.name: a.choose_action(state, locs) for a in agents}
            (next_state, next_locs, rewards), done = env.step(acts)

            avg_reward = sum(rewards.values()) / len(rewards)
            for a in agents:
                total_rewards[a.name] += avg_reward
                a.learn(state, locs, acts[a.name], avg_reward, next_state, next_locs)

                comm_key = (acts[a.name], tuple(sorted(state.items())))
                comm_q[comm_key] += avg_reward * 0.1

            state, locs = next_state, next_locs

        for a in agents:
            a.epsilon = max(0.05, a.epsilon * 0.99)

        if ep % 10 == 0 or ep == 1:
            print(f"Episode {ep}: rewards = " + ", ".join([f"{k}:{v}" for k, v in total_rewards.items()]))

    # ✅ Simpan Q-table sebagai dict biasa
    with open("mas_qtable.pkl", "wb") as f:
        pickle.dump([a.export_q_table() for a in agents], f)
    print("💾 Q-tables saved to mas_qtable.pkl")

if __name__ == "__main__":
    train(episodes=200)
