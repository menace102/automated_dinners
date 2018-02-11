from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def strip_amazon_title(title):
    stripped_title = title
    keywords_to_remove = [
        'Amazon.com',
        '(frozen)',
        'Grocery & Gourmet Food',
        'Prime Pantry',
        ':',
        ]
    for keyword in keywords_to_remove:
        stripped_title = stripped_title.replace(keyword, '')
    stripped_title = stripped_title.strip()
    return stripped_title

def parse_data_from_amazon_title(title):
    stripped_title = strip_amazon_title(title)
    
    comma_split = stripped_title.split(',')
    # print(comma_split[:-1])
    units = comma_split[-1]
    units = units.strip()
    units = units.split(' ')
    # print(units)
    # assert len(units) == 2
    if len(units) != 2:
        print("WARNING: more than two fields found in unit area of name: {}".format(units))
    ingredient_dict = {}
    ingredient_dict['name'] = ','.join(comma_split[:-1]) 
    ingredient_dict['unittype'] = units[1]
    ingredient_dict['units'] = units[0]
    return ingredient_dict

def parse_ingredient_from_amazon(driver, address):
    print(address)
    if 'http://' not in address:
        address = 'http://'+address

    try:
        driver.get(address)
    except:
        return {}
    # check that address is valid, and show an ingredient

    title_elem = driver.find_elements_by_tag_name('title')
    if len(title_elem) != 1:
        print("ERROR parsing amazon at {}: more than one 'title' tag found".format(address))
    title = title_elem[0].get_attribute('innerText')

    ingredient_dict = parse_data_from_amazon_title(title)

    price_elem = driver.find_elements_by_tag_name('priceblock_ourprice')
    if len(price_elem) > 1:
        print("ERROR parsing amazon at {}: more than one 'priceblock_ourprice' element id found".format(address))
    elif len(price_elem) == 0:
        print("ERROR parsing amazon at {}: no 'priceblock_ourprice' element id found".format(address))
    else:
        price = price_elem[0].get_attribute('innerText')
        ingredient_dict['price'] = price

    ingredient_dict['amazonid'] =  address
    # ingredient_dict['unittypeid'] = get_unittypeid()

    print(title)
    for key in ingredient_dict:
        print("{}: {}".format(key, ingredient_dict[key]))
    print('\n')

    return ingredient_dict


def batch_parsing_ingredient_from_amazon():
    addresses = [
    "http://www.amazon.com/gp/product/B000VCBXVC?fpw=fresh"
    "www.amazon.com/gp/product/B000P6J0SM?fpw=fresh",
    "www.amazon.com/gp/product/B000SE9NUG?fpw=fresh",
    "www.amazon.com/gp/product/B000PXYFTY?fpw=fresh",
    "www.amazon.com/gp/product/B000YMZU1I?fpw=fresh",
    "www.amazon.com/gp/product/B00J3VHERY?fpw=fresh",
    "www.amazon.com/gp/product/B000NSIAGA?fpw=fresh",
    "www.amazon.com/gp/product/B000O6IBOW?fpw=fresh",
    "www.amazon.com/gp/product/B000PXZZQG?fpw=fresh",
    "www.amazon.com/gp/product/B000VB47YI?fpw=fresh",
    "www.amazon.com/gp/product/B000VCBXVC?fpw=fresh",
    "www.amazon.com/gp/product/B0011EIZJW?fpw=fresh",
    "www.amazon.com/gp/product/B004E2X9YY?fpw=fresh",
    "www.amazon.com/gp/product/B004E303EW?fpw=fresh",
    "www.amazon.com/gp/product/B008NUQY90?fpw=fresh",
    "www.amazon.com/gp/product/B00LY3TBKW?fpw=fresh",
    "www.amazon.com/gp/product/B00M8ZEG1E?fpw=fresh",
    "www.amazon.com/gp/product/B00RWTVI9Y?fpw=fresh",
    "www.amazon.com/gp/product/B01BWM57CK?fpw=fresh",
    "www.amazon.com/gp/product/B0005ZU8UW?fpw=fresh",
    "www.amazon.com/gp/product/B0005ZV770?fpw=fresh",
    "www.amazon.com/gp/product/B000NOGLY2?fpw=fresh",
    "www.amazon.com/gp/product/B000O6GAWM?fpw=fresh",
    "www.amazon.com/gp/product/B000P6L3SM?fpw=fresh",
    "www.amazon.com/gp/product/B000P6X5F6?fpw=fresh",
    ]

    driver = webdriver.Chrome()

    for a in addresses: 
        parse_ingredient_from_amazon(driver, a)

    driver.close()

