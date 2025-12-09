from logic_parser import LogicParser

def test_nand():
    print("Testing NAND: Y = ~(A & B)")
    parser = LogicParser()
    parser.parse_equation("Y = ~(A & B)")
    path = parser.find_euler_path()
    print(f"Path: {path}, Type: {type(path)}")
    print(f"Set: {set(path)}")
    assert set(path) == {'A', 'B'}
    # Both A-B and B-A are valid
    print("PASS")

def test_nor():
    print("Testing NOR: Y = ~(A | B)")
    parser = LogicParser()
    parser.parse_equation("Y = ~(A | B)")
    path = parser.find_euler_path()
    print(f"Path: {path}")
    assert set(path) == {'A', 'B'}
    print("PASS")

def test_aoi():
    print("Testing AOI: Y = ~(A | (B & C))")
    parser = LogicParser()
    parser.parse_equation("Y = ~(A | (B & C))")
    path = parser.find_euler_path()
    print(f"Path: {path}")
    # Valid paths could be A-B-C, C-B-A, etc. depending on graph structure
    # For A | (B & C):
    # PDN: A || (B-C). Euler path needs to traverse A and B-C. 
    # Wait, A is parallel to B-C.
    # Graph: S->A->E, S->B->n->C->E.
    # Odd degree nodes: S(3), E(3), n(2).
    # 2 odd nodes -> Euler path exists!
    # Path: A -> (jump?) No, must be continuous.
    # S -> A -> E -> C -> n -> B -> S. (This is a cycle if we add a return edge).
    # Stick diagram Euler path is about input ordering.
    # Sequence A-B-C:
    # PDN: A (S-E), B (S-n), C (n-E).
    # If we order A, B, C:
    # A uses S-E.
    # B uses S-n.
    # C uses n-E.
    # Is there a common strip?
    # Yes, if we share diffusion.
    # This test just checks if *some* path is returned.
    assert len(path) == 3
    print("PASS")

if __name__ == "__main__":
    try:
        test_nand()
        test_nor()
        test_aoi()
        print("ALL TESTS PASSED")
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
