import unittest

class TestRecipe(unittest.TestCase):
    def setUp(self):
        from pathlib import Path
        from src.Recipe import Recipe
        from tests.utils import save_json, load_json
        from src.Metadata_tools.Book import Book
        
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
        
        self.root_book_files = root_cooklang_test / 'books'
        
        self.root_cookbooks = main_folder / 'test_data' / 'cookbooks'
        
        path_empty_book = str(self.root_book_files / 'EmptyBook.book')
        self.empty_bk = Book(path_empty_book, biblio = None, root_obsidian = self.root_obsidian_test, path_env = self.path_test_environment)
        
        path_practicebook = str(self.root_book_files / 'Practice.book')
        self.practice_bk = Book(path_practicebook, biblio = None, root_obsidian = self.root_obsidian_test, path_env = self.path_test_environment)
    
        path_tags_book = str(self.root_book_files / 'BookTags.book')
        self.tags_bk = Book(path_tags_book, biblio = None, root_obsidian = self.root_obsidian_test, path_env = self.path_test_environment)
        
    def test_parse_book(self):
        self.empty_bk.parse_book()
        self.assertEqual(self.empty_bk.dic_page_recipes_bk, {})
        self.assertEqual(self.empty_bk.book_index, [])
        self.assertEqual(self.empty_bk.tag_info, {})
        
        # Testing general book parsing
        self.practice_bk.parse_book()
        self.assertEqual(self.practice_bk.dic_page_recipes_bk,
                         {27: ["Griess soupe à l'alsacienne", "Une autre soupe"], 38: ['Gelée de volaille']})
        self.assertEqual(self.practice_bk.book_index,
                         [('title_1', None, 'Les recettes'), ('title_2', 25, 'Potages'), ('title_2', 31, 'Sauces')])
        
        # Testing tags parsing
        self.tags_bk.parse_book()
        self.assertEqual(self.tags_bk.tag_info,
                         {'pdf': 'someNameFile.pdf', 'chef': "Paul Bocuse", 'tags': "simple, en avance"})
        
    def test_get_path_biblio(self):
        self.assertTrue(self.empty_bk.get_path_biblio().endswith('test_data/cooklang_folder/books'))
        
    def test_get_pdf(self):
        self.assertEqual(self.empty_bk.get_pdf(), '')
        self.assertEqual(self.tags_bk.get_pdf(), 'someNameFile.pdf')
        
    def test_get_authors(self):
        self.assertEqual(self.empty_bk.get_authors(), '')
        self.assertEqual(self.tags_bk.get_authors(), 'Paul Bocuse')
        
    def test_get_chef(self):
        self.assertEqual(self.empty_bk.get_chef(), '')
        self.assertEqual(self.tags_bk.get_chef(), 'Bocuse')
        
    def test_get_tags(self):
        self.assertEqual(self.empty_bk.get_tags(), '')
        self.assertEqual(self.tags_bk.get_tags(), ['simple', 'en avance'])
        
    def test_get_full_link_pdf(self):
        import os
        
        cookbooks = os.listdir(str(self.root_cookbooks))
        link_cookbooks = [os.path.join(str(self.root_cookbooks), file) for file in cookbooks]
                
        ending = os.path.join('test_data', 'cookbooks', 'someNameFile.pdf')
        self.assertTrue(self.tags_bk.get_full_link_pdf(link_cookbooks).endswith(ending))
        
if __name__ == '__main__':
    unittest.main()