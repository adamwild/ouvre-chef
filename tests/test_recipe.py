import unittest

class TestRecipe(unittest.TestCase):
    def setUp(self):
        from pathlib import Path
        from src.Recipe import Recipe
        from tests.utils import save_json, load_json
        
        main_folder = Path(__file__).parent.parent
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
        
        self.rcp_empty = Recipe(str(path_folder_cook / 'EmptyCookFile.cook'),
                                root_cooklang_test,
                                root_obsidian_test)
        
        self.rcp_all_metadata = Recipe(str(path_folder_cook / 'AllMetadata.cook'),
                                root_cooklang_test,
                                root_obsidian_test,self.path_test_environment)
        
        self.rcp_all_timers = Recipe(str(path_folder_cook / 'AllTimers.cook'),
                                root_cooklang_test,
                                root_obsidian_test,self.path_test_environment)
        
        self.rcp_full = Recipe(str(path_folder_cook / 'FullRecipe.cook'),
                                root_cooklang_test,
                                root_obsidian_test,self.path_test_environment)
        
        self.rcp_several_books = Recipe(str(path_folder_cook / 'SeveralBooks.cook'),
                                root_cooklang_test,
                                root_obsidian_test,self.path_test_environment)
        
        self.rcp_with_tags = Recipe(str(path_folder_cook / 'WithTags.cook'),
                                root_cooklang_test,
                                root_obsidian_test,self.path_test_environment)
        
        self.rcp_with_tags2 = Recipe(str(path_folder_cook / 'folder_nested' / 'WithTags2.cook'),
                                root_cooklang_test,
                                root_obsidian_test,self.path_test_environment)
        
        # Save the result of a computation, to be used as benchmark for future tests
        self.st = lambda data, test_name : save_json(data, self.root_expected_outputs, test_name)
        
        # Load the expected result of a given test name
        self.lt = lambda test_name : load_json(self.root_expected_outputs, test_name)
        
    def tearDown(self):
        import os
        
        # Cleanup the test environment
        if os.path.isfile(self.path_test_environment):
            os.remove(self.path_test_environment)
    
    def test_make_parsed_cook(self):
        self.assertEqual(self.rcp_empty.parsed_cook, [], 'empty file is not read as empty')
        
        self.assertEqual(self.rcp_all_metadata.parsed_cook,
                         self.lt('MakeParsedCook_AllMetadata'),
                         'cannot read metadata from cookfile')
        
        self.assertEqual(self.rcp_all_timers.parsed_cook,
                         self.lt('MakeParsedCook_AllTimers'),
                         'cannot read timers from cookfile')
        
        self.assertEqual(self.rcp_full.parsed_cook,
                         self.lt('MakeParsedCook_FullRecipe'),
                         'cannot read a complete recipe from cookfile')
        
    def test_get_book_name(self):
        self.assertEqual(self.rcp_empty.get_book_name(), None, 'does not return None when no book is specified')
        self.assertEqual(self.rcp_all_metadata.get_book_name(), None, 'does not return None when no book is specified')
        self.assertEqual(self.rcp_full.get_book_name(), 'A good cooking book', 'can not get book name')
        
        self.assertEqual(self.rcp_several_books.get_book_name(),
                         'A first book',
                         'cannot retrieve the first book when several books are specified in source')
        
    def test_load_root_cookbooks(self):
        from src.Recipe import Recipe
        from tests.utils import update_test_environment
      
        self.rcp_env = Recipe(str(self.path_folder_cook / 'EmptyCookFile.cook'),
                                self.root_cooklang_test,
                                self.root_obsidian_test,
                                self.path_test_environment)
        
        # Test loading a lonely path
        update_test_environment('ROOTS_COOKBOOKS', "/a/single/path", self.path_test_environment)
        self.rcp_env.load_root_cookbooks()
        self.assertEqual(self.rcp_env.root_cookbooks, ['/a/single/path'], 'cannot read single root_cookbooks')
        
        # Test loading several paths
        update_test_environment('ROOTS_COOKBOOKS', '/some/path1, /some/path2', self.path_test_environment)
        self.rcp_env.load_root_cookbooks()
        self.assertEqual(self.rcp_env.root_cookbooks, ['/some/path1', '/some/path2'], 'cannot read multiple root_cookbooks')
        
    
    def test_update_book(self):
        import os
        from tests.utils import update_test_environment
        
        update_test_environment('ROOTS_COOKBOOKS', self.path_test_cookbooks, self.path_test_environment)
        self.rcp_full.update_book()
        book_path = str(self.root_obsidian_test / "Livres" / 'A good cooking book.md')
        self.assertTrue(os.path.exists(book_path), 'cannot update book from recipe')
        
        os.remove(book_path)
        
    def test_grab_manually_timed_moments(self):
        self.assertEqual(self.rcp_empty.grab_manually_timed_moments(), [], "no manually timed moment does not return as empty")
        self.assertEqual(self.rcp_all_timers.grab_manually_timed_moments(),
                         [('t_actif', 8), ('t_batteur', 4), ('t_repos', 45), ('t_cuisson', 35), ('t_repos', 105), ('t_repos', 105), ('t_repos', 105)],
                         "cannot grab the lanually timed moments")
        
    def test_make_schedule_bar(self):
        self.assertEqual(self.rcp_empty.make_schedule_bar(),
                         '',
                         "schedule bar is not an empty string when no manually timed moments exist")
        self.assertEqual(self.rcp_all_timers.make_schedule_bar(),
                         self.lt("MakeScheduleBar_AllTimers"),
                         "cannot make schedule bar")
        
    def test_make_manual_timings(self):
        self.assertEqual(self.rcp_empty.make_manual_timings(), '', "not empty")
        self.assertEqual(self.rcp_all_timers.make_manual_timings(),
                         self.lt("MakeManualTimings_AllTimers"),
                         "cannot make manual timings")
        
    def test_grab_specific_metadata(self):
        self.assertEqual(self.rcp_empty.grab_specific_metadata('type_liens'), {}, "doesn't return empty dictionary when no metadata exists")
        
        dic_typeliens = {'type_liens': 'Vidéo, Site'}
        self.assertEqual(self.rcp_full.grab_specific_metadata('type_liens'), dic_typeliens, 'cannot get metadata from string')
        self.assertEqual(self.rcp_full.grab_specific_metadata(['type_liens']), dic_typeliens, 'cannot get metadata from single key in list')
        
        self.assertEqual(self.rcp_full.grab_specific_metadata(['type_liens', 'cuisson']),
                         {'cuisson': '35 minutes', 'type_liens': 'Vidéo, Site'},
                         "cannot get multiple metadata")
        
    def test_grab_separate_tags(self):
        self.rcp_full.grab_separate_tags()
        self.assertEqual((self.rcp_full.extra_tags, self.rcp_full.written_tags),
                         (['folder_cookfiles1'], []), 
                         'cannot extract extra tag from simple nested recipe')
        
        self.rcp_with_tags.grab_separate_tags()
        self.assertEqual((self.rcp_with_tags.extra_tags, self.rcp_with_tags.written_tags),
                         (['folder_cookfiles1'], ['simple', 'frais', 'en avance']), 
                         'cannot extract written tags')
        
        self.rcp_with_tags2.grab_separate_tags()
        self.assertEqual((self.rcp_with_tags2.extra_tags, self.rcp_with_tags2.written_tags),
                         (['folder_cookfiles1', 'folder_nested'], ['été', 'complexe']), 
                         'cannot extract extra tag from nested recipe')
        
    def test_grab_full_tags(self):
        self.assertEqual(self.rcp_full.grab_full_tags(), ['folder_cookfiles1'])
        
        self.assertEqual(self.rcp_with_tags.grab_full_tags(),
                         ['en avance', 'folder_cookfiles1', 'frais', 'simple'])
        
        self.assertEqual(self.rcp_with_tags2.grab_full_tags(),
                         ['complexe', 'folder_cookfiles1', 'folder_nested', 'été'])

    def test_make_tags(self):
        print(self.rcp_with_tags.make_tags())
            
if __name__ == '__main__':
    unittest.main()