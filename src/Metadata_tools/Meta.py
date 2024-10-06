class Meta:
    def __init__(self, root_cooklang, metadata_key=None, load_csv_metadata = False) -> None:
        self.root_cooklang = root_cooklang
        
        self.metadata_key = metadata_key
        
        self.cookfiles = None
        self.recipe2path = None
        self.dic_metadata = None
        
        self.df_recipe_metadata = None
        self.metadata_counts = None
        
        self.load_csv_metadata = load_csv_metadata
    
    def get_cook_files(self):
        """Gets all files ending in '.cook' in the folder and its nested folders from 'root_cooklang'."""
        import os
        from pathlib import Path
        result = list(Path(self.root_cooklang).rglob("*.[cC][oO][oO][kK]"))
        
        files_timestamp = [(file, os.path.getmtime(file)) for file in result]
        files_timestamp.sort(key=lambda x :-x[1])
        
        cookfiles = [str(file) for file, _ in files_timestamp]
        self.cookfiles = cookfiles
            
    def make_recipe2path(self):
        """Returns a dictionary with the recipe names and the path to the cooklang file
        
        returns:
        {recipe_name : '/path/to/recipe_name.cook}"""
        import os
        
        if self.cookfiles is None:
            self.get_cook_files()
        
        recipe2path = {os.path.basename(cookfile.replace('.cook', '')):cookfile for cookfile in self.cookfiles}
        self.recipe2path = recipe2path
            
    def make_dic_metadata(self):
        """Gathers the metadata in the recipes using 'metadata_key'
        For instance, if 'metadata_key' is 'Tags', the output will be
        {recipe_name: ['tag1', 'tag2'], ...}"""
        from src.Recipe import Recipe
        
        if self.recipe2path is None:
            self.make_recipe2path()
        
        dic_metadata = {}
        
        for recipe, path_recipe in self.recipe2path.items():
            rcp = Recipe(path_recipe)
            metadata = rcp.grab_specific_metadata(self.metadata_key)
            
            if metadata:
                dic_metadata[recipe] = [elt.strip() for elt in metadata[self.metadata_key].split(',')]
                # dic_metadata[recipe] = metadata[self.metadata_key].replace(' ', '').split(',')
            else:
                dic_metadata[recipe] = []
                
        self.dic_metadata = dic_metadata
        
    def make_df_recipe_metadata(self):
        """Makes a dataframe containing all the metadata information.
        Written with "metadata_key=Tags" in mind but may be reused for other purposes in the future
        
        returns:
        self.all_tags: A list containing all metadata values found in the recipes
        self.df_recipe_metadata: A DataFrame, rows are recipes, columns are metadata values, cells are booleans
        self.metadata_counts: A list of tuples containing the tags with their respective counts
        """
        import pandas as pd
        
        if self.dic_metadata is None:
            self.make_dic_metadata()
        
        all_tags = set([metadata for _, metadatas in self.dic_metadata.items() for metadata in metadatas])
        all_tags = list(all_tags)
        all_tags.sort()
        
        self.all_tags = all_tags
                
        # Create an empty DataFrame
        df = pd.DataFrame(index=self.dic_metadata.keys(), columns=all_tags, dtype=bool)
        df.values[:] = False

        # Populate the DataFrame based on the metadata
        for recipe_name, tags in self.dic_metadata.items():
            df.loc[recipe_name, tags] = True
            
        # Sort recipes alphabetically
        df.sort_index(inplace=True)
            
        self.df_recipe_metadata = df
        
        # Create a list of tuples containing tag names and their corresponding counts
        self.metadata_counts = [(tag, df[tag].sum()) for tag in all_tags]
        
    def pp_metadata_counts(self):
        """Pretty printer for self.metadata_counts
        Prints the tuples 'Metadata value - Metadata value count' in descending order"""
        if self.metadata_counts is None:
            if self.load_csv_metadata:
                self.load_df_metadata()
            else:
                self.make_df_recipe_metadata()
            
        ordered_metadata_counts = sorted(self.metadata_counts, key=lambda x: x[1], reverse=True)

        max_name_length = max(len(name) for name, _ in ordered_metadata_counts)

        for name, value in ordered_metadata_counts:
            print(f"{name:{max_name_length}} {value}")

        
    def select_recipe_by_metadata(self, list_tags):
        """Selects the recipes that contains the same metadata as in 'list_tags'"""
        if self.df_recipe_metadata is None:
            if self.load_csv_metadata:
                self.load_df_metadata()
            else:
                self.make_df_recipe_metadata()
            
        if type(list_tags) is not list:
            list_tags = [list_tags]
            
        list_tags = [tag.replace('_', ' ') for tag in list_tags]
            
        recognized_tags = [tag for tag in list_tags if tag in self.all_tags]
        unrecognized_tags = [tag for tag in list_tags if tag not in self.all_tags]
        
        if unrecognized_tags:
            for tag in unrecognized_tags:
                print("Warning: {0} not in known tags !".format(tag))
            
            if not recognized_tags:
                return None
            
            print()
        df = self.df_recipe_metadata
        filtered_recipes = df[df[recognized_tags].all(axis=1)].index.tolist()
        
        return filtered_recipes


if __name__ == '__main__':
    pass