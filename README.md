Scraper

Scraper is a Python script, which scrapes a data from the Czech's election 2017 statistics web page and save the data of single areas under the chosen district. Output file is csv type with comma separated values.
Then the elections data (area's political parties results) can be visualised to the user.



Installation:
=============

Scraper is a Python script. It requires Python - http://www.python.org

Scraper uses external libraries to work properly
Used external libraries, that should be installed:

    requests
    bs4
    PyQt5
    matplotlib

To run the script in your virtual environment:

1. create the new virtual environment
    
    If using pyenv, run in your shell 
            
            python -m venv env_name

    where env_name is a name of your new virtual environment and name of its directory

2. Download enclosed file requirements.txt into the env_name directory

3. Move to the directory, where requirements.txt is located

4. Activate your virtualenv  (on Windows run env_name/Scripts/activate)

5. Run in your shell to install all requested libraries

            pip install -r requirements.txt 

6. Download files scraper.py, window_pyqt.py and copy them to your env_name directory

Using of Scraper
================

To run the script, use following syntax:

python scraper.py "url" ouput_file.csv

where url should be a link to the existing page of a main district (in czech "Územní celek") and output_file.csv is a name of csv file to be written on your hard disc.

Url examples:
https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=7&xnumnuts=5103  Liberecký kraj/Liberec district
https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103  Olomoucký kraj/Prostějov district
https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101  Středočeský kraj/Benešov district

Output file structure:
======================

Comma separated data output(csv file data structure), first row is used for the data description.

First 5 entries are: location (name of local area), code (area code used for CZ elections),
registered (number of electors), envelopes (used envelopes), valid (total valid votes). Other entries
are numbers of achieved votes for particular parties, which names are in the first row.

Output example:

First row:
location,code,registered,envelopes,valid,Občanská demokratická strana,Řád národa - Vlastenecká unie,CESTA ODPOVĚDNÉ SPOLEČNOSTI,Česká str.sociálně demokrat.,Radostné Česko,STAROSTOVÉ A NEZÁVISLÍ,Komunistická str.Čech a Moravy,Strana zelených,"ROZUMNÍ-stop migraci,diktát.EU",Strana svobodných občanů,Blok proti islam.-Obran.domova,Občanská demokratická aliance,Česká pirátská strana,Unie H.A.V.E.L.,Referendum o Evropské unii,TOP 09,ANO 2011,Dobrá volba 2016,SPR-Republ.str.Čsl. M.Sládka,Křesť.demokr.unie-Čs.str.lid.,Česká strana národně sociální,REALISTÉ,SPORTOVCI,Dělnic.str.sociální spravedl.,Svob.a př.dem.-T.Okamura (SPD),Strana Práv Občanů

Second row:
Benešov,529303,13104,8485,8437,1052,10,2,624,3,802,597,109,35,112,6,11,948,3,6,414,2577,3,21,314,5,58,17,16,682,10

Third row:
Bernartice,532568,191,148,148,4,0,0,17,0,6,7,1,4,0,0,0,7,0,0,3,39,0,0,37,0,3,0,0,20,0

.
.
.