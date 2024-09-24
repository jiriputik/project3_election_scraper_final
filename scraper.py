"""
scraper.py: Third project for Engeto Online Python Academy - Election scraper
window_pyqt.py: additional file for data visualisation

author: Jiri Putik
email: j.putik@gmail.com
discord: peen_cz
"""

import os
import csv
import time
from sys import platform, argv, exit
from requests import get
from bs4 import BeautifulSoup
from window_pyqt import run_app_window


def check_system() -> bool:                # check user's system -> win/other
    return True if platform.startswith("win") else False


def clear_screen():                 # clear screen
    os.system('cls') if check_system else os.system('clear')


def check_input_url(run_params: list) -> bool:    # 
    """
    Check of entered url, testing the correct server and content.
    Returns True/False
    Example correct url: 
    https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101
    """
    url_prefix = "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj="
    if ( not (run_params[1].startswith(url_prefix)) \
        or not (run_params[1][-4:]).isdigit() \
        or not (run_params[1][-15:-14]).isdigit() \
        or (get(run_params[1]).status_code != 200) \
        or get_header(read_main_page(run_params[1]))[0].get_text().strip() == "Page not found!"):
        return True
    return False


def read_params_from_line() -> list:
    """
    Read of config from entered arguments when script is started,
    like: "filename argument1 argument2"
    Testing of correct input and print of entered parameters.
    EXAMPLE:
    filename.py "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101"  file_output.csv
    """
    run_params = argv
    if len(run_params) < 3:         # testing of correct number of parameters
        print("Invalid number of parameters!")
        exit()
    elif check_input_url(run_params):           # test url
        print("Bad format of requested url address or \
parameters entered in a wrong order!")
        exit()
    else:
        print(f"Parameters to proceed:\n\
requested url: {run_params[1]}\n\
output file: {run_params[2]}")
    return (run_params[1],run_params[2])


def read_main_page(url: str) -> BeautifulSoup:            
    """
    Connection to the server and download of the html page to the soup object
    """
    page_down = get(url)
    return BeautifulSoup(page_down.text, "html.parser")


def get_header(soup_page: BeautifulSoup) -> list:
    """
    Get and return info from headers h3, 
    either page not found or info about region, 
    returns a list with the result.
    """
    return(soup_page.find_all("h3")[:2])


def get_all_rows(soup_page: BeautifulSoup) -> list:       
    """
    Returns all rows from the table with <tr> tag.
    """
    return soup_page.find_all("tr")


def grab_url_from_td(row: BeautifulSoup) -> str:           
    """
    Returns the url from the table's cell, <a> tag.
    """
    return(row.a['href'])


def separate_municipality(soup_page: BeautifulSoup) -> dict:    
    """
    Return dict with data in format dict:
      {municipality_name:[municipality_code, results_url]}
    """
    # fixed first part of every url in the table:  
    muni_url_start = "https://volby.cz/pls/ps2017nss/"      
    muni_dict_urls = dict()
    # from table are acquired second parts of urls
    rows = get_all_rows(soup_page)
    for table_row in rows:
        row = table_row.find("td")
        if row and row.text != "-":
            url = grab_url_from_td(row)
            muni_dict_urls.update({(row.find_next_sibling("td").get_text()):[row.get_text(), (muni_url_start + url)]})  # comment this row to get only one municipality, for testing
            #muni_dict_urls = ({(row.find_next_sibling("td").get_text()):[row.get_text(), (muni_url_start + url)]})   # uncomment this row to get only one municipality (the last), for testing
    return muni_dict_urls


def get_election_data_from_url(location: str, given_url_list: list) -> dict:  
    """
    Get election data from given urls for each municipality.
    """
    # printing of symbol "#" in a row to represent data processing
    print("#", end="", flush=True)      
    statistics_list = list()
    table_overall = read_main_page(given_url_list[1]).find("table")
    table_data = table_overall.find_all_next("table")
    for overall_stats in table_overall.find_all("td"):
        statistics_list.append(overall_stats.get_text().replace("\xa0",""))
    statistics_dict = {
        'location':location,
        'code':given_url_list[0],
        'registered':int(statistics_list[3]), 
        'envelopes':int(statistics_list[4]), 
        'valid':int(statistics_list[7]),
        }
    for table in table_data:
        data_rows = get_all_rows(table)
        for _ in data_rows:
            data_row = _.find("td")
            if data_row and data_row.text != "-":
                party_name = data_row.find_next_sibling("td").get_text()
                party_result = int((data_row.find_next_sibling("td").find_next_sibling("td").get_text()).replace("\xa0",""))
                statistics_dict.update({party_name:party_result})
    return statistics_dict


def write_to_csv(stats_list:list, file:str):
    """
    Write the passed data in the format of list of dicts to the file "file" 
    in csv format, the first row of the csv file will be the keys taken from
    the dict.
    """
    with open(file, mode="w", encoding="utf-8", newline="") as f:
            for index,data in enumerate(stats_list):
                writer = csv.DictWriter(f, data.keys())
                writer.writeheader() if index == 0 else ...
                writer.writerow(data)


def check_generate_graph() -> bool:      # user's choice to generate graphs
    visual = ""
    while visual not in ["Y", "Yes", "y", "N", "No", "n"]:
        visual = input("Do you want to visualize downloaded and exported data?\
 (Yes/No) ")
    return False if visual.casefold().startswith("n") else True


def format_data_for_graph(stats:list) -> list:       
    """
    Format data for the graphical output:
        - cut the municipality code
        - cut additional statistics 
          (registered, envelopes, valid numbers of votes)
        - remove parties with a result of 0
        - sort by total number of votes

    Returns: list of dicts, where dict is in format:
    {'location':'city', 'party1':votes, 'party2':votes, 'party3':votes..}    
    """
    formatted_list = list()
    formatted_dict = dict()
    for data_dict in stats:
        formatted_dict['location'] = data_dict['location']     
        # cut first five data sets (municipality, code, unused statistics):     
        votes = dict(list(data_dict.items())[5:])                                       
        # cut the parties with 0 votes:
        votes = {key: value for key, value in votes.items() if value > 0}   
        # sort the parties by total number of votes:           
        sorted_votes = (sorted(votes.items(), 
                               key=lambda item: item[1], reverse=True))  
        formatted_dict['votes'] = dict(sorted_votes)
        formatted_list.append(dict(formatted_dict))
    return formatted_list


# main part

# Data for testing: 
# uncomment one of urls and file with csv_output 
# and run the script without any parameters.
#url_page = "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=7&xnumnuts=5103"
# test some other region
#url_page = "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101"
# test some other region
#url_page = "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103"
# csv_output = "output.csv"


if __name__ == "__main__":
    clear_screen()
    params = read_params_from_line()
    url_page = params[0]
    csv_output = params[1]
    stats = list()
    region_page_soup = read_main_page(url_page)
    headers = (get_header(region_page_soup))
    print(f"District: {headers[0].get_text()[6:]}\
Region: {headers[1].get_text()[7:]}")
    print("Getting requested data ...")
    municipalities_url_dict = separate_municipality(region_page_soup)
    for location,url_list in municipalities_url_dict.items():
        stats.append(get_election_data_from_url(location, url_list))
    print("\nDone!")
    for i in range(10):
        time.sleep(0.2)
    
    # uncomment the next rows for a control print to terminal (for testing)
    #for data in stats:  
    #    print(f"City: {data['location']}, city ID {data['code']}, \
    #registered voters: {data['registered']}, envelopes: {data['envelopes']}")
    
    print(f"Writing data to csv file, name:{csv_output}") 
    write_to_csv(stats, csv_output)
    print("All tasks done!")
    if check_generate_graph():
        normalized_stats = format_data_for_graph(stats)
        print("Opening the new window with a visualised data...")
        # data handover to the window_pyqt.py for visualisation
        run_app_window(normalized_stats)  
    else:
        print("Goodbye")
    

    # structure of a variable 'stats' is list of dicts

    # dict structure: 

    # {
    #                    'location':city_name
    #                    'code':city_code
    #                    'registered':number
    #                    'envelopes':number
    #                    'valid':number
    #                    'first_party_name':number_of_votes
    #                    .
    #                    .
    #                    'parties_names':number_of_votes
    #                    .
    #                    .
    #                    'last_party_name':number_of_votes 
    #                                     
    # }
    

    # Formatted data for graph, variable 'normalized_stats', values in key 'votes' are sorted in descending order and must be > 0:
    # 
    #  [
    #     {'location': 'Praha', 'votes': {'partyname1': 40, 'partname2': 30, 'partyname3': 20}},
    #     {'location': 'Brno', 'votes': {'partyname1': 25, 'partyname2': 15, 'partyname3': 5}},
    #     {'location': 'Ostrava', 'votes': {'partyname1': 31, 'partyname2': 28, 'partyname3': 25, 'partyname4':12}},
    #     {'location': 'Plzeň', 'votes': {'partyname1': 20, 'partyname2': 19}},
    #     {'location': 'Liberec', 'votes': {'partyname1': 5, 'partyname2': 3, 'partyname3': 1}}
    #       .
    #       .
    #       . 
    # ]
    # 

