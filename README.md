# DOI meta-data retriever (python 3 and python 2.7)

By Bingyin Hu

Designed for publishing groups including:
Wiley, RSC, AIP, ACS, APS, Nature, Taylor & Francis, Springer, Sage, AIAA, MDPI,
IOP. Also compatible for other publishing groups whose websites follow standard 
meta info formatting.

### Python 2.7 version see 'python2.7' branch. For Python 3+, use the 'master' branch directly.

### 1. System preparation

Required packages:

- MechanicalSoup
  - https://mechanicalsoup.readthedocs.io/en/stable/
  - A python3 alternative for mechanize.

- Beautiful Soup 4
  - https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.html
    
- os
  - Python default package

- ast
  - Python default package
  - Used here to turn a string expression into a dictionary

- collections
  - Python default package
  - Used here to save the metadata results in an OrderedDict()

- datetime
  - Python default package
  - Used here to log in the date of citation

Open the command or terminal and run
```
pip install -r requirements.txt
```

### 2. How to use

Apply for an account at https://apps.crossref.org/requestaccount/ for the Crossref Query Services and save the email address in `account.txt` as required by the DOI query module.

In python environment:
```
from doiretriever import mainDOI
doi = "10.1021/acsmacrolett.7b00603"
output = mainDOI(doi)
```
or
```
output = mainDOISoupFirst(doi)
```
then the information will be saved in a dictionary, returned, and get by output.


### 3. Others

Checklist for adding a new journal site if it cannot be queried from CrossRef:
- add a default dictionary with the mapping of meta data names
- add an accurate search term into getPublisher(url)
- add a blurry search term into getPublisher(url)
- determine which of "soup_only", "txt_only", or "soup_txt_mix" that the journal belongs to, add it in
- add the journal into collectMeta(doi, url, publisher), follow the convention of other journals
- add the data fetching method for the journal (e.g. wileyMeta(metas, doi), rscMeta(metas, doi) etc.)

==========================================================================

09/28/2017: Tests passed for Wiley and RSC journal papers.

09/29/2017: Tests passed for Elsevier journal papers.

09/30/2017: Tests passed for AIP and APS journal papers.

10/01/2017: Tests passed for ACS journal papers and IEEE journal and conference papers.

10/02/2017: Tests passed for Nature, Springer, T&F, Sage, AIAA journal papers and MDPI logged papers.

02/22/2018: Tests passed for IOP Publishing, AIP modules are updated according to a recent update of the website formatting.

06/18/2018: A query layer is added before the bs4 module works. The CrossRef Query Services  is utilized through OpenURL to fetch the doi metadata much faster than the previous bs4 module. 

Note: Keywords are not available through query. Affiliations might not be 
      fetchable in some cases.