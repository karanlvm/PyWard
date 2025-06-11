# triggers check_string_concat_in_loop
s = ""
for c in ["a", "b", "c"]:
    s = s + c
    s += "-"  # both patterns
print(s)
