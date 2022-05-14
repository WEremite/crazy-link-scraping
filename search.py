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
import mysql.connector
from mysql.connector import Error
import credential


@click.command()
@click.option('-s', '--search', "user_query", default='World', help="User's search query")
@click.option('-b', '--browser', "browser", default='Chrome', help="Browser to use")
@click.option('-o', '--output', "output", default='not', help="File to save the results")
def main(user_query, browser, output):
    Database().create_database()

    Query(QueryCommand().clear_table()).execute_query()

    print(f"Searching for {user_query} in {browser}...")

    Output(user_query, output)


class Connection:
    host_name = 'localhost'
    user_name = 'root'
    user_password = credential.password

    def create_server_connection(self):
        connection = None
        try:
            connection = mysql.connector.connect(
                host=self.host_name,
                user=self.user_name,
                passwd=self.user_password
            )
            print("MySQL Database connection successful")
        except Error as err:
            print(f"Error: '{err}'")

        return connection


class Database(Connection):
    def __init__(self):
        super().__init__()
        self.host_name = Connection.host_name
        self.user_name = Connection.user_name
        self.user_password = Connection.user_password
        self.query = "CREATE DATABASE search_result_db"
        self.db_name = 'search_result_db'
        self.connection = Connection().create_server_connection()

    def create_database(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute(self.query)
            print("Database created successfully")
        except Error as err:
            print(f"Error: '{err}'")

    def create_database_connection(self):
        connection = None
        try:
            connection = mysql.connector.connect(
                host=self.host_name,
                user=self.user_name,
                passwd=self.user_password,
                database=self.db_name
            )
            print("MySQL Database connection successful")
        except Error as err:
            print(f"Error: '{err}'")

        return connection


class Query:
    def __init__(self, query):
        self.query = query
        self.connection = Database().create_database_connection()

    def execute_query(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute(self.query)
            self.connection.commit()
            print("Query successful")
        except Error as err:
            print(f"Error: '{err}'")

    def read_query(self):
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute(self.query)
            result = cursor.fetchall()
            return result
        except Error as err:
            print(f"Error: '{err}'")


class QueryCommand:
    def create_table(self):
        create_result_table = """
        CREATE TABLE result (
            `id` INT NOT NULL AUTO_INCREMENT,
            `title` VARCHAR(255) NOT NULL,
            `link` VARCHAR(255) NOT NULL,
            PRIMARY KEY (id)
        );
        """
        return create_result_table

    def insert_query(self, title, link):
        insert_result = f"""
         INSERT INTO result (title, link)
            VALUES ("{title}", "{link}");
         """
        return insert_result

    def select_query(self):
        select_result = "SELECT * FROM result"
        return select_result

    def clear_table(self):
        clear_table = "TRUNCATE TABLE result"
        return clear_table


class Output(Connection):
    def __init__(self, user_query, output):
        super().__init__()
        self.output_file = Path(output)
        self.result = Results(user_query, output).get_results()
        self.links = self.result[0]
        self.titles = self.result[1]
        self.host_name = Connection.host_name
        self.user_name = Connection.user_name
        self.user_password = Connection.user_password

        if self.output_file.exists():
            self.to_file()
        else:
            self.to_db()

    def to_file(self):
        df = pandas.DataFrame({"Title": self.titles[:10], "Link": self.links[:10]})
        df.to_csv(self.output_file, index=False)

        print(pandas.read_csv(self.output_file))

    def to_db(self):
        Query(QueryCommand().clear_table()).execute_query()
        for (link, title) in zip(self.links[:10], self.titles):
            Query(QueryCommand().insert_query(title, link)).execute_query()

        results = Query(QueryCommand().select_query()).read_query()
        from_db = []

        for result in results:
            result = list(result)
            from_db.append(result)

        columns = ['id', 'title', 'link']
        df = pandas.DataFrame(from_db, columns=columns)
        print(df)


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
