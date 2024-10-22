# Module: tree_search
# 
# This module provides a set o classes for automated
# problem solving through tree search:
#    SearchDomain  - problem domains
#    SearchProblem - concrete problems to be solved
#    SearchNode    - search tree nodes
#    SearchTree    - search tree with the necessary methods for searhing
#
#  (c) Luis Seabra Lopes
#  Introducao a Inteligencia Artificial, 2012-2020,
#  Inteligência Artificial, 2014-2023


from abc import ABC, abstractmethod

# Dominios de pesquisa
# Permitem calcular as accoes possiveis em cada estado
class SearchDomain(ABC):

    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    @abstractmethod
    def actions(self, state):
        pass

    # resultado de uma accao num estado, ou seja, o estado seguinte
    @abstractmethod
    def result(self, state, action):
        pass

    # custo de uma accao num estado
    @abstractmethod
    def cost(self, state, action):
        pass

    # custo estimado de chegar de um estado a outro
    @abstractmethod
    def heuristic(self, state, goal):
        pass

    # test if the given "goal" is satisfied in "state"
    @abstractmethod
    def satisfies(self, state, goal):
        pass


# Problemas concretos a resolver
# dentro de um determinado dominio
class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal
    def goal_test(self, state):
        return self.domain.satisfies(state,self.goal)

# Nos de uma arvore de pesquisa
class SearchNode:
    def __init__(self,state, parent, depth, cost, heuristic): 
        self.state = state
        self.parent = parent
        self.depth = depth
        self.cost = cost
        self.heuristic = heuristic

    def __str__(self):
        return "no(" + str(self.state) + "," + str(self.parent) + ")"
    def __repr__(self):
        return str(self)
    
    # Another approach for exercice 1
    def in_parent(self, newstate):
        if self.parent == None: 
            return False
        
        if self.parent.state == newstate:
            return True
        
        return self.parent.in_parent(newstate)

# Arvores de pesquisa
class SearchTree:

    # construtor
    def __init__(self,problem, strategy='breadth'):
        self.problem = problem
        root = SearchNode(problem.initial, None, depth=0, cost=0, heuristic=self.problem.domain.heuristic(self.problem.initial, self.problem.goal))
        self.open_nodes = [root]
        self.strategy = strategy
        self.solution = None
        self.non_terminals = 0
        self.highest_cost_nodes = [root]
        self.average_depth = root.depth

    @property
    def length(self):
        return self.solution.depth

    @property
    def avg_branching(self):
        return (self.terminals + self.non_terminals - 1) / self.non_terminals

    @property
    def cost(self):
        return self.solution.cost
    
    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return(path)
    
    # procurar a solucao
    def search(self, limit=None):
        visited_nodes = [] # List of visited nodes states 
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
    
            if self.problem.goal_test(node.state):
                self.solution = node
                self.terminals = len(self.open_nodes) + 1
                self.average_depth /= self.terminals + self.non_terminals
                return self.get_path(node)
            
            self.non_terminals += 1

            if limit and node.depth >= limit: continue # Limited depth node search
            
            lnewnodes = []
            visited_nodes.append(node.state) # Add node to the visited_nodes
            for a in self.problem.domain.actions(node.state):
                newstate = self.problem.domain.result(node.state,a)
                #if not node.in_parent(newstate):  # Recursive approach without visited nodes. Check if the newstate is a parent. If it is a parent it has already been visited.
                if not newstate in visited_nodes or newstate not in self.get_path(node): # if newstate has not been visited add it to the open nodes
                    cost = self.problem.domain.cost(node.state, (node.state, newstate))
                    newnode = SearchNode(newstate, node, node.depth+1, node.cost + cost, self.problem.domain.heuristic(newstate, self.problem.goal))
                    
                    if newnode.cost > self.highest_cost_nodes[0].cost:
                        self.highest_cost_nodes = [newnode]
                    elif newnode.cost == self.highest_cost_nodes[0].cost:
                        self.highest_cost_nodes.append(newnode)

                    self.average_depth += newnode.depth
                    
                    lnewnodes.append(newnode)
            self.add_to_open(lnewnodes)
        return None

    # Add new nodes to the open list according to the stategy
    def add_to_open(self,lnewnodes):
        if self.strategy == 'breadth':
            self.open_nodes.extend(lnewnodes)
        elif self.strategy == 'depth':
            self.open_nodes[:0] = lnewnodes
        elif self.strategy == 'uniform':
            self.open_nodes.extend(lnewnodes) # Nodes with less cost have priority
            self.open_nodes.sort(key=lambda node: node.cost)
        elif self.strategy == "greedy":
            self.open_nodes.extend(lnewnodes) # Choose the best option at each step. Best option if the one with least heuristic value
            self.open_nodes.sort(key=lambda node: node.heuristic)
        elif self.strategy == "a*":
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda node: node.cost + node.heuristic) # g + h

        