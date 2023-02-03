# AO3 FAQs Linker

## What it does

This script gathers all questions in the AO3 FAQs that are mentioned in other AO3 FAQs and for each one
list the exact questions where it gets referenced. It displays the result as an HTML list.

## Usage

- Build the python docker container: `docker-compose -f -docker-compose.yml up`
- Enter the container: `docker exec -it ao3-scripts bash`
- Check that the list of FAQs links in ao3-faq-linker.py is up to date
- Run the script: `python3 ao3-faq-linker.py`
- open the generated `list.html` file

This script is composed of three parts. Each can run separately, though they need to run in order as each depends on the previous.
- `python3 ao3-faq-linker.py "extract"` parses the HTML of each FAQ page to extract all the questions and the links they contain
- `python3 ao3-faq-linker.py "match"` takes the included links and matches them to the question they link to 
- `python3 ao3-faq-linker.py "buildHtml"` takes the matched questions and displays them in a more readable html file