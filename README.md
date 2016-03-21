# Web-Scraper


The process behind this web scraper is relatively straight forward:

	- first get all field urls via beautifulsoup using a sample country page
		- here I naturally used the United States

	- field url leads to a page of all available data on the field, sorted by country

	- load all urls and map data field to countries

	- use this map to answer some interesting quesitons below

Wth the help of regex and beautifulsoup, we can answer some interesting questions about different countries in the world: 

1. List countries in South America that are prone to earthquakes.
	- use get_earthquake_in_continent
	    :param hazard: str input of natural hazard name. Must follow CIA convention
	    :param continent: str input of continent. Must follow CIA convention
	    :return: list of countries

2. Find the country with the lowest elevation point in Europe.
	- Note: for simplicity, I assumed the lowest point of countries in question has negative altitude. This seems true after manually checking countries in all continents.

	- use lowest_elevation_in_continent
    	:param continent: str input of continent. Must follow CIA convention
    	:return: str name of country with lowest elevation

3. List all countries in the southeastern hemisphere
	- use country_in_hemisphere
	    :param first_letter: enter S for southern hemisphere, N for northern
    	:param second_letter: enter E for eastern hemisphere, W for western
    	:return: list of countries

    - If inputs are not valid, will throw ValueError

4. List countries in Asia with more than 10 political parties.
	- use continent_political_parties
	    :param continent: str input of continent. Must follow CIA convention
    	:param count: int number of political parties
    	:return: list of countries

5. Find the top 5 countries with the highest electricity consumption per capita. (Electricity consumption / population)
	- use highest_electricity_per_cap
	    :param top_k: int top k number of countries with highest electricity consumption per capita
    	:return: list of top k countries

    - handle "trillion," "billion" and "million" separately

6. Certain countries have one dominant religion (in terms of fraction of the population) whereas other countries don’t. List countries (along with the religion) where the dominant religion accounts for more than 80% of the population. List countries (along with the religions) where the dominant religion accounts for less than 50% of the population.
	- Two goals:
		1. List countries where the dominant religion accounts for more than 80% of the population.
    	2. List countries where the dominant religion accounts for less than 50% of the population.

	- use dominant_religion
	    :param min_percentage: Use for 1. Assume nice input of int - if 80% the input would be 80!
    	:param max_percentage: Use for 2. Assume nice input of int - if 80% the input would be 80!
    	:return: dict of countries satisfying 1 and 2 as two values. None if error.

	- Use max % when given a range on the website (e.g. Muslim 80-90%)

7. A landlocked country is one that is entirely enclosed by land. For example, Austria is landlocked and shares its borders with Germany, Czech Republic, Hungary, etc. There are certain countries that are entirely landlocked by a single country. Find these countries.
    - Use landlocked
    	:return: list of these countries

8. Wild card – come up with an interesting question. List the question and find the answer to it.
	- Use highest_k_sex_ratio(top_k):
     	:param top_k: int top k countries
   		:return: list of top k countries

   	- Interesting questions: find top k countries with highest sex ratio (male / female)




