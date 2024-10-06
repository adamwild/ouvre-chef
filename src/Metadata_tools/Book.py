class Book():
    def __init__(self, path_book, biblio = None, root_obsidian = None, path_env = None):
        import os
        from pathlib import Path
        from dotenv import load_dotenv
        
        main_folder = Path(__file__).parent.parent.parent
        
        if path_env is None:
            self.environment = str(main_folder / 'environment.env')
        else:
            self.environment = path_env

        load_dotenv(dotenv_path=self.environment, override=True)
        
        self.path_book = path_book
        self.root_obsidian = root_obsidian
        self.general_tags = ['pdf', 'chef', 'tags']
        self.tag_info = {}
        
        self.title2indent = {'title_1' : '##', 'title_2' : '######'}
        
        self.namefile = os.path.basename(path_book).replace('.book', '')
        
        #TODO Put this in a setup file
        # self.name_root_biblio_obsi = 'Livres'
        
        self.name_root_biblio_obsi = os.getenv('NAME_BOOK_FOLDER_VAULT')
        # Default folder for .book files output (i.e. markdown files) is <OBSIDIAN_FOLDER> / 'books'
        if self.name_root_biblio_obsi is None:
            self.name_root_biblio_obsi = 'books'
        
        self.parse_book()
        
        self.full_link_pdf = None
        
        verbose_env = os.getenv('VERBOSE')
        if verbose_env is None:
            self.verbose = False
        else:
            self.verbose = bool(verbose_env)
                
        # Handle Biblio related attributes
        if biblio is not None:
            
            # No recipe has a reference to this book
            if self.namefile not in biblio.book2index:
                self.dic_page_recipes_rcp = None
            else:
                self.dic_page_recipes_rcp = biblio.book2index[self.namefile]
            self.list_cookbooks_pdf = biblio.get_all_cookbooks_pdf()
        else:
            self.dic_page_recipes_rcp = None
            self.list_cookbooks_pdf = None
        
    def parse_book(self):
        """Parses a book file and produces tag_info, dic_page_recipes_bk, book_index
        
        tag_info (dict): Dictionary of tags indicated in the .book file
                         {'chef': "Paul Bocuse"}
        dic_page_recipes_bk (dict): Each key is a page number associated to a list of recipes on said page
                        {27: ["Griess soupe à l'alsacienne", "Une autre soupe"]}
        book_index (list[triplet]): List of triplets coding the chapters (type_of_chapter, beginning_of_chapter, title)
                        [('title_1', None, 'Les recettes'), ('title_2', 25, 'Potages')
        """
        dic_page_recipes_bk = {}
        book_index = []
        with open(self.path_book, 'r') as f:
            for line in f.readlines():
                words = line.split() 
                
                if line.startswith('>>'):
                    index_dots = line.index(':')
                    tag = line[2:index_dots].strip()
                    info = line[index_dots+1:].strip()
                    
                    if tag in self.general_tags:
                        self.tag_info[tag] = info
                        
                    if tag.startswith('title'):
                        page_num = None
                        title = tag.strip().split(' ')[0]
                        if '(' and ')' in tag:
                            ind_open_par = tag.index('(')
                            ind_close_par = tag.index(')')
                            page_num = int(tag[ind_open_par+1:ind_close_par])
                        
                        book_index.append((title, page_num, info))
                
                elif words and words[0].isdigit():
                    index_space = line.index(' ')
                    
                    page_num = int(words[0])
                    recipe_name = line[index_space+1:].strip()
                    if page_num not in dic_page_recipes_bk:
                        dic_page_recipes_bk[page_num] = [recipe_name]
                        
                    else:
                        dic_page_recipes_bk[page_num].append(recipe_name)
                           
        self.dic_page_recipes_bk = dic_page_recipes_bk
        self.book_index = book_index
        
    def get_path_biblio(self):
        # Returns full folder path that contains the book file
        from src.utils import get_prepath
        
        return get_prepath(self.path_book, 'books')
        
    def get_pdf(self):
        if 'pdf' not in self.tag_info:
            return ''
        return self.tag_info['pdf']
        
    def get_authors(self):
        if 'chef' not in self.tag_info:
            return ''
        return self.tag_info['chef']
    
    def get_chef(self):
        """Returns the last word under 'Chef' tag
        >> chef: Paul Bocuse
            -> 'Bocuse'
        """
        if 'chef' not in self.tag_info:
            return ''
        return self.tag_info['chef'].split(' ')[-1]
    
    def get_tags(self):
        # Get the list of tags lowered
        if 'tags' not in self.tag_info:
            return ''
        
        tags = [tag.strip().lower() for tag in self.tag_info['tags'].split(',')]
        return tags
    
    def get_full_link_pdf(self, list_cookbooks_pdf = None):
        import os
        
        if list_cookbooks_pdf is None:
            list_cookbooks_pdf = self.list_cookbooks_pdf
        
        pdf_name = self.get_pdf()
                
        if not pdf_name:
            return ''
        
        for path in list_cookbooks_pdf:
            if pdf_name == os.path.basename(path):
                self.full_link_pdf = path
                return path
           
        if self.verbose: 
            print("Warning: No path found for '{0}'!".format(self.namefile))
        
    def get_markdown_path_pdf(self, list_cookbooks_pdf = None):
        import urllib.parse
        
        if list_cookbooks_pdf is None:
            list_cookbooks_pdf = self.list_cookbooks_pdf
        
        if self.full_link_pdf is None:
            self.get_full_link_pdf(list_cookbooks_pdf)
            
        if self.full_link_pdf is None:
            return ''

        html_encoded_string = urllib.parse.quote(self.full_link_pdf)
        
        return 'file://' + html_encoded_string
            
    def fuse_dic_page_recipe(self, dic_page_recipes_rcp = None):
        
        if dic_page_recipes_rcp is None:
            dic_page_recipes_rcp = self.dic_page_recipes_rcp
        
        chef_name = '({0})'.format(self.get_chef())
        fused_page_recipes = {}
        
        def standardize_string(string, name_to_eliminate = chef_name):
            from unidecode import unidecode
            sol = string.replace(name_to_eliminate, '').lower().strip()
            return unidecode(sol)
            
        if dic_page_recipes_rcp is None:
            dic_page_recipes_rcp = {}
                
        dic_page_recipes_bk = self.dic_page_recipes_bk
        chef_name = '({0})'.format(self.get_chef())
        
        all_pages_recipes = list(dic_page_recipes_rcp.keys())
        all_pages_books = list(self.dic_page_recipes_bk.keys())
        all_pages = sorted(list(set(all_pages_recipes + all_pages_books)))
        
        self.all_pages = all_pages
        
        for page in all_pages:
            fused_page_recipes[page] = []
            if page in all_pages_books:
                remaining_bk_recipes = dic_page_recipes_bk[page].copy()
                
                if page in dic_page_recipes_rcp:
                    for recipe_name_rcp in dic_page_recipes_rcp[page]:
                        standardized_recipe_name_rcp = standardize_string(recipe_name_rcp)
                        
                        
                        for recipe_name_bk in dic_page_recipes_bk[page]:
                            standardized_recipe_name_bk = standardize_string(recipe_name_bk)
                            
                            # A match was found, remove the recipe from the book
                            if standardized_recipe_name_rcp == standardized_recipe_name_bk:
                                remaining_bk_recipes.remove(recipe_name_bk)
                            
                        fused_page_recipes[page].append('[[{0}]]'.format(recipe_name_rcp))
                        
                for recipe_name_bk in remaining_bk_recipes:
                    fused_page_recipes[page].append(recipe_name_bk)
                    
            else:
                for recipe_name_rcp in dic_page_recipes_rcp[page]:
                    fused_page_recipes[page].append('[[{0}]]'.format(recipe_name_rcp))

        return fused_page_recipes
    
    def make_intro(self, list_cookbooks_pdf = None):
        if list_cookbooks_pdf is None:
            list_cookbooks_pdf = self.list_cookbooks_pdf
        
        intro = ""
        
        tags = ['#' + tag.replace(' ', '_') for tag in self.get_tags()]
        full_pdf = self.get_markdown_path_pdf(list_cookbooks_pdf)

        if full_pdf:
            intro += '[pdf]({0})\n'.format(full_pdf)
        if tags:
            intro += ' '.join(tags)
            
        return intro.strip()
    
    def make_index(self):
        fused_page_recipes = self.fuse_dic_page_recipe()
        index = ""
        
        interval_pages_title = [page_num for (_, page_num, _) in self.book_index
                                if page_num is not None]
        
        interval_pages_title.append(float('inf'))
        
        curr_max_page_num = interval_pages_title[0]
        ind_fused_page_recipes = 0

        for (title, page_num, category_name) in self.book_index:
            while ind_fused_page_recipes < len(self.all_pages) and self.all_pages[ind_fused_page_recipes] < curr_max_page_num:
                for recipe_name in fused_page_recipes[self.all_pages[ind_fused_page_recipes]]:
                    index += '- p.{0}: {1}\n'.format(self.all_pages[ind_fused_page_recipes], recipe_name)
                ind_fused_page_recipes += 1
            if page_num is not None:
                ind_page_num = interval_pages_title.index(page_num)
                curr_max_page_num = interval_pages_title[ind_page_num+1]
                
            index += self.title2indent[title] + ' ' + category_name + '\n'
            
        for val in self.all_pages[ind_fused_page_recipes:]:
            for recipe_name in fused_page_recipes[val]:
                index += '- p.{0}: {1}\n'.format(val, recipe_name)
            
        return index.strip()

    def to_markdown(self):
        paragraphs = [self.make_intro(), self.make_index()]
        return "\n\n".join(p for p in paragraphs if p)
    
    def save_as_md(self):
        import os
        from pathlib import Path
        
        trailing_path = self.path_book.replace(self.get_path_biblio(), '')[1:]
        
        md = self.to_markdown()

        file_out = os.path.join(self.root_obsidian,
                                self.name_root_biblio_obsi,
                                trailing_path).replace('.book', '.md')
        
        # Create the folder in Vault
        root_obsidian_file = Path(file_out).parent
        os.makedirs(root_obsidian_file, exist_ok=True)

        with open(file_out, 'w') as file:
            file.write(md)

        if self.verbose:
            print('Book printed to', file_out.replace(self.root_obsidian, ""))
        

if __name__ == '__main__':
    pass