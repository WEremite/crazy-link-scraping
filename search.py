import click
import pandas
import time
from bs4 import BeautifulSoup
from bs4.element import Tag
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


@click.command()
@click.option('-s', '--search', "user_query", default='World', help="User's search query")
@click.option('-b', '--browser', "browser", default='Chrome', help="Browser to use")
@click.option('-o', '--output', "output", default='not', help="File to save the results")
def main(user_query, browser, output):
    print(f"Searching for {user_query} in {browser}...")
    if browser.capitalize() == 'Firefox':
        firefox_capabilities = DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = False
        driver = webdriver.Firefox(executable_path="./drivers/geckodriver")
    elif browser.capitalize() == 'Edge':
        driver = webdriver.Edge(executable_path="./drivers/msedgedriver")
    else:
        driver = webdriver.Chrome(executable_path="./drivers/chromedriver")

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


main()
