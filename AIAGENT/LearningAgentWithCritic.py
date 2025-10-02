# learning_agent_3rooms.py
# Learning Agent dengan 3 ruangan dan feedback benar/salah

import random

class LearningAgent:
    def __init__(self, location, environment, alpha=0.5, gamma=0.8, epsilon=0.2):
        """
        location: posisi awal agent ('room-A', 'room-B', 'room-C')
        environment: kondisi ruangan, contoh [['room-A', 'dirty'], ['room-B', 'clean'], ['room-C', 'dirty']]
        alpha: learning rate
        gamma: discount factor
        epsilon: probabilitas eksplorasi (random action)
        """
        self.environment = environment
        self.location = location
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.total_reward = 0

        # Q-Table: { (state, action): value }
        self.q_table = {}

    def get_state(self):
        """Representasi state: posisi + kondisi semua ruangan"""
        rooms = tuple((room[0], room[1]) for room in self.environment)
        return (self.location, rooms)

    def possible_actions(self):
        return ["clean", "move"]

    def perceive(self):
        """Mengamati kondisi ruangan saat ini"""
        for room in self.environment:
            if room[0] == self.location:
                return room
        return None

    def critic(self, action, perception):
        """Evaluasi aksi dan berikan reward + feedback benar/salah"""
        if action == "clean":
            if perception[1] == "dirty":
                print("✅ Benar: Membersihkan ruangan kotor.")
                return 10
            else:
                print("❌ Salah: Ruangan sudah bersih tapi dibersihkan lagi.")
                return -5
        elif action == "move":
            if any(room[1] == "dirty" for room in self.environment):
                print("➡️ Bagus: Pindah cari ruangan kotor.")
                return +3
            else:
                print("❌ Salah: Semua ruangan sudah bersih, pindah tidak perlu.")
                return -10
        return 0

    def clean(self, perception):
        """Membersihkan ruangan"""
        for room in self.environment:
            if room[0] == self.location:
                room[1] = "clean"

    def move(self):
        """Pindah ke ruangan lain (random sederhana)"""
        other_rooms = [room[0] for room in self.environment if room[0] != self.location]
        self.location = random.choice(other_rooms)

    def act(self, action, perception):
        """Lakukan aksi dan dapatkan reward"""
        if action == "clean":
            self.clean(perception)
        elif action == "move":
            self.move()

        reward = self.critic(action, perception)
        self.total_reward += reward
        return reward

    def choose_action(self, state):
        """Gunakan epsilon-greedy untuk pilih aksi"""
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(self.possible_actions())
        else:
            q_values = [self.q_table.get((state, a), 0) for a in self.possible_actions()]
            max_q = max(q_values)
            best_actions = [a for a in self.possible_actions() if self.q_table.get((state, a), 0) == max_q]
            return random.choice(best_actions)

    def learn(self, state, action, reward, next_state):
        """Update Q-Table"""
        old_q = self.q_table.get((state, action), 0)
        future_q = max([self.q_table.get((next_state, a), 0) for a in self.possible_actions()], default=0)
        new_q = old_q + self.alpha * (reward + self.gamma * future_q - old_q)
        self.q_table[(state, action)] = new_q

    def run(self, episodes=5, steps=10):
        for ep in range(1, episodes + 1):
            print(f"\n=== Episode {ep} ===")
            self.total_reward = 0
            for step in range(1, steps + 1):
                print(f"\n--- Step {step} ---")
                state = self.get_state()
                perception = self.perceive()
                print(f"[Perception] Agent di {self.location}, kondisi: {perception[1]}")

                action = self.choose_action(state)
                print(f"[Decision] Action dipilih: {action}")

                reward = self.act(action, perception)
                next_state = self.get_state()

                self.learn(state, action, reward, next_state)
                print(f"[Feedback] Action={action}, Reward={reward}, Total={self.total_reward}")
                print(f"[Q-Table] {self.q_table}")

                if all(room[1] == "clean" for room in self.environment):
                    print("\n🎯 Semua ruangan sudah bersih, berhenti lebih awal.")
                    break

            print(f"\n✅ Episode {ep} selesai, Total Reward: {self.total_reward}")


# Jalankan contoh
if __name__ == "__main__":
    environment = [['room-A', 'dirty'], ['room-B', 'clean'], ['room-C', 'dirty']]
    location = 'room-B'

    agent = LearningAgent(location, environment)
    agent.run(episodes=3, steps=10)
