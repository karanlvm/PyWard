from pyward.optimization.rules.unused_variables import fix_unused_variables


def test_fix_simple_unused_variable():
    # Simple case: remove an unused variable completely
    src = "a = 1\nb = 2\nprint(a)\n"
    changed, fixed, fixes = fix_unused_variables(src)
    
    assert changed is True
    assert "b = 2" not in fixed
    assert "a = 1" in fixed
    assert "print(a)" in fixed
    assert len(fixes) == 1
    assert "Removed unused variable 'b'" in fixes[0]


def test_fix_multiple_assignment():
    # Test fixing variables in tuple unpacking
    src = "a, b = 1, 2\nprint(a)\n"
    changed, fixed, fixes = fix_unused_variables(src)
    
    assert changed is True
    assert "a, _" in fixed
    assert "print(a)" in fixed


def test_fix_all_unused():
    # Test when all variables in an assignment are unused
    src = "x, y = get_values()\nz = 42\n"
    changed, fixed, fixes = fix_unused_variables(src)
    
    assert changed is True
    assert "x, y = get_values()" not in fixed
    assert "z = 42" not in fixed
    assert len(fixes) == 3


def test_fix_for_loop():
    # Test fixing variables in for loop targets
    src = "for i, val in enumerate(items):\n    print(i)\n"
    changed, fixed, fixes = fix_unused_variables(src)
    
    assert changed is True
    assert "for i, _" in fixed
    assert "print(i)" in fixed


def test_fix_function_parameters():
    # Test fixing unused function parameters
    src = "def func(a, b, c):\n    return a + c\n"
    changed, fixed, fixes = fix_unused_variables(src)
    
    assert changed is True
    assert "def func(a, _, c)" in fixed
    assert "return a + c" in fixed


def test_fix_nested_structure():
    # Test fixing variables in nested structures
    src = """def outer():
    x = 10
    y = 20
    
    def inner(a, b):
        print(a)
        return x
        
    return inner(1, 2) + y
"""
    changed, fixed, fixes = fix_unused_variables(src)
    
    assert changed is True
    assert "def inner(a, _)" in fixed
    assert "print(a)" in fixed
    assert "y = 20" in fixed  
    assert "x = 10" in fixed  
    

def test_no_changes_when_no_unused_variables():
    src = "a = 1\nprint(a)\n"
    changed, fixed, fixes = fix_unused_variables(src)
    
    assert changed is False
    assert fixed == src
    assert len(fixes) == 0


def test_fix_preserves_indentation():
    src = """def func():
    if True:
        x = 1
        y = 2
        print(x)
"""
    changed, fixed, fixes = fix_unused_variables(src)
    
    assert changed is True
    assert "y = 2" not in fixed
    assert "        x = 1" in fixed
    assert "        print(x)" in fixed
