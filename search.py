import requests
import click
import webbrowser
import pandas
import os
from bs4 import BeautifulSoup
from pathlib import Path


@click.command()
@click.option('-s', '--search', "user_query", default='World', help="User's search query")
@click.option('-b', '--browser', "browser", default='chrome', help="Browser to use")
@click.option('-o', '--output', "output", default='not', help="File to save the results")
def main(user_query, browser, output):
    print(f"Searching for {user_query} in {browser}...")

    replace_whitespace = user_query.replace(' ', '+')
    number_of_search_results = 10
    url = f"https://www.google.com/search?q={replace_whitespace}&num={number_of_search_results}"
    webbrowser.get(browser).open(url)
    requests_result = requests.get(url)
    soup_link = BeautifulSoup(requests_result.content, "html.parser")
    links = soup_link.find_all("a")

    my_file = Path(output)

    if my_file.exists():
        to_file(links, my_file)
    else:
        to_console(links)


def to_file(links, my_file):
    result = open(my_file, "w")
    result.write("Title,URL\n")

    add_results(links, result)

    print("Done!")


def to_console(links):
    result = open('result.csv', "w")
    result.write("Title,URL\n")

    add_results(links, result)

    answer = pandas.read_csv('result.csv')
    print(answer)

    os.remove('result.csv')

    print("Done!")


def add_results(links, result):
    for link in links:
        link_href = link.get('href')
        if "url?q=" in link_href and "webcache" not in link_href:
            title = link.find_all('h3')
            if len(title) > 0:
                result.write(title[0].getText().replace(",", "") + ",")  # write title
                result.write(link.get('href').split("?q=")[1].split("&sa=U")[0] + "\n")  # write link
    result.close()


main()
