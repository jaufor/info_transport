# Data Analysis of Madrid's public transport network

This repository contains code and resources for studying the public transport network of Madrid, Spain

## Getting Started

To get started with this project, follow the steps below:

1. Clone the repository to your local machine:

```bash
git clone https://eimtgit.uoc.edu/prog_datasci_2/activities/activity_sol_4.git
```

2. Navigate to the project directory:

```bash
cd activity_sol_4
```

3. Install the required dependencies. We recommend creating a virtual environment before installing the dependencies:

```bash
pip install -r requirements.txt
```

5. Run the data analysis:

   - The main script for performing data analysis is `main.py`.
   - To run the data analysis, execute the following command inside the src folder:

   ```bash
   python3 main.py
   ```

## Project Structure

The repository has the following structure:

- `src/`: This directory contains the source code of the project.
  - `main.py`: The main script for trigerring the functions.
  - `data_processing.py`: All the functions to process the data.
  - `data_reading.py`: All the functions needed to populate the graph.
  - `find_coordinates.py`: Contains the function needed to find the coordinates of a postal address.
  - `find_stops.py`: Contains the function needed to find the stops of the public transport network that are near to a given location.
  - `find_routes.py`: All the functions needed to find the shortest paths to go from one place to another.
- `data/`: This directory contains the data datasets used for analysis.
  - `raw/`: GTFS Data extracted from the open data sources of the Consorcio Regional de Transportes de Madrid (CRTM) and Renfe, Spain's national state-owned railway company.
    - `crtm/`:
      - `M4/`: Subway
      - `M6/`: City bus
      - `M10/`: Light subway
      - `M89/`: Intercity bus
    - `renfe/`:
      - `M5/`: Railway
  - `processed/`: The data extracted, filtered and processed. 
- `test/`: This directory contains the source code of tests done.
- `requirements.txt`: A text file specifying the Python dependencies required for the project.
- `README.md`: This file, providing an overview of the repository and instructions for usage.
- `LICENSE.md`: A markdown file specifying the licence of the code in this repository.

## Test
#https://coverage.readthedocs.io/en/7.6.4/
To execute the test and see the coverage of this you need to run the following commands, from the root folder:

1. To create the coverage of the test:
    ```bash
    coverage run --source=. -m unittest discover -s test/
    ```
2. To see the coverage report:
    ```bash
    coverage report
    ```

Output:
```
Name                           Stmts   Miss  Cover
--------------------------------------------------
src\data_filtering.py             20      1    95%
src\data_processing.py            16      0   100%
src\plots.py                      39      0   100%
test\test_data_filtering.py       20      1    95%
test\test_data_processing.py      24      1    96%
test\test_plot.py                 16      1    94%
--------------------------------------------------
TOTAL                            135      4    97%
```

## License

The code in this repository is licensed under the [MIT License](LICENSE.md). Feel free to use and modify the code for your own purposes.




