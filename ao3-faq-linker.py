import asyncio, json, re, requests, sys
from airium import Airium
from bs4 import BeautifulSoup

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

# loop through all FAQ html pages and extract all questions from their h3 tags
# with their names and the links they contain -> we'll use these to determine
# whether a question is featured anywhere else
def extract_questions():
    faqs_map = {}
    for link in faq_links:
        faq_name = re.search('faq\/(.+?)\?', link).group(1)
        print("parsing " + faq_name)
        faqs_map[faq_name] = {}

        res = requests.get(link)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        faqs = soup.find(id="faq")
        for question_title in faqs.find_all('h3'):
            faqs_map[faq_name][question_title.get('id')] = {}
            faqs_map[faq_name][question_title.get('id')]['title'] = question_title.text.strip()
            faqs_map[faq_name][question_title.get('id')]['links'] = []
            #the FAQs are all made of sibling elements, so we start crawling them and stop at the next title
            for sibling in question_title.next_siblings:
                if '<h3 id' not in str(sibling):
                    if "<a " in str(sibling):
                        for child in sibling.children:
                            if "<a " in str(child):
                                try:
                                    link = re.search('href="(.+?)"', str(child)).group(1)
                                except:
                                    print("weird link found: " + str(child))
                                    continue
                                faqs_map[faq_name][question_title.get('id')]['links'].append(link)
                else:
                    break
    with open('questions.json', 'w') as f:
        print(json.dumps(faqs_map), file=f)

# aggregate questions data to figure out which questions are mentioned where
def match_question_locations():
    f = open("questions.json", "r")
    questions_map = json.loads(f.read())
    locations_map = {}
    for container_faq_slug, questions in questions_map.items():
        for container_question_id, links in questions.items():
            for link in links['links']:
                if "/faq/" in link:
                    if "http" in link:
                        link = link.split(".org")[1]
                    try:
                        path = link.split("/")
                        included_question_coordinates = path[2]
                        coordinates_list = included_question_coordinates.split("#")
                        if len(coordinates_list) > 1:
                            included_faq_id = coordinates_list[0]
                            included_question_id = coordinates_list[1]
                            if included_faq_id not in locations_map:
                                locations_map[included_faq_id] = {}
                            if included_question_id not in locations_map[included_faq_id]:
                                locations_map[included_faq_id][included_question_id] = []
                            locations_map[included_faq_id][included_question_id].append({"faq_id": container_faq_slug, "question_id": container_question_id})
                    except Exception as e:
                        print("Error while parsing link " + link)
                        return

                if link.startswith("#"):
                    # these links are anchors, referencing their own same FAQs set
                    included_question_id = link.replace("#", "")
                    if container_faq_slug not in locations_map:
                        locations_map[container_faq_slug] = {}
                    if link not in locations_map[container_faq_slug]:
                        locations_map[container_faq_slug][included_question_id] = []
                    locations_map[container_faq_slug][included_question_id].append({"faq_id": container_faq_slug, "question_id": container_question_id})

    with open('locations.json', 'w') as f:
        print(json.dumps(locations_map), file=f)

# build a simple HTML output page to visualize the matched questions
def build_html():
    f = open("locations.json", "r")
    locations = json.loads(f.read())
    f = open("questions.json", "r")
    questions_links = json.loads(f.read())

    a = Airium()
    a('<!DOCTYPE html>')
    with a.html(lang="pl"):
        with a.head():
            a.meta(charset="utf-8")
            a.title(_t="AO3 FAQs matcher")
        with a.body():
            for faq_id, questions in locations.items():
                with a.ul():
                    with a.li():
                        a(faq_id)
                    for question_id, locations in questions.items():
                        with a.ul():
                            with a.li():
                                try:
                                    a(questions_links[faq_id][question_id]["title"])
                                except Exception as e:
                                    print("Error while retrieving question with id '" + question_id + "' in faq '" + faq_id)
                            for location in locations:
                                with a.ul():
                                    with a.li():
                                        a(questions_links[location['faq_id']][location['question_id']]["title"] + ' (' + location['faq_id'] + ')')
    html = str(a) # casting to string extracts the value
    with open('list.html', 'w') as f:
        print(html, file=f)

async def main():
    await extract_questions()
    match_question_locations()
    build_html()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        asyncio.run(main())
    else:
        operation = sys.argv[1]
        match operation:
            case "extract":
                extract_questions()
            case "match":
                match_question_locations()
            case "buildHtml":
                build_html()