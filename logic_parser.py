import networkx as nx
import re
import itertools

class LogicParser:
    def __init__(self):
        self.pdn = nx.MultiGraph()
        self.pun = nx.MultiGraph()
        self.inputs = set()

    def parse_equation(self, equation):
        """
        Parses a boolean equation and constructs PDN and PUN graphs.
        Equation format example: "Y = ~(A & (B | C))"
        """
        # Clean up equation
        equation = equation.replace(" ", "")
        if "=" in equation:
            equation = equation.split("=")[1]
        
        # Remove outer negation if present (CMOS logic is naturally inverting)
        if equation.startswith("~(") and equation.endswith(")"):
            equation = equation[2:-1]
        elif equation.startswith("~"):
             equation = equation[1:]

        self.inputs = set(re.findall(r'[A-Za-z]+', equation))
        
        # Reset graphs
        self.pdn = nx.MultiGraph()
        self.pun = nx.MultiGraph()
        
        # Construct graphs
        # This is a simplified recursive parser for demo purposes
        # In a real compiler, we'd use an AST. 
        # Here we'll handle basic series/parallel structures.
        
        # For PDN: & is Series, | is Parallel
        # For PUN: & is Parallel, | is Series (Dual)
        
        self._build_graph(equation, self.pdn, 'series', 'parallel')
        self._build_graph(equation, self.pun, 'parallel', 'series')
        
        return self.pdn, self.pun

    def _build_graph(self, expr, graph, and_type, or_type):
        """
        Recursive graph builder.
        and_type/or_type can be 'series' or 'parallel'
        """
        # Base case: single variable
        if re.match(r'^[A-Za-z]+$', expr):
            u, v = self._get_new_nodes(graph)
            graph.add_edge(u, v, label=expr)
            return u, v

        # Handle parentheses - find the main operator
        # This is a tricky part without a full parser. 
        # We'll assume fully parenthesized or simple precedence for this demo.
        # A better approach for the "hackathon" speed:
        # Split by top-level OR, then top-level AND.
        
        # Try splitting by | at top level
        sub_exprs = self._split_by_op(expr, '|')
        if len(sub_exprs) > 1:
            # It's an OR operation
            if or_type == 'series':
                return self._connect_series(sub_exprs, graph, and_type, or_type)
            else:
                return self._connect_parallel(sub_exprs, graph, and_type, or_type)

        # Try splitting by & at top level
        sub_exprs = self._split_by_op(expr, '&')
        if len(sub_exprs) > 1:
            # It's an AND operation
            if and_type == 'series':
                return self._connect_series(sub_exprs, graph, and_type, or_type)
            else:
                return self._connect_parallel(sub_exprs, graph, and_type, or_type)

        # If wrapped in parens, strip and recurse
        if expr.startswith('(') and expr.endswith(')'):
            return self._build_graph(expr[1:-1], graph, and_type, or_type)
            
        return None, None

    def _split_by_op(self, expr, op):
        """Splits expression by operator, respecting parentheses."""
        parts = []
        depth = 0
        current = ""
        for char in expr:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            elif char == op and depth == 0:
                parts.append(current)
                current = ""
                continue
            current += char
        parts.append(current)
        return parts

    def _get_new_nodes(self, graph):
        if not graph.nodes:
            return 0, 1
        m = max(graph.nodes)
        return m + 1, m + 2

    def _connect_series(self, sub_exprs, graph, and_type, or_type):
        # Connect sub-graphs in series: S -> [A] -> n1 -> [B] -> E
        start_node = None
        end_node = None
        prev_end = None
        
        for i, sub in enumerate(sub_exprs):
            s, e = self._build_graph(sub, graph, and_type, or_type)
            if i == 0:
                start_node = s
            else:
                # Merge prev_end with current start (s)
                self._merge_nodes(graph, prev_end, s)
                s = prev_end # s is now merged into prev_end
            
            prev_end = e
            
        return start_node, prev_end

    def _connect_parallel(self, sub_exprs, graph, and_type, or_type):
        # Connect sub-graphs in parallel: S -> [A] -> E, S -> [B] -> E
        starts = []
        ends = []
        
        for sub in sub_exprs:
            s, e = self._build_graph(sub, graph, and_type, or_type)
            starts.append(s)
            ends.append(e)
            
        # Merge all starts into one node
        common_start = starts[0]
        for s in starts[1:]:
            self._merge_nodes(graph, common_start, s)
            
        # Merge all ends into one node
        common_end = ends[0]
        for e in ends[1:]:
            self._merge_nodes(graph, common_end, e)
            
        return common_start, common_end

    def _merge_nodes(self, graph, keep_node, remove_node):
        """Merges remove_node into keep_node."""
        if keep_node == remove_node:
            return
        
        # Move edges from remove_node to keep_node
        # List edges first to avoid modifying while iterating
        edges = list(graph.edges(remove_node, data=True))
        for u, v, data in edges:
            # u is remove_node (or v is)
            neighbor = v if u == remove_node else u
            # Add edge to keep_node
            graph.add_edge(keep_node, neighbor, **data)
            
        # Remove old node
        graph.remove_node(remove_node)

    def find_euler_path(self):
        """
        Finds a common Euler path (or best matching sequence) for PDN and PUN.
        Returns: List of input labels in order.
        """
        # Get all Euler paths for PDN
        pdn_paths = self._get_all_euler_paths(self.pdn)
        pun_paths = self._get_all_euler_paths(self.pun)
        
        # Find intersection
        common_paths = set(pdn_paths) & set(pun_paths)
        
        if common_paths:
            return list(common_paths)[0] # Return any valid one
        
        # If no common path, return a default order (e.g., alphabetical)
        # In a real tool, we'd try to minimize breaks.
        return sorted(list(self.inputs))

    def _get_all_euler_paths(self, graph):
        if not nx.is_connected(graph):
             return []

        # Check degrees
        odd_degree_nodes = [v for v, d in graph.degree() if d % 2 == 1]
        if len(odd_degree_nodes) > 2:
            return [] # No single strip possible
            
        inputs = [data['label'] for u, v, data in graph.edges(data=True)]
        
        if len(inputs) != len(set(inputs)):
            return []
            
        valid_seqs = []
        for perm in itertools.permutations(inputs):
            if self._is_valid_path(graph, perm):
                valid_seqs.append(perm)
        return valid_seqs

    def _is_valid_path(self, graph, sequence):
        edge_map = {}
        for u, v, data in graph.edges(data=True):
            label = data['label']
            edge_map[label] = (u, v)
            
        for start_node in graph.nodes():
            curr = start_node
            valid = True
            temp_edge_map = edge_map.copy()
            
            for label in sequence:
                if label not in temp_edge_map:
                    valid = False
                    break
                
                u, v = temp_edge_map[label]
                if curr == u:
                    curr = v
                elif curr == v:
                    curr = u
                else:
                    valid = False
                    break
            
            if valid:
                return True
                
        return False

if __name__ == "__main__":
    parser = LogicParser()
    eq = "Y = ~(A & (B | C))"
    pdn, pun = parser.parse_equation(eq)
    print("Inputs:", parser.inputs)
    print("PDN Nodes:", pdn.nodes())
    print("PDN Edges:", pdn.edges(data=True))
    path = parser.find_euler_path()
    print("Optimal Path:", path)
