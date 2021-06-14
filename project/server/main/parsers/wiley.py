import json
from project.server.main.parsers.strings import get_orcid, get_clean_text, normalize_text, keep_digits, remove_punction


# doi 10.1002, 10.1111, 10.1142
def parse_wiley(soup, doi):
    res = {"doi": doi}
    res.update(parse_abstract(soup))
    res.update(parse_figures(soup))
    res.update(parse_keywords(soup))
    res.update(parse_fundings(soup))
    res.update(parse_authors(soup))
    res.update(parse_script(soup))
    return res

def parse_authors(soup):
    res = {}
    authors = []
    affiliations = []
    institution_soup = soup.find_all(attrs={"name": "citation_author_institution"})
    all_aff = []
    if institution_soup:
        affiliations = [{'name': a.get("content")} for a in institution_soup]
        all_aff = [normalize_text(remove_punction(a.get("content"))) for a in institution_soup]
    for author in soup.find_all(class_="accordion-tabbed__tab-mobile"):
        a = author.find(class_="author-name")
        if a and a.get("data-id", "am-no-id")[0:2] != "am":
            doc = {}
            doc["full_name"] = get_clean_text(author.find("a"))
            doc["affiliations"] = []
            info = author.find(class_="author-info")
            if info:
                for aff in info.find_all("a"):
                    if aff and aff.get("href", "").startswith("mailto"):
                        doc["email"] = get_clean_text(aff)
                        doc["cooresponding"] = True
                    if aff and "orcid" in aff.get("href", ""):
                        doc["orcid"] = get_orcid(get_clean_text(aff['href']))
                for aff in info.find_all("p"):
                    if aff and normalize_text(remove_punction(get_clean_text(aff))) in all_aff:
                        doc["affiliations"].append({"name": get_clean_text(aff)})
                    elif aff and not all_aff:
                        current_aff = get_clean_text(aff)
                        skip = False
                        for f in ['by this author', 'e-mail', 'corresponding']:
                            if f in current_aff.lower():
                                skip = True
                        if len(current_aff) < 2:
                            skip = True
                        if not skip:
                            current_aff_doc = {'name': get_clean_text(aff)}
                            doc["affiliations"].append(current_aff_doc)
                            if current_aff_doc not in affiliations:
                                affiliations.append(current_aff_doc)
            authors.append(doc)
    if affiliations:
        res["affiliations"] = affiliations
    
    for ix, a in enumerate(authors):
        a['author_position'] = ix+1
    
    if authors:
        res["authors"] = authors
    return res

def parse_figures(soup):
    res = {}
    figs = []

    for resume_elem in soup.find_all(class_="article-section__abstract"):
        elems = resume_elem.find_all("figure")
        for f in elems:
            if f.find("img") and 'src' in f.find("img")['attrs']:
                figs.append({'url': "https://onlinelibrary.wiley.com" + f.find("img").get("src")})
    if figs:
        res["images"] = figs
    return res

def parse_abstract(soup):
    res = {}
    abstracts = []
    for resume_elem in soup.find_all(class_="article-section__abstract"):
        lang = resume_elem.get("data-lang") or resume_elem.get("lang")
        abstract = {
            "abstract": get_clean_text(resume_elem.find(class_="article-section__content"))
        }
        if lang:
            abstract['lang'] = lang
        abstracts.append(abstract)
    if abstracts:
        res["abstract"] = abstracts
    return res

def parse_keywords(soup):
    res = {}
    keywords = []
    kw = soup.find(class_="keywords")
    if kw:
        for keyword in kw.find_all("li"):
            if keyword:
                keywords.append({"keyword": get_clean_text(keyword)})
    if keywords:
        res["keywords"] = keywords
    return res

def parse_fundings(soup):
    res = {}
    fundings = []
    fund = soup.find(class_="funding-information")
    if fund:
        for f in fund.find_all("li"):
            fundings.append({ "funding": get_clean_text(f) })
    if fundings:
        res["fundings"] = fundings
    return res

def parse_script(soup):
    res = {}
    script = soup.find(attrs={"id": "analyticDigitalData"})
    try:
        data = json.loads(script.get_text().split("=")[1])
        item_topics = data.get("publication", {}).get("item", {}).get("topics")
        topics = [{"label": t.get("topicLabel"), "code": t.get("topicUri"), "reference": "WileyGlobalSubjectCodes"} for t in item_topics if t.get("taxonomyUri") == "global-subject-codes"]
        if topics:
            res["classifications"] = topics
    except:
        return res
    return res
