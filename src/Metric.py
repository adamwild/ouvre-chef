class Metric:
    def __init__(self, path_metric_conf):
        self.path_metric_conf = path_metric_conf
        
        self.load_metric()
        
        self.all_units = list(self.metric2main_metric.keys())
        
    def load_metric(self):
        with open(self.path_metric_conf, 'r') as file:
            full_file = file.readlines()
        
        # main_metric2readables: {'g': ['kg', 'g']}
        # metric2main_metric: {'CàS': [15, 'ml']}   
        main_metric2readables, metric2main_metric = {}, {}
        
        for line in full_file:
            line = line.replace('\n', '')
            left, right = line.split('|')
            
            main_metric = right.split(',')[0].strip()
            readables = [elt.strip() for elt in left[1:-1].split(',')]
            
            main_metric2readables[main_metric] = readables
            
            metric2main_metric[main_metric] = [1, main_metric]
            
            other_metrics = []
            if ',' in right:
                for elt in right.split(',')[1:]:
                    extra_unit = elt.strip()
                    index_space = extra_unit.index(' ')
                    a, b = extra_unit[:index_space], extra_unit[index_space+1:]
                    other_metrics.append((a, b))
                
                for other_metric in other_metrics:
                    scale, unit = other_metric
                    scale = max((int(scale), float(scale)))
                    metric2main_metric[unit] = [scale, main_metric]
                    
        self.main_metric2readables = main_metric2readables
        self.metric2main_metric = metric2main_metric
        
        return main_metric2readables, metric2main_metric
        
    
    def convert_to_master_metric(self, value, metric):
        if not metric:
            return value, metric
        new_value = value*self.metric2main_metric[metric][0]
        new_metric = self.metric2main_metric[metric][1]
        
        new_value = max(int(new_value), new_value)
        
        return new_value, new_metric
        
    
    def make_readable(self, value, metric):
        value, metric = self.convert_to_master_metric(value, metric)
        
        if not metric:
            if value:
                return str(value)
            else:
                return ""
        
        optional_space = ""
        if metric not in ['g', 'ml']:
            optional_space = ' '
            
        readables = self.main_metric2readables[metric]
        for ind, candidate_metric in enumerate(readables):
            if ind == len(readables):
                return str(value) + optional_space + metric
            
            scale = self.metric2main_metric[candidate_metric][0]
            value_scaled = float(value)/scale
            
            if value_scaled >= 1:
                value_scaled = round(value_scaled, 2)
                value_scaled = max(int(value_scaled), value_scaled)
                return str(value_scaled) + optional_space + candidate_metric
            
    def metricize_ingredients(self, list_ingredients, aisle_obj):
        sol = []
        for ingredient in list_ingredients:

            quantity, unit, ingredient_name = ingredient
            
            metric_quantity, metric_unit = self.convert_to_master_metric(quantity, unit)
            metric_ingredient_name = aisle_obj.normalize_ingredient(ingredient_name)

            sol.append([metric_quantity, metric_unit, metric_ingredient_name])
            
        return sol
    
    def aggregate_ingredient_quantities(self, list_ingredients):
        ingredient_dict = {}
    
        for ingredient in list_ingredients:
            # print(ingredient)
            quantity, unit, ingredient_name = ingredient
            
            if ingredient_name in ingredient_dict and ingredient_dict[ingredient_name][0]:
                if quantity:
                    ingredient_dict[ingredient_name][0] += quantity
            else:
                ingredient_dict[ingredient_name] = [quantity, unit]
        
        return ingredient_dict
            
    
if __name__ == '__main__':
    pass
