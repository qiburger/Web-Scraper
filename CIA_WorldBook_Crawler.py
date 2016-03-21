import os
import pickle
from collections import defaultdict
import re
from operator import itemgetter

from bs4 import BeautifulSoup
import urllib

FEED_URL = 'https://www.cia.gov/library/publications/resources/the-world-factbook/'
SAMPLE_URL = "https://www.cia.gov/library/publications/resources/the-world-factbook/geos/us.html"


def get_all_countries_url():
    """
        Get all urls to all countries in CIA World Factbook
    :return: list of url
    """
    all_country_url = []
    r = urllib.urlopen(FEED_URL).read()
    soup = BeautifulSoup(r, "lxml")
    options_in_homepage = soup.find_all("option")
    for option in options_in_homepage:
        rel_addr = option["value"]

        # exclude "world"
        if len(rel_addr) > 1 and ("xx.html" not in rel_addr):
            abs_addr = FEED_URL + rel_addr
            print rel_addr
            all_country_url.append(abs_addr)
    return all_country_url


def get_field_url():
    """
    Scrap all the fields available in the SAMPLE URL
    :return: defaultdict of field->url
    """
    field_url = defaultdict(str)

    r = urllib.urlopen(SAMPLE_URL).read()
    soup = BeautifulSoup(r, "lxml")
    field_divs = soup.find_all("div", id='field')

    for div in field_divs:
        field_name = div.get_text()[:-1]
        field_rel_addr = div.find_all('a')[1]["href"]

        field_abs_addr = (FEED_URL + field_rel_addr[2:])[:-3]
        field_url[field_name] = field_abs_addr

    return field_url


def load_country_data():
    """
    Load all data fields and map to countries
    :return: defaultdict(dict) : map of country -> ( map of data field -> data )
    """
    country_data_dict = defaultdict(dict)
    counter = 0

    field_url = get_field_url()
    for field, link in field_url.iteritems():
        r = urllib.urlopen(link).read()
        soup = BeautifulSoup(r, "lxml")
        table_row = soup.find_all('tr')
        for row in table_row:
            country_name_tag = row.find_all('td', class_="country")
            if len(country_name_tag) > 0:
                country_name = country_name_tag[0].get_text()

                country_data_tag = row.find_all('td', class_="fieldData")
                if len(country_data_tag) > 0:
                    country_data = country_data_tag[0].get_text()
                    country_data_dict[country_name][field] = country_data.rstrip().lstrip()

    pickle.dump(country_data_dict, open('country_data.p', 'wb'))
    return country_data_dict


def country_data_load_helper():
    """
    Helps load the saved country data
    :return: output of load_country_data
    """
    if os.path.isfile("country_data.p"):
        return pickle.load(open('country_data.p', 'rb'))
    else:
        return load_country_data()


def get_earthquake_in_continent(continent="South America", hazard="earthquakes"):
    """
    List countries in South America/given continent that are prone to earthquakes/given hazard.
    :param hazard: str input of natural hazard name. Must follow CIA convention
    :param continent: str input of continent. Must follow CIA convention
    :return: list of countries
    """
    output = []

    country_data_dict = country_data_load_helper()

    for country in country_data_dict:
        if "Natural hazards" in country_data_dict[country]:
            if hazard in country_data_dict[country]["Natural hazards"]:
                if "Location" in country_data_dict[country]:
                    if continent in country_data_dict[country]["Location"]:
                        output.append(country)
    return output


def lowest_elevation_in_continent(continent="Europe"):
    """
    Find the country with the lowest elevation point in Europe/given continent.
    :param continent: str input of continent. Must follow CIA convention
    :return: str name of country with lowest elevation
    """
    lowest = 1000
    lowest_country = "United States"
    lowest_regex = re.compile("lowest point(.*)-[0-9]+")
    elevation_regex = re.compile("-[0-9]+")

    country_data_dict = country_data_load_helper()

    for country in country_data_dict:
        if "Elevation" in country_data_dict[country]:
            if "lowest point" in country_data_dict[country]["Elevation"]:
                if "Location" in country_data_dict[country]:
                    if continent in country_data_dict[country]["Location"]:
                        data = country_data_dict[country]["Elevation"]
                        find_lowest = re.findall(lowest_regex, data)
                        regex_find = re.findall(elevation_regex, data)
                        if len(regex_find) > 0:
                            find_elevation = float(regex_find[0])
                            if find_elevation < lowest:
                                lowest_country = country
                                lowest = find_elevation
                                print country
                                print find_elevation

    return lowest_country


def country_in_hemisphere(first_letter='S', second_letter='E'):
    """
    List all countries in the southeastern / any given hemisphere.
    :type second_letter: char
    :type first_letter: char
    :param first_letter: enter S for southern hemisphere, N for northern
    :param second_letter: enter E for eastern hemisphere, W for western
    :return: list of countries
    """
    output = []

    if len(first_letter) != 1 or (first_letter != 'S' and first_letter != 'N'):
        raise ValueError("illegal input parameter")
    if len(second_letter) != 1 or (second_letter != 'E' and second_letter != 'W'):
        raise ValueError("illegal input parameter")

    pattern_string = "[0-9 ]+" + first_letter + ",[0-9 ]+" + second_letter

    se_regex = re.compile(pattern_string)

    country_data_dict = country_data_load_helper()

    for country in country_data_dict:
        if "Geographic coordinates" in country_data_dict[country]:
            data = country_data_dict[country]["Geographic coordinates"]
            found = re.findall(se_regex, data)
            if len(found) > 0:
                output.append(country)

    return output


def continent_political_parties(continent="Asia", count=10):
    """
        List countries in Asia with more than 10 political parties.
    :param continent: str input of continent. Must follow CIA convention
    :param count: int number of political parties
    :return: list of countries
    """
    output = []

    country_data_dict = country_data_load_helper()

    for country in country_data_dict:
        if "Location" in country_data_dict[country]:
            if continent in country_data_dict[country]["Location"]:
                if "Political parties and leaders" in country_data_dict[country]:
                    if len(country_data_dict[country]["Political parties and leaders"]) > 0:
                        if country_data_dict[country]["Political parties and leaders"].count('\n') > count:
                            output.append(country)
    return output


def highest_electricity_per_cap(top_k=5):
    """
    Find the top k countries with the highest electricity consumption per capita
    :param top_k: int top k number of countries with highest electricity consumption per capita
    :return: list of top k countries
    """
    country_data_dict = country_data_load_helper()
    consumption_dict = {}

    population_pattern = re.compile("[0-9,]+")

    for country in country_data_dict:
        if "Electricity - consumption" in country_data_dict[country]:
            if "Population" in country_data_dict[country]:
                population_text = country_data_dict[country]["Population"]
                electricity_text = country_data_dict[country]["Electricity - consumption"]

                if len(population_text) > 0:
                    population_find = re.findall(population_pattern, population_text)[0]
                    population = int(population_find.replace(",", ""))

                    if len(electricity_text) > 0:
                        consumption = electricity_text.split()[:2]
                        consumption_per_cap = float(consumption[0].replace(",", "")) / population

                        if "trillion" in consumption:
                            consumption_per_cap *= pow(10, 12)
                        elif "billion" in consumption:
                            consumption_per_cap *= pow(10, 9)
                        elif "million" in consumption:
                            consumption_per_cap *= pow(10, 6)

                        consumption_dict[country] = consumption_per_cap

    return top_n_in_dict(consumption_dict, 1, top_k)


def top_n_in_dict(input_dict, sort_index, k):
    """
    Helper function that gets first k pairs with highest valeus
    :param k: first k pairs
    :type input_dict: dict
    :param input_dict: input dictionary
    :param sort_index: top n pairs
    """
    return sorted(input_dict.iteritems(), key=itemgetter(sort_index), reverse=True)[:k]


def dominant_religion(min_percentage, max_percentage):
    """
    1. List countries where the dominant religion accounts for more than 80% of the population.
    2. List countries where the dominant religion accounts for less than 50% of the population.
    :param min_percentage: Use for 1. Assume nice input of int - if 80% the input would be 80!
    :param max_percentage: Use for 2. Assume nice input of int - if 80% the input would be 80!
    :return: dict of countries satisfying 1 and 2 as two values. None if error.
    """
    min_percentage = float(min_percentage)
    max_percentage = float(max_percentage)
    min_string_key = "Dominant religion > " + str(min_percentage) + "%: "
    max_string_key = "Dominant religion < " + str(max_percentage) + "%: "

    output = defaultdict(list)

    if min_percentage <= 0 or max_percentage <= 0:
        return None

    country_data_dict = country_data_load_helper()

    pattern = re.compile("[0-9.]+%")

    for country in country_data_dict:
        if "Religions" in country_data_dict[country]:
            string = country_data_dict[country]["Religions"]

            if len(string) > 0:
                dominant_string = string.split(",")[0]
                found = re.findall(string=dominant_string, pattern=pattern)

                if len(found) > 0:
                    percentage = float(found[0][:-1])

                    if percentage > min_percentage or percentage < max_percentage:

                        if '(' in dominant_string:
                            first_bracket = string.index('(')

                            m = re.search("\d", dominant_string)
                            first_percentage = m.start()

                            min_index = min(first_bracket, first_percentage)

                        else:
                            m = re.search("\d", dominant_string)
                            min_index = m.start()

                        religion = dominant_string[:min_index].rstrip()

                        if percentage > min_percentage:
                            output[min_string_key].append((country, religion))
                        if percentage < max_percentage:
                            output[max_string_key].append((country, religion))

    return output


def landlocked():
    """
    Find countries landlocked by a single country
    :return: list of these countries
    """
    output = []

    country_data_dict = country_data_load_helper()

    for country in country_data_dict:
        if "Land boundaries" in country_data_dict[country]:
            if "border countries (1)" in country_data_dict[country]["Land boundaries"]:
                if "Coastline" in country_data_dict[country]:
                    if "landlocked" in country_data_dict[country]["Coastline"]:
                        output.append(country)
    return output


def highest_k_sex_ratio(top_k):
    """
    Interesting questions: find top k countries with highest sex ratio (male / female)
    :param top_k: int top k countries
    :return: list of top k countries
    """
    country_data_dict = country_data_load_helper()
    output = {}

    pattern = re.compile("total population: [0-9.]+")

    for country in country_data_dict:
        if "Sex ratio" in country_data_dict[country]:
            sex_ratio_text = country_data_dict[country]["Sex ratio"]
            if len(sex_ratio_text) > 0:
                sex_ratio_found = re.findall(pattern, sex_ratio_text)

                if len(sex_ratio_found) > 0:
                    sex_ratio = float(sex_ratio_found[0].split()[-1])
                    output[country] = sex_ratio

    return top_n_in_dict(output, 1, top_k)


if __name__ == "__main__":
    print "Follow doc string / readme to start"