import random

class LearningAgent:
    def __init__(self, location, environment):
        """
        location: posisi awal agent ('room-A', 'room-B', 'room-C')
        environment: [['room-A', 'dirty'], ['room-B', 'clean'], ['room-C', 'dirty']]
        """
        self.environment = environment
        self.location = location
        self.model = {room[0]: room[1] for room in environment}
        self.total_reward = 0
        self.q_values = {}  # untuk simpan hasil belajar (state-action value)

    def perceive(self):
        for room in self.environment:
            if room[0] == self.location:
                return room
        return None

    def update_model(self, perception):
        self.model[perception[0]] = perception[1]

    def critic(self, action, perception):
        """Evaluasi hasil aksi"""
        if action == "clean":
            if perception[1] == "dirty":
                return 10
            else:
                return -5
        elif action == "move":
            # kalau pindah dan ruangan berikutnya kotor → bagus
            if any(room[1] == "dirty" for room in self.environment):
                return +1
            else:
                return -2
        return 0

    def problem_generator(self, actions):
        """Mendorong eksplorasi random supaya belajar"""
        if random.random() < 0.3:  # 30% coba aksi random
            return random.choice(actions)
        return None

    def choose_action(self, perception):
        state = (self.location, perception[1])  # (lokasi, kondisi)
        actions = ["clean", "move"]

        # Problem Generator → eksplorasi
        explore_action = self.problem_generator(actions)
        if explore_action:
            return explore_action

        # Exploitasi → pilih aksi terbaik yang sudah dipelajari
        q_for_state = self.q_values.get(state, {})
        if q_for_state:
            return max(q_for_state, key=q_for_state.get)  # pilih aksi dengan Q tertinggi
        else:
            return random.choice(actions)

    def clean(self, perception):
        for room in self.environment:
            if room[0] == self.location:
                room[1] = "clean"
        self.model[self.location] = "clean"
        print(f"[Action] Membersihkan {self.location}")

    def move(self):
        # Pindah random ke ruangan lain
        next_rooms = [room[0] for room in self.environment if room[0] != self.location]
        self.location = random.choice(next_rooms)
        print(f"[Action] Pindah ke {self.location}")

    def learn(self, state, action, reward):
        # Update Q-values
        if state not in self.q_values:
            self.q_values[state] = {}
        old_value = self.q_values[state].get(action, 0)
        new_value = old_value + 0.5 * (reward - old_value)  # simple update
        self.q_values[state][action] = new_value

    def run(self, steps=10):
        for step in range(1, steps + 1):
            print(f"\n--- Step {step} ---")
            perception = self.perceive()
            self.update_model(perception)

            state = (self.location, perception[1])
            action = self.choose_action(perception)

            # Lakukan aksi
            if action == "clean":
                self.clean(perception)
            elif action == "move":
                self.move()

            # Evaluasi dengan Critic
            reward = self.critic(action, perception)
            self.total_reward += reward

            # Learning update
            self.learn(state, action, reward)

            print(f"[Feedback] Action={action}, Reward={reward}, Total={self.total_reward}")
            print(f"[Q-values] {self.q_values}")

        print("\n✅ Sesi selesai")
        print(f"Kondisi akhir environment: {self.environment}")
        print(f"Total Reward: {self.total_reward}")


# Test program
if __name__ == "__main__":
    # 3 ruangan: A kotor, B bersih, C kotor
    environment = [['room-A', 'dirty'], ['room-B', 'clean'], ['room-C', 'dirty']]
    location = 'room-B'

    agent = LearningAgent(location, environment)
    agent.run(steps=12)
