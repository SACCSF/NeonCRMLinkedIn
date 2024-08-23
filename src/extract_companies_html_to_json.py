from bs4 import BeautifulSoup
from utils import remove_html_tags, row_with_most_non_nans, parse_arguments
from pathlib import Path
import json, sys, time
import pandas as pd

# This value is used to extract the relevant JSON data from the HTML file.
# LinkedIn may change this value in the future. There is no good way to automate this.
ELEMENT_WITH_RELEVANT_DATA = 20


def read_html_file(html_file_path: Path) -> pd.DataFrame:
    """
    Reads an HTML file and extracts company information from it.

    Args:
        html_file_path (Path): The path to the HTML file to be processed.

    Returns:
        pd.DataFrame: A DataFrame containing the extracted company information.

    Detailed Steps:
    1. Read the contents of the HTML file using `read_text()` method.
    2. Parse the HTML content using BeautifulSoup with the "html.parser" parser.
    3. Find all the <code> elements in the parsed HTML content.
    4. Remove the HTML tags from each <code> element using the `remove_html_tags` function.
    5. Parse the JSON data from the relevant <code> element (determined by `ELEMENT_WITH_RELEVANT_DATA`).
    6. Extract the relevant fields from the JSON data and create a new row DataFrame.
    7. Concatenate the new row to the main DataFrame.

    Example:
    >>> html_file_path = Path('company.html')
    >>> df = read_html_file(html_file_path)
    >>> print(df.head())
    """

    contents = html_file_path.read_text()
    soup = BeautifulSoup(contents, "html.parser")
    data = soup.findAll("code")

    # remove code annotaion
    raw_data = [remove_html_tags(str(d)) for d in data]

    try:
        js = json.loads(raw_data[ELEMENT_WITH_RELEVANT_DATA])
    except json.decoder.JSONDecodeError:
        print("Error while parsing JSON data")
        sys.exit(1)

    df = pd.DataFrame()

    for lines in js["included"]:
        # Extract relevant fields from the JSON data
        name = lines.get("name")
        tagline = lines.get("tagline")
        description = lines.get("description")
        founded_on = lines.get("foundedOn", {}).get("year")
        headquarter_city = lines.get("headquarter", {}).get("address", {}).get("city")
        headquarter_country = (
            lines.get("headquarter", {}).get("address", {}).get("country")
        )
        geographic_area = (
            lines.get("headquarter", {}).get("address", {}).get("geographicArea")
        )
        website_url = lines.get("websiteUrl")
        phone = lines.get("phone", {}).get("number")
        employee_count_range_start = lines.get("employeeCountRange", {}).get("start")
        employee_count_range_end = lines.get("employeeCountRange", {}).get("end")
        specialities = lines.get("specialities")

        # Create a new row DataFrame
        new_row = {
            "name": name,
            "tagline": tagline,
            "description": description,
            "websiteUrl": website_url,
            "foundedOn": founded_on,
            "headquarterCity": headquarter_city,
            "headquarterCountry": headquarter_country,
            "geographicArea": geographic_area,
            "phone": phone,
            "specialities": specialities,
            "employeeCountRangeStart": employee_count_range_start,
            "employeeCountRangeEnd": employee_count_range_end,
        }
        row = pd.DataFrame([new_row])
        # Concatenate the new row to the main DataFrame
        df = pd.concat([df, row], ignore_index=True)

    return df


def get_all_information(directory_path: str) -> pd.DataFrame:
    """
    Aggregates data from all HTML files in a specified directory into a single DataFrame.

    This function searches for all HTML files within the given directory, reads each file, drops any rows with NaN values,
    and concatenates the resulting DataFrames into one combined DataFrame.

    Parameters:
    - directory_path (str): The path to the directory containing the HTML files to be processed.

    Returns:
    - pd.DataFrame: A DataFrame containing the combined data from all HTML files in the directory, with any rows containing NaN values removed.

    Notes:
    - The function assumes that the HTML files have a structure that is compatible with `read_html_file` function.
    - Ensure that the `get_all_files_in_folder` and `read_html_file` functions are defined and properly implemented to handle the file reading and data extraction.

    Example:
    >>> df = get_all_informations('/path/to/directory')
    >>> print(df.head())
    """

    data = pd.DataFrame()
    directory_pathlib = Path(directory_path)
    # Iterate over all HTML files in the specified directory
    for file in directory_pathlib.rglob("*.html"):
        print(f"Processing file: {file.name}")
        df = read_html_file(file)
        row = row_with_most_non_nans(df)
        data = pd.concat([data, row], axis=1)

    data.to_json(
        directory_pathlib.joinpath(f"{directory_pathlib.name}.json"),
        orient="records",
        force_ascii=False,
    )


if __name__ == "__main__":
    t1 = time.time()
    args = parse_arguments()
    get_all_information(args.directory)
    print(f"Main program finished in {time.time() - t1} seconds")
