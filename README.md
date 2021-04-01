# Fiware4Water Sofia Challenge

Script to transform .csv data into **ETSI NGSI-LD** payload and upload to a **FIWARE Context Broker**. This python
script is associated to the corresponding **Fiware4Water Challenge** - South West region in the United Kingdom.

## Requisites

- docker version 20.10.5, build 55c4c88. To install docker engine, follows the guidelines
  [here](https://docs.docker.com/get-docker).
- docker-compose version 1.28.5, build c4eb3a1f. To install docker-compose follow the guidelines
  [here](https://docs.docker.com/compose/install).
- python version 3.9. To install this python version, follow the guidelines 
  [here](https://www.python.org/downloads). It is probable that the script works with previous versions of python,
  but it has not been tested on those environments.
- virtualenv >= 20.4.3. Python3.9 requires an updated version of virtualenv. You can do it executing the command:
  ```bash
  sudo pip install virtualenv --upgrade
  ```

## Configuration

The `config` folder includes a `configuration.json` file that contains all the configuration variables that are needed
to execute the script. The meaning of each parameter is the following:

- **_context_**, the JSON-LD file that contains the description of the ETSI NGSI-LD context 
  (e.g. [mlaas-compound.jsonld](https://raw.githubusercontent.com/easy-global-market/ngsild-api-data-models/feature/mlaas-models/mlaas/jsonld-contexts/mlaas-compound.jsonld)).
- **_files_**, folder in which the csv files are located (by default `data`). This folder has to be located in the home
  folder of the deployment of this code.
- **_broker_**, basic url of an instance of the FIWARE Context Broker (e.g. http://127.0.0.1:1026).
- **_log_level_**, the specific level of the logs. The expected values are:
  - CRITICAL 
  - ERROR 
  - WARNING 
  - INFO 
  - DEBUG 
  - NOTSET
- **_scope_**, (Optional) time in seconds to wait after sending a request to the FIWARE Context Broker instance. 

## Installation

- Clone this repository
  ```bash
  git clone https://github.com/easy-global-market/f4w-challenges-sww.git
  ```
- Create virtualenv
  ```bash
  virtualenv -ppython3.9 .env
  ```
- Activate the python virtual environment:
  ```bash
  source .env/bin/activate
  ```
- Install requirements:
  ```bash
  pip install -r requirements.txt
  ```
- Execute the python script:
  ```bash
  python upload.py
  ```

## Testing

In order to test the execution of the script in a local environment, you can find inside the [./docker](./docker)
folder a `docker-compose.yaml` file and the corresponding `.env` configuration file. You can launch an instance
of a FIWARE Context Broker (in this case the FIWARE Orion-LD implementation) to test the execution of the script.

```bash
docker-compose up -d
```

To stop the execution of the instances, just execute the command:

```bash
docker-compose down
```

## License

[Apache2.0](LICENSE) © 2021 FIWARE Foundation, e.V.
