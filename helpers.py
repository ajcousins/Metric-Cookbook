######## INGREDIENTS LIST FUNCTIONS ########
import re



def ingredientItemList(text_to_search):

    # Split big string into list for each line.
    # Now redundant in web use.

    item_list = text_to_search
    
    
    temp = []
    while item_list:
        x = item_list.pop()
        if x != '':
            temp.append(x)
    while temp:
        item_list.append(temp.pop())

    # Declare empty list & flush out previous entries.
    ingredients_list = []
    ingredients_list.clear()

    # Populate with dicts with blank quantity and unit values.
    for item in item_list:
        dict_item = {'ingredient':'','quantity':0,'unit':''} 
        dict_item['ingredient'] = item
        ingredients_list.append(dict_item) 
    
    ingredients_list = check_units(ingredients_list)

    # DEBUGGING 2/3
    #print(ingredients_list)
    return ingredients_list
    

def check_units(ingredients_list):

    ###### --- METRIC --- ######

    # Define pattern: g
    grams = re.compile(r'([0-9\s]{0,4})?,?([0-9½¼/]{1,3})(\.?[0-9½¼/]{1,3})?\s?(g|gs|grams)\b[\s|,]{0,}(.*)')
    ingredients_list = list_update(grams, 'g', ingredients_list)

    # Define pattern: kg
    kilos = re.compile(r'([0-9\s]{0,4})?,?([0-9½¼/]{1,3})(\.?[0-9½¼/]{1,3})?\s?(kg|kgs|kilograms|kilos|kilo)\b[\s|,]{0,}(.*)')
    ingredients_list = list_update(kilos, 'kg', ingredients_list)

    # Define pattern: ml
    ml = re.compile(r'([0-9\s]{0,4})?,?([0-9½¼/]{1,3})(\.?[0-9½¼/]{1,3})?\s?(mL|mLs|ml|mls|milliliter|milliliters)\b[\s|,]{0,}(.*)')
    ingredients_list = list_update(ml, 'ml', ingredients_list)

    # Define pattern: L
    L = re.compile(r'([0-9\s]{0,4})?,?([0-9½¼/]{1,3})(\.?[0-9½¼/]{1,3})?\s?(L|l|litre|litres)\b[\s|,]{0,}(.*)')
    ingredients_list = list_update(L, 'L', ingredients_list)


    ###### --- IMPERIAL --- ######

    # Define pattern: tsp
    tsp = re.compile(r'([0-9\s]{0,4})?,?([0-9½¼/]{1,3})(\.?[0-9½¼/]{1,3})?\s?(tsp|tsps|teaspoon|teaspoons)\b[\s|,]{0,}(.*)')
    ingredients_list = list_update(tsp, 'tsp', ingredients_list)

    # Define pattern: tbsp
    tbsp = re.compile(r'([0-9\s]{0,4})?,?([0-9½¼/]{1,3})(\.?[0-9½¼/]{1,3})?\s?(tbsp|tbsps|tablespoon|tablespoons)\b[\s|,]{0,}(.*)')
    ingredients_list = list_update(tbsp, 'tbsp', ingredients_list)

    # Define pattern: cup
    cup = re.compile(r'([0-9\s]{0,4})?,?([0-9½¼/]{1,3})(\.?[0-9½¼/]{1,3})?\s?(cup|cups)\b[\s|,]{0,}(.*)')
    ingredients_list = list_update(cup, 'cup', ingredients_list)

    # Define pattern: fl oz
    floz = re.compile(r'([0-9\s]{0,4})?,?([0-9½¼/]{1,3})(\.?[0-9½¼/]{1,3})?\s?(fl\soz|fl\sozs|fluid ounce|fluid ounces)\b[\s|,]{0,}(.*)')
    ingredients_list = list_update(floz, 'fl oz', ingredients_list)

    # Define pattern: oz
    oz = re.compile(r'([0-9\s]{0,4})?,?([0-9½¼/]{1,3})(\.?[0-9½¼/]{1,3})?\s?(oz|ozs|ounce|ounces)\b[\s|,]{0,}(.*)')
    ingredients_list = list_update(oz, 'oz', ingredients_list)

    # Define pattern: lb
    lb = re.compile(r'([0-9\s]{0,4})?,?([0-9½¼/]{1,3})(\.?[0-9½¼/]{1,3})?\s?(lb|lbs|pounds|pound)\b[\s|,]{0,}(.*)')
    ingredients_list = list_update(lb, 'lb', ingredients_list)

    # Define pattern: pint
    pint = re.compile(r'([0-9\s]{0,4})?,?([0-9½¼/]{1,3})(\.?[0-9½¼/]{1,3})?\s?(pint|pints|pt|pts)\b[\s|,]{0,}(.*)')
    ingredients_list = list_update(pint, 'pint', ingredients_list)

    # Define pattern: quart
    qt = re.compile(r'([0-9\s]{0,4})?,?([0-9½¼/]{1,3})(\.?[0-9½¼/]{1,3})?\s?(qt|qts|quart|quarts)\b[\s|,]{0,}(.*)')
    ingredients_list = list_update(qt, 'qt', ingredients_list)

    # Define pattern: gallon
    gal = re.compile(r'([0-9\s]{0,4})?,?([0-9½¼/]{1,3})(\.?[0-9½¼/]{1,3})?\s?(gal|gals|gallon|gallons)\b[\s|,]{0,}(.*)')
    ingredients_list = list_update(gal, 'gal', ingredients_list)


    # Last check finds any remaining numbers on list. 
    # Should NOT replace quantity if there is already a quantity listed for that item.

    # Define pattern: misc/ whole item
    item = re.compile(r'([0-9\s]{0,4})?,?([0-9½¼/]{1,3})(\.?[0-9½¼/]{1,3})?\s?()\b[\s|,]{0,}(.*)')
    ingredients_list = list_update(item, None, ingredients_list)

    return ingredients_list


def parseFraction(a, b, c):

    # Check for spaces in 'a'
    # round(number, ndigits)
    if ' ' in a:
        if len(a) == 4:
            z = a[0:2]
            x = a[3]
            y = b[1]
        else:
            z = a[0]
            x = a[2]
            y = b[1]
        decimal = round((int(z) + (int(x) / int(y))), 3)
    else:
        # Convert number to decimal.
        x = a
        y = b[1]
        decimal = round((int(x)/int(y)), 3)

    return decimal


def list_update(pattern, unit_symbol, ingredients_list):
    # Iterate through INGREDIENTS list of dicts and identify unit and quantity.
    for item in ingredients_list:
        matches = pattern.finditer(item['ingredient'])
        # Finditer will always return a list back- not a single item, 
        #   as there can be more than one match per one line.
        
        # Extract quantities
        for match in matches:
            
            # Only proceed if unit is empty.
            if item['unit'] == '':
                
                # DEBUGGING 3/3
                #print(item['ingredient'])
                #print(match.group(1,2,3,4))

                quantity = 0

                if "/" in match.group(2):
                    quantity = parseFraction(match.group(1), match.group(2), match.group(3))
                else:
                    string = ''
                    # Add group 1 digit to string
                    if match.group(1) != '':
                        string = match.group(1)
                    
                    # Check for fraction symbols in group 2.
                    if bytes(match.group(2), 'UTF-16') == bytes('½', 'UTF-16'):
                        string += '.5'
                    elif bytes(match.group(2), 'UTF-16') == bytes('¼', 'UTF-16'):
                        string += '.25'
                    else:
                        string += match.group(2)

                    # Check for fraction symbols in group 3.
                    if match.group(3) != None:
                        if bytes(match.group(3), 'UTF-16') == bytes('½', 'UTF-16'):
                            string += '.5'
                        elif bytes(match.group(3), 'UTF-16') == bytes('¼', 'UTF-16'):
                            string += '.25'
                        else: 
                            string += match.group(3)
                    quantity = float(string)
                
                if quantity > 0:
                    if unit_symbol != None:
                        item['quantity'] = wholeNumber(quantity)
                        item['unit'] = unit_symbol
                        subbed_string = pattern.sub(r'\5', item['ingredient'])
                        item['ingredient'] = subbed_string
                    elif item['quantity'] == 0:
                        item['quantity'] = quantity
                        subbed_string = pattern.sub(r'\5', item['ingredient'])
                        item['ingredient'] = subbed_string

    return ingredients_list



#### CONVERT TO METRIC ####

def convertMetric(ingredients_list):
    """ Volume """
    #tsp to mL
    for item in ingredients_list:
        if item['unit'] == 'tsp':
            unitParseLitres(item['quantity'] * 5, item)

    #tbsp to mL
    for item in ingredients_list:
        if item['unit'] == 'tbsp':
            unitParseLitres(item['quantity'] * 15, item)

    #cups to mL
    for item in ingredients_list:
        if item['unit'] == 'cup':
            unitParseLitres(item['quantity'] * 240, item)

    #fl oz to mL
    for item in ingredients_list:
        if item['unit'] == 'fl oz':
            unitParseLitres(item['quantity'] * 29.57, item)

    #pints to mL
    for item in ingredients_list:
        if item['unit'] == 'pint':
            unitParseLitres(item['quantity'] * 473, item)


    """ Mass """
    #oz to g
    for item in ingredients_list:
        if item['unit'] == 'oz':
            unitParseGrams(item['quantity'] * 28.35, item)

    #lb to g
    for item in ingredients_list:
        if item['unit'] == 'lb':
            unitParseGrams(item['quantity'] * 454, item)


    return ingredients_list


def unitParseLitres(x, item):
    if x > 999.99:
        x = round(x / 1000, 2)
        item['unit'] = 'L'
    else:
        item['unit'] = 'ml'
    item['quantity'] = round(x, 2)

    return None

def unitParseGrams(x, item):
    if x > 999.99:
        x = round(x / 1000, 2)
        item['unit'] = 'kg'
    else:
        item['unit'] = 'g'
    item['quantity'] = round(x, 2)

    return None




def wholeNumber(x):

    # Returns None if zero.
    if x == 0:
        return ""

    # Returns number without decimals if none exist.
    if x - int(x) == 0:
        return (int(x))
    else:
        return (float(x))

