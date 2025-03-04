import requests
import pandas as pd
from typing import List, Optional, Tuple
def fetch_papers(query: str, max_results: int = 20) -> List[dict]:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": str(max_results),
        "retmode": "json",
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    paper_ids = response.json()['esearchresult']['idlist']
    papers = []
    for paper_id in paper_ids:
        paper_details = fetch_paper_details(paper_id)
        papers.append(paper_details)
    return papers
def fetch_paper_details(pubmed_id: str) -> dict:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": pubmed_id,
        "retmode": "xml",
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    paper_info = parse_paper_details(response.text)
    return paper_info
def parse_paper_details(xml_data: str) -> dict:
    from xml.etree import ElementTree as ET
    root = ET.fromstring(xml_data)
    article = root.find(".//PubmedArticle")
    title = article.find(".//ArticleTitle").text if article.find(".//ArticleTitle") else "N/A"
    publication_date = article.find(".//PubDate/Year").text if article.find(".//PubDate/Year") else "N/A"
    authors = [author.find(".//LastName").text for author in article.findall(".//Author")]
    affiliations = [aff.text for aff in article.findall(".//Affiliation")]
    corresponding_email = article.find(".//Author/Email").text if article.find(".//Author/Email") else "N/A"
    non_academic_authors, companies = identify_non_academic(authors, affiliations)
    paper_info = {
        "PubmedID": article.find(".//PMID").text,
        "Title": title,
        "Publication Date": publication_date,
        "Non-academic Author(s)": non_academic_authors,
        "Company Affiliation(s)": companies,
        "Corresponding Author Email": corresponding_email,
    }
    return paper_info
def identify_non_academic(authors: List[str], affiliations: List[str]) -> Tuple[str, str]:
    non_academic_authors = []
    companies = []
    company_keywords = ["pharma", "biotech", "inc", "Ltd", "laboratories", "corporation"]
    for affiliation in affiliations:
        if any(keyword in affiliation.lower() for keyword in company_keywords):
            companies.append(affiliation)
            idx = affiliations.index(affiliation)
            non_academic_authors.append(authors[idx])
    return ", ".join(non_academic_authors), ", ".join(companies)
def save_to_csv(papers: List[dict], filename: Optional[str] = None):
    df = pd.DataFrame(papers)
    if filename:
        df.to_csv(filename, index=False)
        print(f"Results saved to {filename}")
    else:
        print(df)