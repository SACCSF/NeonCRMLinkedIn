import logging

from bs4 import BeautifulSoup
from lxml import etree
from pathlib import Path
import json, os, time
import pandas as pd


def remove_html_tags(text):
    """
    Removes HTML tags from a given string of text.

    Args:
        text (str): The input string containing HTML content.

    Returns:
        str: The text with all HTML tags removed, leaving only the plain text content.

    Detailed Steps:
    1. Create an HTML parser using `etree.HTMLParser()`.
    2. Parse the input HTML string into an element tree using `etree.fromstring()`.
    3. Convert the element tree back to a string, extracting only the text content and ignoring the HTML tags.

    Example:
        >>> clean_text = remove_html_tags('<p>Hello, <b>world</b>!</p>')
        >>> print(clean_text)  # Output: "Hello, world!"
    """
    parser = etree.HTMLParser()
    tree = etree.fromstring(text, parser)
    return etree.tostring(tree, encoding='unicode', method='text')

def read_html_file(html_file_path):
    """
    Reads an HTML file, extracts JSON data embedded within <code> tags,
    and converts it into a Pandas DataFrame.

    Args:
        html_file_path (str): The file path to the HTML file that contains the data.

    Returns:
        pd.DataFrame: A DataFrame containing the extracted data with columns
                      'name', 'subtitle', and 'linkedinurl'.

    Detailed Steps:
    1. Read the contents of the specified HTML file.
    2. Parse the HTML content using BeautifulSoup to find all code tags.
    3. Extract and clean the data within the code tags by removing HTML tags.
    4. Load the JSON data from the cleaned string found within the 16th code tag.
    5. Save the loaded JSON data to a file named 'data.json' for debugging purposes.
    6. Iterate over the 'included' array in the JSON data:
        - For each item, extract the 'title', 'primarySubtitle', and 'bserpEntityNavigationalUrl' fields.
        - Create a DataFrame for each extracted row and concatenate it to the main DataFrame.
    7. Return the final DataFrame containing the extracted and processed data.

    Notes:
    - This function assumes the 16th code tag contains the relevant JSON data.
    - The JSON structure is expected to have an 'included' key containing the data array.

    Example:
        df = read_html_file('path/to/your/file.html')
        print(df.head())
    """
    contents = Path(html_file_path).read_text()
    soup = BeautifulSoup(contents, 'html.parser')
    data = soup.findAll('code')

    # remove <code> </code>
    raw_data = []
    for d in data:
        raw_data.append(remove_html_tags(str(d)))

    # load specific data
    js = json.loads(raw_data[16])

    # for debugging
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(js, f, ensure_ascii=False, indent=4)

    # Initialize an empty DataFrame
    df = pd.DataFrame()

    # length of json
    iteration = 0
    length = len(js['included'])

    while iteration < length:
        # Split rows
        j = js['included'][iteration]

        # Extract data with checks
        title = j.get('title', {}).get('text', None)
        subtitle = j.get('primarySubtitle', {}).get('text', None)
        linkedinurl = j.get('bserpEntityNavigationalUrl', None)

        # Create a new row DataFrame
        new_row = {"name": title, "subtitle": subtitle, "linkedinurl": linkedinurl}
        row = pd.DataFrame([new_row])

        # Concatenate the new row to the main DataFrame
        df = pd.concat([df, row], ignore_index=True)

        # Increment the iteration counter
        iteration += 1

    # Display the final DataFrame
    return df


def get_all_files_in_folder(path='.'):
    """
    Recursively retrieves all file paths from a given directory and its subdirectories.

    Args:
        path (str, optional): The directory path to start searching from.
                              Defaults to the current directory ('.').

    Returns:
        list: A list containing the full paths of all files found in the directory and its subdirectories.

    Example:
        files = get_all_files_in_folder('/path/to/directory')
        print(files)  # Output: ['/path/to/directory/file1.txt', '/path/to/directory/subdir/file2.txt', ...]
    """
    files_list = []

    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            files_list.extend(get_all_files_in_folder(full_path))
        else:
            files_list.append(full_path)

    return files_list


def get_all_informations(directory_path):
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
        df = get_all_informations('/path/to/directory')
        print(df.head())
    """
    files = get_all_files_in_folder(directory_path)

    data = pd.DataFrame()
    for file in files:
        df = read_html_file('./' + file)  # Read data from each HTML file
        df = df.dropna()  # Drop rows with any NaN values
        data = pd.concat([data, df], ignore_index=True)  # Concatenate to the main DataFrame

    return data

def main():

    t1 = time.time()
    print(f"Main program started")
    # Specify the directory path you want to start from
    merged_df = get_all_informations('files')
    merged_df.to_csv('linkedin.csv')
    print(f"Main program finished in {time.time() - t1} seconds")


if __name__ == "__main__":
    main()