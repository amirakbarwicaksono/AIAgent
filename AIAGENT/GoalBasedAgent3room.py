# goal_based_agent_3rooms.py
# Implementasi Goal-Based Agent untuk Vacuum World (3 rooms)

class GoalBasedAgent:
    def __init__(self, location, environment, goal):
        """
        location: posisi awal agent ('room-A', 'room-B', 'room-C')
        environment: list kondisi ruangan, contoh [['room-A', 'dirty'], ['room-B', 'clean'], ['room-C', 'dirty']]
        goal: tujuan akhir (misalnya semua ruangan 'clean')
        """
        self.environment = environment
        self.location = location
        self.goal = goal  # target kondisi akhir
        self.model = {room[0]: room[1] for room in environment}  # model internal

    def perceive(self):
        for room in self.environment:
            if room[0] == self.location:
                perception = room
                break
        print(f"[Perception] Agent berada di {perception[0]}, kondisi: {perception[1]}")
        return perception

    def update_model(self, perception):
        self.model[perception[0]] = perception[1]
        print(f"[Model Update] {perception[0]} sekarang {perception[1]}")
        print(f"[Internal Model] {self.model}")

    def goal_test(self):
        # Cek apakah semua ruangan sudah sesuai goal
        for room in self.environment:
            if room[1] != self.goal:
                return False
        return True

    def clean(self):
        for room in self.environment:
            if room[0] == self.location:
                room[1] = "clean"
        self.model[self.location] = "clean"
        print(f"[Action] Membersihkan {self.location}")

    def move(self):
        # Strategi: cari ruangan lain yang belum sesuai goal
        for room in self.environment:
            if room[1] != self.goal:
                self.location = room[0]
                print(f"[Action] Pindah ke {self.location}")
                return
        print("[Action] Tidak ada ruangan kotor untuk dituju.")

    def run_until_goal(self):
        step = 0
        while not self.goal_test():
            step += 1
            print(f"\n--- Step {step} ---")
            perception = self.perceive()
            self.update_model(perception)

            if perception[1] != self.goal:
                self.clean()
            else:
                self.move()

        print("\n🎯 Tujuan tercapai: semua ruangan sudah bersih!")
        print(f"Kondisi akhir environment: {self.environment}")


# Test program
if __name__ == "__main__":
    # Sekarang ada 3 ruangan
    environment = [['room-A', 'dirty'], ['room-B', 'clean'], ['room-C', 'clean']]
    location = 'room-A'
    goal = 'clean'

    agent = GoalBasedAgent(location, environment, goal)
    agent.run_until_goal()
