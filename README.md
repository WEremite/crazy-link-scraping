# Crazy Link Scraping

Console program which takes user's query, searches for links and returns results of ten links with titles.

To install dependencies use command:

1. Install virtual environment: <br />
```
pip install virtualenv
```
2. Create new environment: <br />
```
virtualenv <name_your_environment>
```
3. Activate the new environment: <br />
```
source <name_your_environment>/bin/activate
```
4. Install the requirements in the current environment: <br />
```
pip install -r requirements.txt
```
5. To use program:

```
python3 search.py -s "your query" -b "browser name" -o "output file name"
```
```-s``` - user's searching query. This parameter is <b>mandatory!</b> <br />

```-b``` - browser name:<br />
* "Chrome" - for Chrome browser <br />
* "Firefox" - for Firefox browser <br />
* "Edge" - for Edge browser <br />

Default value is "Chrome". This parameter is optional. <br />

```-o``` - path to <b>.csv</b> file for saving search result. For example: "/dir/dir2/result.csv" If file doesn't exit result will be shown in terminal. This parameter is optional. <br />