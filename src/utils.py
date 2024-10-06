def ingredient2listecourse(value, metric, name, metric_obj):
    if not metric:
        preposition = ""
        if value:
            preposition = ' '
    else:
        preposition = ' de '
        if name[0] in ['a', 'e', 'i', 'o', 'u', 'y', 'h']:
            preposition = " d'"
                        
    need_extra_space = ["pincée", "pincées", 'gros', 'CàS', 'càc', 'gousse', 'gousses']
    if metric in need_extra_space:
        metric = ' ' + metric
        
    read = metric_obj.make_readable(value, metric)
    
    return read + preposition + name

def new_ingredient2listecourse(ingredient, no_extra_space = ['', 'kg', 'g', 'mg', 'l', 'dl', 'cl', 'ml']):
    quantity, unit, name = ingredient
                
    if not unit:
        preposition = ""
        if quantity:
            preposition = ' '
    else:
        preposition = ' de '
        if name[0] in ['a', 'e', 'i', 'o', 'u', 'y', 'h', 'œ', 'é', 'è', 'ê']:
            preposition = " d'"
    
    if unit not in no_extra_space:
        unit = ' ' + unit   

    return str(quantity) + unit + preposition + name

def decorate_ingredients(html_ingredients):
    sep_line = '----------------------'
    decorated = sep_line + '\n' + html_ingredients + '\n\n----------------------'
    
    return decorated

def get_prepath(path, cutout_folder):
    import os
        
    path_components = path.split(os.path.sep)
    book_index = path_components.index(cutout_folder)
    path_up_to_book = os.path.sep.join(path_components[:book_index + 1])
        
    return path_up_to_book

def windower(list_words, window_size=4):
    len_list = len(list_words)
    for word_ind, word_center in enumerate(list_words):
        window_left = list_words[max(0,word_ind-window_size):word_ind]
        window_right = list_words[min(word_ind+1, len_list):min(word_ind+1+window_size, len_list)]
        window_left.extend(window_right)
        print(window_left)

def backlink(filename):
    return '[[' + filename + ']]'

def retrieve_book_title(source):
    if '[[' and ']]' in source:
        beg = source.index('[[')
        end = source.index(']]')
        return source[beg+2:end]

if __name__ == '__main__':
    pass