import requests
from bs4 import BeautifulSoup
import os
import click


@click.command()
@click.option('-s', '--search', "user_query", default='World', help="User's search query")
@click.option('-b', '--browser', "browser", default='Chrome', help="Browser to use")
def main(user_query, browser):
    print(f"Searching for {user_query} in {browser}...")

    replace_whitespace = user_query.replace(' ', '+')
    number_of_search_results = 10
    url = f"https://www.google.com/search?q={replace_whitespace}&num={number_of_search_results}"

    requests_results = requests.get(url)
    soup_link = BeautifulSoup(requests_results.content, "html.parser")
    links = soup_link.find_all("a")

    result = open("results.txt", "w")

    print("Pushing results in file -> results.txt...")

    for link in links:
        link_href = link.get('href')
        if "url?q=" in link_href and "webcache" not in link_href:
            title = link.find_all('h3')
            if len(title) > 0:
                result.write(title[0].getText() + "\n")  # write title
                result.write(link.get('href').split("?q=")[1].split("&sa=U")[0] + "\n\n")  # write link

    result.close()

    if os.path.getsize("results.txt") == 0:
        print("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    print("Done!")


main()
