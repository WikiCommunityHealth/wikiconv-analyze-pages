from typing import Optional
import networkx as nx
from networkx.algorithms.shortest_paths.unweighted import predecessor

class DiscussionGraph:
    def __init__(self, root_label: str = 'root', root_color: str = 'yellow'):
        self.G = nx.DiGraph()
        self.add_node(
            root_label,
            root_label,
            None,
            None,
            None,
            None,
            root_color
        )
        
    def add_node(self, label: Optional[str], action_type: Optional[str], parent_id: Optional[str], ancestor_id: Optional[str], replyto_id: Optional[str], timestamp: Optional[str], color: Optional[str]):
        if label is None:
            print('Errore')
            print(label, action_type, parent_id, ancestor_id, replyto_id, timestamp, color)
        self.G.add_node(
            label,
            action=action_type,
            parent_id=parent_id,
            ancestor_id=ancestor_id,
            replyto_id=replyto_id,
            timestamp=timestamp,
            color=color
        )
        
    
    def is_node_inside(self, node: str):
        return node in self.G.nodes
    
    
    def add_edge(self, node_1: str, node_2: str):
        for node in [node_1, node_2]:
            if not self.is_node_inside(node):
                self.add_node(
                    node,
                    'unknown1',
                    None,
                    None,
                    None,
                    None,
                    'pink'
                )
                
        self.G.add_edge(node_1, node_2)
        
    def get_node(self, node_label: str):
        #print(node_label)
        return self.G.nodes[node_label]
        
    def get_graph(self):
        return self.G

    def get_parent(self, node_label: str) -> Optional[str]:
        return next(self.G.predecessors(node_label), None)
    
    def get_color_list(self):
        return [attributes['color'] for node, attributes in self.G.nodes.data()]
    
    def reset(self):
        self.G.reset()