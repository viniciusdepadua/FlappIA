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
        self.rewardf = {0: 0,
                        1: -1000}  # valores heuristico para uma função de rewards -1000 para morte e 0 para não
        # estar morto
        self.discount_factor = 0.97  # discount factor do QLearning
        self.alpha = 0.707  # valor heuristico para taxa de aprendizado
        self.moves = []
        self.last_state = "0_0_0"  # valor de inicialização dos estados
        self.last_action = 0
        self.q_values_load()

    def q_values_load(self):
        """
        carega os q-valores já aprendidos de um arquivo JSON
        """
        self.q_values = {}
        try:
            file = open("data/qvalues.json", "r")
        except IOError:
            return
        self.q_values = json.load(file)
        file.close()

    def act(self, x, y, v):
        """
        Escolhe a melhor ação entre as possíveis. 0 - > Don't flap
        :param x: distância horizontal até o proximo tubo
        :param y: distância vertical até o proximo tubo
        :param v: velocidade do passaro
        """
        state = self.hash_state(x, y, v)
        self.moves.append((self.last_state, self.last_action, state))
        self.last_state = state

        if self.q_values[state][0] >= self.q_values[state][1]:
            self.last_action = 0
            return 0
        else:
            self.last_action = 1
            return 1

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

        self.games += 1
        if update_values:
            self.update_values()
        self.moves = []  # limpa o historico para proxima iteração

    def hash_state(self, x, y, v):
        """
        faz um hashing entre os valores e o estado em grid "x_y_v"
        valores consideados, por heurística, são:
        X -> [-40,-30...120] U [140, 210 ... 420]
        Y -> [-300, -290 ... 160] U [180, 240 ... 420]
        """
        # posição do passaro em relação ao cano

        if x < 140:
            x = int(x) - int(x) % 10
        else:
            x = int(x) - int(x) % 70

        if y < 180:
            y = int(y) - (int(y) % 10)
        else:
            y = int(y) - (int(y) % 60)

        return str(int(x)) + "_" + str(int(y)) + "_" + str(v)

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
