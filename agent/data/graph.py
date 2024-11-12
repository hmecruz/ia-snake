import json
import matplotlib.pyplot as plt
import os

def create_graph():
    # Caminho do diretório onde o script está localizado
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Lista todos os ficheiros JSON no diretório do script
    json_files = [
        os.path.join(script_dir, f) 
        for f in os.listdir(script_dir) 
        if f.endswith('.json')
    ]

    if not json_files:
        print("Nenhum ficheiro JSON encontrado no diretório do script.")
        return
    
    plt.figure(figsize=(10, 5))
    
    for i, file_path in enumerate(json_files):
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Verificar se os dados estão no formato de deque (lista de pares)
        if isinstance(data, list) and all(isinstance(item, list) and len(item) == 2 for item in data):
            food, steps = zip(*data)  # Descompactar os pares em duas listas: food e steps
            food = list(map(int, food))   # Converter valores de 'food' para inteiros
            plt.plot(food, steps, label=f'Ficheiro {i + 1}')
        else:
            print(f"Aviso: {file_path} não contém uma lista de pares. Ignorando este ficheiro.")
    
    plt.title('Passos dados até food')
    plt.xlabel('Food')
    plt.ylabel('Steps')
    plt.legend()
    
    # Salvar o gráfico como um arquivo de imagem no mesmo diretório do script
    output_path = os.path.join(script_dir, 'steps_per_food.png')
    plt.savefig(output_path)
    print(f'Gráfico criado com sucesso e salvo como {output_path}.')

if __name__ == '__main__':
    create_graph()
