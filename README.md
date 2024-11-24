# Ouvre-chef

## Description

**Ouvre-chef** is a command-line interface (CLI) tool that leverages the [Cooklang](https://cooklang.org/) Markup Language to efficiently manage a large recipe database. It allows a personal cook to keep all of their recipes in one place, easily generate grocery lists, organize cookbooks, and more.
## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Extensions](#extensions)
- [Configuration](#configuration)
- [License](#license)
- [Contact](#contact)

## Installation

**Ouvre-chef** requires Python and a Cooklang parser such as [cooklang-rs](https://github.com/Net-Mist/cooklang-rs).

Clone the project, activate your virtual environment and install the required dependencies.

```bash
pip install -r requirements.txt
```

To use Ouvre-chef, you will need some Cooklang recipe files and basic configuration files. If you are new to Cooklang, consider getting started with the [official CLI](https://cooklang.org/cli/).

Once everything is installed, proceed to the [Configuration](#configuration) section to customize Ouvre-chef to your needs.

For writing Cooklang files, I recommend using VSCode with the official [Cook extension](vscode:extension/dubadub.cook) by Alexey Dubovskoy. To read the parsed recipes in Markdown, I personally use [Obsidian](https://obsidian.md/) and to synch the files between your different device use a cloud storage or [Syncthing](https://syncthing.net/).
## Usage

### General Usage

To run the CLI, use:

```bash
python3 -m /path/to/main.py [arguments]
```

For convenience, we expect you to add this command to your system's PATH as `ochef`. From here on, all references to running the command will use `ochef`.

For instance:
```bash
ochef [arguments]
```
### Convert Cooklang Recipe Files to Human-Readable Markdown

The main goal is to write all of your recipes using the Cooklang format and then convert them into Markdown. All the recipes will follow the same format.

In your Cooklang folder, write .cook files. Then use Ouvre-chef for conversion. 

```bash
# Converts as the Cooklang file is written, every time it is saved.
ochef -w

# Converts all recipes and all books to Markdown
ochef -cvall

# Converts all books to Markdown
ochef -cvb
```

![Demo](https://github.com/adamwild/open-data/blob/main/ochef/ochef-w.gif)

### Making Groceries List

In `config.py`, set the desired folder name that will contain your list of recipes by updating the value of `NAME_SHOPPING_LIST_FOLDER_VAULT`. Note that this folder will be located where your Markdown files are created.

To create a groceries list, use a file named `Planning recettes`. Write the name of your list followed by the recipes you want to make, like so:

```bash
2024-07-19 Collations été
[[Cake au citron]]
[[Granité au citron]]
750*[[Pâte sucrée]]
```
In this example, you can also scale the recipes. If the `pour` metadata is not used in the recipe, the quantities are simply multiplied. However, if `pour` is specified, the recipe is scaled to adjust the quantity accordingly. For instance, `Pâte sucrée` is originally for 500g; here, it is scaled to 750g.

Once the file saved, you can create your groceries list by using:

```bash
ochef -l
```

This command will create a file in the same folder, named after the first line in `Planning recettes`. A summary of the recipes will also be provided. For example:

```bash
- 1 [[Cake au citron]]
- 1 litre de [[Granité au citron]]
- 750g de [[Pâte sucrée]]
```

This summary is followed by a list of groceries to buy. You can check off the ingredients you already have and type `y` when prompted to clean up your list, leaving you with your final groceries list.

![Demo](https://github.com/adamwild/open-data/blob/main/ochef/ochef-l.gif)

### Tagging recipes

As the number of recipes grows, finding specific recipes can become challenging. To address this, tag the recipes with meaningful information. Create a list of tags in the `tags.conf` file, located in the `config` sub-folder within your main Cooklang directory. For example:

```bash
entrée
plat
accompagnement
café
dessert

simple
complexe

rapide
long
```

Tag your recipes using the `tags` metadata:
```bash
>> tags: Alsace, petit-déjeuner, brunch
```

You can then use **Ouvre-chef** to interact with your recipes:
```bash
# List each tag followed by the count of recipes that have the tag
ochef -t [list of tags]
ochef -t
ochef -t simple rapide

# Find recipes containing a set of tags
ochef -f [list of tags]
ochef -f hiver
ochef -f hiver roboratif

# List all tags in descending order
ochef -tcount

# Build the recipe_metadata.csv file. This is not used usually as converting files from Cooklang to Markdown does this automatically
ochef -mtags
```

![Demo](https://github.com/adamwild/open-data/blob/main/ochef/ochef-f.png)

### Quality of Life: Keeping Config Files Updated

For proper functionality, both the official CLI and **Ouvre-chef** require certain configuration files to be updated with each new ingredient added. To facilitate this, use:

```bash
ochef -d
```

This command will return all untracked ingredients that need to be added to the `aisle.conf` file. 

You can also delete any files in your Obsidian folder that do not have a corresponding Cooklang file:

```bash
ochef -cl
```
## Extensions

### Additions to the .cook files

Some additions have been made to the recipe files to facilitate the recording of French recipes and to support new functionalities.

```bash

# 'pour' replaces the previous metadata 'servings'. This is what is used to scale the recipe.
>> pour: 8 personnes

# 'liens' is a url, 'types_liens' is what the url links to, a youtube video, a blog, ...
>> liens: https://www.youtube.com/watch, https://www.cookwebsite.com
>> type_liens: Vidéo, Site

# To indicate how long each part of the recipe makes use 'préparation', 'repos' and 'cuisson'
>> préparation: 20 minutes
>> repos: 1 heure
>> cuisson: 20 minutes

# Use 'tags' to search your recipes easily
>> tags: dessert, simple, rapide


# These metadata additions are used to link a recipe to the book it originated from
# 'page' refers to the page in the book
>> page: 157

# 'source' can link to a book, when done so, the Markdown file of the book will also be updated 
>> source: [[Myhrvold, Modernist Bread (Vol. 5) - Recipes 2]]
```

### The .book files

**Ouvre-chef** also introduces a new format for managing cookbooks. It displays the table of contents for the book, complete with links to recipes in Cooklang format. During the conversion from `.book` to Markdown, the tool can locate the corresponding PDF file (if it exists) and update its contents if a recipe has been created that references it.

Some basic metadata are:
```bash
# 'pdf' is the plain-text name of the pdf file
>> pdf: My Favorite Cookbook.pdf

# 'chef' is self-explanatory
>> chef: Joêl Robuchon
```

To code for the table of contents, use 'title' metadata: 
```bash
# 'title_1' is for the main chapters
>> title_1: Entrées

>> title_2 (13): Les entrées - Les amuse-gueules
>> title_2 (32): Crèmes, potages et soupes
>> title_2 (59): Entrées froides et salades
>> title_2 (121): Entrées chaudes

# Alternate between 'title_1' and 'title_2' to write the entire table of contents
>> title_1: Poissons & crustacés

>> title_2 (147): Crustacés et coquillages
>> title_2 (193): Poissons
```

In this small example, **'Entrées'** has four sub-chapters, each with a starting page indicated in brackets. It is assumed that a sub-chapter ends when another begins.

Recipes are added to this table of contents if a Cooklang recipe references the cookbook but you can also bookmark your favorite recipes of a book without having the full recipe in Cooklang. For that, simply start a line with a number indicating the page of the recipe, followed by the name of the recipe. You can have these anywhere in the file.

For instance:
```bash
240 Cuisses de grenouille à la crème de persil aux échalotes
310 Marrons confits aux petits oignons, fenouil et noix
322 Petits navets nouveaux étuvés au jus

>> title_1: Entrées

>> title_2 (13): Les entrées - Les amuse-gueules
>> title_2 (32): Crèmes, potages et soupes

>> title_1: Desserts

>> title_2 (328): Desserts froids
335 Crème glacée au yaourt, coulis de mûres, pain de Gènes
```

![Demo](https://github.com/adamwild/open-data/blob/main/ochef/ochef_books.gif)

## Configuration

To use **Ouvre-chef**, you need to set up two folders: one for the Cooklang recipes and one for the converted Markdown recipes. Additionally, you need to customize the `config.py` file located in the project's main folder.

### Cooklang folder

Your Cooklang folder contains `.cook` files for recipes and `.book` files for the cookbooks. You will also need to setup the configuration files. Here is what it should look like:

```bash
cooklang/
├── books/
├── Cuisine/
├── config/
	├── aisle.conf
	├── metric.conf
	├── special_conversions.conf
	└── tags.conf
└── Desserts/
```

#### aisle.conf

Please refer to the original [documentation](https://cooklang.org/docs/spec/#the-shopping-list-specification) for this file.

#### metric.conf

The `metric.conf` file defines the standard metrics to be used. When combining recipes and quantities to produce a groceries list, this file helps merge different units of measurement.

```bash
[metric1, metric2, ...]|smallest_metric, multiplication_value metric_name, ...
```

This may seem complicated, here is how you should read this `metric.conf` file:
```bash
[kg, g]|g, 1000 kg, 1 pincée, 1 pincées, 1 petit verre, 10 noix
[l, ml]|ml, 1000 l, 100 dl, 10 cl, 5 càc, 15 CàS, 240 verre, 300 tasse, 1000 litre
```

In this example:

- `kg` and `g` are standardized metrics, with `g` being the preferred unit. If a quantity exceeds 1000, it is expressed in `kg`.
- The conversions specify that `1 kg = 1000 g`, and "une noix" (e.g., "noix de beurre") is equivalent to 10 `g`.
- Similarly, for volumes, `1 dl = 100 ml`, and so on.

#### special_conversions.conf

This file assists in generating grocery lists by solving what I call the "egg problem." When different recipes require varying parts and quantities of an egg—such as 3 egg yolks, 50g of egg white, one whole egg, or 200g of whole egg—how do you determine the total number of eggs needed?
**Ouvre-chef** computes this automatically, but you need to specify the weight of each component, as shown below:

```bash
oeufs|jaunes d'oeufs,15| blancs d'oeufs,35
citron vert|zeste de citron vert,3|jus de citron vert,5
tomates|tomates,125
```

In this example:

- An egg consists of two components: an egg yolk weighing 15 grams and an egg white weighing 35 grams. **Ouvre-chef** converts all quantities to grams and calculates the total number of eggs required accordingly.
- The same logic applies to other items. For instance, if one recipe requires 2 tomatoes and another calls for 250g of tomatoes, the tool will add 4 tomatoes to the grocery list.
#### tags.conf

Contains the list of tags most commonly used for your recipes. Here is an example:

```bash
simple
complexe

rapide
long

minute
en avance

solo
familial
raffiné
festif
```

### Obsidian folder

The Obsidian folder contains recipes converted to Markdown. This is what you should use while cooking. Most of the conversion will be handled automatically by **Ouvre-chef**. Here is an example of how it might look, based on the previous example:

```bash
obsidian_vault/
├── Livres/
├── Cuisine/
├── Desserts/
└── Liste_courses/
	└── Planning recettes
```

### config.py

The `config.py` file is located at the same level as `main.py` in the main project folder. You should create this file if it doesn't exist. Here is what it should contain:

```bash
# Define the roots containing your cooklang folder, it must contains a config folder.
ROOT_COOKLANG = '/path/to/cooklang'

# The root of the obsidian vault or where recipes in markdown will written.

ROOT_OBSIDIAN = '/path/to/obsidian_vault'


# Specify one or several folders containing cookbook files.
ROOTS_COOKBOOKS = '/path/to/Documents/Cuisine, /media/path/other/my_books'


# Name for the folder containing the books in markdownn.
# This folder will be stored under the vault root
NAME_BOOK_FOLDER_VAULT = 'Livres'

# Name for the folder containing the groceries shopping list
NAME_SHOPPING_LIST_FOLDER_VAULT = 'Liste_courses'

# Define if script is verbose, default is False
VERBOSE = 'True'

# Define if untracked files/folders are automatically deleted
AUTO_DELETE = False
```

## License

This project is licensed under the MIT License. If you intend to use my code, please feel free to send me a message.

## Contact

For this project, find me on the [Discord server](https://discord.gg/fUVVvUzEEK) of the main project.