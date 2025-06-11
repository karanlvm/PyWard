# triggers check_unreachable_code
def bar(x):
    if x < 0:
        return "negative"
        print("this is never reached")
    raise ValueError("oops")
    x += 1  # unreachable
