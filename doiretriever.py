## DOI information extraction tool developed by Bingyin Hu
from bs4 import BeautifulSoup
import os
import mechanize
import ast
from datetime import date # for logging the Date of Citation
### This script is used to retrieve meta datas based on the input doi string.
### Different publisher have different meta data format embedded in their sites,
### Based on the publisher, we will determine our way to collect meta datas.
### Some can use only the bs4 package to collect all meta datas we want, while
### some publishers partially support bs4 and others do not.

# can collect all meta datas we need by bs4 package
soup_only = ["wiley", "rsc", "aip", "acs", "aps", "nature",
             "tf", "springer", "sage", "aiaa", "mdpi"] 
txt_only = ["ieee"] # bs4 package down, use the old-fashioned way
soup_txt_mix = ["elsevier"] # some data not retrievable by bs4

# A dictionary for major journals metadata name mapping
wiley    = {"Publication": "citation_journal_title",
            "Title": "citation_title",
            "Author": "citation_author",
            "Keyword": "citation_keywords",
            "Publisher": "citation_publisher",
            "PublicationYear": "citation_publication_date",
            "Volume": "citation_volume",
            "URL": "citation_abstract_html_url",
            "Institution": "citation_author_institution",
            "ISSN": "citation_issn",
            "Issue": "citation_issue"}
rsc      = {"Publication": "citation_journal_title",
            "Title": "citation_title",
            "Author": "citation_author",
            "Publisher": "DC.publisher",
            "PublicationYear": "citation_publication_date",
            "Volume": "citation_volume",
            "URL": "citation_abstract_html_url",
            "Institution": "citation_author_institution",
            "ISSN": "citation_issn",
            "Issue": "citation_issue"}
elsevier = {"Publication": "citation_journal_title",
            "Title": "citation_title",
            "Publisher": "citation_publisher",
            "PublicationYear": "citation_publication_date",
            "Volume": "citation_volume",
            "ISSN": "citation_issn",
            "Issue": "citation_issue"}
aip      = {"Publication": "citation_journal_title",
            "Title": "dc.Title",
            "Author": "dc.Creator",
            "Keyword": "keywords",
            "Publisher": "dc.Publisher",
            "PublicationYear": "dc.Date",
            "Volume": "dc.volume",
            "Issue": "dc.issue"}
acs      = {"Title": "dc.Title",
            "Author": "dc.Creator",
            "Publisher": "dc.Publisher",
##            "PublicationYear": "dc.Date",
            "Keyword": "keywords"}
aps      = {"Publication": "citation_journal_title",
            "Title": "citation_title",
            "Author": "citation_author",
            "Publisher": "citation_publisher",
            "PublicationYear": "citation_date",
            "Volume": "citation_volume",
            "Institution": "citation_author_institution",
            "Issue": "citation_issue"}
nature   = {"Publication": "citation_journal_title",
            "Title": "citation_title",
            "Author": "citation_author",
            "Publisher": "citation_publisher",
            "PublicationYear": "citation_online_date",
            "Volume": "citation_volume",
            "ISSN": "prism.issn",
            "Issue": "citation_issue"}
tf       = {"Publication": "citation_journal_title",
            "Title": "dc.Title",
            "Author": "dc.Creator",
            "Keyword": "keywords",
            "Publisher": "dc.Publisher",
            "PublicationYear": "dc.Date"}
springer = {"Publication": "citation_journal_title",
            "Title": "citation_title",
            "Author": "citation_author",
            "Publisher": "citation_publisher",
            "PublicationYear": "citation_online_date",
            # some springer paper use "citation_cover_date"
            "Volume": "citation_volume",
            "URL": "citation_abstract_html_url",
            "Institution": "citation_author_institution",
            "ISSN": "citation_issn",
            "Issue": "citation_issue"}
sage     = {"Publication": "citation_journal_title",
            "Title": "dc.Title",
            "Author": "dc.Creator",
            "Keyword": "keywords",
            "Publisher": "dc.Publisher",
            "PublicationYear": "dc.Date"}
mdpi     = {"Publication": "citation_journal_title",
            "Title": "citation_title",
            "Author": "dc.creator",
            "Keyword": "dc.subject",
            "Publisher": "citation_publisher",
            "PublicationYear": "citation_date",
            "Volume": "citation_volume",
            "Issue": "citation_issue"}
general  = {"Publication": ["citation_journal_title", "prism.publicationName"],
            "Title": ["citation_title", "DC.Title", "dc.Title", "title"],
            "Author": ["citation_author", "dc.Creator", "DC.Contributor",
                       "dc.creator"],
            "Keyword": ["citation_keywords", "keywords", "dc.subject"],
            "Publisher": ["citation_publisher", "dc.Publisher",
                          "DC.publisher", "dc.publisher"],
            "PublicationYear": ["citation_publication_date",
                                "citation_online_date",
                                "citation_cover_date",
                                "citation_date",
                                "dc.Date", "dc.date",
                                "DC.Date", "prism.publicationDate"],
            "Volume": ["citation_volume", "dc.volume",
                       "DC.Volume", "prism.volume"],
            "Institution": ["citation_author_institution"],
            "ISSN": ["citation_issn", "prism.issn"],
            "Issue": ["citation_issue", "dc.issue",
                      "DC.Issue", "prism.number"]}
################################################################################
# input a string of doi, output the url
def doiToURL(doi):
    assert(type(doi) == str or type(doi) == unicode)
    url = "https://doi.org/" + doi
    # exception for t&f publishing:
    # International Journal of Smart and Nano Materials
    # doi link for this journal doesn't work properly
    if (doi.split("/")[0] == "10.1080"):
        url = "https://www.tandfonline.com/doi/abstract/" + doi
    return url

# determine publisher based on the redirected url
def getPublisher(url):
    assert(type(url) == str)
    # Start with accurate search
    # Wiley
    if ("wiley.com" in url.lower()):
        return "wiley"
    # Elsevier
    if ("sciencedirect.com" in url.lower() or "elsevier.com" in url.lower()):
        return "elsevier"
    # Institute of Electrical and Electronics Engineers (IEEE)
    if ("ieeexplore.ieee.org" in url.lower()):
        return "ieee"
    # American Chemistry Society (ACS)
    if ("pubs.acs.org" in url.lower()):
        return "acs"
    # American Physical Society (APS)
    if ("journals.aps.org" in url.lower()):
        return "aps"
    # American Institute of Physics (AIP)
    if ("aip.scitation.org" in url.lower()):
        return "aip"
    # The Royal Society of Chemistry
    if ("pubs.rsc.org" in url.lower()):
        return "rsc"
    # Nature Publishing Group
    if ("nature.com" in url.lower()):
        return "nature"
    # Taylor and Francis
    if ("tandfonline.com" in url.lower()):
        return "tf"
    # Springer
    if ("link.springer.com" in url.lower()):
        return "springer"
    # Sage
    if ("journals.sagepub.com" in url.lower()):
        return "sage"
    # American Institute of Aeronautics and Astronautics
    if ("arc.aiaa.org" in url.lower()):
        return "aiaa"
    # Molecular Diversity Preservation International
    if ("mdpi.com" in url.lower()):
        return "mdpi"
    
    # Followed by blurry search
    # Wiley
    if ("wiley" in url.lower()):
        return "wiley"
    # Elsevier
    if ("sciencedirect" in url.lower() or "elsevier" in url.lower()):
        return "elsevier"
    # Institute of Electrical and Electronics Engineers (IEEE)
    if ("ieee" in url.lower()):
        return "ieee"
    # American Chemistry Society (ACS)
    if ("acs" in url.lower()):
        return "acs"
    # American Physical Society (APS)
    if ("aps" in url.lower()):
        return "aps"
    # American Institute of Physics (AIP)
    if ("aip" in url.lower()):
        return "aip"
    # The Royal Society of Chemistry
    if ("rsc" in url.lower()):
        return "rsc"
    # Nature Publishing Group
    if ("nature" in url.lower() or "nmat" in url.lower()):
        return "nature"
    # Taylor and Francis
    if ("tandf" in url.lower() or "tf" in url.lower()):
        return "tf"
    # Springer
    if ("springer" in url.lower()):
        return "springer"
    # Sage
    if ("sage" in url.lower()):
        return "sage"
    # American Institute of Aeronautics and Astronautics
    if ("aiaa" in url.lower()):
        return "aiaa"
    # Molecular Diversity Preservation International
    if ("mdpi" in url.lower()):
        return "mdpi"
    
    # unspecified publisher
    return "unknown"

# fetch the redirected url and publisher  
def fetchRdrctURLPub(url):
    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    browser.addheaders = [("User-agent", "Chrome")]
##    browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'), ('Accept', '*/*')]
    fin = browser.open(url)
    newURL = fin.geturl()
    # elsevier's redirection does not take us to the final page
    if ("linkinghub.elsevier.com" in newURL):
        newURL = ("https://www.sciencedirect.com/science/article" +
                  newURL.split("/retrieve")[-1])
                 # I want everything after "/retrieve"
    publisher = getPublisher(newURL)
    browser.close()
    return (newURL, publisher)

def fetchSoupByURL(url):
    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    browser.addheaders = [("User-agent", "Chrome")]
##    browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'), ('Accept', '*/*')]
    fin = browser.open(url)
    soup = BeautifulSoup(fin, 'html5lib')
    browser.close()
    return soup

def fetchTxtByURL(url):
    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    browser.addheaders = [("User-agent", "Chrome")]
##    browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'), ('Accept', '*/*')]
    fin = browser.open(url)
    txt = fin.read()
    browser.close()
    return txt


# collect meta data
def collectMeta(doi, url, publisher):
    assert(type(publisher) == str)
    # Option 1: use bs4 package
    if (publisher in soup_only):
        soup = fetchSoupByURL(url)
        # wiley
        if (publisher == "wiley"):
            outputDict = wileyMeta(soup, doi)
            return outputDict
        # rsc
        if (publisher == "rsc"):
            outputDict = rscMeta(soup, doi)
            return outputDict
        # aip
        if (publisher == "aip"):
            outputDict = aipMeta(soup, doi, url)
            return outputDict
        # acs
        if (publisher == "acs"):
            outputDict = acsMeta(soup, doi, url)
            return outputDict
        # aps
        if (publisher == "aps"):
            outputDict = apsMeta(soup, doi, url)
            return outputDict
        # nature
        if (publisher == "nature"):
            outputDict = natureMeta(soup, doi, url)
            return outputDict
        # tf
        if (publisher == "tf"):
            outputDict = tfMeta(soup, doi, url)
            return outputDict
        # springer
        if (publisher == "springer"):
            outputDict = springerMeta(soup, doi, url)
            return outputDict
        # sage
        if (publisher == "sage"):
            outputDict = sageMeta(soup, doi, url)
            return outputDict
        # aiaa
        if (publisher == "aiaa"):
            outputDict = aiaaMeta(soup, doi, url)
            return outputDict
        # mdpi
        if (publisher == "mdpi"):
            outputDict = mdpiMeta(soup, doi, url)
            return outputDict
    
    # Option 2: partially use bs4 package and old-fashioned txt crawling
    if (publisher in soup_txt_mix):
        soup = fetchSoupByURL(url)
        metas = soup.find_all("meta")
        txt = fetchTxtByURL(url)
        # elsevier
        if (publisher == "elsevier"):
            outputDict = elsevierMeta(soup, txt, doi, url)
            return outputDict

    # Option 3: use txt only
    if (publisher in txt_only):
        txt = fetchTxtByURL(url)
        # ieee
        if (publisher == "ieee"):
            outputDict = ieeeMeta(txt, doi, url)
            return outputDict

    # Option 4: unspecified publisher, use general method
    soup = fetchSoupByURL(url)
    metas = soup.find_all("meta")
    outputDict = generalMeta(soup, doi, url)
    return outputDict

################################################################################
# wiley
def wileyMeta(soup, doi):
    metas = soup.find_all("meta")
    outputDict = makeMetaDict(doi)
    for key in wiley:
        assert(key in outputDict)
        outputDict[key] = getMetaFromSoup(metas, wiley[key])
    return outputDict

# rsc
def rscMeta(soup, doi):
    metas = soup.find_all("meta")
    outputDict = makeMetaDict(doi)
    for key in rsc:
        assert(key in outputDict)
        outputDict[key] = getMetaFromSoup(metas, rsc[key])
    # Switch the first name and last name format
    outputDict["Author"] = nameLastFirst(outputDict["Author"])
    return outputDict

# elsevier
def elsevierMeta(soup, txt, doi, url):
    metas = soup.find_all("meta")
    outputDict = makeMetaDict(doi)

    # Author, Institution, Keyword needs to be obtained from txt
    # Author
    # find first name under tag "span"
    # Example: <span class="text given-name" data-reactid="99">Tao</span>
    author_fname = []
    # find last name under tag "span"
    # Example: <span class="text surname" data-reactid="100">Hu</span>
    author_lname = []
    tagSpans = soup.find_all("span")
    for tagSpan in tagSpans:
        if ("class" in tagSpan.attrs):
            if ("text" in tagSpan["class"] and
                "given-name" in tagSpan["class"]):
                author_fname.append(tagSpan.string)
            if ("text" in tagSpan["class"] and
                "surname" in tagSpan["class"]):
                author_lname.append(tagSpan.string)
    
    # put them into outputDict
    assert(len(author_fname) == len(author_lname))
    for x in xrange(len(author_fname)):
        outputDict["Author"].append(author_fname[x] + " " + author_lname[x])
    # now eliminate duplicate names
    outputDict["Author"] = noDup(outputDict["Author"])

    # Institution
    # to avoid including editor's institution, find institution info after the
    # occurrence of "authors":{"content":[ in txt
    institution = txtDigger(txt, '''{"#name":"textfn","_":''',
                            '''"authors":{"content":[''')
    for x in xrange(len(institution)):
        outputDict["Institution"].append(institution[x])
    # now eliminate duplicate names
    outputDict["Institution"] = noDup(outputDict["Institution"])

    # Keyword
    keyword = txtDigger(txt,
                        '''{"#name":"keyword","$$":[{"#name":"text","_":''', '')
    for x in xrange(len(keyword)):
        outputDict["Keyword"].append(keyword[x])
    # now eliminate duplicate names
    outputDict["Keyword"] = noDup(outputDict["Keyword"])

    # URL is put manually
    outputDict["URL"] = [url]

    # Now let's get whatever we can from soup
    for key in elsevier:
        assert(key in outputDict)
        outputDict[key] = getMetaFromSoup(metas, elsevier[key])

    # Switch the first name and last name format
    outputDict["Author"] = nameLastFirst(outputDict["Author"])
    return outputDict


# aip
def aipMeta(soup, doi, url):
    outputDict = makeMetaDict(doi)
    # Institution needs to be obtained from
    # tag "a" in soup with class="affiliations"
    # Countries of the institutions from tag "span" with class="country"
    # Some cases dc.Creator does not have all the authors, e.g. 10.1063/1.4959771
    # need to be extracted from <a href="/author/
    # Author
    tagAs = soup.find_all("a")
    for tagA in tagAs:
        if ("href" in tagA.attrs):
            if ('''/author/''' in tagA["href"]):
                outputDict["Author"].append(tagA.string.strip())
    # Institution    
    tagSpans = soup.find_all("span")
    institution = getTagStringFromSoup(tagAs, "institution", "class")
    country = getTagStringFromSoup(tagSpans, "country", "class")
    # assemble the insitution and the country into outputDict
    if (len(institution) == len(country)):
        for x in xrange(len(institution)):
            outputDict["Institution"].append(institution[x] + ", " +
                                             country[x])
    if (len(country) == 0):
        for x in xrange(len(institution)):
            outputDict["Institution"].append(institution[x])
    # eliminate duplicates
    outputDict["Institution"] = noDup(outputDict["Institution"])
    
    # URL is put manually
    outputDict["URL"] = [url]

    # Now let's get whatever we can from soup
    metas = soup.find_all("meta")
    for key in aip:
        assert(key in outputDict)
        outputDict[key] += getMetaFromSoup(metas, aip[key])
        outputDict[key] = noDup(outputDict[key])

    # Switch the first name and last name format
    outputDict["Author"] = nameLastFirst(outputDict["Author"])
    
    return outputDict

# acs
def acsMeta(soup, doi, url):
    outputDict = makeMetaDict(doi)
    # Institution, Volume, and Issue need to be obtained
    # from tag "div" and tag "span" in soup
    # Publication year also in tag "span"
    # Publication (Journal) in tag "title"
    # example: <title>Tuning Glass Transition in Polymer Nanocomposites with Functionalized Cellulose Nanocrystals through Nanoconfinement - Nano Letters (ACS Publications)</title>
    tagDivs = soup.find_all("div")
    tagSpans = soup.find_all("span")
    # there should be just one <title>
    tagTitle = soup.find_all("title")[0]
    institution = []
    country = []
    # Publication
    for ele in tagTitle.string.split("-"):
        if ("(ACS Publications)" in ele):
            # we want whatever before "(ACS Publications"
            outputDict["Publication"] = [unicode(ele.split("(ACS")[0].strip())]
    #Volume, and Issue
    for tagDiv in tagDivs:
        if ("id" in tagDiv.attrs):
            if (tagDiv["id"] == "citation"):
                # Volume and Issue
                divCont = tagDiv.contents
                issueNext = False
                for cont in divCont:
                    if (issueNext == True):
                        # issue is always following volume in tagDiv.contents
                        issueStr = cont.string
                        # find the number between the parentheses
                        left = issueStr.index("(") + 1
                        right = issueStr.index(")")
                        outputDict["Issue"] = [issueStr[left:right]]
                        break
                    if ("citation_volume" in str(cont)):
                        outputDict["Volume"] = [cont.string]
                        issueNext = True
                
    # Institution
    for tagDiv in tagDivs:
        if ("class" in tagDiv.attrs):
            if ("affiliations" in str(tagDiv["class"])):
                institution = tagDiv.contents
                break
    # Now we need to loop through institution[] to eliminate whatever between
    # the "<" and ">"for inst in institution:
    for inst in institution:
        instStr = str(inst)
        instStrNew = bracketRemove(instStr, " ") # remove those tags in the brackets
        outputDict["Institution"].append(instStrNew.strip())
    # eliminate duplicates
    outputDict["Institution"] = noDup(outputDict["Institution"])
    # Publication year
    for tagSpan in tagSpans:
        if ("class" in tagSpan.attrs):
            if ("citation_year" in str(tagSpan["class"])):
                outputDict["PublicationYear"] = [tagSpan.string]
                break

    # URL is put manually
    outputDict["URL"] = [url]

    # Now let's get whatever we can from soup
    metas = soup.find_all("meta")
    for key in acs:
        assert(key in outputDict)
        outputDict[key] = getMetaFromSoup(metas, acs[key])
    # acs might put labels with authors' name, need to get rid of them
    for name in xrange(len(outputDict["Author"])):
        trueName = outputDict["Author"][name].split(",")[0]
        # truncate the name until its last char is an alphabet
        while (not trueName[-1].isalpha()):
            trueName = trueName[:-1]
        outputDict["Author"][name] = trueName

    # Switch the first name and last name format
    outputDict["Author"] = nameLastFirst(outputDict["Author"])

    return outputDict
    
# aps
def apsMeta(soup, doi, url):
    outputDict = makeMetaDict(doi)
    # Keyword and ISSN need to be obtained from tag "a" and "p" in soup
    tagAs = soup.find_all("a")
    tagPs = soup.find_all("p")
    # Keyword
    keyword = []
    for tagA in tagAs:
        if ("class" in tagA.attrs):
            if ("physh-concept" in str(tagA["class"])):
                keyword.append(tagA.string)
    outputDict["Keyword"] = noDup(keyword)
    # ISSN
    for tagP in tagPs:
        if ("class" in tagP.attrs):
            if ("legal" in str(tagP["class"])):
                for cont in tagP.contents:
                    if ("ISSN" in cont):
                        # example of cont: 'ISSN 2475-9953 (online). \xa92017 '
                        # 'ISSN 2469-9969 (online), 2469-9950 (print). \xa92017'
                        left = cont.index("ISSN") + len("ISSN") + 1
                        right = cont.index("(online)") - 1
                        outputDict["ISSN"] = [cont[left:right]]
                        break
                break
    # URL is put manually
    outputDict["URL"] = [url]

    # Now let's get whatever we can from soup
    metas = soup.find_all("meta")
    for key in aps:
        assert(key in outputDict)
        outputDict[key] = getMetaFromSoup(metas, aps[key])

    # Switch the first name and last name format
    outputDict["Author"] = nameLastFirst(outputDict["Author"])
    
    return outputDict
    
# nature
def natureMeta(soup, doi, url):
    outputDict = makeMetaDict(doi)
    # Institution need to be obtained from tag "ol" and subtag "li" in soup or
    # tag "h3" in soup
    # Keyword N/A, but can fetch from tag "p" class = "category" and subtag "a"
    tagOls = soup.find_all("ol")
    tagPs = soup.find_all("p")
    tagH3s = soup.find_all("h3")
    # Institution
    for tagOl in tagOls:
        if ("class" in tagOl.attrs):
            if ("decimal" in str(tagOl["class"])):
                for cont in tagOl.contents:
                    outputDict["Institution"].append(cont.string)
    for tagH3 in tagH3s:
        if ("class" in tagH3.attrs):
            if ("emphasis" in str(tagH3["class"])):
                outputDict["Institution"].append(tagH3.text)
    outputDict["Institution"] = noDup(outputDict["Institution"])
    # Keyword
    categories = []
    for tagP in tagPs:
        if ("class" in tagP.attrs):
            if ("category" in str(tagP["class"])):
                categories = tagP.find_all("a")
                break
    for category in categories:
        outputDict["Keyword"].append(category.string)
    outputDict["Keyword"] = noDup(outputDict["Keyword"])
    
    # URL is put manually
    outputDict["URL"] = [url]

    # Now let's get whatever we can from soup
    metas = soup.find_all("meta")
    for key in nature:
        assert(key in outputDict)
        outputDict[key] = getMetaFromSoup(metas, nature[key])

    # Switch the first name and last name format
    outputDict["Author"] = nameLastFirst(outputDict["Author"])
    
    return outputDict

# tf
def tfMeta(soup, doi, url):
    outputDict = makeMetaDict(doi)
    # Institution need to be obtained from tag "span" class="overlay"
    # then use .contents[0], it's always the first content
    tagSpans = soup.find_all("span")
    # Institution
    for tagSpan in tagSpans:
        if ("class" in tagSpan.attrs):
            if (type(tagSpan["class"]) == list):
                if ("overlay" in tagSpan["class"]):
                    outputDict["Institution"].append(tagSpan.contents[0])
            if (type(tagSpan["class"]) == unicode):
                if (tagSpan["class"] == "overlay"):
                    outputDict["Institution"].append(tagSpan.contents[0])
    outputDict["Institution"] = noDup(outputDict["Institution"])
    # Volume and Issue are parsed from <meta property="og:description" ...>
    metas = soup.find_all("meta")
    description = ""
    for meta in metas:
        if ("property" and "content" in meta.attrs):
            if ("og:description" in str(meta)):
                description = meta["content"]
                break
    # some newly posted papers might not have a volume or an issue yet
    if ("Vol." in description):
        volume_left = description.index("Vol.") + len("Vol.")
        volume_right = description.index(",", volume_left)
        outputDict["Volume"] = [description[volume_left:volume_right].strip()]
    if ("No." in description):
        issue_left = description.index("No.") + len("No.")
        issue_right = description.index(",", issue_left)
        outputDict["Issue"] = [description[issue_left:issue_right].strip()]
    
    # URL is put manually
    outputDict["URL"] = [url]

    # Now let's get whatever we can from soup
    metas = soup.find_all("meta")
    for key in tf:
        assert(key in outputDict)
        outputDict[key] = getMetaFromSoup(metas, tf[key])

    # Switch the first name and last name format
    outputDict["Author"] = nameLastFirst(outputDict["Author"])
    
    return outputDict

# springer
def springerMeta(soup, doi, url):
    outputDict = makeMetaDict(doi)
    # URL is put manually
    outputDict["URL"] = [url]

    # Now let's get whatever we can from soup
    metas = soup.find_all("meta")
    for key in springer:
        assert(key in outputDict)
        outputDict[key] = getMetaFromSoup(metas, springer[key])

    if (outputDict["PublicationYear"] == []):
        outputDict["PublicationYear"] = getMetaFromSoup(metas,
                                                        "citation_cover_date")
    # Switch the first name and last name format
    outputDict["Author"] = nameLastFirst(outputDict["Author"])

    return outputDict

# sage
def sageMeta(soup, doi, url):
    outputDict = makeMetaDict(doi)
    # Institution need to be obtained from tag "div" class="artice-info-affiliation"
    # Volume, Issue, and ISSN need to be obtained from tag "span"
    tagDivs = soup.find_all("div")
    tagSpans = soup.find_all("span")
    # Institution
    for tagDiv in tagDivs:
        if ("class" in tagDiv.attrs):
            if ("artice-info-affiliation" in str(tagDiv["class"])):
                outputDict["Institution"].append(tagDiv.contents[-1])
    outputDict["Institution"] = noDup(outputDict["Institution"])
    # Volume and Issue
    for tagSpan in tagSpans:
        if ("class" in tagSpan.attrs):
            if ("volume" in str(tagSpan["class"])):
                outputDict["Volume"].append(tagSpan.string)
            if ("issue" in str(tagSpan["class"])):
                outputDict["Issue"].append(tagSpan.string)
    outputDict["Volume"] = noDup(outputDict["Volume"])
    outputDict["Issue"] = noDup(outputDict["Issue"])
    # ISSN
    count = 0
    for tagSpan in tagSpans:
        if (tagSpan.string is None):
            continue
        if ("ISSN:" in tagSpan.string):
            left = tagSpan.string.index("ISSN:") + len("ISSN:") + 1
            outputDict["ISSN"].append(tagSpan.string[left:])
        
    outputDict["ISSN"] = noDup(outputDict["ISSN"])
    # URL is put manually
    outputDict["URL"] = [url]

    # Now let's get whatever we can from soup
    metas = soup.find_all("meta")
    for key in sage:
        assert(key in outputDict)
        outputDict[key] = getMetaFromSoup(metas, sage[key])

    # Switch the first name and last name format
    outputDict["Author"] = nameLastFirst(outputDict["Author"])
    
    return outputDict

# aiaa
def aiaaMeta(soup, doi, url):
    outputDict = makeMetaDict(doi)
    # Only conference paper in aiaa archive, thus no volume or issue
    # Publisher
    outputDict["Publisher"] = ["American Institute of Aeronautics and Astronautics"]
    # PublicationYear
    # extract from doi: 10.2514/6.2014-0816  10.2514/6.2003-1702
    year = unicode(doi.split("-")[0].split(".")[-1])
    outputDict["PublicationYear"] = [year]
    # Title, Author
    tagSpans = soup.find_all("span")
    for tagSpan in tagSpans:
        if ("class" in tagSpan.attrs):
            if ("title" in tagSpan["class"]):
                outputDict["Title"] = [tagSpan.string.strip()]
            if ("NLM_string-name" in tagSpan["class"]):
                outputDict["Author"].append(tagSpan.string.strip())
    # Institution in tag "aff"
    tagAffs = soup.find_all("aff")
    for tagAff in tagAffs:
        outputDict["Institution"].append(tagAff.string.strip())
    # Publication (Or conference name actually)
    tagDivs = soup.find_all("div")
    for tagDiv in tagDivs:
        if ("id" in tagDiv.attrs):
            if (tagDiv["id"] == "articleContent"):
                outputDict["Publication"] = [tagDiv.a.string.strip()]
                break
    # URL is put manually
    outputDict["URL"] = [url]
    
    for key in outputDict:
        outputDict[key] = noDup(outputDict[key])

    # Switch the first name and last name format
    outputDict["Author"] = nameLastFirst(outputDict["Author"])

    return outputDict  

# mdpi
def mdpiMeta(soup, doi, url):
    outputDict = makeMetaDict(doi)
    # Institution in tag "div" class "affiliation-name" within <div class="art-affiliations">
    # ISSN in tag "span" example: <span>EISSN 2073-4360</span>
    # Institution
    tagDivs = soup.find_all("div")
    for tagDiv in tagDivs:
        if ("class" in tagDiv.attrs):
            if ("art-affiliations" in str(tagDiv["class"])):
                subDivs = tagDiv.find_all("div")
                for subDiv in subDivs:
                    if ("affiliation-name" in str(subDiv["class"])):
                        outputDict["Institution"].append(subDiv.string.strip())
    # ISSN
    tagSpans = soup.find_all("span")
    for tagSpan in tagSpans:
        if (tagSpan.string is not None and "ISSN" in tagSpan.string):
            # get rid of the leading non-integer chars
            myISSN = tagSpan.string
            mychar = myISSN[0]
            while (not mychar.isdigit()):
                myISSN = myISSN[1:]
                mychar = myISSN[0]
            outputDict["ISSN"] = [myISSN]

    # URL is put manually
    outputDict["URL"] = [url]

    # Now let's get whatever we can from soup
    metas = soup.find_all("meta")
    for key in mdpi:
        assert(key in outputDict)
        outputDict[key] = getMetaFromSoup(metas, mdpi[key])
    
    # Switch the first name and last name format
    outputDict["Author"] = nameLastFirst(outputDict["Author"])

    return outputDict

            
# ieee
def ieeeMeta(txt, doi, url):
    outputDict = makeMetaDict(doi)
    # clip the section with meta data by searching "global.document.metadata"
    start = txt.index("global.document.metadata")
    # the section ends with "</script>"
    end = txt.index("</script>", start)
    # clip out
    metas = txt[start:end]

    # IEEE paper could be conference paper that has no volume or issue
    isJournal = False
    isConference = False
    assert('"isJournal"' or '"isConference"' in metas)
    # only journal paper and conference paper are accepted
    assert('"isJournal":true' or '"isConference":true' in metas)
    if ('"isJournal":true' in metas):
        isJournal = True
    elif ('"isConference":true' in metas):
        isConference = True
    
    # Author and Institution
    # author and institution informations start with "authors"
    author_left = metas.index('"authors"')
    if (',"issn"' in metas and ',"isbn"' in metas):
        author_right = min(metas.index(',"issn"', author_left),
                           metas.index(',"isbn"', author_left))
    if (',"issn"' in metas and ',"isbn"' not in metas):
        author_right = metas.index(',"issn"', author_left)
    if (',"issn"' not in metas and ',"isbn"' in metas):
        author_right = metas.index(',"isbn"', author_left)
    author = metas[author_left:author_right]
    # now make it a dictionary using ast package
    authorDict = ast.literal_eval("{" + author + "}")
    for authorSubDict in authorDict["authors"]:
        if ("name" in authorSubDict):
            outputDict["Author"].append(bracketRemove(authorSubDict["name"], ""))
        if ("affiliation" in authorSubDict):
            outputDict["Institution"].append(bracketRemove(authorSubDict["affiliation"], ""))
    outputDict["Institution"] = noDup(outputDict["Institution"])

    # ISSN Example: "issn":[{"format":"Print ISSN","value":"0084-9162"}]
    if ('"issn"' in metas):
        issn_left = metas.index('"issn"')
        issn_right = metas.index("]", issn_left) + 1
        issn = metas[issn_left:issn_right]
        # now make it a dictionary using ast package
        issnDict = ast.literal_eval("{" + issn + "}")
        for issnSubDict in issnDict["issn"]:
            if ("value" in issnSubDict):
                outputDict["ISSN"] = [issnSubDict["value"]]

    # Keyword Example: "keywords":[{"type":"IEEE Keywords","kwd":["Electric breakdown","Conductivity","Nanostructured materials","Conducting materials","Dielectric materials","Dielectrics and electrical insulation","Polyethylene","Magnesium oxide","Dielectric measurements","Volume measurement"]},{"type":"INSPEC: Controlled Indexing","kwd":["power cable insulation","electric breakdown","filled polymers","magnesium compounds","nanocomposites","polyethylene insulation"]},{"type":"INSPEC: Non-Controlled Indexing","kwd":["MgO","DC breakdown strength","conduction current","magnesium oxide-LDPE composite material","filler size","electrical insulation","impulse breakdown strength","low-density polyethylene","McKeown type electrode"]}],"
    if ('"keywords"' in metas):
        keyword_left = metas.index('"keywords"')
        keyword_right = metas.index('],"', keyword_left) + 1
        keyword = metas[keyword_left:keyword_right]
        # now make it a dictionary using ast package
        keywordDict = ast.literal_eval("{" + keyword + "}")
        for keywordSubDict in keywordDict["keywords"]:
            if ("kwd" in keywordSubDict):
                outputDict["Keyword"] += keywordSubDict["kwd"]
        outputDict["Keyword"] = noDup(outputDict["Keyword"])
        for kwd in xrange(len(outputDict["Keyword"])):
            outputDict["Keyword"][kwd] = bracketRemove(outputDict["Keyword"][kwd], "")
        
    # Title Example: "formulaStrippedArticleTitle":"DC Breakdown Strength and Conduction Current of MgO/LDPE Composite Influenced by Filler Size","
    if ('"formulaStrippedArticleTitle"' in metas):
        title_left = metas.index('"formulaStrippedArticleTitle"')
        title_right = metas.index('","', title_left) + 1
        title = metas[title_left:title_right]
        # now make it a dictionary using ast package
        titleDict = ast.literal_eval("{" + title + "}")
        outputDict["Title"] = [bracketRemove(titleDict.values()[0], "")]
    
    # Publication Example: "displayPublicationTitle":"Electrical Insulation and Dielectric Phenomena, 2008. CEIDP 2008. Annual Report Conference on","    
    if ('"displayPublicationTitle"' in metas):
        pub_left = metas.index('"displayPublicationTitle"')
        pub_right = metas.index('","', pub_left) + 1
        pub = metas[pub_left:pub_right]
        # now make it a dictionary using ast package
        pubDict = ast.literal_eval("{" + pub + "}")
        outputDict["Publication"] = pubDict.values()
    
    # Publication Date Example: "publicationDate":"Oct. 2008","
    if ('"publicationDate"' in metas):
        pubDate_left = metas.index('"publicationDate"')
        pubDate_right = metas.index('","', pubDate_left) + 1
        pubDate = metas[pubDate_left:pubDate_right]
        # now make it a dictionary using ast package
        pubDateDict = ast.literal_eval("{" + pubDate + "}")
        outputDict["PublicationYear"] = pubDateDict.values()
    
    # Publisher = "IEEE"
    outputDict["Publisher"] = ["IEEE"]
    
    # Volume, issue Example: "volume":"12","issue":"6",
    if (isJournal == True):
        # volume
        vol_left = metas.index('"volume"')
        vol_right = metas.index('","', vol_left) + 1
        vol = metas[vol_left:vol_right]
        # now make it a dictionary using ast package
        volDict = ast.literal_eval("{" + vol + "}")
        outputDict["Volume"] = volDict.values()
        # issue
        issue_left = metas.index('"issue"')
        issue_right = metas.index('","', issue_left) + 1
        issue = metas[issue_left:issue_right]
        # now make it a dictionary using ast package
        issueDict = ast.literal_eval("{" + issue + "}")
        outputDict["Issue"] = issueDict.values()
        
    # URL is put manually
    outputDict["URL"] = [url]

    # Switch the first name and last name format
    outputDict["Author"] = nameLastFirst(outputDict["Author"])

    return outputDict

# general approach for unspecified publisher
def generalMeta(soup, doi, url):
    outputDict = makeMetaDict(doi)
    # URL is put manually
    outputDict["URL"] = [url]

    # Now let's get whatever we can from soup
    metas = soup.find_all("meta")
    for keys in general:
        assert(keys in outputDict)
        for key in general[keys]: # this case we will try several keys
            outputDict[keys] = getMetaFromSoup(metas, key)
            if (outputDict[keys] != []):
                break
    # Switch the first name and last name format
    outputDict["Author"] = nameLastFirst(outputDict["Author"])

    return outputDict
################################################################################

# Remove whatever between the brackets in myStr
# sep: separator
def bracketRemove(myStr, sep):
    myStrNew = myStr
    if (">" in myStr):
        myStrList = myStr.split(">")
        for x in xrange(len(myStrList)):
            ele = myStrList[x]
            if ("<" in ele):
                if (ele.index("<") == 0 or "/sup" in ele):
                    # if ele starts with "<"
                    # or there's a superscript sign (for author institution mapping)
                    myStrList[x] = ""
                else:
                    myStrList[x] = ele[0 : ele.index("<")]
                    myStrList[x] = myStrList[x].replace("\n", " ")
                    myStrList[x] = myStrList[x].strip()
        myStrNew = sep.join(myStrList) # join str's with the specified separator
    return myStrNew

# to find the value following the given "expression" in "txt" after the
# occurrence of the given str "after"
# For expressions like:
# {"#name":"given-name","_":"A"},{"#name":"surname","_":"Leyland"}
def txtDigger(txt, expression, after):
##    assert (expression in txt)
    if (expression not in txt):
        return []
    if (after != ''):
        # current index of our search
        current = txt.index(after) + len(after)
    else:
        current = 0
    # the thing we are digging
    treasure = []
    # find the index of the last occurrence of the expression
    lastOne = txt.rindex(expression)
    while current < lastOne:
        # start our search from current
        left = txt.index(expression, current) + len(expression)
        # left should be the index of the leading " of the thing we want
        left += 1
        # now left should move to the first letter we want
        right = txt.index('"', left)
        # right should be the index of the finishing "
        # might break if the thing we want has a " in it
        # if that really happens, use } as a finishing sign then -1
        treasure.append(txt[left:right])
        # now update current
        current = left
    return treasure


# find the specified string data within different tags
# in the soup instance created by bs4 package
# e.g. tags: span, a, div using soup.find_all(tags)
#      myID: "country", "affiliation", "institution"
#      pageID: "class", "property"
#      vessel: contains outputs
def getTagStringFromSoup(tags, myID, pageID):
    vessel = []
    for tag in tags:
        if (pageID in tag.attrs):
            if (type(tag[pageID]) == list):
                if (myID in tag[pageID]):
                    vessel.append(tag.string)
            if (type(tag[pageID]) == unicode):
                if (tag[pageID] == myID):
                    vessel.append(tag.string)
    return vessel


# find the meta data in the soup instance created by bs4 package
def getMetaFromSoup(metas, name):
    output = []
    for meta in metas:
        if ("name" in meta.attrs):
            if (meta["name"] == name):
                output.append(bracketRemove(meta["content"].strip(), ""))
    output = noDup(output)
    return output
    
# initialize a dictionary to map all meta datas
# DOI is loaded into the dictionary at the time of creation
def makeMetaDict(doi):
    pairs = [("Publication", []), ("Title", []), ("PublicationYear", []),
             ("Volume", []), ("Issue", []), ("URL", []), ("ISSN", []), 
             ("DOI", [doi]), ("Author", []), ("Institution", []),
             ("Keyword", []), ("Publisher", []), ("DateOfCitation", [])]
    metaDict = dict(pairs) # initialize the dictionary
    return metaDict

# eliminate duplicate in a python list with preserved order
# reference: https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-whilst-preserving-order
def noDup(myList):
    seen = set()
    seen_add = seen.add
    return [x for x in myList if not (x in seen or seen_add(x))]

# extract year from date
def yearFromDate(date):
    date = str(date)
    alleles = [] # container
    # first split by white space
    eles = date.split(" ")
    # then split by "/" and "-"
    for ele in eles:
        alleles += ele.split("/")
        alleles += ele.split("-")
    for ele in alleles:
        if (ele.isdigit() and int(ele) > 1800):
            return unicode(ele)
    return "Year extraction failed"

# convert all author names into Last name, First name sequence
def nameLastFirst(nameList):
    for seq in xrange(len(nameList)):
        name = nameList[seq]
        lastName = name.split(" ")[-1].strip()
        firstName = name[:len(name)-len(lastName)].strip()
        nameList[seq] = lastName + ", " + firstName
    return nameList

# main function, input doi string, output meta data in a dictionary
def mainDOI(doi):
    url = doiToURL(doi)
    (url, publisher) = fetchRdrctURLPub(url)
    txt = fetchTxtByURL(url)
    myDict = collectMeta(doi, url, publisher)
    myDict["DateOfCitation"].append(date.today().isoformat())
    # extract year from date
    if (myDict["PublicationYear"] != []):
        myDict["PublicationYear"] = [yearFromDate(myDict["PublicationYear"][0])]
##    for key in myDict:
##        print key + " : " + str(myDict[key])
##        print "==============================================="
    return myDict

if __name__ == "__main__":
##    testDOI = "10.1002/adfm.200700200" # wiley test 1 PASS
##    testDOI = "10.1002/adma.200401816"
##    testDOI = "10.1016/j.polymer.2014.12.002"
##    testDOI = "10.1002/1097-4628(20001220)78:13<2272::AID-APP50>3.0.CO;2-U"
##    testDOI = "10.1039/C5CS00258C" # rsc test PASS
##    testDOI = "10.1016/j.compositesa.2004.12.010" # elsevier test PASS
##    testDOI = "10.1063/1.4892695" # aip test 1 PASS
##    testDOI = "10.1063/1.4994293" # aip test 2, multiple institutions, PASS
##    testDOI = "10.1021/ja963361g" # acs test 1, PASS
##    testDOI = "10.1021/acs.macromol.5b01573" # acs test 2, macromol, multiple institutions, PASS
##    testDOI = "10.1021/acsmacrolett.7b00603" # acs test 3, macrolett
##    testDOI = "10.1103/PhysRevMaterials.1.043606" # aps test 1 PASS
##    testDOI = "10.1103/PhysRevB.96.104426" # aps test 2 PASS
##    testDOI = "10.1038/nmat1107" # nature test 1
##    testDOI = "10.1109/CEIDP.2008.4772933" # ieee test 1 PASS
##    testDOI = "10.1109/TNANO.2013.2285438" # ieee test 2 PASS
##    testDOI = "10.1080/19475411.2016.1269027" # tf test 1 PASS
##    testDOI = "10.1080/19475411.2017.1377312" # tf test 2, a new paper without volume or issue yet PASS
##    testDOI = "10.1177/0021998316644846" # sage test 1 PASS
##    testDOI = "10.1177/0021998316644847" # sage test 2 PASS
##    testDOI = "10.1063/1.4960137"
    testDOI = "10.1038/nnano.2008.96"
    testDict = mainDOI(testDOI)
    for key in testDict:
        print key + " : " + str(testDict[key])
        print "==============================================="