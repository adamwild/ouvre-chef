def save_json(data, root_expected_outputs, test_name):
    import json
    
    json_file = str(root_expected_outputs / test_name)
    
    if not json_file.endswith('.json'):
        json_file += '.json'
        
    with open(json_file, 'w') as file:
        json.dump(data, file)
        
def load_json(root_expected_outputs, test_name):
    import json
    
    json_file = str(root_expected_outputs / test_name)
    
    if not json_file.endswith('.json'):
        json_file += '.json'
    
    with open(json_file, 'r') as file:
        return json.load(file)
    
def update_test_environment(name_constant, value, test_env):
    with open(test_env, 'w') as file:
        file.write("VERBOSE = ''\n".format(name_constant, value))
        file.write("{0} = '{1}'".format(name_constant, value))