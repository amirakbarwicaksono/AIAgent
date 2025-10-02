# learning_agent_3rooms_qtable.py
# Learning Agent dengan Q-learning untuk 3 ruangan + epsilon decay + save/load Q-table

import random
import pickle
import os
import matplotlib.pyplot as plt

class LearningAgent:
    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=1.0, epsilon_decay=0.99, epsilon_min=0.05, qtable_file="qtable.pkl"):
        self.q_table = {}  # (state, action) -> value
        self.actions = actions
        self.alpha = alpha          # learning rate
        self.gamma = gamma          # discount factor
        self.epsilon = epsilon      # awal: banyak explore
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.qtable_file = qtable_file

        # Coba load Q-table kalau ada file
        if os.path.exists(self.qtable_file):
            self.load_q_table()

    def get_state(self, environment, location):
        return (tuple([tuple(r) for r in environment]), location)

    def choose_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(self.actions)  # eksplorasi
        else:
            # eksploitasi
            q_values = [self.q_table.get((state, a), 0) for a in self.actions]
            max_q = max(q_values)
            return self.actions[q_values.index(max_q)]

    def update_q(self, state, action, reward, next_state):
        old_value = self.q_table.get((state, action), 0)
        next_max = max([self.q_table.get((next_state, a), 0) for a in self.actions], default=0)

        new_value = old_value + self.alpha * (reward + self.gamma * next_max - old_value)
        self.q_table[(state, action)] = new_value

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save_q_table(self):
        with open(self.qtable_file, "wb") as f:
            pickle.dump(self.q_table, f)
        print(f"💾 Q-table disimpan ke {self.qtable_file}")

    def load_q_table(self):
        with open(self.qtable_file, "rb") as f:
            self.q_table = pickle.load(f)
        print(f"📂 Q-table dimuat dari {self.qtable_file} (size: {len(self.q_table)})")

# ----- Environment -----
class Environment:
    def __init__(self):
        self.reset()

    def reset(self):
        # Reset ke kondisi awal (acak untuk variasi)
        self.environment = [
            ['room-A', random.choice(['dirty', 'clean'])],
            ['room-B', random.choice(['dirty', 'clean'])],
            ['room-C', random.choice(['dirty', 'clean'])]
        ]
        self.location = random.choice(['room-A', 'room-B', 'room-C'])
        return self.get_state()

    def get_state(self):
        return (tuple([tuple(r) for r in self.environment]), self.location)

    def step(self, action):
        reward = 0

        if action == "clean":
            for room in self.environment:
                if room[0] == self.location:
                    if room[1] == "dirty":
                        room[1] = "clean"
                        reward = 10
                    else:
                        reward = -2  # rugi bersihin ruangan bersih

        elif action == "move":
            dirty_rooms = [r for r in self.environment if r[1] == "dirty"]
            if dirty_rooms:
                next_room = random.choice(dirty_rooms)
                self.location = next_room[0]
                reward = 5
            else:
                reward = -10  # pindah padahal semua sudah bersih

        done = all(r[1] == "clean" for r in self.environment)
        return self.get_state(), reward, done

# ----- Training -----
if __name__ == "__main__":
    actions = ["clean", "move"]
    agent = LearningAgent(actions)

    env = Environment()
    episodes = 200
    rewards_per_episode = []

    for ep in range(episodes):
        state = env.reset()
        total_reward = 0

        for step in range(20):  # batas langkah per episode
            action = agent.choose_action(state)
            next_state, reward, done = env.step(action)

            agent.update_q(state, action, reward, next_state)

            state = next_state
            total_reward += reward

            if done:
                break

        agent.decay_epsilon()  # kurangi epsilon setelah setiap episode
        rewards_per_episode.append(total_reward)

        print(f"Episode {ep+1}, Total Reward: {total_reward}, Epsilon: {agent.epsilon:.3f}")

    # Simpan Q-table setelah training
    agent.save_q_table()

    # ----- Plot hasil belajar -----
    plt.plot(rewards_per_episode)
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.title("Learning Progress (Q-learning with Epsilon Decay)")
    plt.show()
