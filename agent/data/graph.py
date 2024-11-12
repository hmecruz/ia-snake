import json
import matplotlib.pyplot as plt

def create_graph(json_files: list[str]): # testar
    plt.figure(figsize=(10, 5))  # Define o tamanho da figura
    
    for i, file_path in enumerate(json_files):
        # Carregar os dados do ficheiro JSON
        with open(file_path, 'r') as f:
            steps_per_food = json.load(f)
        
        # Obter as chaves e valores para o gráfico
        food = list(map(int, steps_per_food.keys()))    # Converte as chaves para inteiros
        steps = list(steps_per_food.values())
        
        # Adicionar uma linha ao gráfico para este ficheiro
        plt.plot(food, steps, label=f'Ficheiro {i + 1}')
    
    # Adicionar título, rótulos e legenda
    plt.title('Passos dados até food')
    plt.xlabel('Food')
    plt.ylabel('Steps')
    plt.legend()  # Exibe a legenda para distinguir as linhas
    
    # Salvar o gráfico como um arquivo de imagem
    plt.savefig('./data/steps_per_food.png')
    
    # Exibir o gráfico (opcional)
    # plt.show()

create_graph()



# How to use:
# criar uma lista com os nomes dos ficheiros
# json_files = [steps_per_food1.json, steps_per_food2.json, steps_per_food3.json, ]
#
# chamar a função com json_files como argumento
# create_graph(json_files)