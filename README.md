# Cook Book
###### CS50x 2021 - Final Project
Alvin Cousins


### Brief
The aim was to create an online web app which processes recipe ingredient quantities and units. The program is able to recognise numbers and units within an ingredient list for the purposes of performing unit conversions and scaling the number of servings.
Project uses Flask/ Python to handle the processing of data, which is stored in a SQLite3 database.  Javascript is also used on the frontend to render changes to serving quantities.


### app.py
This file contains all of the routes for the flask application and handles the conditions when writing to the SQLite database.

'/' - Renders the index page, which is a list of all recipes by all users.

'/profile' - Displays recipes unique to the user that is logged in.

'/user_view' - Displays recipes to other users, who the signed in user does not have editing permission.

'/view' - Retrieves data to render a single recipe page.

'/edit' - Handles edits to a single recipe, and listens out for whether the request is to 'update', 'delete', or just to return/ go 'back' to the edit page. Performs in a similar way to '/view' when the method is GET.

'/edit_ingredient' - Updates single ingredient items in the databases, ensuring they are first processed by the helper functions, which recognises and splits them into dict components: ingredient, unit, quantity.

'/contribute' - Handles the form for submitting a recipe. Takes data for title, author, ingredients list, method and writes them to the database.

'/check' - By default, recipes' 'published' value is set to '0' and will not be displayed on the index page. These recipes are considered abandoned and are subsequently deleted. If recipes are confirmed, then this /check route sets 'published' to '1', which allowing them to be viewable on the index page, and not automatically deleted.

'/delete' - Deletes recipes sent from /view.

'/edit_method' - Fetches the data stored in the method column for a particular recipe for editing.

'/update_method' - Handles updating the database, specifically for the method column.

'/register' - Carries out check on the username and password before storing to a user table on the database.

'/login' - Logs a registered user in.

'/logout' - Logs a registered user out.



### helpers.py
Stores helper functions.

ingredientItemList(text_to_search):
Creates an item list for ingredients and parses the string into key/value pairs: ingredient, qauntity and unit.

check_units(ingredients_list):
List of regex patterns which look for units and formatting patterns of numbers.

parseFraction(a, b, c):
Handles numbers in the format a/b. 'a, b, c' are groups defined in the regex patterns.

list_update():
Updates the ingredients list with correct quantities, converting a string into a float for processing.

convertMetric():
Converts imperial units to metric.

unitParseLitres():
Changes ml to L if number exceeds 999.

untParseGrams():
Changes g to kg if number exceeds 999.

wholeNumber():
Returns number without decimal if none exists. Returns a space is quantity is zero, for formatting.


### data.db
Contains tables: recipes, ingredients and users.



