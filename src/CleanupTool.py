"""Used to track deprecated files in the obsidian folder, files that do not correspond to a file in the cooklang folder"""

class CleanupTool:
    def __init__(self, root_cook=None,
                 root_obsidian =None):
        
        from config import ROOT_COOKLANG, ROOT_OBSIDIAN

        self.root_cook = ROOT_COOKLANG if root_cook is None else root_cook
        self.root_obsidian = ROOT_OBSIDIAN if root_obsidian is None else root_obsidian
        
        self.legitimate_folders = None
               
    def get_cooklang_files(self):
        # Get all .book and .cook files under the cooklang folder
        from pathlib import Path
        cookfiles = list(Path(self.root_cook).rglob("*.[cC][oO][oO][kK]"))
        bookfiles = list(Path(self.root_cook).rglob("*.[bB][oO][oO][kK]"))
        cookfiles.extend(bookfiles)
        cookfiles = [str(file) for file in cookfiles]

        return cookfiles
    
    def get_legitimate_folders(self):
        # legitimate_folders are all folders that should contain recipes and books
        import os
        from config import NAME_BOOK_FOLDER_VAULT
        
        if self.legitimate_folders is not None:
            return self.legitimate_folders
        
        legitimate_folders = [file for file in os.listdir(self.root_cook)
                              if not file.startswith('.')
                              and file not in['README.md', 'config', 'books']]
        legitimate_folders.append(NAME_BOOK_FOLDER_VAULT)
        
        self.legitimate_folders = legitimate_folders
        
        return legitimate_folders

    def get_obsidian_files(self):
        # Get all files in the obsidian folder
        # We only track markdown files
        import os
        from pathlib import Path
        
        # Get all markdown files that are under legitimate folders
        legitimate_folders = self.get_legitimate_folders()
        
        md_files = []
        for legitimate_folder in legitimate_folders:
            local_folder = os.path.join(self.root_obsidian, legitimate_folder)
            local_files = list(Path(local_folder).rglob("*.[mM][dD]"))
            md_files.extend(local_files)
            
        md_files = [str(file) for file in md_files]
                
        return md_files
    
    def get_untracked(self):
        # Compares files in cooklang and their corresponding files in obsidian
        # Returns the files in obsidian that have no antecedent in the cooklang folder
        import os
        from config import NAME_BOOK_FOLDER_VAULT
        
        root_books_cooklang = os.path.join(self.root_cook, 'books')
        root_books_obsidian = os.path.join(self.root_obsidian, NAME_BOOK_FOLDER_VAULT)
        
        # tracked_files contains all files we expect in the obsidian folder
        cookfiles = self.get_cooklang_files()
        tracked_files = []
        for cookfile in cookfiles:
            if cookfile.startswith(root_books_cooklang):
                cookfile = cookfile.replace(root_books_cooklang, root_books_obsidian)
                cookfile = cookfile.replace('.book', '.md')
            else:
                cookfile = cookfile.replace(self.root_cook, self.root_obsidian)
                cookfile = cookfile.replace('.cook', '.md')
            
            tracked_files.append(cookfile)
        
        # untracked_files contains, well, unexpected files, probably produced from cooklang files that were moved or deleted
        md_files = self.get_obsidian_files()
        untracked_files = [file for file in md_files if file not in tracked_files]
        
        return untracked_files
    
    def get_empty_folders(self):
        # Get the empty folders
        import os
        
        def find_empty_directories(path):
            empty_directories = []

            for root, dirs, files in os.walk(path):
                if not dirs and not files:
                    empty_directories.append(root)

            return empty_directories
        
        empty_dir = []
        for folder in self.get_legitimate_folders():
            curr_folder = os.path.join(self.root_obsidian, folder)
            empty_dir.extend(find_empty_directories(curr_folder))
            
        return empty_dir
    
    def __str__(self):
        str_self = "Untracked files in Vault ({0}):\n".format(self.root_obsidian)
        str_self += "\n".join([path.replace(self.root_obsidian, "") for path in self.get_untracked()])
        
        return str_self
    
    def delete_menu(self):
        import os
        import readchar
        
        untracked_files = self.get_untracked()
        
        if not untracked_files:
            return
        
        # Prompting the user to delete untracked file by untracked file
        print("-- delete untracked files --")
        for ind, file in enumerate(untracked_files):
            print('({0}/{1}) del? {2}'.format(ind+1, len(untracked_files), file))
            key = readchar.readkey()
            
            if key in ('y', '1'):
                os.remove(file)
                print('file deleted\n')
                
        # Deleting the folders that have been emptied
        new_empty_folders = self.get_empty_folders()
        old_folders = []
        if new_empty_folders:
            print("-- delete untracked folders --")
        
        while new_empty_folders:
            for folder in new_empty_folders:
                print('del? {0}'.format(folder))
                
                key = readchar.readkey()
            
                if key in ('y', '1'):
                    os.rmdir(folder)
                    print('folder deleted\n')
                    
                else:
                    old_folders.append(folder)
                    
            new_empty_folders = [folder for folder in self.get_empty_folders() if folder not in old_folders]
            
    def auto_delete(self):
        # Automatically delete all untracked files and empty folders
        import os
        
        # delete untracked files
        untracked_files = self.get_untracked()
        
        if not untracked_files:
            return
        
        print("-- delete untracked files/folders --")
        for ind, file in enumerate(untracked_files):
            os.remove(file)
            print('del file {2}'.format(ind+1, len(untracked_files), file))
            
        # delete empty folders
        empty_folders = self.get_empty_folders()
        
        while empty_folders:
            for folder in empty_folders:
                os.rmdir(folder)
                print('del folder {0}'.format(folder))
                
            empty_folders = self.get_empty_folders()

if __name__ == '__main__':
    ct = CleanupTool()
    
    ct.auto_delete()