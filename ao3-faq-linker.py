from bs4 import BeautifulSoup
import json
import re
import requests

faq_links = [
 "https://archiveofourown.org/faq/about-the-archive?language_id=en",
 "https://archiveofourown.org/faq/contacting-the-staff?language_id=en",
 "https://archiveofourown.org/faq/invitations?language_id=en",
 "https://archiveofourown.org/faq/your-account?language_id=en",
 "https://archiveofourown.org/faq/profile?language_id=en",
 "https://archiveofourown.org/faq/pseuds?language_id=en",
 "https://archiveofourown.org/faq/preferences?language_id=en",
 "https://archiveofourown.org/faq/accessing-fanworks?language_id=en",
 "https://archiveofourown.org/faq/downloading-fanworks?language_id=en",
 "https://archiveofourown.org/faq/search-and-browse?language_id=en",
 "https://archiveofourown.org/faq/tags?language_id=en",
 "https://archiveofourown.org/faq/bookmarks?language_id=en",
 "https://archiveofourown.org/faq/comments-and-kudos?language_id=en",
 "https://archiveofourown.org/faq/history-and-mark-for-later?language_id=en",
 "https://archiveofourown.org/faq/subscriptions-and-feeds?language_id=en",
 "https://archiveofourown.org/faq/formatting-content-on-ao3-with-html?language_id=en",
 "https://archiveofourown.org/faq/posting-and-editing?language_id=en",
 "https://archiveofourown.org/faq/tutorial-posting-a-work-on-ao3?language_id=en"
 "https://archiveofourown.org/faq/tutorial-importing-text-based-works?language_id=en",
 "https://archiveofourown.org/faq/series?language_id=en",
 "https://archiveofourown.org/faq/statistics?language_id=en",
 "https://archiveofourown.org/faq/orphaning?language_id=en",
 "https://archiveofourown.org/faq/collections?language_id=en",
 "https://archiveofourown.org/faq/tutorial-creating-a-collection?language_id=en",
 "https://archiveofourown.org/faq/gift-exchange?language_id=en",
 "https://archiveofourown.org/faq/tutorial-running-a-gift-exchange-on-ao3?language_id=en",
 "https://archiveofourown.org/faq/prompt-meme?language_id=en",
 "https://archiveofourown.org/faq/tutorial-running-a-prompt-meme-on-ao3?language_id=en",
 "https://archiveofourown.org/faq/tag-sets?language_id=en",
 "https://archiveofourown.org/faq/skins-and-archive-interface?language_id=en",
 "https://archiveofourown.org/faq/tutorial-creating-a-work-skin?language_id=en",
 "https://archiveofourown.org/faq/unofficial-browser-tools?language_id=en",
 "https://archiveofourown.org/faq/tutorials?language_id=en",
 "https://archiveofourown.org/faq/glossary?language_id=en",
 "https://archiveofourown.org/faq/collections-and-challenges?language_id=en",
]

def extract_questions():
    faqs_map = {}
    for link in faq_links:
        faq_name = re.search('faq\/(.+?)\?', link).group(1)
        faqs_map[faq_name] = {}

        res = requests.get(link)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        faqs = soup.find(id="faq")
        # print(faqs)
        for title in faqs.find_all('h3'):
            faqs_map[faq_name][title.get('id')] = []
            for sibling in title.next_siblings:
                if '<h3 id' not in str(sibling):
                    if "<a " in str(sibling):
                        for child in sibling.children:
                            if "<a " in str(child):
                                try:
                                    link = re.search('href="(.+?)"', str(child)).group(1)
                                except:
                                    print("there are some weird links, sometimes...")
                                    print(str(child))
                                    continue
                                faqs_map[faq_name][title.get('id')].append(link)
                else:
                    break
    with open('questions.json', 'w') as f:
        print(json.dumps(faqs_map), file=f)


def match_question_locations():
    f = open("questions.json", "r")
    questions_links = json.loads(f.read())
    locations_map = {}
    for faq, questions in questions_links.items():
        for question, links in questions.items():
            for link in links:
                if "/faq/" in link and "http" not in link:
                    try:
                        link_parts = link.split("/")
                        locator = link_parts[2]
                        faq_path = locator.split("#")
                        if len(faq_path) > 1:
                            faq_id = faq_path[0]
                            question_id = faq_path[1]
                            if faq not in locations_map:
                                locations_map[faq] = {}
                            if question not in locations_map[faq]:
                                locations_map[faq][question] = []
                            locations_map[faq][question].append(faq_id + "#" + question_id)
                    except Exception as e:
                        print("Error while parsing link " + link)
                        print(str(e))
                        return
    with open('locations.json', 'w') as f:
        print(json.dumps(locations_map), file=f)



# extract_questions()
match_question_locations()