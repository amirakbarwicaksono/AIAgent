# multi_agent_vacuum_mas.py
# Multi-Agent System (MAS) for Vacuum World
# - Multiple agents operate in same environment
# - Independent Q-learning per agent
# - Simple communication: broadcast perceptions to shared knowledge
# - Conflict handling (collision, redundant cleaning)
# - Save/Load Q-table per agent
# Usage: python multi_agent_vacuum_mas.py

import random
import pickle
import os
import matplotlib.pyplot as plt

# -------------------------
# Environment
# -------------------------
class Environment:
    def __init__(self, room_names):
        self.room_names = list(room_names)
        self.reset()

    def reset(self, init_dirty_prob=0.5):
        # randomize dirty/clean per room
        self.rooms = {r: ( "dirty" if random.random() < init_dirty_prob else "clean") for r in self.room_names}
        # keep track of which agent is in which room (none start)
        self.agent_locations = {}
        return self.get_state()

    def get_state(self):
        # return a snapshot (rooms dict and agent_locations)
        return (self.rooms.copy(), self.agent_locations.copy())

    def place_agent(self, agent_id, room):
        self.agent_locations[agent_id] = room

    def step(self, agent_actions):
        """
        agent_actions: dict agent_id -> action dict e.g.
           {"agent0": ("clean", None), "agent1": ("move", "room-C")}
        Returns:
           rewards: dict agent_id -> reward (int)
           info: dict for logging (collisions, redundant)
           done: bool all clean
        """
        rewards = {aid: 0 for aid in agent_actions}
        info = {aid: "" for aid in agent_actions}

        # Resolve moves first: collect requested moves
        move_requests = {}
        for aid, (act, target) in agent_actions.items():
            if act == "move":
                # if target None, pick random other room
                tgt = target if target else random.choice([r for r in self.room_names if r != self.agent_locations.get(aid)])
                move_requests.setdefault(tgt, []).append(aid)

        # Handle move conflicts: if multiple request same target, allow one randomly and penalize others
        for tgt, aids in move_requests.items():
            chosen = random.choice(aids)
            for aid in aids:
                if aid == chosen:
                    # perform move
                    self.agent_locations[aid] = tgt
                    rewards[aid] += 0  # small neutral reward for moving
                    info[aid] += f"moved-> {tgt}. "
                else:
                    # conflict penalty
                    rewards[aid] += -3
                    info[aid] += f"move_conflict-> attempted {tgt}, penalized. "

        # Handle agents that requested move to unique targets (not in move_requests because only one requested)
        # (already handled above since chosen will be that single aid)

        # Now handle cleaning actions
        # If multiple agents in same room try to clean same dirty room: give reward to the first one (random order)
        # We'll collect cleaners per room
        cleaners = {}
        for aid, (act, _) in agent_actions.items():
            if act == "clean":
                room = self.agent_locations.get(aid)
                cleaners.setdefault(room, []).append(aid)

        for room, aids in cleaners.items():
            if self.rooms.get(room) == "dirty":
                # choose one successful cleaner (random) to get full reward
                winner = random.choice(aids)
                for aid in aids:
                    if aid == winner:
                        rewards[aid] += 10
                        self.rooms[room] = "clean"  # room is now clean
                        info[aid] += f"cleaned {room}. "
                    else:
                        # redundant cleaners penalized moderately
                        rewards[aid] += -5
                        info[aid] += f"redundant_clean_attempt at {room}, penalized. "
            else:
                # room already clean -> cleaning is a mistake for all cleaners
                for aid in aids:
                    rewards[aid] += -4
                    info[aid] += f"cleaned_clean_room {room}, penalized. "

        # Small penalty for staying idle (if agent didn't move or clean)
        for aid, (act, _) in agent_actions.items():
            if act not in ("move", "clean"):
                rewards[aid] += -1
                info[aid] += "idle_penalty. "

        done = all(state == "clean" for state in self.rooms.values())
        return rewards, info, done

# -------------------------
# Agent (Independent Q-Learning with simple comms)
# -------------------------
class MASAgent:
    def __init__(self, agent_id, actions=("clean","move","idle"), alpha=0.2, gamma=0.9,
                 epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.05, qfile=None, comm_enabled=True):
        self.agent_id = agent_id
        self.actions = list(actions)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.qtable_file = qfile or f"qtable_{agent_id}.pkl"
        self.q_table = {}
        self.comm_enabled = comm_enabled
        # simple shared knowledge store (other agents can read)
        self.knowledge = {}

        # try load
        if os.path.exists(self.qtable_file):
            self.load_q_table()

    def state_repr(self, env_rooms, location, shared_knowledge=None):
        # create a compact state tuple: (location, tuple of rooms states)
        rooms_t = tuple((r, env_rooms[r]) for r in sorted(env_rooms.keys()))
        # optionally include a summary of shared knowledge (e.g., known dirty rooms)
        shared_summary = tuple(sorted(shared_knowledge)) if shared_knowledge else ()
        return (location, rooms_t, shared_summary)

    def choose_action(self, state):
        # epsilon-greedy
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        # exploit
        qvals = [ self.q_table.get((state, a), 0) for a in self.actions ]
        max_q = max(qvals)
        # tie-breaking random among best
        best = [a for a, q in zip(self.actions, qvals) if q == max_q]
        return random.choice(best)

    def update_q(self, state, action, reward, next_state):
        old = self.q_table.get((state, action), 0)
        next_max = max([ self.q_table.get((next_state, a), 0) for a in self.actions ], default=0)
        new = old + self.alpha * (reward + self.gamma*next_max - old)
        self.q_table[(state, action)] = new

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save_q_table(self):
        with open(self.qtable_file, "wb") as f:
            pickle.dump(self.q_table, f)

    def load_q_table(self):
        with open(self.qtable_file, "rb") as f:
            self.q_table = pickle.load(f)

    # communication: broadcast perceived dirty rooms (simple)
    def broadcast(self, perception_rooms):
        if not self.comm_enabled: 
            return {}
        # perception_rooms: dict room->state from current perception
        # we'll share list of rooms believed dirty
        known_dirty = [r for r,s in perception_rooms.items() if s=="dirty"]
        return { "dirty_rooms": known_dirty }

    def integrate_knowledge(self, shared_messages):
        # simple merge: union of dirty rooms lists
        known = set()
        for msg in shared_messages:
            if not msg: continue
            known.update(msg.get("dirty_rooms", []))
        self.knowledge["dirty_rooms"] = known

# -------------------------
# MAS Trainer
# -------------------------
def train_multi_agent(num_agents=3, room_names=("room-A","room-B","room-C"),
                      episodes=200, steps_per_episode=30, enable_comm=True, save_q=True):
    env = Environment(room_names)
    # initialize agents and place randomly
    agents = []
    for i in range(num_agents):
        a = MASAgent(f"agent{i}", qfile=f"qtable_agent{i}.pkl", comm_enabled=enable_comm)
        agents.append(a)

    rewards_history = {a.agent_id: [] for a in agents}

    for ep in range(1, episodes+1):
        env.reset()
        # random start positions
        for a in agents:
            start = random.choice(room_names)
            env.place_agent(a.agent_id, start)

        total_rewards = {a.agent_id: 0 for a in agents}

        for step in range(steps_per_episode):
            # each agent perceives local environment (in this simplified setup they perceive all rooms)
            perceptions = { a.agent_id: env.rooms.copy() for a in agents }

            # agents optionally broadcast their known dirty rooms
            messages = [ a.broadcast(perceptions[a.agent_id]) for a in agents ] if enable_comm else [None]*len(agents)
            # integrate shared knowledge
            for a in agents:
                a.integrate_knowledge(messages)

            # agents form state and pick actions (move->target chosen later)
            chosen_actions = {}
            states = {}
            for a in agents:
                state = a.state_repr(env.rooms, env.agent_locations.get(a.agent_id), shared_knowledge=a.knowledge.get("dirty_rooms"))
                states[a.agent_id] = state
                action = a.choose_action(state)
                # if move, pick preferred target: choose known dirty room first if any
                target = None
                if action == "move":
                    known_dirty = list(a.knowledge.get("dirty_rooms", []))
                    # prefer a dirty room not current
                    candidates = [r for r in known_dirty if r != env.agent_locations.get(a.agent_id)]
                    if candidates:
                        target = random.choice(candidates)
                    else:
                        # pick random other room
                        target = random.choice([r for r in room_names if r != env.agent_locations.get(a.agent_id)])
                chosen_actions[a.agent_id] = (action, target)

            # apply joint step
            rewards, info, done = env.step(chosen_actions)

            # learning update per agent
            for a in agents:
                aid = a.agent_id
                next_state = a.state_repr(env.rooms, env.agent_locations.get(aid), shared_knowledge=a.knowledge.get("dirty_rooms"))
                r = rewards.get(aid, 0)
                a.update_q(states[aid], chosen_actions[aid][0], r, next_state)
                total_rewards[aid] += r

                # optionally log (comment out for less verbose)
                # print(f"[{aid} Step{step}] action={chosen_actions[aid]} reward={r} info={info[aid]}")

            if done:
                break

        # episode finished: decay epsilon and save stats
        for a in agents:
            a.decay_epsilon()
            rewards_history[a.agent_id].append(total_rewards[a.agent_id])
            if save_q:
                a.save_q_table()

        if ep % 10 == 0 or ep==1:
            print(f"Episode {ep}: rewards = " + ", ".join(f"{aid}:{total_rewards[aid]}" for aid in total_rewards))

    # plot total reward per agent
    for aid, series in rewards_history.items():
        plt.plot(series, label=aid)
    plt.xlabel("Episode")
    plt.ylabel("Total Reward per Episode")
    plt.title("MAS Agents Learning Progress")
    plt.legend()
    plt.show()

    return agents, env, rewards_history

# -------------------------
# Run training if this file run as script
# -------------------------
if __name__ == "__main__":
    agents, env, history = train_multi_agent(num_agents=3, episodes=200, steps_per_episode=30, enable_comm=True, save_q=True)
