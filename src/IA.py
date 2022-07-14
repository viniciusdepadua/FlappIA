import json
import random


class FbIa:
    """
    classe para a IA que usa Qlearning para jogar flappy bird
    """

    def __init__(self, train):
        self.train = train  # ou treina ou apenas joga
        self.update_iteration = 20
        self.games = 0
        self.cumulative_reward = []
        self.rewardf = {0: 0,
                        1: -1000}  # valores heuristico para uma função de rewards -1000 para morte e 0 para não
        # estar morto
        self.epsilon = 0.3  # política epsilon-greedy
        self.discount_factor = 0.97  # discount factor do QLearning
        self.discounted_cumulative_reward = 0
        self.alpha = 0.707  # valor heuristico para taxa de aprendizado
        self.moves = []
        self.last_state = "0_0_0_0"  # estado inicial
        self.last_action = 0
        self.q_values = {}
        self.initState(self.last_state)
        self.q_values_load()

    def q_values_load(self):
        """
        carega os q-valores já aprendidos de um arquivo JSON
        """
        try:
            file = open("data/qvalues.json", "r")
        except IOError:
            return
        self.q_values = json.load(file)
        file.close()

    def initState(self, state):
        if state not in self.q_values:
            self.q_values[state] = [0, 0]

    def act(self, x, y, v, pipe):
        """
        Escolhe a melhor ação entre as possíveis. 0 - > Don't flap
        :param x: distância horizontal até o proximo tubo
        :param y: distância vertical até o proximo tubo
        :param v: velocidade do passaro
        """
        state = self.hash_state(x, y, v, pipe)
        self.moves.append((self.last_state, self.last_action, state))
        self.save_scores()
        self.last_state = state

        self.last_action = self.q_values[state].index(
            max(self.q_values[state])) if random.random() >= self.epsilon else random.choice([0, 1])
        return self.last_action

    def save_scores(self):
        # tira da cache memória para acelerar execução
        if len(self.moves) > 6_000_000:
            history = list(reversed(self.moves[:5_000_000]))
            for move in history:
                state, action, new_state = move
                self.q_values[state][action] = (1 - self.alpha) * self.q_values[state][action] + \
                                               self.alpha * (self.rewardf[0] + self.discount_factor * max(self.q_values[new_state]))
            self.moves = self.moves[5_000_000:]

    def update_scores(self, update_values=True):
        """
        atualiza q_values de acordo com a experiência
        :param update_values: se é para atualizar ou não
        """
        history = list(reversed(self.moves))
        last_flap = True
        # a visão do estado causa com que as vezes o passaro acabe morrendo no tubo de cima
        # cria-se uma flag para caso isso aconteça, para que ele apenas não flap nesse caso

        flag_top_death = True if int(history[0][2].split("_")[1]) > 120 else False

        t = 1
        for move in history:
            state = move[0]
            action = move[1]
            new_state = move[2]
            current_reward = self.rewardf[0]
            # dois passos lookahead: ação da morte e antes da morte são penalizadas
            if t == 1 or t == 2:
                current_reward = self.rewardf[1]
                if action:
                    last_flap = False
            elif (last_flap or flag_top_death) and action:
                # penalização de flap
                current_reward = self.rewardf[1]
                last_flap = False
                flag_top_death = False

            # função de atualização da q_table
            self.q_values[state][action] = (1 - self.alpha) * (self.q_values[state][action]) + \
                                           self.alpha * (current_reward + self.discount_factor * max(
                self.q_values[new_state]))

            t += 1
            self.discounted_cumulative_reward = self.discount_factor * self.discounted_cumulative_reward + current_reward

        self.epsilon *= 0.98
        self.games += 1
        if update_values:
            self.update_values()
        self.moves = []  # limpa o historico para proxima iteração

    def hash_state(self, x, y, v, pipe):
        """
        faz um hashing entre os valores e o estado em grid "x_y_v_yp"
        """
        pipe0 = pipe[0]
        pipe1 = pipe[1]
        if x - pipe[0]["x"] >= 50:
            pipe0 = pipe[1]
            if len(pipe) > 2:
                pipe1 = pipe[2]

        x0 = pipe0["x"] - x
        y0 = pipe0["y"] - y
        if -50 < x0 <= 0:
            y1 = pipe1["y"] - y
        else:
            y1 = 0

        if x0 < -40:
            x0 = int(x0)
        elif x0 < 140:
            x0 = int(x0) - (int(x0) % 10)
        else:
            x0 = int(x0) - (int(x0) % 70)

        if -180 < y0 < 180:
            y0 = int(y0) - (int(y0) % 10)
        else:
            y0 = int(y0) - (int(y0) % 60)

        if -180 < y1 < 180:
            y1 = int(y1) - (int(y1) % 10)
        else:
            y1 = int(y1) - (int(y1) % 60)

        state = str(int(x0)) + "_" + str(int(y0)) + "_" + str(int(v)) + "_" + str(int(y1))
        self.initState(state)
        return state

    def update_values(self, force=False):
        """
            atualiza os valores e joga no arquivo .json
            :param force: força bruta, caso de ruim
            """

        if self.games % self.update_iteration == 0 or force:
            file = open("data/qvalues.json", "w")
            json.dump(self.q_values, file)
            file.close()
            print("Atualizado os Q-values no arquivo em data/qvalues.json.")
