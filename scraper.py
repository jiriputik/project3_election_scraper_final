import requests
from bs4 import BeautifulSoup
from sys import platform, argv, exit
import csv
import os
import time
from window_pyqt import run_app_window


def check_system():                # zjistit systém -> win/něco jiného
    return True if platform.startswith("win") else False

def clear_screen():                 # smaž konzoli
    os.system('cls') if check_system else os.system('clear')

def check_input_url(run_params: list) -> bool:    # správný url formát příklad: https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101
    '''
    Vyhodnocení zadaného url, testuje zda pochází ze správného serveru a jestli vrací smysluplný obsah.
    Vrací True/False
    '''
    if ( not (run_params[1].startswith("https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=")) or 
        not (run_params[1][-4:]).isdigit() or
        not (run_params[1][-15:-14]).isdigit() or
        (requests.get(run_params[1]).status_code != 200) or
        get_header(read_main_page(run_params[1]))[0].get_text().strip() == "Page not found!"):
        return True
    return False

def read_params_from_line() -> list:
    '''
    Načtení předané konfigurace z příkazové řádky. 
    Otestuje ¨správnost zadání a v případě úspěchu vypíše parametry předané z promptu.
    EXAMPLE:
    filename.py "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101"  file_output.csv
    '''
    run_params = argv
    if len(run_params) < 3:                     # test počtu parametrů
        print("Invalid number of parameters!")
        exit()
    elif check_input_url(run_params):           # test url
        print("Bad format of requested url address or parameters entered in wrong order!")
        exit()
    else:
        print(f"Parameters to proceed:\nrequested url: {run_params[1]}\noutput file: {run_params[2]}")
    return (run_params[1],run_params[2])

def read_main_page(url):            
    '''
    Načtení html stránky do soup objektu
    '''
    page_down = requests.get(url)
    page_down_soup = BeautifulSoup(page_down.text, "html.parser")
    return page_down_soup

def get_header(soup_page: BeautifulSoup) -> list:
    '''
    Získej a vrať získané info v headers h3m buď page not found nebo info o kraji/regionu, 
    vrací list s výsledkem
    '''
    headers = soup_page.find_all("h3")[:2]
    return(headers)


def get_all_rows(soup_page: BeautifulSoup) -> list:       # vrať řádky z tabulky
    return soup_page.find_all("tr")

def grab_url_from_td(row: BeautifulSoup) -> str:           # vrať odkaz z buňky tabulky
    return(row.a['href'])

def separate_municipality(soup_page: BeautifulSoup) -> dict:    
    '''
    vrátí dict ve formě {město:[kód města, url na výsledky]}
    '''
    muni_url_start = "https://volby.cz/pls/ps2017nss/"      # fixní začátek každé url v tabulce, z tabulky jsou získány druhé části
    muni_dict_urls = dict()
    rows = get_all_rows(soup_page)
    for _ in rows:
        row = _.find("td")
        if row and row.text != "-":
            url = grab_url_from_td(row)
            muni_dict_urls.update({(row.find_next_sibling("td").get_text()):[row.get_text(), (muni_url_start + url)]})  # zakomentovat pouze pro jednu obec
            #muni_dict_urls = ({(row.find_next_sibling("td").get_text()):[row.get_text(), (muni_url_start + url)]})   # odkomentovat pouze pro jednu (poslední) obec
    return muni_dict_urls

def get_election_data_from_url(location: str, given_url_list: list) -> dict:  
    '''
    Načti volební data z daných url pro jednotlivé obce
    '''
    print("#", end="", flush=True)      # zobrazení průběhu stahování dat, aby uživatel věděl, že se něco děje
    statistics_dict = dict()
    statistics_list = list()
    table_overall = read_main_page(given_url_list[1]).find("table")
    table_data = table_overall.find_all_next("table")
    for index, overall_stats in enumerate(table_overall.find_all("td")):
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
    '''
    Zapiš předaná data ve formálu list dictů do souboru "file" ve formátu csv, 
    první řádek csv souboru budou klíče převzaté z dict.
    '''
    with open(file, mode="w", encoding="utf-8", newline="") as f:
            for index,data in enumerate(stats_list):
                writer = csv.DictWriter(f, data.keys())
                writer.writeheader() if index == 0 else ...
                writer.writerow(data)

def check_generate_graph():                     # požadavek na vizualizaci ano/ne
    visual = ""
    while visual not in ["Y", "Yes", "y", "N", "No", "n"]:
        visual = input("Do you want to visualize downloaded and exported data? (Yes/No) ")
    return False if visual.casefold().startswith("n") else True

def format_data_for_graph(stats:list) ->list:       
    '''
    Formátuj data pro grafický výstup:
        - ořízni kód města
        - ořízni počty hlasů (registered, envelopes, valid)
        - vyhoď strany s výsledkem 0
        - seřaď dle počtu hlasů
    
    Vrací výsledek: list dictů, kde dict je ve formátu dict {'lokalita':'město', 'strana1':počet, 'strana2':počet, 'strana3':počet..} 
    '''
    formatted_list = list()
    formatted_dict = dict()
    votes = dict()
    for data_dict in stats:
        formatted_dict['location'] = data_dict['location']          
        votes = dict(list(data_dict.items())[5:])                                       # odfiltrování prvních pěti údajů (obec, kód, součty)
        votes = {key: value for key, value in votes.items() if value > 0}               # odfiltrování stran s nulovým počtem hlasů
        sorted_votes = (sorted(votes.items(), key=lambda item: item[1], reverse=True))  # setřídění podle počtu hlasů
        formatted_dict['votes'] = dict(sorted_votes)
        formatted_list.append(dict(formatted_dict))
    return formatted_list




# main part

# Data pro testování: (odkomentovat jeden z url a soubor s výstupem, spouštět bez parametrů)
#url_page = "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=7&xnumnuts=5103"
#url_page = "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101" # test jiného kraje
#url_page = "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103" # test jiného kraje
# csv_output = "output.csv"

if __name__ == "__main__":
    clear_screen()
    params = read_params_from_line()
    url_page = params[0]
    csv_output = params[1]
    stats = list()
    region_page_soup = read_main_page(url_page)
    headers = (get_header(region_page_soup))
    print(f"District: {headers[0].get_text()[6:]}Region: {headers[1].get_text()[7:]}")
    print("Getting requested data ...")
    municipalities_url_dict = separate_municipality(region_page_soup)
    for location,url_list in municipalities_url_dict.items():
        stats.append(get_election_data_from_url(location, url_list))
    print("\nDone!")
    for i in range(10):
        time.sleep(0.2)
    
    # odkomentovat tyto dva řádky pro kontrolní výpis do terminálu:
    #for data in stats:  
    #    print(f"Obec: {data['location']}, kód obce {data['code']}, voličů: {data['registered']}, obálek: {data['envelopes']}")
    
    print(f"Writing data to csv file, name:{csv_output}") 
    write_to_csv(stats, csv_output)
    print("All tasks done!")
    if check_generate_graph():
        normalized_stats = format_data_for_graph(stats)
        print("Opening the new window with a visualised data...")
        run_app_window(normalized_stats)  # předání dat pro vykreslení grafu
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

