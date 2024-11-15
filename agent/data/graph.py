import json
import matplotlib.pyplot as plt
import os

def create_graph():
    # Path to the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List all JSON files in the script's directory
    json_files = [
        os.path.join(script_dir, f) 
        for f in os.listdir(script_dir) 
        if f.endswith('.json')
    ]

    if not json_files:
        print("No JSON files found in the script's directory.")
        return
    
    plt.figure(figsize=(10, 5))
    
    for i, file_path in enumerate(json_files):
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check if the data is in deque format (list of pairs)
        if isinstance(data, list) and all(isinstance(item, list) and len(item) == 2 for item in data):
            food, steps = zip(*data)  # Unpack the pairs into two lists: food and steps
            food = list(map(int, food))  # Convert 'food' values to integers
            plt.plot(food, steps, label=f'File {i + 1}')
        else:
            print(f"Warning: {file_path} does not contain a list of pairs. Skipping this file.")
    
    plt.title('Steps Taken per Food')
    plt.xlabel('Food')
    plt.ylabel('Steps')
    plt.legend()
    
    # Save the graph as an image file in the same directory as the script
    output_path = os.path.join(script_dir, 'steps_per_food.png')
    plt.savefig(output_path)
    print(f'Graph successfully created and saved as {output_path}.')

if __name__ == '__main__':
    create_graph()
    