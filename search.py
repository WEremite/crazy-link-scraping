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

    Output(user_query, output)


class Output:
    def __init__(self, user_query, output):
        self.output_file = Path(output)
        self.result = Results(user_query, output).get_results()
        self.links = self.result[0]
        self.titles = self.result[1]

        if self.output_file.exists():
            self.to_file()
        else:
            self.to_console()

    def to_file(self):
        df = pandas.DataFrame({"Title": self.titles[:10], "Link": self.links[:10]})
        df.to_csv(self.output_file, index=False)

        print(pandas.read_csv(self.output_file))

    def to_console(self):
        for (link, title) in zip(self.links[:10], self.titles):
            print(f"{title} \n - {link} \n ------------------------------")


class Results:
    def __init__(self, user_query, output):
        self.result_div = Search(user_query, output).get_div()
        self.links = []
        self.titles = []

        self.save_results()

    def save_results(self):
        for result in self.result_div:
            link = result.find('a', href=True)
            title = result.find('h3')

            if isinstance(title, Tag):
                title = title.get_text()

            if link != '' and link['href'][0] != "/" and title != '':
                self.links.append(link['href'])
                self.titles.append(title)

    def get_results(self):
        return self.links, self.titles


class Search:
    def __init__(self, user_query, browser):
        self.user_query = user_query
        self.driver = Browser(browser).get_driver()
        self.result_div = None

        self.searching()

    def searching(self):
        self.driver.get("https://www.google.com")

        search_bar = self.driver.find_element(by="name", value="q")
        search_bar.clear()
        search_bar.send_keys(self.user_query)
        search_bar.send_keys(Keys.RETURN)

        time.sleep(3)

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        self.result_div = soup.find_all('div', attrs={'class': 'g'})

    def get_div(self):
        return self.result_div


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


if __name__ == "__main__":
    main()
