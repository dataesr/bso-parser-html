import re, bs4
from project.server.main.parsers.strings import get_clean_text, get_text_obj, get_orcid


# doi 10.1103
def parse_aps(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    return res

def parse_authors(soup):
    res = {}
    affiliations_dict = {}
    for elt in soup.find_all(class_='authors'):
        for aff_elt in elt.find_all('li'):
            aff_id = get_text_obj(aff_elt, 'sup')
            _ = [e.extract() for e in aff_elt.find_all('sup')]
            aff_name = get_clean_text(aff_elt)
            affiliations_dict[aff_id] = {'name': aff_name}
    affiliations = list(affiliations_dict.values())
    if affiliations:
        res["affiliations"] = affiliations

    authors_elem = None
    for elem in soup.find_all(class_='authors'):
        first_author_elem = elem.find("a", href = re.compile(r'.*/author/.*'))
        if first_author_elem:
            authors_elem = first_author_elem.parent
            break

    if authors_elem is None:
        return res

    authors = []
    none_authors_has_affiliation = True
    author = None
    for tag in authors_elem.find_all():
        if 'href' in tag.attrs and "/author/" in tag.attrs['href']:
            # include the previous author if not empty
            if author:
                authors.append(author)
            author = {"full_name": get_clean_text(tag)}
            current_affiliations = []
        if 'href' in tag.attrs and "/orcid.org/" in tag.attrs['href']:
            author['orcid'] = get_orcid(tag.attrs['href'])
        if tag.name == "sup":
            for aff_id in get_clean_text(tag).split(','):
                if aff_id in affiliations_dict:
                    if '@' not in affiliations_dict[aff_id]['name']:
                        current_affiliations.append(affiliations_dict[aff_id])
                    else:
                        author['email'] = affiliations_dict[aff_id]['name'].lower().replace("corresponding author","")
                        author['corresponding'] = True
            if current_affiliations:
                author['affiliations'] = current_affiliations
                none_authors_has_affiliation = False
    # include the last author
    if author and author not in authors:
        authors.append(author)

    if none_authors_has_affiliation and affiliations:
        for a in authors:
            a['affiliations'] = affiliations

    for ix, a in enumerate(authors):
        a['author_position'] = ix+1

    if authors:
        res["authors"] = authors

    return res

def parse_abstract(soup):
    res = {}
    abstract_elem = soup.find(class_="abstract")
    if abstract_elem:

        # abstract
        abstract_text_elem = abstract_elem.find('p')
        if abstract_text_elem:
            res['abstract'] = [{'abstract': get_clean_text(abstract_text_elem)}]

        # images
        images = []
        for e in abstract_elem.find_all('img'):
            if 'src' in e.attrs:
                images.append({"url": "https://journals.aps.org"+e.attrs['src'].replace('thumbnail', 'medium')})
        if images:
            res['images'] = images

        # classifications
        classifications = []
        for d in soup.find_all(class_ = "physh-discipline"):
            classifications.append({"reference": "physh-discipline", "label": get_clean_text(d)})
        for d in soup.find_all(class_ = "physh-concept"):
            classifications.append({"reference": "physh-concept", "label": get_clean_text(d)})
        if classifications:
            res["classifications"] = classifications

    return res

