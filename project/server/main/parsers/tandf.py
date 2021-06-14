from project.server.main.parsers.strings import get_orcid, get_clean_text

def parse_tandf(soup, doi):
    res = {"doi": doi}
    res.update(parse_abstract(soup))
    res.update(parse_authors(soup))
    return res

def parse_authors(soup):
    res = {}
    authors, affiliations = [], []
    authors_soup = soup.find_all(class_="entryAuthor")
    if authors_soup:
        for author_soup in authors_soup:
            author = {}
            current_affiliations = []
            author["full_name"] = author_soup.contents[0].strip()
            orcid = author_soup.find("span", attrs={'class' : "orcid-author"})
            if orcid and orcid.get("data"):
                author["orcid"] = get_orcid(orcid.get("data"))
            email = author_soup.find("span", attrs={'data-mailto' : True})
            if email:
                author["email"] = get_clean_text(email)
                author["corresponding"] = True
            affiliation = author_soup.find("span", class_="overlay")
            if affiliation and len(affiliation.contents) > 0:
                affs = affiliation.contents[0].split(';')
                if affs:
                    for a in affs:
                        current_aff = {"name": a.strip()}
                        current_affiliations.append(current_aff)
                        if current_aff not in affiliations:
                            affiliations.append(current_aff)
                if current_affiliations:
                    author["affiliations"] = current_affiliations
            if author:
                authors.append(author)
    
    for ix, a in enumerate(authors):
        a['author_position'] = ix+1
    
    if authors:
        res = {"authors": authors}
    if affiliations:
        res = {"affiliations": affiliations}
    return res

def parse_abstract(soup):
    res = {}
    abstract_soup = soup.find(class_="abstractSection")
    if abstract_soup:
        abstract = get_clean_text(abstract_soup)
        if abstract:
            res["abstracts"] = [ {"abstract": abstract} ]
    return res
