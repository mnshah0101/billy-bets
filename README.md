# Billy Bets - Sports Data Analysis Model

Billy Bets project is aimed at developing a cutting-edge language model that answers sports stats-related queries articulated in natural language. This project employs advanced technologies including LangChain, Pandas, SportsData.io and OpenAI.

## Table of Contents

1. [Getting Started](#gettingstarted)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Contribution](#contribution)
6. [License](#license)

## Getting Started <a name = "gettingstarted"></a>

To get started, you should clone the repository to your local machine by using Git commands.

## Prerequisites <a name = "prerequisites"></a>

You need to have the following installed on your machine:

1. Python: Make sure you have the latest version of Python installed.
2. Django: This project uses Django for its backend.
3. Pandas: Used for data manipulation and analysis.
4. LangChain: Incorporated to improve the language processing.
5. SportsData.io: Provides the sports statistics.
6. OpenAI: Used to facilitate machine learning.

## Installation <a name = "installation"></a>

After fulfilling the prerequisites, follow these steps:

1. Clone the repository to your local workspace.
2. Install the required packages using the command `pip install -r requirements.txt`.
3. Migrate the database using the command `python manage.py migrate`.
4. Now, you are all set to run the server using the command `python manage.py runserver`.

## Usage <a name = "usage"></a>

Once the server is up and running, you can interact with the model by sending a POST request to the server with the sports stats query articulated in natural language. The server will return the desired output in a structured JSON format.

## Contribution <a name = "contribution"></a>

Collaborations are welcome! For enhancements, please open an issue first to discuss what you would like to change.

## License <a name = "license"></a>

This project is licensed under the MIT license. For more information refer to the `LICENSE` file in the repository.

Remember to always comment your code to make it easily understandable.

Visit our [FAQ](FAQ.md) and [WIKI](WIKI.md) for more information.
