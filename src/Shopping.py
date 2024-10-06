class Shopping:
    def __init__(self, path_meals, path_groceries, root_cooklang, root_obsidian, metric_obj, aisle_obj) -> None:
        import os
        
        self.path_meals = path_meals
        self.path_groceries = path_groceries
        self.working_folder = os.path.dirname(path_groceries)
        
        self.root_cooklang = root_cooklang
        self.root_obsidian = root_obsidian
        
        self.metric_obj = metric_obj
        self.aisle_obj = aisle_obj
        
        self.recipes = []
        
    def build_recipe(self, recipe_name):
        import os
        from src.Recipe import Recipe
        
        def find_file(name, root):
            for path, dirs, files in os.walk(root):
                if name in files:
                    return os.path.join(path, name)
            return None
        
        for elt in ['[', ']', '\n']:
            recipe_name = recipe_name.replace(elt, '')
        recipe_name+='.cook'
            
        path_cook = find_file(recipe_name, self.root_cooklang)
        rcp = Recipe(path_cook)
        
        return rcp
    
    def gather_ingredients(self):
        
        # Gather ingredients from all meals
        all_ingredients = []
        
        with open(self.path_meals) as f:
            lines = f.readlines()
            
        for line in lines:
            scaler, recipe_name = '', ''
            if '*' in line:
                scaler, recipe_name = line.split('*')
            elif '[[' in line:
                recipe_name = line
                
            if recipe_name:
                rcp = self.build_recipe(recipe_name)
                
                if scaler:
                    scaler*rcp
                
                rcp.save_as_md()
                
                self.recipes.append(rcp)
            
                all_ingredients.extend(rcp.get_list_ingredients())
            
        # Gather ingredients from the groceries list
        with open(self.path_groceries) as f:
            lines = f.readlines()
            
        for line in lines:
            if not line.startswith('-'):
                curr_aisle = line.replace('#', '').strip()
            elif line.startswith('- [x]'):
                ingredient = line.replace('- [x]', '').strip()
                if ingredient not in [ingr[2] for ingr in all_ingredients]:
                    all_ingredients.append(['', '', ingredient])
                    self.aisle_obj.add_ingredient(ingredient, curr_aisle)
        
          
        metric_list_ingredients = self.metric_obj.metricize_ingredients(all_ingredients, self.aisle_obj)

        import os
        from src.SpecialConverter import SpecialConverter
        file_special_conv = os.path.join(self.root_cooklang, 'config', 'special_conversions.conf')
        scv = SpecialConverter(file_special_conv)
        special_parsed_list_ingredients = scv.generate_converted(metric_list_ingredients)
        # special_parsed_list_ingredients = self.egg_counter(metric_list_ingredients)
            
        aggregated_ingredients = self.metric_obj.aggregate_ingredient_quantities(special_parsed_list_ingredients)
        
        return aggregated_ingredients
    
    def dispatch_ingredients(self, ingredients_list):
        from src.utils import ingredient2listecourse
        
        ordered_aisle = self.aisle_obj.ordered_aisle
        
        sol = ""
    
        for aisle in ordered_aisle:
            if set(ordered_aisle[aisle]).intersection(set(ingredients_list)):
                sol += "##### " + aisle +'\n'
                
                for ingr in ordered_aisle[aisle]:
                    if ingr in ingredients_list:
                        value, metric = ingredients_list[ingr]
                        sol += '- [ ] '
                        sol += ingredient2listecourse(value, metric, ingr, self.metric_obj) + '\n'
                sol += '\n'
                
        return sol.strip()
    
    def pp_meals(self):
        sol = ""
        for recipe in self.recipes:
            sol += '- ' + recipe.pp_quantity() + '\n'
        return sol.strip()
        
    def __str__(self):
        ingredients_list = self.gather_ingredients()
        
        shopping_list_md = self.dispatch_ingredients(ingredients_list)
        return '\n\n'.join([self.pp_meals(), shopping_list_md])
    
    def to_file(self, path_file):
        with open(path_file, 'w') as f:
            f.write(str(self))
            
    def get_path_final_file(self):
        import os
        with open(self.path_meals, 'r') as f:
            file_data = f.read()
            
        title = file_data.split('\n')[0] + '.md'
        path_final = os.path.join(self.working_folder, title)
        self.path_final = path_final
        
        return path_final
            
    def check_and_trigger(self):
        path_final = self.get_path_final_file()
        
        self.to_file(path_final)
        
    def read_final_file(self):
        final_list = {}
        with open(self.path_final, 'r') as f:
            file_data = f.readlines()
            
        for line in file_data:
            if '[[' in line:
                continue
            
            if line.startswith('#####'):
                aisle = line.replace('#####', '').strip()
                
            elif line.startswith('- [ ]'):
                grocery = line.replace('- [ ]', '').strip()
                if aisle not in final_list:
                    final_list[aisle] = [grocery]
                else:
                    final_list[aisle].append(grocery)
            
        return final_list
    
    def get_updated_final_file(self):
        sol = ""
        with open(self.path_final, 'r') as f:
            file_data = f.readlines()
            
        for line in file_data:
            if line.startswith('#####'):
                break
            sol += line
            
        final_list = self.read_final_file()
        
        for aisle in final_list:
            sol += '##### ' + aisle + '\n'
            for grocery in final_list[aisle]:
                sol += '- [ ] ' + grocery + '\n'
            sol += '\n'
                
        return sol.strip()
            
    def cleanup(self):
        """Removes items already crossed in the final file and uncrosses those in the
        groceries list file
        """
        # Remove items already crossed in the final file
        self.get_path_final_file()
        update_final_file = self.get_updated_final_file()
        
        with open(self.path_final, 'w') as f:
            f.write(update_final_file)
            
        # Uncrosse items in the groceries list file
        with open(self.path_groceries) as f:
            file_data = f.read()
            file_data = file_data.replace('- [x]', '- [ ]')
            
        with open(self.path_groceries, 'w') as f:
            f.write(file_data)


    
if __name__ == '__main__':
    pass