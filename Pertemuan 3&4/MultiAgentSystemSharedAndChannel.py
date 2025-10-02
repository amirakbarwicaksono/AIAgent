# mas_shared_comm.py
import random

class Environment:
    def __init__(self, rooms):
        self.rooms = {room: "dirty" for room in rooms}

    def is_dirty(self, room):
        return self.rooms[room] == "dirty"

    def clean(self, room):
        self.rooms[room] = "clean"

    def all_clean(self):
        return all(state == "clean" for state in self.rooms.values())


class Agent:
    def __init__(self, name, env, location, comm_channel, agents_list):
        self.name = name
        self.env = env
        self.location = location
        self.reward = 0
        self.comm_channel = comm_channel  # shared communication channel
        self.agents_list = agents_list    # reference to all agents

    def perceive(self):
        return self.env.rooms[self.location]

    def clean(self):
        if self.env.is_dirty(self.location):
            self.env.clean(self.location)
            reward = 10
            print(f"{self.name} membersihkan {self.location} ✅ (+10)")
            # Kirim informasi ke channel
            self.comm_channel[self.location] = "clean"
        else:
            reward = -2
            print(f"{self.name} mencoba membersihkan {self.location} tapi sudah bersih ❌ (-2)")
        self.add_shared_reward(reward)

    def move(self):
        # Hindari ruangan yang sudah ditandai bersih di comm_channel
        possible_rooms = [room for room, state in self.env.rooms.items() 
                          if self.comm_channel.get(room, "dirty") == "dirty"]

        if possible_rooms:
            self.location = random.choice(possible_rooms)
            reward = 5
            print(f"{self.name} pindah ke {self.location} 🚶 (+5)")
        else:
            reward = -5
            print(f"{self.name} pindah tapi semua sudah bersih ❌ (-5)")

        self.add_shared_reward(reward)

    def add_shared_reward(self, base_reward):
        # Shared reward system (50% ke agent lain)
        share = base_reward // 2
        self.reward += base_reward
        for ag in self.agents_list:
            if ag != self:
                ag.reward += share

    def act(self):
        if self.perceive() == "dirty":
            self.clean()
        else:
            self.move()


class MASimulation:
    def __init__(self, num_agents=3):
        rooms = ["room-A", "room-B", "room-C"]
        self.env = Environment(rooms)
        self.comm_channel = {}  # global channel
        self.agents = []
        for i in range(num_agents):
            agent = Agent(f"Agent-{i}", self.env, random.choice(rooms), self.comm_channel, self.agents)
            self.agents.append(agent)

    def run(self, episodes=5, steps=10):
        for ep in range(1, episodes+1):
            print(f"\n=== Episode {ep} ===")
            # Reset environment dan komunikasi
            self.env = Environment(["room-A", "room-B", "room-C"])
            self.comm_channel.clear()
            for ag in self.agents:
                ag.reward = 0
                ag.location = random.choice(list(self.env.rooms.keys()))

            for step in range(steps):
                if self.env.all_clean():
                    print("🎯 Semua ruangan sudah bersih!")
                    break
                for ag in self.agents:
                    ag.act()

            # Hasil akhir episode
            print(f"\n[Episode {ep} Result]")
            for ag in self.agents:
                print(f"{ag.name} total reward: {ag.reward}")


if __name__ == "__main__":
    sim = MASimulation(num_agents=3)
    sim.run(episodes=5, steps=10)
