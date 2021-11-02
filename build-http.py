from pathlib import Path
import logging
import shutil
from pydantic import ValidationError
from jinja2 import Environment, FileSystemLoader
from model import Recipe

WEBSITE_NAME = 'My Recipes'
RECIPE_FOLDER = Path('../recipe/')
BUILD_LOCATION = Path('./build/')
STATIC_LOCATION = Path('./static/')


logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def find_image(recipe_path: Path):
    "Return image corresponding to .yaml or None"
    EXTs = ['.jpg', '.png', '.webm']
    for ext in EXTs:
        # check if an image with the same name exists
        img = recipe_path.parent / (recipe_path.stem + ext)
        if img.is_file():
            return img
    # If no matching image is found, return None
    return None


def main():
    # Set up the Jinja renderer
    env = Environment(loader=FileSystemLoader('templates'), trim_blocks=True,
                      lstrip_blocks=True)

    # clear the build folder
    shutil.rmtree(BUILD_LOCATION, ignore_errors=True)
    BUILD_LOCATION.mkdir()

    # copy static folder to build
    shutil.copytree(STATIC_LOCATION, BUILD_LOCATION / 'static')

    # grab all the recipes
    recipes = {}
    for file in RECIPE_FOLDER.iterdir():
        if file.suffix != '.yaml':
            continue
        try:
            r = Recipe.parse_file(file)
        except ValidationError as e:
            logger.error(f'Could not parse {file}', e)
            continue
        img = find_image(file)
        recipes[r.recipe_name] = {
            'recipe': r,
            'image': img,
            'filename': f'{file.stem}.html',
        }

    # render the index page
    index = env.get_template("index.html")
    html = index.render(title=WEBSITE_NAME, recipes=[
        {'name': r, 'url': recipes[r]['filename']} for r in recipes]
    )
    with open(BUILD_LOCATION / 'index.html', 'wt') as f:
        f.write(html)

    # render the recipe pages
    template = env.get_template('recipe.html')
    for r in recipes:
        html = template.render(title=f'{WEBSITE_NAME} - {r}',
                               recipe=recipes[r]['recipe'],
                               img=recipes[r]['image'],
        )
        with open(BUILD_LOCATION / recipes[r]['filename'], 'wt') as f:
            f.write(html)
        img = recipes[r]['image']
        if img:
            shutil.copyfile(img, BUILD_LOCATION / img.name)


if __name__ == '__main__':
    main()
