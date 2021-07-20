#FlappIA, Projeto de CMC-12
##Alunos: Henrique Fernandes, Thomas Neto, Vinícius Araújo


Para rodar nossa IA, você pode usar a q-table já fornecida em `qvalues.json` e depois executar no seu terminal `python3 
src/game.py` 

Para treinar sua IA do zero, faça inicialmente `python3 src/qvalues_init.py`, para zerar
os valores e, então escolha: Se deseja treinar e observar o treino graficamente,
rode `python3 src/game.py`, a q-table será atualizada a cada 25 mortes. Caso deseje treinar mais
rapidamente, rode `python3 src/train.py --iter number_of_iterations_que_desejar`. Para observar
o score a cada iteração do treinamento, adicione o argumento `--verbose`.