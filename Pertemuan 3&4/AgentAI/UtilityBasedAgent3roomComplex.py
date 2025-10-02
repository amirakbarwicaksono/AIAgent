# utility_based_agent_3rooms.py
# Utility-Based Agent dengan 3 ruangan (versi dengan kondisi untung & rugi)

class UtilityBasedAgent:
    def __init__(self, location, environment):
        """
        location: posisi awal agent ('room-A', 'room-B', 'room-C')
        environment: list kondisi ruangan, contoh [['room-A', 'dirty'], ['room-B', 'clean'], ['room-C', 'dirty']]
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
                return 10   # reward besar kalau berhasil membersihkan
            else:
                return -5   # rugi besar kalau bersih tapi tetap dicoba bersihkan
        elif action == "move":
            if any(room[1] == "dirty" for room in self.environment):
                # pindah bisa untung/rugi tergantung target
                for room in self.environment:
                    if room[0] != self.location:
                        if room[1] == "dirty":
                            return +3   # pindah ke ruangan kotor (cukup berguna)
                        else:
                            return -4   # pindah ke ruangan bersih (buang waktu)
            else:
                return -10  # rugi besar kalau pindah padahal semua sudah bersih
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
        # Cari ruangan kotor dulu
        for room in self.environment:
            if room[1] == "dirty":
                self.location = room[0]
                reward = self.utility("move", ["dummy", "dirty"])
                self.total_utility += reward
                print(f"[Action] Pindah ke {self.location} (Utility: {reward}, Total: {self.total_utility})")
                return

        # Kalau tidak ada yang kotor, pindah sembarang
        for room in self.environment:
            if room[0] != self.location:
                self.location = room[0]
                reward = self.utility("move", ["dummy", "clean"])
                self.total_utility += reward
                print(f"[Action] Pindah ke {self.location} (Utility: {reward}, Total: {self.total_utility})")
                return

        print("[Action] Tidak ada ruangan untuk dituju.")

    def run(self, steps=10):
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

            # hentikan lebih awal kalau semua ruangan sudah bersih
            if all(room[1] == "clean" for room in self.environment):
                print("\n🎯 Semua ruangan sudah bersih, berhenti lebih awal.")
                break

        print("\n✅ Sesi selesai")
        print(f"Kondisi akhir environment: {self.environment}")
        print(f"Total Utility: {self.total_utility}")


# Test program
if __name__ == "__main__":
    # 3 ruangan: A kotor, B bersih, C kotor
    environment = [['room-A', 'dirty'], ['room-B', 'clean'], ['room-C', 'clean']]
    location = 'room-A'

    agent = UtilityBasedAgent(location, environment)
    agent.run(steps=10)
