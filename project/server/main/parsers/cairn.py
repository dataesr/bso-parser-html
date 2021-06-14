import re, bs4
from project.server.main.parsers.strings import get_clean_text, get_doi, get_text_class, normalize_text


# doi 10.3917
def parse_cairn(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    res.update(parse_text(soup))
    res.update(parse_references(soup))
    return res

def parse_authors(soup):
    authors = []
    affiliations = []

    author_elts = soup.find_all(class_="auteur")
    for author_elt in author_elts:
        author = {}
        _ = [e.extract() for e in author_elt.find_all(class_="renvoi")]

        elem = get_text_class(author_elt, "prenom")
        if elem:
            author['first_name'] = elem

        elem = get_text_class(author_elt, "nomfamille")
        if elem:
            author['last_name'] = elem

        elem = get_text_class(author_elt, "nompers")
        if elem:
            author['full_name'] = elem

        elem = get_text_class(author_elt, "affiliation")
        if elem:
            current_affiliation = {'name': elem}
            if current_affiliation not in affiliations:
                affiliations.append(current_affiliation)
            author['affiliations'] = [current_affiliation]
        elem = get_text_class(author_elt, "wrapper-note")
        if elem:
            current_affiliation = {'name': elem}
            if current_affiliation not in affiliations:
                affiliations.append(current_affiliation)
            author['affiliations'] = [current_affiliation]

        elem = get_text_class(author_elt, "courriel")
        if elem:
            author['email'] = elem.replace('.at.', '@').replace("Courriel :", "").replace("<", "").replace(">", "").strip()
            author['corresponding'] = True

        if len(author)>0:
            authors.append(author)

    for ix, a in enumerate(authors):
        a['author_position'] = ix+1

    return {"authors": authors, "affiliations": affiliations}

def parse_references(soup):
    res = {}
    references = []
    for w in soup.find_all(class_ = "refbiblio"):
        ref = {}
        link_elem = w.find('a')
        if link_elem and 'href' in link_elem.attrs:
            link = link_elem.attrs['href']
            ref['link']=link
            remove = [e.extract() for e in w.find_all("a")]
            if 'doi' in link:
                ref['doi'] = get_doi(link)
        ref['reference'] = get_clean_text(w)
        references.append(ref)

    if len(references) > 0:
        res.update({"references": references})
    return res

def parse_abstract(soup):
    res = {}
    abstracts = []
    jels = []
    keywords = []

    abstract_elts = soup.find_all(class_="resume")
    for abstract_elt in abstract_elts:
        abstract = {}
        lang = normalize_text(get_text_class(abstract_elt, "locale-name"))[0:2]
        abstract['lang'] = lang
        elem = get_text_class(abstract_elt, "corps")
        if elem and "abstract on Cairn International Edition" not in elem:
            abstract['abstract'] = elem

        #abstract['marquage'] = get_text_class(abstract_elt, "marquage")
        if abstract.get('abstract') and "Classification JEL" in abstract['abstract']:
            tmp = re.sub(".*Classification JEL(.*)","\g<1>", abstract['abstract'] ).replace(':','').strip()
            for j in tmp.split(','):
                jel = j.replace('.', '').strip()
                if len(jel) == 0:
                    continue
                current_jel = {'reference': 'JEL', 'code': jel}
                if current_jel not in jels:
                    jels.append(current_jel)
        if len(abstract)>0:
            abstracts.append(abstract)

        keywords += [{'lang': lang,
               'keyword': get_clean_text(w)
              } for w in abstract_elt.find_all(class_ = "motcle")]

    if len(abstracts) > 0:
        res.update({'abstract': abstracts})

    if len(jels) > 0:
        res.update({"classifications": jels})

    if len(keywords) > 0:
        res.update({"keywords": keywords})

    return res

def parse_text(soup):
    res = {}
    elem = get_text_class(soup, "premieres-lignes")
    if elem:
         res.update({'incipit': elem})

    elem = soup.find("div", {"id": "article-texte"})
    if elem:
         res.update({'presentation': get_clean_text(elem)})

    return res
