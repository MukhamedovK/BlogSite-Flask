from playhouse.shortcuts import model_to_dict

def model_converter(data):
    return [model_to_dict(item) for item in data]