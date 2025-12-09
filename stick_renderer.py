import matplotlib.pyplot as plt
import matplotlib.patches as patches

class StickRenderer:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        # Constants for drawing
        self.poly_width = 0.5
        self.diff_height = 1.0
        self.metal_height = 0.5
        self.contact_size = 0.3
        self.pitch = 2.0 # Distance between gates
        
        # Y-coordinates
        self.y_pun = 6.0
        self.y_pdn = 2.0
        self.y_vcc = 8.0
        self.y_gnd = 0.0
        self.y_out = 4.0

    def draw_layout(self, euler_path, pdn_graph, pun_graph):
        """
        Draws the stick diagram based on the Euler path.
        euler_path: List of input labels (e.g., ['A', 'B', 'C'])
        """
        self.ax.clear()
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        if not euler_path:
            self.ax.text(0.5, 0.5, "No Euler Path Found - Cannot Draw Single Strip", 
                         ha='center', va='center', transform=self.ax.transAxes)
            return self.fig

        num_inputs = len(euler_path)
        width = (num_inputs + 1) * self.pitch
        
        # 1. Draw Rails (Metal 1 - Blue)
        # VCC
        self._add_rect(0, self.y_vcc, width, self.metal_height, 'blue', 'VCC')
        # GND
        self._add_rect(0, self.y_gnd, width, self.metal_height, 'blue', 'GND')
        
        # 2. Draw Diffusion Strips
        # PUN (P-Diff - Yellow/Orange)
        self._add_rect(0, self.y_pun, width, self.diff_height, 'orange', 'P-Diff')
        # PDN (N-Diff - Green)
        self._add_rect(0, self.y_pdn, width, self.diff_height, 'green', 'N-Diff')
        
        # 3. Draw Polysilicon Gates (Red)
        for i, label in enumerate(euler_path):
            x = (i + 1) * self.pitch
            # Draw vertical poly strip crossing both diffusions
            self._add_rect(x, self.y_pdn - 1, self.poly_width, self.y_pun + 2, 'red', label)
            # Add label
            self.ax.text(x + self.poly_width/2, self.y_pun + 2.5, label, 
                         ha='center', va='bottom', color='red', fontsize=12, fontweight='bold')

        # 4. Draw Connections (Simplified for MVP)
        # We need to connect sources/drains based on the graph topology.
        # This is the tricky part: mapping graph nodes to physical regions between gates.
        
        # The Euler path defines the sequence of gates.
        # The regions between gates (and ends) correspond to nodes in the graph.
        # Sequence: Node0 - Gate1 - Node1 - Gate2 - Node2 ...
        
        # We need to figure out which node in the graph corresponds to which region.
        # We can trace the path in the graph.
        
        # Trace PDN
        pdn_nodes = self._trace_nodes(pdn_graph, euler_path)
        # Trace PUN
        pun_nodes = self._trace_nodes(pun_graph, euler_path)
        
        # Draw contacts and metal connections for these nodes
        self._draw_connections(pdn_nodes, self.y_pdn, 'GND', self.y_gnd)
        self._draw_connections(pun_nodes, self.y_pun, 'VCC', self.y_vcc)
        
        # Draw Output connections
        # Find the output node (usually connected to PUN and PDN common point?)
        # In our graph, we didn't explicitly mark VCC/GND/Out nodes.
        # Assumption: 
        # In PDN, one node is GND, one is Out.
        # In PUN, one node is VCC, one is Out.
        # We need to identify them.
        # Heuristic: 
        # - VCC/GND are usually the nodes with high degree or specific connectivity?
        # - Actually, for a single complex gate:
        #   - PDN connects Out to GND.
        #   - PUN connects Out to VCC.
        #   - So the "common" node between all parallel branches in PDN is usually GND/Out.
        
        # Let's assume the parser can identify Source/Drain nodes?
        # Or simpler: The user gives Y = ...
        # The "Output" is the node that connects PUN and PDN.
        # In our trace, we have a list of nodes [n0, n1, n2...] corresponding to regions.
        # We need to find which n_i is connected to VCC/GND/Out.
        
        # Hack for MVP:
        # Just draw contacts.
        # If a region corresponds to a node that should be VCC, draw via to VCC rail.
        # If GND, draw via to GND rail.
        # If Out, draw via to Output rail (middle).
        
        # Since we don't have full circuit extraction, we'll use a visual heuristic:
        # - Leftmost/Rightmost are often power/ground/out.
        # - Alternating source/drain.
        
        # Let's draw the Output Rail in the middle
        self._add_rect(0, self.y_out, width, self.metal_height/2, 'blue', 'Output')
        
        return self.fig

    def _trace_nodes(self, graph, path):
        # Reconstruct the sequence of nodes visited by the Euler path
        # Returns a list of nodes corresponding to regions [Left, Between 1-2, Between 2-3, ..., Right]
        
        # Find start node that allows this path
        # We did this in parser._is_valid_path
        
        edge_map = {}
        for u, v, data in graph.edges(data=True):
            label = data['label']
            edge_map[label] = (u, v)
            
        # Find valid start node
        start_node = None
        for node in graph.nodes():
            curr = node
            valid = True
            temp_map = edge_map.copy()
            for label in path:
                if label not in temp_map:
                    valid = False
                    break
                u, v = temp_map[label]
                if curr == u:
                    curr = v
                elif curr == v:
                    curr = u
                else:
                    valid = False
                    break
            if valid:
                start_node = node
                break
        
        if start_node is None:
            return []
            
        # Now trace and record nodes
        nodes = [start_node]
        curr = start_node
        # We need to be careful about parallel edges or reused labels?
        # Assuming unique labels for now.
        for label in path:
            u, v = edge_map[label]
            if curr == u:
                curr = v
            else:
                curr = u
            nodes.append(curr)
            
        return nodes

    def _draw_connections(self, nodes, y_diff, rail_name, y_rail):
        # This is where we guess which node is Power/Ground/Output
        # In a real tool, we'd know.
        # Here, let's assume:
        # - If it's PDN: One set of nodes is GND, one is Output.
        # - If it's PUN: One set of nodes is VCC, one is Output.
        
        # We need to know which graph node is which.
        # Let's assume node 0 is Output? And node 1 is Power/Ground?
        # This depends on how _build_graph constructed it.
        # In _build_graph:
        # Series: S -> ... -> E. 
        # Parallel: S -> ... -> E.
        # Usually S is one terminal, E is the other.
        # Let's assume Start Node (lowest ID?) is Output, End Node is VCC/GND?
        # Or vice versa.
        
        # Let's just visualize the nodes with text for now to debug.
        # And draw contacts.
        
        for i, node in enumerate(nodes):
            x = i * self.pitch + self.pitch/2
            # Draw Contact
            self._add_contact(x, y_diff)
            
            # Label the diffusion region with node ID
            self.ax.text(x, y_diff, f"n{node}", ha='center', va='center', fontsize=8, color='black')
            
            # Heuristic connection:
            # If node ID is 0, connect to Output (Middle)
            # If node ID is 1, connect to Rail (VCC/GND)
            # This relies on the parser's node numbering: 0 and 1 are initial nodes.
            
            if node == 0: # Output
                self._add_wire(x, y_diff, self.y_out)
                self._add_contact(x, self.y_out)
            elif node == 1: # Power/Ground
                self._add_wire(x, y_diff, y_rail)
                self._add_contact(x, y_rail)

    def _add_rect(self, x, y, w, h, color, label=None):
        rect = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor='none', facecolor=color, alpha=0.7)
        self.ax.add_patch(rect)
        if label and x == 0: # Label only once at start
            self.ax.text(x - 0.5, y + h/2, label, ha='right', va='center', color=color, fontsize=10)

    def _add_contact(self, x, y):
        # Draw X
        size = self.contact_size
        self.ax.plot([x-size, x+size], [y-size, y+size], 'k-', linewidth=1)
        self.ax.plot([x-size, x+size], [y+size, y-size], 'k-', linewidth=1)
        # Draw box
        rect = patches.Rectangle((x-size, y-size), 2*size, 2*size, linewidth=1, edgecolor='black', facecolor='none')
        self.ax.add_patch(rect)

    def _add_wire(self, x, y1, y2):
        self.ax.plot([x, x], [y1, y2], 'b-', linewidth=2, alpha=0.6)

if __name__ == "__main__":
    renderer = StickRenderer()
    # Dummy data for testing
    # renderer.draw_layout(['A', 'B', 'C'], None, None)
    # plt.show()
