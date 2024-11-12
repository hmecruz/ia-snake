import matplotlib.pyplot as plt # Biblioteca para o gráfico, instalar se ainda não tiver feito (pip install matplotlib)

def create_graph(steps_per_food: dict[int, int]):
    food = list(steps_per_food.keys())     # Os meses
    steps = list(steps_per_food.values())  # Os valores correspondentes

    # Criar o gráfico de barras
    plt.figure(figsize=(10, 5))  # Define o tamanho da figura
    plt.bar(food, steps, color='skyblue')  # Cria o gráfico de barras com cor

    # Adicionar título e rótulos
    plt.title('Passos dados até food')
    plt.xlabel('Food')
    plt.ylabel('Steps')

    # Salvar o gráfico como um arquivo de imagem
    plt.savefig('./data/steps_per_food.png')  # Salva como 'grafico_vendas.png' no diretório atual

    # Exibir o gráfico (opcional)
    # plt.show()