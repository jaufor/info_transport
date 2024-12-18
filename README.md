# Data Analysis of Madrid's public transport network

This repository contains code and resources for studying the public transport network of Madrid, Spain

## Getting Started

To get started with this project, follow the steps below:

1. Clone the repository to your local machine:

```bash
git clone https://github.com/jaufor/info_transport.git
```

2. Navigate to the project directory:

```bash
cd info_transport
```

3. Install the required dependencies. We recommend creating a virtual environment before installing the dependencies:

```bash
pip install -r requirements.txt
```

5. Run the data analysis:

   - The main script for performing data analysis is `main.py`.
   - To run the data analysis, execute the following command inside the project directory:

   ```bash
   python3 src/main.py
   ```

   The script will ask the street, house number and city name of the origin and destination addresses. 

## Project Structure

The project has the following structure:

- `src/`: This directory contains the source code of the project.
  - `main.py`: The main script for trigerring the functions.
  - `data_processing.py`: All the functions to process the data.
  - `data_reading.py`: All the functions needed to populate the graph.
  - `find_coordinates.py`: Contains the function needed to find the coordinates of a postal address.
  - `find_stops.py`: Contains the function needed to find the stops of the public transport network that are near to a given location.
  - `find_routes.py`: All the functions needed to find the shortest paths to go from one place to another.
- `data/`: This directory contains the datasets used for analysis.
  - `ontology/`: this directory contains two ontologies:
    - `gtfs.ttl`: the designed ontology wthout any instances of Stop, Route and Transfer
    - `gtfs_with_subway.ttl`: the designed ontology with all the instances of the subway data source
    - `gtfs_with_all_modes.ttl`: the designed ontology with all the instances of all data sources (subway, light subway, railway, Madrid's city bus and intercity bus). 
  - `raw/`: GTFS Data extracted from the open data sources of the Consorcio Regional de Transportes de Madrid (CRTM).
     This folder hasn't been upload to repository because the size of some files exceeds the limit of my account in Github.
    - `crtm/`:
      - `M4/`: Subway
      - `M5/`: Railway
      - `M6/`: Madrid's city bus
      - `M10/`: Light subway
      - `M89/`: Intercity bus
  - `processed/`: The data extracted, filtered and processed. 
- `test/`: this folder contains the file gtfs_shapes.txt with the SHACL rules that the data graph must comply.
- `requirements.txt`: A text file specifying the Python dependencies required for the project.
- `README.md`: This file, providing an overview of the repository and instructions for usage.

## License

The code in this repository is licensed under the [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 License](https://creativecommons.org/licenses/by-nc-nd/4.0/deed.en). Feel free to use and modify the code for your own purposes.




