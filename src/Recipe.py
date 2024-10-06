class Recipe:
    
    def __init__(self, path_cookfile,
                 root_cook= None,
                 root_obsidian = None,
                 path_env = None) -> None:
        import os
        from pathlib import Path
        from dotenv import load_dotenv
        
        main_folder = Path(__file__).parent.parent
        
        if path_env is None:
            self.environment = str(main_folder / 'environment.env')
        else:
            self.environment = path_env
            
        load_dotenv(dotenv_path=self.environment, override=True)
        
        self.path_cookfile = path_cookfile
        
        if root_cook is None:
            from config import ROOT_COOKLANG
            # self.root_cook = os.getenv('ROOT_COOKLANG')
            self.root_cook = ROOT_COOKLANG
        else:
            self.root_cook = root_cook
            
        if root_obsidian is None:
            from config import ROOT_OBSIDIAN
            # self.root_obsidian = os.getenv('ROOT_OBSIDIAN')
            self.root_obsidian = ROOT_OBSIDIAN
        else:
            self.root_obsidian = root_obsidian
        
        self.manually_timed_moments = None
        
        self.recipe_name = os.path.basename(path_cookfile).replace('.cook', '')
        
        self.keys_color_code = ['t_actif', 't_batteur', 't_repos', 't_cuisson']
        self.color_code = {'t_actif': '#c03737', 't_batteur': '#E37448', 't_repos': '#526A7D', 't_cuisson': '#987302'}
        # self.need_extra_space = ["pincée", "pincées", 'gros', 'CàS', 'càc', 'gousse', 'gousses', 'verre']
        self.no_extra_space = ['', 'kg', 'g', 'mg', 'l', 'dl', 'cl', 'ml']
        
        self.make_parsed_cook()
        self.grab_ingredients()
        self.set_scale()
        
    def make_parsed_cook(self):
        """Reads a .cookland file and produces the parsed version
        """
        from cooklang import parse
        
        with open(self.path_cookfile, 'r') as file:
            file_data = file.read()
            if not file_data:
                self.parsed_cook = []
                return
            
        self.parsed_cook = parse(file_data)
        
    def get_book_name(self):
        """Retrieves the book name from the 'source' metadata.
        
        Returns the first string contained between double square brackets, like [[this]].
        Returns None if no book name can be found.

        Returns:
            book_name (str): Name of the book used as a reference for the recipe
        """
        from src.utils import retrieve_book_title
        metadata = self.grab_specific_metadata('source')
        
        if 'source' not in metadata:
            return None
        
        book_name = retrieve_book_title(metadata['source'])
        return book_name
    
    def load_root_cookbooks(self):
        import os
        from config import ROOTS_COOKBOOKS
        
        self.root_cookbooks = [root_cookbook.strip() for root_cookbook in ROOTS_COOKBOOKS.split(',')]
    
    def update_book(self):
        """Finds the book associated with the recipe, 
        updates/builds the corresponding markdown file"""
        from src.Metadata_tools.Biblio import Biblio
        
        self.load_root_cookbooks()
        
        book_name = self.get_book_name()
        
        bbl = Biblio(self.root_cook, self.root_obsidian, self.root_cookbooks, path_env = self.environment)
        book = bbl.get_book_from_name(book_name)
        
        if book is not None:
            book.save_as_md()
        
    def grab_manually_timed_moments(self):
        """Parses the recipe in search of the metadata that appear in self.keys_color_code
        i.e. t_actif, t_batteur, ...
        
        All associated metadata is turned into a list of tuples, each "timed moment" is associated
        with the time in minutes. 
        Dots and spaces are removed before parsing, use 'h' and 'min' to write in the cooklang file
        
        example:
        Cooklang file:
        >> t_actif: 8 min.
        >> t_repos: 45 min.
        >> t_repos:1h45min.
        
        returns:
        [('t_actif', 8), ('t_repos', 45), ('t_repos', 105)]
        """
        if self.manually_timed_moments is not None:
            return self.manually_timed_moments
        
        def str2time(str_time):
            multiplier = {'h': 60, 'min': 1}
            
            str_time = str_time.replace('.', '')
            str_time = str_time.replace(' ', '')
            
            import re
            str_time = re.split(r'(\d+)', str_time)[1:]
            # str_time = re.split('(\d+)',str_time)[1:]

            int_time = 0
                        
            ind = 1
            while ind <= len(str_time):
                curr_mult = multiplier[str_time[ind]]
                int_time += int(str_time[ind-1]) * curr_mult
                ind += 2
                
            return int_time
    
        manually_timed_moments = []
    
        for row in self.parsed_cook:
            first_parsed = row[0]
            if 'type' in first_parsed and first_parsed['type'] == 'metadata' and first_parsed['key'] in self.keys_color_code:
                manually_timed_moments.append((first_parsed['key'], first_parsed['value']))
     
        manually_timed_moments = [(a, str2time(b)) for a,b in manually_timed_moments]
        self.manually_timed_moments = manually_timed_moments
        
        return manually_timed_moments
        
    def make_schedule_bar(self):
        """Turns manually timed moments into a color coded bar indicating how long each steps take and
        the nature of the step."""
        self.grab_manually_timed_moments()
        
        if not self.manually_timed_moments:
            return ''
        
        def timed_moments2html(timer_info, scale=2, height=30, color_code=self.color_code):
            html = "<table>\n  <tr>\n"
            for timer, size in timer_info:
                color = color_code[timer]
                html += '    <td style="width:{0}px; height:{1}px; background-color:{2}"></td>\n'.format(size*scale, height, color)
            html += "  </tr>\n</table>"
            
            return html
        
        return timed_moments2html(self.manually_timed_moments)
    
    def make_manual_timings(self):
        """Sums up what time is needed to complete the recipe.
        Outputs looks like : "Total time : 50 minutes, Active time : 20 minutes, Cooking time: 30 minutes"
        
        TODO: French version is hard-coded here, to change in the future for an english version"""
        self.grab_manually_timed_moments()
        
        if not self.manually_timed_moments:
            return ''
        
        def time2str(minutes):
            hours = int(minutes/60)
            remaining_minutes = minutes%60
            
            str_time = ''
            
            if hours == 1:
                str_time += '1 heure '
            elif hours > 1:
                str_time += str(hours) + ' heures '
                
            if remaining_minutes == 1:
                str_time += '1 minute'
            elif remaining_minutes > 1:
                str_time += str(remaining_minutes) + ' minutes'
                
            return str_time
        
        fused_timer_info = {}
        for timer, time in self.manually_timed_moments:
            if timer not in fused_timer_info:
                fused_timer_info[timer] = time
                
            else:
                fused_timer_info[timer] += time
        total_time = sum([time for _, time in self.manually_timed_moments])
        
        rounding_total_time = 10
        total_time = (total_time - total_time%rounding_total_time) + rounding_total_time
        intro = 'Temps total: ' + time2str(total_time)+'\n\n'
        existing_timers = [timer for timer, _ in self.manually_timed_moments]
        for key in self.keys_color_code:
            if key == 't_actif' and key in existing_timers:
                intro += 'Temps actif: {0}\n'.format(time2str(fused_timer_info[key]))
                
            elif key in existing_timers:
                intro += 'Temps de {1}: {0}\n'.format(time2str(fused_timer_info[key]), key.split('_')[1])
                
        return intro[:-1]
    
    def grab_specific_metadata(self, keywords):
        """Collects the keywords and related metadata from the recipe.
        Warning, if the keyword appears several times in the recipe, only the last reference in the recipe is used.

        If the keyword is found in the cooklang file, it is included in the 'specific_metadata' dictionary.
        
        returns:
        {'keyword1': 'value_of_keyword1', 'keyword2': 'value_of_keyword2', ...}
        """
        if type(keywords) is not list:
            keywords = [keywords]
            
        specific_metadata = {}
        for elt in self.parsed_cook:
            for dic in elt:
                if dic.get('type') == 'metadata' and dic.get('key') in keywords:
                    specific_metadata[dic['key']] = dic['value']
        return specific_metadata
    
    def grab_separate_tags(self):
        """Grabs both extra and written tags
        extra tags are tags not explicitly written in the recipe
        -> Folder names containing the recipe are extra tags
        
        written tags are tags in the cookfile under the metadata "tags"
        i.e.: >> tags: en avance, été, simple
        
        """
        tags = self.grab_specific_metadata('tags')
        folders_file = str(self.path_cookfile).replace(str(self.root_cook), '')
        extra_tags = folders_file.split('/')[1:-1]
        
        written_tags = []
        if tags:
            written_tags = tags['tags'].split(',')
            written_tags = [tag.strip() for tag in written_tags]
            
        self.extra_tags, self.written_tags = extra_tags, written_tags
    
    def grab_full_tags(self):
        """Merges all tags into one list, removes duplicates, lowers and sorts them"""
        self.grab_separate_tags()
        
        full_tags = list(set(self.written_tags+self.extra_tags))
        full_tags = [tag.lower() for tag in full_tags]
        full_tags.sort()
        
        return full_tags
    
    def make_tags(self):
        from src.Metadata_tools.Tags import Tags
        
        tgs = Tags(self.root_cook)
        full_tags = self.grab_full_tags()
        
        # print(full_tags)
        
        written_tags = tgs.write_ordered_tags(full_tags)
        
        return written_tags
    
    def make_default_intro(self, keywords_intro, intro_metadata):
        intro = ""
        for key in keywords_intro[1:]:
            if key in intro_metadata:
                intro += 'Temps de ' + key + ': ' + intro_metadata[key] + '\n'
                
        return intro[:-1]
    
    def make_intro(self):
        keywords_intro = ['pour', 'préparation', 'repos', 'cuisson']
        intro_metadata = self.grab_specific_metadata(keywords_intro)
        
        
        """
        intro = ''
        if 'pour' in intro_metadata:
            intro += 'Pour' + ' ' + intro_metadata['pour'] + '\n\n'
        """
        intro = 'Pour' + ' ' + str(self.pour[0]) + self.pour[1] + '\n\n'
        
        schedule_bar = self.make_schedule_bar()
        
        if schedule_bar:
            manual_timings = self.make_manual_timings()
            intro += manual_timings + '\n\n' + schedule_bar
            
        else:
            intro += self.make_default_intro(keywords_intro, intro_metadata)

        return intro.strip()
    
    def grab_ingredients(self):
        current_part = 'None'
        ingredients = {}
        parts = []
        
        def to_number(strnum):
            if not strnum:
                return ''
            try:
                num = int(strnum)
            except ValueError:
                num = float(strnum)
            return num
        
        for row in self.parsed_cook:
            for elt in row:
                if 'key' in elt and elt['key'] == 'steps':
                    current_part = elt['value']
                    parts.append(current_part)
                    ingredients[current_part] = []
                    
                if 'type' in elt and elt['type'] == 'ingredient':
                    if current_part == 'None' and 'None' not in ingredients:
                        ingredients['None'] = []
                        parts.append('None')
                        
                    if elt['units']=='':
                        if ' ' not in elt['quantity']:
                            quantity = elt['quantity']
                            units = ''
                        else:
                            quantity, units = elt['quantity'].split(' ')
                    else:
                        quantity, units = elt['quantity'], elt['units']
                    quantity = to_number(quantity)
                    name = elt['name']
                    
                    ingredients[current_part].append([quantity, units, name])
                    
        self.ingredients = ingredients
        self.parts = parts
        return ingredients, parts
    
    def get_list_ingredients(self):
        ingredients, parts = self.ingredients, self.parts
        
        return [ingredient for part in parts for ingredient in ingredients[part]]
        
    def set_scale(self):
        import re
        dic_metadata_pour = self.grab_specific_metadata(['pour'])
        
        if not dic_metadata_pour:
            self.scale = 1
            self.scale_type = self.recipe_name
            self.pour = [1, ' ' + self.recipe_name.lower()]
            return self.scale, self.scale_type
        
        metadata_pour = dic_metadata_pour['pour']
        scale = re.search(r'\d+', metadata_pour).group()
        self.pour = [scale, metadata_pour.split(scale)[1].lower()]
        self.scale_type = metadata_pour.replace(scale, '').strip()
        
        self.scale = int(scale)
            
        return self.scale, self.scale_type
    
    def __rmul__(self, new_scale):
        ingredients, parts = self.grab_ingredients()
        
        scaler = float(new_scale)/self.scale
        scaler = max(int(scaler), scaler)
        
        for part in parts:
            for ingr in ingredients[part]:
                
                # If ingredient is just 'some butter' i.e. ['', '', 'butter], don't scale it
                if ingr[0] != '':
                    ingr[0] *= scaler
                    
                if ingr[0]:
                    ingr[0] = int(ingr[0]*100)/100.0
                    ingr[0] = max(int(ingr[0]), ingr[0])
        
        self.pour[0] = new_scale
        self.ingredients = ingredients
        self.parts = parts
        self.scale = new_scale
        
        
    def make_ingredients(self):
        
        # for testing purposes !
        return self.make_split_ingredients()
        
        from src.utils import new_ingredient2listecourse
        str_ingredients = ""
        ingredients, parts = self.ingredients, self.parts
        no_empty_parts = [part for part in parts if ingredients[part]]
        
        for ind, part in enumerate(no_empty_parts):
            if ind > 0:
                str_ingredients += '\n'
            if part != 'None':
                str_ingredients += '#### ' + part + '\n'
            for ingr in ingredients[part]:
                str_ingredients += '- ' + new_ingredient2listecourse(ingr, self.no_extra_space) + '\n'
                
        return str_ingredients.strip()
    
    def make_tabular_ingredient(self):

        def make_div(name_part, ingredients_part):
            from src.utils import new_ingredient2listecourse
            
            local_div = '  <div style="display: inline-block; width: 100%;">\n'
            if name_part != 'None':
                local_div += '    <h4 style="font-weight: bold; margin-top: 0;">{0}</h4>\n'.format(name_part)
            local_div += '    <ul style="list-style-type: none; padding: 0;">\n'
            for ingr in ingredients_part:
                local_div += '      <li>{0}</li>\n'.format(new_ingredient2listecourse(ingr))
            local_div += '    </ul>\n'
            local_div += '  </div>\n'
            
            return local_div
        
        ingredients, parts = self.ingredients, self.parts
        no_empty_parts = [part for part in parts if ingredients[part]]
        html_ingredient = '<div style="-webkit-column-count: 2; -moz-column-count: 2; column-count: 2;">\n'
        
        """
        # split into 2 columns/divs if ingredients is just one single nameless list
        if len(no_empty_parts) == 1 and no_empty_parts[0] == "None":
            ingredient_list = ingredients['None']
            num_ingr = len(ingredient_list)
            split = num_ingr - num_ingr//2
            
            html_ingredient += make_div('None', ingredient_list[:split])
            html_ingredient += make_div('None', ingredient_list[split:])"""
            
        # the ingredient list is made of one or several named/unnamed parts, split them into separate divs

        for part in no_empty_parts:
            html_ingredient += make_div(part, ingredients[part])
            
        html_ingredient += '</div>'
        
        if not (len(no_empty_parts) == 1 and no_empty_parts[0] == "None"):
            sep_line = '----------------------'
            html_ingredient = sep_line + '\n' + html_ingredient + '\n\n----------------------'
        
        return html_ingredient
    
    def make_split_ingredients(self):

        def make_mini_div(sublist_ingredients):
            from src.utils import new_ingredient2listecourse
            
            def make_h4_title(title):
                return '    <h4 style="font-weight: bold; margin-top: 0;">{0}</h4>\n'.format(title)
            
            local_div = ''
            making_listing = False
            
            for elt in sublist_ingredients:
                
                # We start the div with a title
                if type(elt) == str:
                    # We have a title after listing ingredients, we have to finish the listing first
                    if making_listing:
                        local_div += '    </ul>\n'
                        making_listing = False
                    local_div += make_h4_title(elt)
                
                # We have an ingredient
                else:
                    # Start a new listing
                    if not making_listing:
                        local_div += '    <ul style="list-style-type: none; padding: 0;">\n'
                    local_div += '      <li>{0}</li>\n'.format(new_ingredient2listecourse(elt))
                    making_listing = True
                    
            # If we were listing ingredients when we have to finish the div, we close the listing
            if local_div:
                local_div += '    </ul>\n'
            local_div += '  </div>\n'
            
            return local_div
        
        def split_ingredients():
            # Split the ingredients into 2 balanced lists
            
            ingredients, parts = self.ingredients, self.parts
            no_empty_parts = [part for part in parts if ingredients[part]]
            
            single_split = False
            
            # split into 2 columns/divs if ingredients is just one single list
            if len(no_empty_parts) == 1:
                name_part = no_empty_parts[0]
                ingredient_list = ingredients[name_part]
                
                num_ingr = len(ingredient_list)
                split = num_ingr - num_ingr//2
                
                left = ingredient_list[:split]
                right = ingredient_list[split:]
                
                if name_part !='None':
                    left.insert(0, name_part)
                    last_left = left.pop()
                    right.insert(0, last_left)
                    
                else:
                    single_split = True

            # We have named parts
            else:
                len_parts = [2*int(part!='None')+len(ingredients[part]) for part in no_empty_parts]
                
                i_left = -1
                i_right = len(len_parts)
                
                count_left = 0
                count_right = 0
                
                left, right = [], []
                
                sum_parts = sum(len_parts)
                
                while count_left + count_right != sum_parts:
                    if count_left > count_right:
                        i_right -= 1
                        count_right += len_parts[i_right]
                                                
                    else:
                        i_left += 1
                        count_left += len_parts[i_left]
                                                
                for ind, part in enumerate(no_empty_parts):
                    if ind <= i_left:
                        if part != "None":
                            left.append(part)
                        for elt in ingredients[part]:
                            left.append(elt)
                            
                    else:
                        if part != "None":
                            right.append(part)
                        for elt in ingredients[part]:
                            right.append(elt)
                            
            return left, right, single_split
                
                
        # Build the 2 column html table of ingredients
        left, right, single_split = split_ingredients()

        html_ingredient = '<div style="display: flex;">\n'
        
        # First column
        html_ingredient += '  <div style="flex: 1; margin-right: 10px;">\n'
        html_ingredient += make_mini_div(left)
        
        # Second column
        html_ingredient += '  <div style="flex: 1;">\n'
        html_ingredient += make_mini_div(right)
        
        html_ingredient += '</div>'
        
        if not single_split:
            from src.utils import decorate_ingredients
            html_ingredient = decorate_ingredients(html_ingredient)

        return html_ingredient
                
    def make_instructions(self):
        str_instructions = ""
        parsed_cook = self.parsed_cook
        ingredients_list = self.get_list_ingredients()
        
        instruction_count = 0
        
        for row in parsed_cook:
            flag = True
            for elt in row:
                if 'key' in elt and elt['key']=='steps':
                    if instruction_count:
                        str_instructions +='\n'
                    str_instructions += "#### " + elt['value'] +'\n'
                if 'text' in elt:
                    if flag:
                        instruction_count += 1
                        str_instructions += str(instruction_count) + '. ' + elt['text']
                        flag = False
                        continue
                    
                    if elt['text'][0] not in [',', '.', "'"]:
                        str_instructions += ' '
                        
                    str_instructions += elt['text']
                    
                if 'type' in elt:
                    if elt['type'] == 'ingredient':
                        str_instructions += ' ' + elt['name']
                        qte, unit, _ = ingredients_list.pop(0)
                        if elt['quantity'] != '':
                            
                            str_instructions += ' (' + str(qte) + unit + ')'
                            # str_instructions += ' (' + elt['quantity'] + elt['units'] + ')'
                    if elt['type'] == 'cookware':
                        str_instructions += ' ' + elt['name']
                        
                    if elt['type'] == 'timer':
                        str_instructions += ' ' + elt['quantity'] + ' ' + elt['units']
            if not flag:
                str_instructions += '\n'
                
                    
        str_instructions = str_instructions.replace('  ', ' ')
        str_instructions = str_instructions.replace("' ", "'")
        str_instructions = str_instructions.replace("’ ", "’")
        str_instructions = str_instructions.replace(" .", ".")

        str_instructions = str_instructions.replace("( ", "(")
        str_instructions = str_instructions.replace(" )", ")")
        
        return str_instructions.strip()
        
    def make_outro(self):
        outro_info = self.grab_specific_metadata(['source', 'page', 'liens', 'type_liens'])
        outro_text = ""
        
        if 'source' in outro_info:
            outro_text += 'Source: ' + outro_info['source']
            if 'page' in outro_info:
                outro_text += ' (p.{0})'.format(outro_info['page'])
            outro_text += '\n'
            
        if 'liens' in outro_info:
            for lien, type_lien in zip(outro_info['liens'].split(','), outro_info['type_liens'].split(',')):
                outro_text += '[{0}]({1})'.format(type_lien.strip(), lien.strip()) + '\n'
                
        return outro_text.strip()
    
    def pp_quantity(self):
        from src.utils import backlink
        recipe_name = self.recipe_name
        
        concat_pour = str(self.pour[0]) + self.pour[1]
        last_word_pour = self.pour[1].split(' ')[-1]
        first_word_recipe = recipe_name.split(' ')[0]
        first_word_recipe_low = first_word_recipe.lower()
        
        if last_word_pour == first_word_recipe_low:
            concat_pour = concat_pour.replace(last_word_pour, "")
            return concat_pour + backlink(recipe_name)
        elif recipe_name.lower() == self.pour[1].strip():
            return str(self.pour[0]) + ' ' + backlink(recipe_name)
        else:
            return backlink(recipe_name) + ' pour ' + concat_pour

    def to_markdown(self):
        paragraphs = [self.make_tags(), self.make_intro(), self.make_ingredients(), self.make_instructions(), self.make_outro()]
        return "\n\n".join(p for p in paragraphs if p)

    def save_as_md(self):
        import os
        from pathlib import Path
        
        md = self.to_markdown()
        file_out = str(self.path_cookfile).replace(self.root_cook, self.root_obsidian).replace('.cook', '.md')

        # Create the folder in Vault
        root_obsidian_file = Path(file_out).parent
        os.makedirs(root_obsidian_file, exist_ok=True)

        with open(file_out, 'w') as file:
            file.write(md)

        print('Updated to', file_out.replace(self.root_obsidian, ""))

                
                
if __name__ == '__main__':
    pass
        
    