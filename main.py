if __name__ == '__main__':
	import sys
	import argparse
 
	import os
	folder_main = os.path.dirname(os.path.realpath(__file__))
	sys.path.append(folder_main)
 
	sys.stdout.reconfigure(encoding='utf-8')

	parser = argparse.ArgumentParser()

	parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

	
	parser.add_argument("-l", "--list", help="create groceries list from recipes", action="store_true")
	parser.add_argument("-s", "--server", help="launch cooklang local webserver", action="store_true")
 
	# Maintenance tools
	parser.add_argument("-d", "--diagnostic", help="run all diagnostic tools", action="store_true")
	parser.add_argument("-cl", "--cleanup", help="find untracked files and deletes them if prompted", action="store_true")
 
	# Conversion tools
	parser.add_argument("-w", "--write", help="convert cook files to md when a cook file is modified", action="store_true")
	parser.add_argument("-cvall", "--convert_all", help="convert all cooklang files to md", action="store_true")
	parser.add_argument("-cvb", "--convert_all_books", help="convert all book files to md", action="store_true")
 
	# Functions related to tags
	parser.add_argument("-tcount", "--tags_count", help="display all tags, ranked by usage", action="store_true")
	parser.add_argument("-mtags", "--make_tags", help="build the recipe_metadata.csv file", action="store_true")
	parser.add_argument("-t", "--tags_ordered", help="display all tags, ranked by folders and the configuration file", nargs='*', required=False)
	parser.add_argument("-f", "--find", help="find all recipes described by a set of tags", nargs='*', required=False)
 
	args = parser.parse_args()

	from config import ROOT_COOKLANG, ROOT_OBSIDIAN, NAME_SHOPPING_LIST_FOLDER_VAULT

	folder_cooklang = ROOT_COOKLANG
	folder_obsidian = ROOT_OBSIDIAN
	folder_courses = os.path.join(folder_obsidian, NAME_SHOPPING_LIST_FOLDER_VAULT)
 
	file_metric = os.path.join(folder_cooklang, 'config', 'metric.conf')
	file_aisle = os.path.join(folder_cooklang, 'config', 'aisle.conf')
	file_special_conv = os.path.join(folder_cooklang, 'config', 'special_conversions.conf')

	from src.routine import convert_on_save, reconvert_all, make_liste_courses, run_diagnostics, run_cleanup, display_tags_count, display_select_recipe_by_metadata
	from src.routine import display_tags_ordered, make_df_recipe_metadata, reconvert_all_books
 
	if args.write:
		convert_on_save(folder_cooklang, folder_obsidian)
   
	if args.list:
		make_liste_courses(folder_courses, file_aisle, file_metric, folder_cooklang, folder_obsidian)
  
	if args.server:
		os.system("cook server {0}".format(folder_cooklang))
  
	if args.diagnostic:
		run_diagnostics(folder_cooklang, folder_obsidian, file_metric, file_aisle, file_special_conv)
	
	if args.cleanup:
		run_cleanup(folder_cooklang, folder_obsidian)
  
	if args.convert_all:
		reconvert_all(folder_cooklang, folder_obsidian)
  
	if args.convert_all_books:
		reconvert_all_books(folder_cooklang, folder_obsidian)
  
	if args.make_tags:
		make_df_recipe_metadata(folder_cooklang)
  
	if args.tags_ordered is not None:
		display_tags_ordered(folder_cooklang, args.tags_ordered)
  
	if args.tags_count:
		display_tags_count(folder_cooklang)
  
	if args.find is not None:
		display_select_recipe_by_metadata(folder_cooklang, args.find)
  
  
