class DiagnosticTool:
    def __init__(self, root_cook='/home/adam/Documents/cooklang',
                 root_obsidian = '/home/adam/Documents/GoogleDrive/Vault'):
        
        self.root_cook = root_cook
        self.root_obsidian = root_obsidian
        
        self.cookfiles = self.get_cook_files()
       
    def get_cook_files(self):
        from pathlib import Path
        result = list(Path(self.root_cook).rglob("*.[cC][oO][oO][kK]"))

        return result
        
    def different_names(self):
        # Check that all recipes have different names
        import os
        all_names = [os.path.basename(path_cookfile) for path_cookfile in self.cookfiles]
        
        if len(all_names) != len(set(all_names)):
            for full_path, name in zip(self.cookfiles, all_names):
                if all_names.count(name) > 1:
                    print(str(full_path) + ' is a duplicate')
                    
    def grab_all_from_recipes(self, element_to_grab='ingredients'):
        from src.Recipe import Recipe
        
        ind_grab = ['', 'quantities', 'ingredients'].index(element_to_grab)

        ingredients_recipe = []
        for cookfile in self.cookfiles:
            rcp = Recipe(cookfile)
            ingredients_cookfile = [elt[ind_grab] for elt in rcp.get_list_ingredients()]
            ingredients_recipe.extend(ingredients_cookfile)
            
        return ingredients_recipe
                    
    def ingredients_classification(self, file_aisle):
        # Check that all ingredients in all recipes are described in the aisle.conf file
        from src.Aisle import Aisle

        ingredients_recipe = self.grab_all_from_recipes()
        
        aisl = Aisle(file_aisle) 
        ingredients_aisle = aisl.all_ingredients
        
        not_in_aisles = list(set(ingredients_recipe) - set(ingredients_aisle))
        if not_in_aisles:
            for ingr in not_in_aisles:
                print(ingr + " is not in an aisle")
                
    def check_metrics(self, file_metric):
        # Check that all metrics/quantities are described in the metric.conf file
        from src.Metric import Metric
        
        quantities_recipe = self.grab_all_from_recipes('quantities')
        quantities_recipe = [elt for elt in list(set(quantities_recipe)) if elt]
        
        mtc = Metric(file_metric)
        metrics_conf_file = mtc.all_units
        
        not_in_metric = list(set(quantities_recipe) - set(metrics_conf_file))
        if not_in_metric:
            for unit in not_in_metric:
                print(unit + ' is not described in the metric.conf file')
                
    def check_ingredient_types(self, file_aisle, file_special_conv):
        """Check if ingredients are both countable and quantified,
        which causes issues when making shopping lists
        Countable: Discrete values are used. ex: 3 oranges, 5 oignons
        Quantified: A measurement is used. ex: 500g, 20ml"""
        from src.Aisle import Aisle
        from src.Recipe import Recipe
        from src.SpecialConverter import SpecialConverter
        
        aisl = Aisle(file_aisle)
        scv = SpecialConverter(file_special_conv)
        
        conflicts = {}
        prev_conflict = []
        
        for cookfile in self.cookfiles:
            rcp = Recipe(cookfile)
            list_ingredients = rcp.get_list_ingredients()
            for quantity, unit, ingredient_name in list_ingredients:
                norm_ingredient_name = aisl.normalize_ingredient(ingredient_name)

                if not quantity or norm_ingredient_name in scv.dic_breakdowns.keys():
                    continue
                
                if norm_ingredient_name not in conflicts:
                    conflicts[norm_ingredient_name] = []
                
                if unit and 'quantified' not in conflicts[norm_ingredient_name]:
                    conflicts[norm_ingredient_name].append('quantified')
                    
                if not unit and 'countable' not in conflicts[norm_ingredient_name]:
                    conflicts[norm_ingredient_name].append('countable')
                    
                if len(conflicts[norm_ingredient_name]) == 2 and norm_ingredient_name not in prev_conflict:
                    prev_conflict.append(norm_ingredient_name)
                    print("Ingredient '{0}' is both countable and quantified, specify a conversion in 'special_conversions.conf'".format(norm_ingredient_name))

    def run_all_tools(self, file_metric, file_aisle, file_special_conv):
        self.different_names()
        self.check_metrics(file_metric)
        self.ingredients_classification(file_aisle)
        self.check_ingredient_types(file_aisle, file_special_conv)
    
if __name__ == '__main__':
    pass