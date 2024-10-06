from src.Metadata_tools.Meta import Meta

class Tags(Meta):
    def __init__(self, root_cooklang, metadata_key=None, load_csv_metadata = False):
        import os
        super().__init__(root_cooklang, metadata_key, load_csv_metadata)
        
        self.seperated_full_tags = None
        self.path_csv_metadata = os.path.join(self.root_cooklang, 'config', 'recipe_metadata.csv')
        
        
    def make_dic_metadata(self):
        """Makes the dictionary {'recipe_name': [list of full tags]}"""
        from src.Recipe import Recipe
        
        if self.recipe2path is None:
            self.make_recipe2path()
        
        dic_metadata = {}
        
        for recipe, path_recipe in self.recipe2path.items():
            rcp = Recipe(path_recipe)
            metadata = rcp.grab_full_tags()
            
            if metadata:
                dic_metadata[recipe] = metadata
            else:
                dic_metadata[recipe] = []
                
        self.dic_metadata = dic_metadata
        
    def get_folder_tags(self):
        """Returns a list containing all folders under the root_cooklang folder.
        This method scans only one subfolder deep, meaning it will not scan further subfolders within the subfolders.
        For example, it can only retrieve folders like root_cooklang/folder1/subfolderA.
        This limitation is due to the current unnecessary complexity of using multiple subfolders.

        Whenever a new folder is scanned, it is represented in the list by an empty string.

        Output example: ['folder1', 'folder2', '', 'subfolder1A', 'subfolder1B', '', 'subfolder2A']
        """
        def extend_list(list_of_lists):
            solution = []
            for i, sublist in enumerate(list_of_lists):
                solution.extend(sublist)
                
                if i < len(list_of_lists) - 1:
                    solution.append('')

            return solution
        
        if not self.cookfiles:
            self.get_cook_files()
            
        folder_tags = []
            
        self.cookfiles.sort()
        for cookfile in self.cookfiles:
            end_file = cookfile.replace(str(self.root_cooklang), '')
            folders = end_file.split('/')[1:-1]
            
            for ind, folder in enumerate(folders):
                while len(folder_tags) < len(folders):
                    folder_tags.append([])
                    
                if folder.lower() not in folder_tags[ind]:
                    folder_tags[ind].append(folder.lower())
                    if len(folder_tags) > ind + 1 and folder_tags[ind+1]:
                        folder_tags[ind+1].append('')
                
        return extend_list(folder_tags)
        
    def load_tags(self):
        """Loads the 'config/tags.conf' file. Also combines these tags with the folder_tags from the get_folder_tags method.
        
        Makes:
        self.tags: List of the tags written in 'config/tags.conf'
        self.seperated_full_tags: List of all the tags, first the folder_tags, then the tags.
            Subcategories are separated by empty strings.

        Raises:
            FileNotFoundError: Raised when 'config/tags.conf' does not exist.

        Returns:
            self.tags
        """
        import os
        
        path_tags_conf = os.path.join(self.root_cooklang, 'config', 'tags.conf')
        
        if not os.path.exists(path_tags_conf):
            raise FileNotFoundError("The tags.conf file was not found in the 'config' folder")
        
        with open(path_tags_conf, 'r') as f:
            lines = f.readlines()
            
        tags = [tag.strip() for tag in lines if tag.strip()]
        
        self.tags = tags
        
        # Full list of tags, starts with the folder tags then the config tags
        # Different categories are separated by an empty string
        seperated_full_tags = self.get_folder_tags()
        seperated_full_tags.append('')
        for tag in lines:
            to_append = ''
            if tag.strip():
                to_append = tag.strip()
            seperated_full_tags.append(to_append)
            
        self.seperated_full_tags = seperated_full_tags
        
        return tags
    
    def save_df_metadata(self):
        """Makes and save the DataFrame containing all the recipes with their respective Tags.
        Usually called 'recipe_metadata.csv'
        """
        if not self.df_recipe_metadata:
            self.make_df_recipe_metadata()
            
        self.df_recipe_metadata.to_csv(self.path_csv_metadata)
        
    def load_df_metadata(self):
        """Loads 'df_recipe_metadata', 'all_tags' and 'metadata_counts' from 'recipe_metadata.csv'
        """
        import pandas as pd

        self.df_recipe_metadata = pd.read_csv(self.path_csv_metadata, index_col=0)
        
        all_tags = list(self.df_recipe_metadata.columns)
        self.all_tags = all_tags
        self.metadata_counts = [(tag, self.df_recipe_metadata[tag].sum()) for tag in all_tags]
        
    def subselection_recipe_by_tags(self, list_tags):
        """Recomputes 'df_recipe_metadata' and 'metadata_counts' by ignoring all recipes that do not have all the tags specified in 'list_tags'

        Args:
            list_tags (list): List of tags, ['simple', 'en avance']
        """
        if not self.metadata_counts:
            if self.load_csv_metadata:
                self.load_df_metadata()
            else:
                self.make_df_recipe_metadata()
                
        condition = self.df_recipe_metadata[list_tags].all(axis=1)

        self.df_recipe_metadata = self.df_recipe_metadata[condition]
        self.metadata_counts = [(tag, self.df_recipe_metadata[tag].sum()) for tag in self.all_tags]
    
    def pp_tags(self):
        """Pretty printer for 'metadata_counts'. Prints each tag with the corresponding count
        Could be prettier though.
        """
        if not self.seperated_full_tags:
            self.load_tags()
            
        if not self.metadata_counts:
            if self.load_csv_metadata:
                self.load_df_metadata()
            else:
                self.make_df_recipe_metadata()
            
        dic_metadata_counts = {tuple[0]:tuple[1] for tuple in self.metadata_counts}
        # Find the length of the longest key
        max_key_length = max(len(key) for key in self.seperated_full_tags)

        # Iterate through the keys and print key and value
        for key in self.seperated_full_tags:
            value = dic_metadata_counts.get(key, "")
            if not value:
                value = 0
            if key == "":
                print("")
            else:
                print(f"{key:{max_key_length}} {value}")
        
    def write_ordered_tags(self, list_full_tags):
        """From a list of tags of a given recipe, produces the string that
        will be read in the corresponding recipe in markdown.
        
        First we write the tags described in 'tags.conf', respecting the same order
        then we write all other tags that were not in said conf file.

        Args:
            list_full_tags list[str]: _description_
        """
        self.load_tags()
        # Create a dictionary to store the indices of words in list A
        index_map = {word.replace: index for index, word in enumerate(self.tags)}
        
        # Sort list B based on the custom order defined by list A
        sorted_tags = sorted(list_full_tags, key=lambda word: index_map.get(word, len(self.tags)))
        
        # Replace spaces with underscore
        sorted_tags = [tag.replace(' ', '_') for tag in sorted_tags]
        
        written_tags = '#' + ' #'.join(sorted_tags)
        return written_tags
        
if __name__ == '__main__':
    pass