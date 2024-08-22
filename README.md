# LinkedIn Data Scraping

![Swiss American Chamber of Commerce Logo](https://saccsf.com/wp-content/uploads/2015/05/saccsf-logo.jpg)

This report contains code to extract data from LinkedIn HTML files and convert them into a JSON file. The code is programmed to extract data from company pages of the about section. The data can be extracted from individual persons via the person search. The advantage is that several HTML files can be stored in the designated person or company folder and the data is stored in a single JSON.
This code may violate LinkedIn's Code of Conduct and is executed at your own risk. 


## Documentation
We generate all code documentation automatically. This is automatically updated on a daily basis.

[Documentation](https://saccsf.github.io/NeonCRMLinkedIn/)


## Run Locally

Clone the project

```bash
  git clone https://github.com/SACCSF/NeonCRMLinkedIn.git
```

Go to the project directory

```bash
  cd NeonCRMLinkedIn
```

Install dependencies

```bash
  pip install -r ./requirements.txt
```

Prepare and download html files
- Go to [Linkedin](linkedin.com) and log in to your existing account
- Search with the following link https://www.linkedin.com/company/company_keyword/about/ for the company you want to have the information of 
- Or search with the following link for the persons page to download https://www.linkedin.com/search/results/people/?keywords=company_keyword
- Safe all files in the folder persons or companies

Run the code
```bash
  python ./extract_persons_html_to_json.py
  python ./extract_companies_html_to_json.py
```

Grab all data out of the files companies.json and persons.json


## Authors

- [@nicola-hermann](https://github.com/nicola-hermann)
- [@flawas](https://github.com/flawas)

