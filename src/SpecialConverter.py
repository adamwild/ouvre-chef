class SpecialConverter:
    def __init__(self, path_special_conv):
        self.path_special_conv = path_special_conv
        
        self.load_special_conv()
        
    def load_special_conv(self):
        dic_breakdowns, prime_ingredients = {}, {}
        
        with open(self.path_special_conv, 'r') as file:
            full_file = file.readlines()
            for line in full_file:
                splitted_line = line.split('|')
                prime_ingredient = splitted_line[0]
                sub_ingredients = splitted_line[1:]
                
                tuples_line = [(tuple.split(',')[0].strip(), int(tuple.split(',')[1].strip()))
                               for tuple in sub_ingredients]
                
                dic_breakdowns[prime_ingredient] = tuples_line
                
                full_weight = sum([tupl[1] for tupl in tuples_line])
                prime_ingredients[prime_ingredient] = full_weight
                
                for tuple in tuples_line:
                    dic_breakdowns[tuple[0]] = [tuple]
                    
        self.dic_breakdowns = dic_breakdowns
        self.prime_ingredients = prime_ingredients
        
    def break_ingredients(self, metric_list_ingredients):
        """Breaks down ingredients into sub-ingredients and converts sub-ingredients, already in the list, into grams
        ex: 1 oeuf -> 15 g de jaune, 35g de blanc
            1 jaune -> 15 g de jaune

        Args:
            metric_list_ingredients (_type_): _description_
        """
        multiplier={'kg':1000, 'g':1}
        ingr_count = {}
        
        special_parsed_list_ingredients = []
        
        for ingredient in metric_list_ingredients:
            quantity, unit, ingredient_name = ingredient
            if ingredient_name not in self.dic_breakdowns:
                special_parsed_list_ingredients.append(ingredient)
                continue
                
            full_weight = float(sum([tupl[1] for tupl in self.dic_breakdowns[ingredient_name]]))
            
            for sub_ingredient in self.dic_breakdowns[ingredient_name]:
                sub_ingredient_name, sub_ingredient_weight = sub_ingredient
                proportion = sub_ingredient_weight/full_weight
                if unit:
                    new_quant = quantity * multiplier[unit] * proportion
                else:
                    new_quant = quantity * sub_ingredient_weight
                    

                if sub_ingredient_name not in ingr_count:
                    ingr_count[sub_ingredient_name] = new_quant
                else:
                    ingr_count[sub_ingredient_name] += new_quant
                    
        return special_parsed_list_ingredients, ingr_count
    
    def generate_converted(self, metric_list_ingredients):
        import math
        
        metric_list_ingredients, ingr_count = self.break_ingredients(metric_list_ingredients)
        
        for prime_ingredient in self.prime_ingredients:
            num_integer_ingredient = 0
            for sub_ingredient in self.dic_breakdowns[prime_ingredient]:
                sub_ingredient_name, sub_ingredient_weight = sub_ingredient
                
                if sub_ingredient_name not in ingr_count:
                    continue
                
                num_integer_ingredient = max(num_integer_ingredient, math.ceil(ingr_count[sub_ingredient_name]/sub_ingredient_weight))
                
            if num_integer_ingredient:
                metric_list_ingredients.append([num_integer_ingredient, '', prime_ingredient])
                
        return metric_list_ingredients
        
        
if __name__ == '__main__':
    pass