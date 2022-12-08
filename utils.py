def timeout(obj):
    function = obj.get('function')

    if function:
        del obj['function']
        return {key: function(**value) for key, value in obj.items()}
    else:
        return obj
