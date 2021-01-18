def eval_float(text, min_=None, max_=None):
    try:
        val = float(eval(str(text)))
        if min_ is not None: val = max(val, min_)
        if max_ is not None: val = min(val, max_)
        return val
    except Exception as err:
        print("Error setting value: {}".format(text))
        print(err)

def eval_int(text, min_=None, max_=None):
    try:
        val = int(eval(str(text)))
        if min_ is not None: val = max(val, min_)
        if max_ is not None: val = min(val, max_)
        val = int(val)
        return val
    except Exception as err:
        print("Error setting value: {}".format(text))
        print(err)

def eval_bool(text):
    try:
        if text == "true":
            text = "True"
        if text == "false":
            text = "False"
        val = bool(eval(str(text)))
        return val
    except Exception as err:
        print(err)

def eval_str(text):
    # print("setSRT")
    # print(text)
    return str(text)