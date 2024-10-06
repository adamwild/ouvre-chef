import unittest

class TestRecipe(unittest.TestCase):
    def setUp(self):
        from pathlib import Path
        from src.Recipe import Recipe
        from tests.utils import save_json, load_json
        from src.Metadata_tools.Tags import Tags
        
        main_folder = Path(__file__).parent.parent.parent
        self.main_folder = main_folder
        root_cooklang_test = main_folder / 'test_data' / 'cooklang_folder'
        root_obsidian_test = main_folder / 'test_data' / 'test_outputs' / 'obsidian_vault'
        
        self.root_cooklang_test = root_cooklang_test
        self.root_obsidian_test = root_obsidian_test
        
        self.path_test_environment = str(self.main_folder / 'test_data' / 'test_environment.env')
                
        path_folder_cook = root_cooklang_test / 'folder_cookfiles1'
        self.path_folder_cook = path_folder_cook
        self.path_test_cookbooks = str(self.main_folder / 'test_data' / 'cookbooks')
        
        self.root_expected_outputs = main_folder / 'test_data' / 'test_outputs' / 'test_recipe'
        
        self.tgs = Tags(root_cooklang_test)
    
    def test_make_dic_metadata(self):
        self.tgs.make_dic_metadata()
        
        self.assertTrue('EmptyCookFile' in self.tgs.dic_metadata)
        self.assertTrue('complexe' in self.tgs.dic_metadata['WithTags2'])
        
    def test_get_folder_tags(self):
        self.assertEqual(self.tgs.get_folder_tags(), ['folder_cookfiles1', '', 'folder_nested'])
        
    def test_load_tags(self):
        self.tgs.load_tags()
        
        self.assertEqual(self.tgs.tags, ['minute', 'en avance', 'simple', 'frais', 'été', 'hiver', 'automne'])
        self.assertEqual(self.tgs.seperated_full_tags, ['folder_cookfiles1', '',
                                                        'folder_nested', '',
                                                        'minute', 'en avance', '',
                                                        'simple', 'frais', '',
                                                        'été', 'hiver', 'automne'])
        
    def test_save_df_metadata(self):
        import os
        path_recipe_metadata = str(self.root_cooklang_test / 'config' / 'recipe_metadata.csv')
        
        if os.path.isfile(path_recipe_metadata):
            os.remove(path_recipe_metadata)
        
        self.tgs.save_df_metadata()
        
        self.assertTrue(os.path.isfile(path_recipe_metadata))
        os.remove(path_recipe_metadata)
        
    def test_load_df_metadata(self):
        import os
        import pandas as pd
        path_recipe_metadata = str(self.root_cooklang_test / 'config' / 'recipe_metadata.csv')
        
        self.tgs.save_df_metadata()
        
        prev_df_recipe_metadata = self.tgs.df_recipe_metadata
        prev_all_tags = self.tgs.all_tags
        prev_metadata_counts = self.tgs.metadata_counts
        
        self.tgs.load_df_metadata()
        pd.testing.assert_frame_equal(self.tgs.df_recipe_metadata, prev_df_recipe_metadata)
        self.assertEqual(self.tgs.all_tags, prev_all_tags)
        self.assertEqual(self.tgs.metadata_counts, prev_metadata_counts)
        
        os.remove(path_recipe_metadata)
        
    def test_subselection_recipe_by_tags(self):
        self.tgs.subselection_recipe_by_tags(['printemps'])
        
        self.assertTrue(('simple', 0) in self.tgs.metadata_counts)
        
    def test_write_ordered_tags(self):
        self.assertEqual(self.tgs.write_ordered_tags(['simple', 'en avance']), '#simple #en_avance')
        
if __name__ == '__main__':
    unittest.main()