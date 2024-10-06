from src.Metadata_tools.Meta import Meta

class Biblio(Meta):
    def __init__(self, root_cooklang, root_obsidian, folders_cookbooks = [],
                 path_env = None):
        import os
        super().__init__(root_cooklang)
        
        from pathlib import Path
        from dotenv import load_dotenv
        
        main_folder = Path(__file__).parent.parent.parent
        
        if path_env is None:
            self.environment = str(main_folder / 'environment.env')
        else:
            self.environment = path_env
        
        self.root_cooklang = root_cooklang
        self.root_obsidian = root_obsidian     
        # self.root_books = os.path.join(self.root_cooklang, 'config', 'books')
        self.root_books = os.path.join(self.root_cooklang, 'books')
        
        self.folders_cookbooks = folders_cookbooks

        self.book2index = self.find_recipes_from_books()
        self.all_cookbooks_pdf = None
        
        self.get_books()
        self.load_books()
        
    def get_books(self):
        from pathlib import Path

        book_files = list(Path(self.root_books).rglob("*.[bB][oO][oO][kK]"))
        book_files = [str(book_file) for book_file in book_files]
        
        self.path_books = book_files
        
    def get_book_from_name(self, name):
        for book in self.books:
            book_name = book.namefile
            if name == book_name:
                return book
        
    def find_recipes_from_books(self):
        from src.Recipe import Recipe
        
        def retrieve_book_title(source):
            if '[[' and ']]' in source:
                beg = source.index('[[')
                end = source.index(']]')
                return source[beg+2:end]
        
        if not self.cookfiles:
            self.get_cook_files()
            
        book2index = {}
            
        for cookfile in self.cookfiles:
            rcp = Recipe(cookfile)
            metadata = rcp.grab_specific_metadata(['source', 'page'])
            
            if 'page' in metadata:
                page_num = int(metadata['page'])
                book_name = retrieve_book_title(metadata['source'])
                
                if book_name not in book2index:
                    book2index[book_name] = {page_num: [rcp.recipe_name]}

                else:
                    if page_num not in book2index[book_name]:
                        book2index[book_name][page_num] = [rcp.recipe_name]
                    else:
                        book2index[book_name][page_num].append(rcp.recipe_name)

            
        # Order the recipes according to their page number
        self.book2index = book2index
        
        return book2index
    
    def list_all_cookbooks_pdf(self):
        from pathlib import Path
        
        all_cookbooks_pdf = []
        
        for path in self.folders_cookbooks:
            result = list(Path(path).rglob("*.[pP][dD][fF]"))
            result.extend(list(Path(path).rglob("*.[e][p][u][b]")))
            result = [str(path) for path in result]
            
            all_cookbooks_pdf.extend(result)
            
        self.all_cookbooks_pdf = all_cookbooks_pdf
        
        return all_cookbooks_pdf
    
    def get_all_cookbooks_pdf(self):
        if self.all_cookbooks_pdf is None:
            self.list_all_cookbooks_pdf()
            
        return self.all_cookbooks_pdf
    
    def load_books(self):
        from src.Metadata_tools.Book import Book
        
        self.books = [Book(path_book, self, self.root_obsidian, path_env = self.environment) for path_book in self.path_books]

    def make_all_cookbooks_to_md(self):
        for bk in self.books:
            bk.save_as_md()
        
if __name__ == '__main__':
    pass