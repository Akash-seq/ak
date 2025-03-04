import argparse
from get_papers import fetch_papers, save_to_csv


def main():
    parser = argparse.ArgumentParser(description="Fetch papers from PubMed based on a query.")
    parser.add_argument('query', type=str, help="The query string to search PubMed.")
    parser.add_argument('-f', '--file', type=str, help="Filename to save the results.")
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug mode.")
    
    args = parser.parse_args()
    
    if args.debug:
        print(f"Searching PubMed for query: {args.query}")
    
    papers = fetch_papers(args.query)
    
    if args.debug:
        print(f"Found {len(papers)} papers.")
    
    save_to_csv(papers, args.file)


if __name__ == "__main__":
    main()
