def is_string_true_or_false(item: str) -> bool:
    """Takes a string and returns whether it's True or False"""
    res = False
    if type(item) == str:
        if item.isdigit():
            item = int(item)
        if item in ['false', 'False']:
            item = 0
        res = bool(item)
    else:
        raise ValueError('Only str allowed')

    return res
