from bs4 import BeautifulSoup
from pathlib import Path
import json
import pandas as pd
from utils import remove_html_tags, exclude_rows_with_x_nans, parse_arguments
import sys
import time

# Those values are used to extract the relevant JSON data from the HTML file.
# LinkedIn may change those values in the future. There is no good way to automate this.
ELEMENTS_WITH_RELEVANT_DATA = [14, 16]


def read_html_file(html_file_path: Path) -> pd.DataFrame:
    """
    Reads an HTML file and extracts person information from it.

    Args:
        html_file_path (Path): The path to the HTML file to be processed.

    Returns:
        pd.DataFrame: A DataFrame containing the extracted person information.

    Detailed Steps:
    1. Read the contents of the HTML file using `read_text()` method.
    2. Parse the HTML content using BeautifulSoup with the "html.parser" parser.
    3. Find all the <code> elements in the parsed HTML content.
    4. Remove the HTML tags from each <code> element using the `remove_html_tags` function.
    5. Parse the JSON data from the relevant <code> element (determined by `ELEMENTS_WITH_RELEVANT_DATA`).
    6. Extract the relevant fields from the JSON data and create a new row DataFrame.
    7. Concatenate the new row to the main DataFrame.

    Example:
    >>> html_file_path = Path('person.html')
    >>> df = read_html_file(html_file_path)
    >>> print(df.head())
    """

    contents = Path(html_file_path).read_text()
    soup = BeautifulSoup(contents, "html.parser")
    data = soup.findAll("code")

    # remove code annotaion
    raw_data = [remove_html_tags(str(d)) for d in data]

    for element in ELEMENTS_WITH_RELEVANT_DATA:
        try:
            js = json.loads(raw_data[element])
        except json.decoder.JSONDecodeError:
            continue
        break

    # Check if the JSON data is loaded correctly
    if "js" not in locals():
        print("Error while parsing JSON data")
        sys.exit(1)

    # Initialize an empty DataFrame
    df = pd.DataFrame()

    for lines in js["included"]:
        # Extract relevant fields from the JSON data
        title = lines.get("title", {}).get("text")
        subtitle = lines.get("primarySubtitle", {}).get("text")
        position = lines.get("summary", {}).get("text")
        linkedin_url = lines.get("bserpEntityNavigationalUrl")

        # Create a new row DataFrame
        new_row = {
            "name": title,
            "subtitle": subtitle,
            "position": position,
            "linkedinUrl": linkedin_url,
        }
        row = pd.DataFrame([new_row])
        # Concatenate the new row to the main DataFrame
        df = pd.concat([df, row], ignore_index=True)

    # Display the final DataFrame
    return df


def get_all_information(directory_path: Path) -> None:
    """
    Extracts person information from all HTML files in the specified directory.

    Args:
        directory_path (Path): The path to the directory containing the HTML files.

    Returns:
        None

    Detailed Steps:
    1. Initialize an empty DataFrame to store the extracted data.
    2. Iterate over all HTML files in the specified directory.
    3. Read each HTML file and extract person information using the `read_html_file` function.
    4. Exclude rows with more than 2 NaN values using the `exclude_rows_with_x_nans` function.
    5. Concatenate the extracted data to the main DataFrame.
    6. Save the extracted data to a JSON file in the same directory.

    Example:
    >>> directory_path = Path('persons')
    >>> get_all_information(directory_path)
    """

    data = pd.DataFrame()
    directory_pathlib = Path(directory_path)

    for file in directory_pathlib.rglob("*.html"):
        print(f"Processing file: {file.name}")
        df = read_html_file(file)
        rows = exclude_rows_with_x_nans(df, 2)

        data = pd.concat([data, rows], axis=1)

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
