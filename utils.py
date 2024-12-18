import os
from dotenv import load_dotenv
import requests
from typing import Final
import logging

URL: Final = "https://nailshopai.onrender.com/inference"


def load_env_variable(var_name):
    """
    Load an environment variable from a custom .env file.

    Parameters:
    var_name (str): The name of the environment variable to load.

    Returns:
    str: The value of the environment variable if found, otherwise None.
    """
    # Load the .env file
    for path in ['.env', '../.env', '../../.env', '../../../.env']:
        if os.path.exists(path):
            load_dotenv(dotenv_path=path)
            break

    # Get the environment variable
    return os.getenv(var_name)


def get_logger(name: str) -> logging.Logger:
    """
    Template for getting a logger.

    Args:
        name: Name of the logger.

    Returns: Logger.
    """

    # Configure
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(name)

    return logger


# Set the headers including the API key
HEADERS = {
    "Content-Type": "application/json",
    "access_token": "123"
}


def inference(prompt: str):
    # Define the data to be sent
    data_item = {
        "query": prompt
    }

    print(data_item)
    # Send the POST request
    response = requests.post(URL, json=data_item, headers=HEADERS)

    # Check the response
    if response.status_code == 200:
        print("Data sent successfully!", response.json())
        return response.json()
    else:
        print("Failed to send Data.")
        print("Status code:", response.status_code)
        print("Response:", response.text)
        return f"{response.status_code}: {response.text}"
