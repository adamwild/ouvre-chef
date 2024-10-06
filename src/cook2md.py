def cook2md(file_cook, folder_out, test=False):
    import os
    from cooklang import parse
    
    with open(file_cook, 'r') as file:
        file_data = file.read()
        if not file_data:
            print("File is empty !")
            return
        parsed_cook = parse(file_data)
        
    intro_info, ingredients, instructions, outro_info = {}, [], '', {}
    instruction_count = 0
    
    keywords_intro = ['pour', 'préparation', 'repos', 'cuisson']
    keywords_outro = ['source', 'liens', 'type_liens', 'page']
    
    # Lower the flag if a text has been found
    flag = True
        
    for elt in parsed_cook:
        flag = True
        for dic in elt:
            if 'type' in dic and dic['type']=='metadata':
                if dic['key'] in keywords_intro:
                    intro_info[dic['key']] = dic['value']
                    
                if dic['key'] in keywords_outro:
                    outro_info[dic['key']] = dic['value']
                    
                if dic['key'] == 'steps':
                    curr_step = dic['value']
                    if type(ingredients) == list:
                        ingredients = {}
                    ingredients[curr_step] = []
                    
                    instructions += '\n#### ' + curr_step + '\n'
            
            if 'text' in dic:
                if flag:
                    instruction_count += 1
                    instructions += str(instruction_count) + '. ' + dic['text']
                    flag = False
                    continue
                
                if dic['text'][0] not in [',', '.', "'"]:
                    instructions += ' '
                    
                instructions += dic['text']
                
            if 'type' in dic:
                if dic['type'] == 'ingredient':
                    instructions += ' ' + dic['name']
                    if dic['quantity'] != '':
                        instructions += ' (' + dic['quantity'] + dic['units'] + ')'
                        
                    if type(ingredients) == list:
                        ingredients.append((dic['quantity'], dic['units'], dic['name']))
                    else:
                        ingredients[curr_step].append((dic['quantity'], dic['units'], dic['name']))
                        
                if dic['type'] == 'cookware':
                    instructions += ' ' + dic['name']
                    
                if dic['type'] == 'timer':
                    instructions += ' ' + dic['quantity'] + ' ' + dic['units']
                    
        if not flag:
            instructions += '\n'
                
                    
    instructions = instructions.replace('  ', ' ')
    instructions = instructions.replace("' ", "'")
    
    def make_intro(intro_info, keywords_intro):
        intro = ''
        if 'pour' in intro_info:
            intro += 'Pour' + ' ' + intro_info['pour'] + '\n\n'
            
        for key in keywords_intro[1:]:
            if key in intro_info:
                intro += 'Temps de ' + key + ': ' + intro_info[key] + '\n'
                
        intro += '\n'
        
        return intro
    
    
    html, timer_info, intro = make_timetable(parsed_cook)
    if html is not None:
        if 'pour' in intro_info:
            intro = 'Pour' + ' ' + intro_info['pour'] + '\n\n' + intro
        intro += '\n' + html + '\n'
            
    else:
        intro = make_intro(intro_info, keywords_intro)
        
    
    def make_ingredients(ingredients):
        def add_ingredient(ingredient):
            if ingredient[0] == '':
                new_ingredient = '- ' + ingredient[2] + '\n'
                return new_ingredient
            elif ingredient[1] == '':
                new_ingredient = '- ' + ingredient[0] + ' ' + ingredient[2] + '\n'
                return new_ingredient
            new_ingredient = '- ' + ingredient[0] + ingredient[1]
            if ingredient[2][0] in ['a', 'e', 'i', 'o', 'u', 'y', 'h']:
                new_ingredient += " d'"
            else:
                new_ingredient += ' de '
            new_ingredient += ingredient[2] + '\n'
            return new_ingredient
        
        ingr_text = ''
        if type(ingredients) == list:
            for ingredient in ingredients:
                ingr_text += add_ingredient(ingredient)
            # ingr_text += '\n'
        else:
            for step in ingredients:
                if ingredients[step]:
                    ingr_text += '#### ' + step + '\n'
                    for ingredient in ingredients[step]:
                        if ingredient[0] == '':
                            ingr_text += '- ' + ingredient[2] + '\n'
                            continue
                        elif ingredient[1] == '':
                            ingr_text += '- ' + ingredient[0] + ' ' + ingredient[2] + '\n'
                            continue
                        ingr_text += '- ' + ingredient[0] + ingredient[1]
                        if ingredient[2][0] in ['a', 'e', 'i', 'o', 'u', 'y', 'h']:
                            ingr_text += " d'"
                        else:
                            ingr_text += ' de '
                        ingr_text += ingredient[2] + '\n'
                    ingr_text += '\n'
                    
        return ingr_text
    
    
    
    ingr_text = make_ingredients(ingredients)
    
    def make_outro(outro_info):
        outro_text = ""
        
        if 'source' in outro_info:
            outro_text += 'Source: ' + outro_info['source']
            if 'page' in outro_info:
                outro_text += ' (p.{0})'.format(outro_info['page'])
            outro_text += '\n'
            
        if 'liens' in outro_info:
            for lien, type_lien in zip(outro_info['liens'].split(','), outro_info['type_liens'].split(',')):
                outro_text += '[{0}]({1})'.format(type_lien.strip(), lien.strip()) + '\n'
                
        return outro_text
        
    outro_text = make_outro(outro_info)
    
    final = intro + ingr_text + instructions + '\n' + outro_text
    
    if test:
        return final
    
    curr_file = os.path.basename(file_cook)
    file_out = os.path.join(folder_out, curr_file.replace('.cook', '.md'))
    
    with open(file_out, 'w') as file:
        file.write(final)
        
    print('Updated to - ' + file_out)
    
def make_timetable(parsed_cook):
    
    def str2time(str_time):
        multiplier = {'h': 60, 'min': 1}
        
        str_time = str_time.replace('.', '')
        str_time = str_time.replace(' ', '')
        
        import re
        str_time = re.split('(\d+)',str_time)[1:]

        int_time = 0
        
        ind = 1
        while ind <= len(str_time):
            curr_mult = multiplier[str_time[ind]]
            int_time += int(str_time[ind-1]) * curr_mult
            ind += 2
            
        return int_time
    
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
    
    keys_color_code = ['t_actif', 't_batteur', 't_repos', 't_cuisson']
    color_code = {'t_actif': '#c03737', 't_batteur': '#E37448', 't_repos': '#526A7D', 't_cuisson': '#987302'}
    
    timer_info = []
    
    for row in parsed_cook:
        first_parsed = row[0]
        if 'type' in first_parsed and first_parsed['type'] == 'metadata' and first_parsed['key'] in color_code:
            timer_info.append((first_parsed['key'], first_parsed['value']))
            
    if not timer_info:
        return None, None, None
            
    timer_info = [(a, str2time(b)) for a,b in timer_info]
    
    fused_timer_info = {}
    for timer, time in timer_info:
        if timer not in fused_timer_info:
            fused_timer_info[timer] = time
            
        else:
            fused_timer_info[timer] += time
    total_time = sum([time for _, time in timer_info])
    
    rounding_total_time = 10
    total_time = (total_time - total_time%rounding_total_time) + rounding_total_time
    intro = 'Temps total: ' + time2str(total_time)+'\n\n'
    existing_timers = [timer for timer, _ in timer_info]
    for key in keys_color_code:
        if key == 't_actif' and key in existing_timers:
            intro += 'Temps actif: {0}\n'.format(time2str(fused_timer_info[key]))
            
        elif key in existing_timers:
            intro += 'Temps de {1}: {0}\n'.format(time2str(fused_timer_info[key]), key.split('_')[1])
    
    
    def alternate2html(timer_info, scale=2, height=30, color_code=color_code):
        html = "<table>\n  <tr>\n"
        for timer, size in timer_info:
            color = color_code[timer]
            html += '    <td style="width:{0}px; height:{1}px; background-color:{2}"></td>\n'.format(size*scale, height, color)
        html += "  </tr>\n</table>\n"
        
        return html
    
    html = alternate2html(timer_info)
    
    return html, timer_info, intro
        
if __name__ == '__main__':
    pass