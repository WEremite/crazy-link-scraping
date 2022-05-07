import click
import pandas
import time
from bs4 import BeautifulSoup
from bs4.element import Tag
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.edge.service import Service


@click.command()
@click.option('-s', '--search', "user_query", default='World', help="User's search query")
@click.option('-b', '--browser', "browser", default='Chrome', help="Browser to use")
@click.option('-o', '--output', "output", default='not', help="File to save the results")
def main(user_query, browser, output):
    print(f"Searching for {user_query} in {browser}...")

    driver = Browser(browser).get_driver()

    driver.get("https://www.google.com")

    search_bar = driver.find_element(by="name", value="q")
    search_bar.clear()
    search_bar.send_keys(user_query)
    search_bar.send_keys(Keys.RETURN)

    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    result_div = soup.find_all('div', attrs={'class': 'g'})

    links = []
    titles = []

    for result in result_div:
        link = result.find('a', href=True)
        title = result.find('h3')

        if isinstance(title, Tag):
            title = title.get_text()

        if link != '' and link['href'][0] != "/" and title != '':
            links.append(link['href'])
            titles.append(title)

    my_file = Path(output)

    if my_file.exists():
        to_file(links, titles, my_file)
    else:
        to_console(links, titles)


def to_console(links, titles):
    for (link, title) in zip(links[:10], titles):
        print(f"{title} \n - {link} \n ------------------------------")


def to_file(links, titles, my_file):
    df = pandas.DataFrame({"Title": titles[:10], "Link": links[:10]})
    df.to_csv(my_file, index=False)

    print(pandas.read_csv(my_file))


class Browser:
    def __init__(self, browser):
        self.driver = None
        self.browser = browser.capitalize()
        
        self.set_driver()

    def set_driver(self):
        if self.browser == "Firefox":
            s = Service("./drivers/geckodriver")
            self.driver = webdriver.Firefox(service=s)
        elif self.browser == "Edge":
            s = Service("./drivers/msedgedriver")
            self.driver = webdriver.Edge(service=s)
        else:
            s = Service("./drivers/chromedriver")
            self.driver = webdriver.Chrome(service=s)

    def get_driver(self):
        return self.driver


main()
