import unittest

class TestRecipe(unittest.TestCase):
    def setUp(self):
        from pathlib import Path
        from src.Metadata_tools.Meta import Meta
        
        main_folder = Path(__file__).parent.parent.parent
        root_cooklang_test = main_folder / 'test_data' / 'cooklang_folder'

        self.mt = Meta(root_cooklang_test, 'tags')
    
    def test_get_cook_files(self):
        self.mt.get_cook_files()
        
        self.assertTrue(len(self.mt.cookfiles) > 0, 'no cooklang file found')
        self.assertTrue(all(file_name.endswith('.cook') for file_name in self.mt.cookfiles),
                        'non cooklang files found when getting cooklang files')
        
    def test_make_recipe2path(self):
        self.mt.make_recipe2path()
        
        self.assertTrue(len(self.mt.recipe2path) > 0)
        
    def test_make_dic_metadata(self):
        self.mt.make_dic_metadata()
        
        self.assertEqual(self.mt.dic_metadata['WithTags2'], ['été', 'complexe'])
        self.assertEqual(self.mt.dic_metadata['AllMetadata'], ['printemps', 'été', 'en avance'])
        
    def test_make_df_recipe_metadata(self):
        self.mt.make_df_recipe_metadata()
        
        self.assertTrue('en avance' in self.mt.all_tags)
        self.assertTrue(self.mt.df_recipe_metadata['printemps']['AllMetadata'])
        self.assertTrue(('en avance', 2) in self.mt.metadata_counts)
        
    def test_select_recipe_by_metadata(self):
        self.assertEqual(self.mt.select_recipe_by_metadata('complexe'), ['WithTags2'])
        self.assertEqual(self.mt.select_recipe_by_metadata(['en avance', 'frais']), ['WithTags'])

        
if __name__ == '__main__':
    unittest.main()