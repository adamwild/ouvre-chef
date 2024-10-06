def get_writable_files(root_cooklang):
    import os
    from pathlib import Path
    cooklang_files = list(Path(root_cooklang).rglob("*.[cC][oO][oO][kK]"))
    book_files = list(Path(root_cooklang).rglob("*.[bB][oO][oO][kK]"))
    
    writable_files = cooklang_files
    writable_files.extend(book_files)
    
    writable_files = [str(writable_file) for writable_file in writable_files]
    
    files_timestamp = [(file, os.path.getmtime(file)) for file in writable_files]
    files_timestamp.sort(key=lambda x :-x[1])
    
    return files_timestamp
        
def migrate_cook2md(file_cooklang, root_cooklang, root_obsidian):
    from src.Recipe import Recipe
    
    rcp = Recipe(file_cooklang, root_cook=root_cooklang, root_obsidian=root_obsidian)
    rcp.save_as_md()
    rcp.update_book()
    
def migrate_book2md(book_file, root_cooklang, root_obsidian):
    from src.Metadata_tools.Book import Book
    from src.Metadata_tools.Biblio import Biblio
    
    #TODO Have this in a setup file
    folder_cookbooks = ['/home/adam/Documents/Cuisine', '/media/adam/Elements/abel_data/books']
    
    bbl = Biblio(root_cooklang, root_obsidian, folder_cookbooks)
    bk = Book(book_file, bbl, root_obsidian)
    
    bk.save_as_md()
    
def make_df_recipe_metadata(root_cooklang):
    from src.Metadata_tools.Tags import Tags
    
    tgs = Tags(root_cooklang)
    tgs.save_df_metadata()
    
def convert_on_save(root_cooklang, root_obsidian):
    import time
    from config import AUTO_DELETE
    from src.CleanupTool import CleanupTool
    
    ct = CleanupTool(root_cooklang, root_obsidian)
    
    ref_time = time.time()
    smallest_diff = 0
    
    while True:
        writable_files = get_writable_files(root_cooklang)
        file, timestamp = writable_files[0]
            
        diff = ref_time - timestamp
        
        if diff < smallest_diff:
            print('Modified:', file.replace(root_cooklang, ''))
            if file.endswith('.cook'):
                migrate_cook2md(file, root_cooklang, root_obsidian)
            elif file.endswith('.book'):
                migrate_book2md(file, root_cooklang, root_obsidian)
            make_df_recipe_metadata(root_cooklang)
            smallest_diff = diff
            
            # auto-cleanup
            if AUTO_DELETE:
                ct.auto_delete()
            
        time.sleep(1)
        
def reconvert_all(root_cooklang, root_obsidian):
    writable_files = get_writable_files(root_cooklang)
    
    for writable_file, _ in writable_files:
        print(writable_file)
        if writable_file.endswith('.cook'):
            migrate_cook2md(writable_file, root_cooklang, root_obsidian)
        elif writable_file.endswith('.book'):
            migrate_book2md(writable_file, root_cooklang, root_obsidian)
        print()
        
    make_df_recipe_metadata(root_cooklang)
    
def reconvert_all_books(folder_cooklang, folder_obsidian):
    from src.Metadata_tools.Biblio import Biblio
    
    folder_cookbooks = ['/home/adam/Documents/Cuisine', '/media/adam/Elements/abel_data/books']
    
    bbl = Biblio(folder_cooklang, folder_obsidian, folder_cookbooks)
    bbl.make_all_cookbooks_to_md()
        
def make_liste_courses(root_courses, file_aisle, file_metric, root_cooklang, root_obsidian):
    import os
    from src.Aisle import Aisle
    from src.Metric import Metric
    from src.Shopping import Shopping
    
    path_meals = os.path.join(root_courses, 'Planning recettes.md')
    path_groceries = os.path.join(root_courses, 'Courses dynamique.md')
    
    aisl = Aisle(file_aisle)
    mtc = Metric(file_metric)
    shp = Shopping(path_meals, path_groceries, root_cooklang, root_obsidian, mtc, aisl)
    
    shp.check_and_trigger()
    
    print('Cleanup? (y/n)')
    user_input = input()
    
    if user_input != 'n':
        shp.cleanup()
        
def display_tags_ordered(root_cooklang, list_tags):
    from src.Metadata_tools.Tags import Tags
    
    tgs = Tags(root_cooklang, load_csv_metadata = True)
    
    if list_tags:
        list_tags = [tag.replace('_', ' ') for tag in list_tags]
        tgs.subselection_recipe_by_tags(list_tags)
    tgs.pp_tags()
        
def display_tags_count(root_cooklang):
    from src.Metadata_tools.Tags import Tags
    
    tgs = Tags(root_cooklang, load_csv_metadata = True)
    tgs.pp_metadata_counts()
    
def display_select_recipe_by_metadata(root_cooklang, list_tags):
    from src.Metadata_tools.Tags import Tags
    
    tgs = Tags(root_cooklang, load_csv_metadata = True)
    filtered_recipes = tgs.select_recipe_by_metadata(list_tags)
    
    if filtered_recipes is not None:
        for elt in filtered_recipes:
            print(elt)
    
def run_diagnostics(root_cooklang, root_obsidian, file_metric, file_aisle, file_special_conv):
    from src.DiagnosticTool import DiagnosticTool
    
    dt = DiagnosticTool(root_cooklang, root_obsidian)
    dt.run_all_tools(file_metric, file_aisle, file_special_conv)
    
def run_cleanup(root_cooklang, root_obsidian):
    from src.CleanupTool import CleanupTool
    
    cl = CleanupTool(root_cooklang, root_obsidian)
    cl.delete_menu()

if __name__ == '__main__':
    pass