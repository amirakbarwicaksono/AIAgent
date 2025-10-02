# utility_based_agent_3rooms.py
# Utility-Based Agent dengan 3 ruangan

class UtilityBasedAgent:
    def __init__(self, location, environment):
        """
        location: posisi awal agent ('room-A', 'room-B', 'room-C')
        environment: list kondisi ruangan, contoh [['room-A', 'dirty'], ['room-B', 'dirty'], ['room-C', 'clean']]
        """
        self.environment = environment
        self.location = location
        self.model = {room[0]: room[1] for room in environment}
        self.total_utility = 0

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

    def utility(self, action, perception):
        if action == "clean":
            if perception[1] == "dirty":
                return 10
            else:
                return -2
        elif action == "move":
            return -1
        return 0

    def clean(self, perception):
        reward = self.utility("clean", perception)
        self.total_utility += reward

        for room in self.environment:
            if room[0] == self.location:
                room[1] = "clean"
        self.model[self.location] = "clean"

        print(f"[Action] Membersihkan {self.location} (Utility: {reward}, Total: {self.total_utility})")

    def move(self):
        # Cari ruangan kotor terdekat (sederhana: pilih ruangan pertama yang ditemukan kotor)
        for room in self.environment:
            if room[1] == "dirty":
                self.location = room[0]
                reward = self.utility("move", None)
                self.total_utility += reward
                print(f"[Action] Pindah ke {self.location} (Utility: {reward}, Total: {self.total_utility})")
                return
        print("[Action] Tidak ada ruangan kotor untuk dituju.")

    def run(self, steps=6):
        for step in range(1, steps + 1):
            print(f"\n--- Step {step} ---")
            perception = self.perceive()
            self.update_model(perception)

            clean_score = self.utility("clean", perception)
            move_score = self.utility("move", perception)

            if clean_score >= move_score:
                self.clean(perception)
            else:
                self.move()

        print("\n✅ Sesi selesai")
        print(f"Kondisi akhir environment: {self.environment}")
        print(f"Total Utility: {self.total_utility}")


# Test program
if __name__ == "__main__":
    # 3 ruangan: A kotor, B bersih, C kotor
    environment = [['room-A', 'dirty'], ['room-B', 'dirty'], ['room-C', 'dirty']]
    location = 'room-B'

    agent = UtilityBasedAgent(location, environment)
    agent.run(steps=8)
