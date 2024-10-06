class Aisle:
    def __init__(self, path_aisle_conf):
        self.path_aisle_conf = path_aisle_conf
        self.load_aisle()
        
        self.all_ingredients = [ingredient for aisle in self.ordered_aisle for ingredient in self.ordered_aisle[aisle]]
        
    def load_aisle(self):
        with open(self.path_aisle_conf, 'r') as file:
            full_file = file.readlines()
        
        ingredient2aisle, ingredient2main_ingredient, ordered_aisle = {}, {}, {}
        
        for line in full_file:
            if line.startswith('['):
                current_aisle = line.replace('[', '').replace(']', '').replace('\n', '')
                ordered_aisle[current_aisle] = []
                continue
            
            line_ingredients = line.split('|')
            for ind, ingredient in enumerate(line_ingredients):
                ingredient = ingredient.replace('\n', '')
                if ingredient:
                    if not ind:
                        main_ingredient = ingredient
                    ingredient2aisle[ingredient] = current_aisle
                    ingredient2main_ingredient[ingredient] = main_ingredient
                    ordered_aisle[current_aisle].append(ingredient)
        
        self.ingredient2aisle = ingredient2aisle
        self.ingredient2main_ingredient = ingredient2main_ingredient
        self.ordered_aisle = ordered_aisle
        
        return ingredient2aisle, ingredient2main_ingredient, ordered_aisle
    
    def normalize_ingredient(self, ingredient):
        import sys
        
        if ingredient not in self.ingredient2main_ingredient:
            print('-'*10)
            print("An error occured.")
            print("This error occurred in the Aisle.normalize_ingredient() function.")
            print("Add '{0}' to 'aisle.conf' and try again.".format(ingredient))
            print('-'*10)
            sys.exit()
            
        return self.ingredient2main_ingredient[ingredient]
    
    def add_ingredient(self, ingredient, aisle):
        if ingredient in self.ingredient2main_ingredient:
            return
        
        self.ingredient2aisle[ingredient] = aisle
        self.ingredient2main_ingredient[ingredient] = ingredient
        
        if aisle not in self.ordered_aisle:
            self.ordered_aisle[aisle] = [ingredient]
        else:
            self.ordered_aisle[aisle].append(ingredient)
        
if __name__ == '__main__':
    pass