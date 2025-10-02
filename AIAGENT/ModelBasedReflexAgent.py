# model_based_reflex_agent.py
# Implementasi Model-Based Reflex Agent untuk Vacuum World

class ModelBasedReflexAgent:
    def __init__(self, location, environment):
        # Environment berbentuk list: [['room-A', 'dirty'], ['room-B', 'clean']]
        self.environment = environment
        self.location = location
        # Model internal (state) → peta key:room, value:clean/dirty
        self.model = {room[0]: room[1] for room in environment}

    def perceive(self):
        # Sensor membaca kondisi ruangan saat ini
        for room in self.environment:
            if room[0] == self.location:
                perception = room
                break
        print(f"[Perception] Agent berada di {perception[0]}, kondisi: {perception[1]}")
        return perception

    def update_model(self, perception):
        # Update model internal dengan hasil persepsi terbaru
        self.model[perception[0]] = perception[1]
        print(f"[Model Update] {perception[0]} sekarang {perception[1]}")
        print(f"[Internal Model] {self.model}")

    def clean(self):
        # Bersihkan ruangan di lokasi sekarang
        for room in self.environment:
            if room[0] == self.location:
                room[1] = "clean"
        self.model[self.location] = "clean"
        print(f"[Action] Membersihkan {self.location}")

    def move(self):
        # Pindah ke ruangan lain
        if self.location == "room-A":
            self.location = "room-B"
            print("[Action] Pindah ke room-B")
        else:
            self.location = "room-A"
            print("[Action] Pindah ke room-A")

    def run(self, steps=10):
        # Jalankan agen untuk sejumlah langkah tertentu
        for step in range(steps):
            print(f"\n--- Step {step+1} ---")
            perception = self.perceive()
            self.update_model(perception)

            if perception[1] == "dirty":
                self.clean()
            else:
                self.move()

        print("\nSelesai. Kondisi akhir environment:")
        print(self.environment)

    def run_until_clean(self):
        # Jalankan agen sampai semua ruangan bersih
        step = 0
        while "dirty" in [room[1] for room in self.environment]:
            step += 1
            print(f"\n--- Step {step} ---")
            perception = self.perceive()
            self.update_model(perception)

            if perception[1] == "dirty":
                self.clean()
            else:
                self.move()

        print("\nSemua ruangan sudah bersih ✅")
        print(f"Kondisi akhir environment: {self.environment}")


# Test program
if __name__ == "__main__":
    environment = [['room-A', 'dirty'], ['room-B', 'dirty']]
    location = 'room-A'
    agent = ModelBasedReflexAgent(location, environment)

    # Bisa pilih salah satu:
    # agent.run(steps=6)           # jalan sejumlah langkah
    agent.run_until_clean()        # jalan sampai semua ruangan bersih
