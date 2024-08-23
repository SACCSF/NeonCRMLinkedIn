from lxml import etree
import pandas as pd
import argparse


def remove_html_tags(text: str) -> str:
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
    >>> html_text = '<p>Hello, <b>world</b>!</p>'
    >>> clean_text = remove_html_tags(html_text)
    >>> print(clean_text)
    'Hello, world!'
    """
    parser = etree.HTMLParser()
    tree = etree.fromstring(text, parser)
    return etree.tostring(tree, encoding="unicode", method="text")


def row_with_most_non_nans(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns the row with the most non-NaN values in a DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.Dataframe: The row with the most non-NaN values.

    Example:
    >>> df = pd.DataFrame({'A': [1, 2, None], 'B': [None, 5, 6], 'C': [7, 8, 9]})
    >>> row = row_with_most_non_nans(df)

    """
    non_nan_counts = df.notna().sum(axis=1)
    max_index = non_nan_counts.idxmax()
    row = df.loc[max_index]
    return pd.DataFrame([row])


def exclude_rows_with_x_nans(df: pd.DataFrame, x: int) -> pd.DataFrame:
    """
    Excludes rows with a specified number of NaN values from a DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame.
        x (int): The number of NaN values to exclude.

    Returns:
        pd.DataFrame: The DataFrame with rows containing x NaN values removed.

    Example:
    >>> df = pd.DataFrame({'A': [1, None, 3], 'B': [4, 5, None], 'C': [None, 8, 9]})
    >>> new_df = exclude_rows_with_x_nans(df, 1)
    >>> print(new_df)
    """
    return df.dropna(thresh=df.shape[1] - x)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments to get the directory path containing the HTML files.

    Returns:
        argparse.Namespace: The parsed arguments as a namespace object.

    Example:
    >>> args = parse_arguments()
    >>> print(args.directory)
    """

    parser = argparse.ArgumentParser(
        description="Extract company information from HTML files and save to JSON."
    )
    parser.add_argument(
        "directory",
        type=str,
        help="The path to the directory containing the HTML files to be processed.",
    )
    return parser.parse_args()
