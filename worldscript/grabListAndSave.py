import requests
from bs4 import BeautifulSoup as BS
import json
import re

JSON_OUTPUT = "Countries_json.json"
CSV_OUTPUT = "Countries_csv.csv"
MAIN_URI = "https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_area"
ROOT_URI = "https://en.wikipedia.org"

bracket_rex = "\[(.*?)\]"
para_rex = "\((.*?)\)"

def filter_table_members(_member):
    mem = re.sub(para_rex, "", _member)
    return mem.replace("\xa0","").replace("\n", "") if len(_member) > 0 else "N/A"

def filter_table_arrays(_member_array):
    arr_len = len(_member_array)
    title_index = 0 
    lim_index = 1 if arr_len == 7 else 0
    body = []


    for m in _member_array[lim_index::]:
        if not m:
            continue

        m = str(m.text).replace("\xa0","").replace("\n","").replace(","," ")
        m = re.sub(bracket_rex, "", m)
        m = re.sub(para_rex, "", m)
        body.append(m) 
    
    title = body[title_index]
    links = _member_array[lim_index::][title_index].findAll("a")

    for l in links:
        if l.get("title"):
            link_suffix = l.get("href")
            body.append(f"{ROOT_URI}{link_suffix}")
           
    return body

def build_table_soup(_main_soup):
    tables = _main_soup.findAll("table")
    country_table = tables[1]
    headers = [filter_table_members(t.text) for t in country_table.findAll("th")][1::]
    headers.append("Link")
    headers.append("Sub Link")
    body_rows = [filter_table_arrays(t.findAll("td")[0::]) for t in country_table.find("tbody").findAll("tr")[2::]]
    return {"headers":headers, "body" : body_rows}

def main():
    resp = requests.get(MAIN_URI) 
    print(resp.ok)
    main_soup = BS(resp.content, features="html.parser")
    table_members = build_table_soup(main_soup)
    
    with open(JSON_OUTPUT, "w") as my_fil:
        my_fil.write(json.dumps(table_members))

    with open(CSV_OUTPUT, "w") as my_fil:
        final_string = ""
        final_string += ",".join(table_members.get("headers"))
        final_string += "\n"
        
        filt_table_members = []
        for b in table_members["body"]:
            filt_table_members.append([str(b2).replace(",","_") for b2 in b])

        final_string += "\n".join([",".join(f) for f in filt_table_members])
        my_fil.write(final_string)

if __name__ == "__main__":
    main()
