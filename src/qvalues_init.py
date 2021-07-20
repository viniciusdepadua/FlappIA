import json
from itertools import chain

# inicialização do arquivo json, cheio de zeros

q_values = {}

# de acordo com o codigo, todos os possiveis estados
for x in chain(list(range(-40, 140, 10)), list(range(140, 421, 70))):
    for y in chain(list(range(-300, 180, 10)), list(range(180, 421, 60))):
        for v in range(-10, 11):
            q_values[str(x) + "_" + str(y) + "_" + str(v)] = [0, 0]


file = open("data/qvalues.json", "w")
json.dump(q_values, file)
file.close()