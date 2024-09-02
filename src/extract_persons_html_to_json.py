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
    Reads an HTML file and extracts person information.

    Args:
        html_file_path (Path): The path to the HTML file.

    Returns:
        pd.DataFrame: A DataFrame containing the extracted person information.

    Detailed Steps:
    1. Read the contents of the HTML file.
    2. Parse the HTML content using BeautifulSoup.
    3. Extract the JSON data from the HTML file.
    4. Initialize an empty DataFrame.
    5. Iterate over the JSON data and extract the relevant fields.
    6. Create a new row DataFrame.
    7. Concatenate the new row to the main DataFrame.

    Example:
    >>> html_file_path = Path('data/file.html')
    >>> read_html_file(html_file_path
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
        title_dict = lines.get("title", {})
        title = title_dict.get("text") if title_dict is not None else None
        subtitle_dict = lines.get("primarySubtitle", {})
        subtitle = subtitle_dict.get("text") if subtitle_dict is not None else None
        position_dict = lines.get("summary", {})
        position = position_dict.get("text") if position_dict is not None else None
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

    return df


def get_all_information(directory_path: Path) -> None:
    """
    Extracts person information from all HTML files in the specified directory.

    Args:
        directory_path (Path): The path to the directory containing the HTML files.

    Returns:
        None

    Detailed Steps:
    1. Iterate over all the files in the specified directory.
    2. Read the HTML file using the `read_html_file` function.
    3. Exclude rows with more than 2 NaN values using the `exclude_rows_with_x_nans` function.
    4. Save the extracted information to a JSON file with the same name as the HTML file.

    Example:
    >>> directory_path = Path('data')
    >>> get_all_information(directory_path)
    """

    directory_pathlib = Path(directory_path)

    for file in directory_pathlib.rglob("*.html"):
        print(f"Processing file: {file.name}")
        df = read_html_file(file)
        rows = exclude_rows_with_x_nans(df, 2)

        rows.to_json(
            directory_pathlib.joinpath(f"{file.stem}.json"),
            orient="records",
            force_ascii=False,
        )


if __name__ == "__main__":
    t1 = time.time()
    args = parse_arguments()
    get_all_information(args.directory)
    print(f"Main program finished in {time.time() - t1} seconds")
