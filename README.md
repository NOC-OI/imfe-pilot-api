# API for User Authentication and Backend Calculations

This API serves a dual purpose:

1. It performs server-side calculations for the Digital Twin project focused on Haig Fras.
2. It manages and provides access to the user table, enabling authentication.

The API receives user data from the frontend, processes it, and returns data or calculation results.

## API Overview

Detailed information about the API and its endpoints can be found in the "api" folder. This folder includes the "fast.py" file, which comprehensively describes all available endpoints and the corresponding functions they execute.

Additionally, the v1 version of the calculations is documented in the "api/v1" folder.

## User Authentication

The user authentication system relies on OAuth connections with ORCID and Microsoft 365 systems. To enable this functionality, the following steps have been taken:

1. Register your application with ORCID and Microsoft.
2. Configure the frontend application to facilitate login and obtain code information.
3. Send this code to the backend to check if the user is among the authorized users (as listed in the "orcid.json" file).
4. Connection with the backend is facilitated through endpoints (GET and POST requests).

### (Deprecated) Database

The database utilized is a PostgreSQL database, created based on the schema described in "schemas/schemas.py." Any changes to the database require generating new migrations. The process for creating and running migrations will be explained during the Docker setup in this readme.

Database access credentials are defined in the "docker-compose" configuration.

### ORCID.json

The "orcid.json" file should contain a list of ORCID IDs and Outlook email addresses that are permitted to access the frontend application. Below is an example of an "orcid.json" file:

```json
{
    "orcid": [
        "0000-0000-0000-0000",
        "email@outlook.com"
    ]
}
```

## User Endpoints

Endpoints for user creation and selection are defined in "api/v1/user.py."

## Object Store Authentication

Some files within the object store are not publicly accessible. In such cases, you can use this repository to obtain signed URLs for the object store files. These signed URLs must be encrypted using a token before passing them to the frontend. The same token must be used by any system responsible for decrypting the signed URLs.

## Calculations

In this repository, we perform a list of calculations on the backend in order to obtain some statistics on the data or some biodiversity calculations.

The following calculations are currently being performed in this project:
- Calculation of mean, median, and standard deviation.
- Calculation of density.
- Calculation of biodiversity based on the Shannon index.
- Calculation of biodiversity based on the Inverse Simpson Index.

Calculations are executed using the code available in "use_cases_calc/get_bucket.py."

### Endpoints

The endpoints for calculations are defined in the files "api/v1/data" and "api/v1/calc."

## Installation

1. Visit [the project repository](https://git.noc.ac.uk/ocean-informatics/imfepilot/api_calculations_use_cases) to access the project, manage issues, set up your SSH public key, and more.

2. Create a Python 3 virtual environment and activate it:

   ```bash
   pyenv virtualenv servercalc
   ```

3. Clone the project and install it:

   ```bash
   git clone git@git.noc.ac.uk:ocean-informatics/imfepilot/api_calculations_use_cases.git
   cd api_calculations_use_cases
   pyenv local servercalc
   pip install -e .
   ```

## Running the Server Locally

If the configuration was done correctly, you can run the following command to launch the API:

```bash
uvicorn api.fast:app --reload
```

This will run the app in development mode. Open [http://localhost:8000](http://localhost:8000) in your browser to access it. The page will automatically reload when you make edits.

### Important

Make sure to set the following environment variables:

- `HASH_PASSWORD`: The password used for encrypting and decrypting signed URLs.
- `JASMIN_API_URL`: The endpoint for Jasmin access.
- `JASMIN_TOKEN`: The token for Jasmin access.
- `JASMIN_SECRET`: The secret for Jasmin access.
- `DATABASE_URL`: Your database URL, formatted as `postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{SERVICE_NAME}:{PORT}`. Typically, `SERVICE_NAME` is set to 'db' (the name of the database service in the Docker Compose file), and `PORT` is set to 5432.
- `VITE_SERVER_ENDPOINT`: The endpoint for the website that accesses the API. Please use [https://imfe-pilot.noc.ac.uk/](https://imfe-pilot.noc.ac.uk/).
- `VITE_ORCID_CLIENT_ID`: The client ID for the ORCID app.
- `VITE_ORCID_CLIENT_SECRET`: The client secret for the ORCID app.
- `VITE_ORCID_CLIENT_REDIRECT_URI`: The redirect URI for ORCID. It should match the one described in the ORCID app. Please use [https://imfe-pilot.noc.ac.uk/auth](https://imfe-pilot.noc.ac.uk/auth).

Save these variables in a .env file at the root of the repository, following this example:

```env
JASMIN_API_URL=https://aaaaaaaaaaaaaa.ac.uk/
JASMIN_TOKEN=bbbbbbbbbbbbbbbbbbbbbbb
JASMIN_SECRET=cccccccccccccccccccc
HASH_TOKEN='dddddddddddddddddddddddddddddddddddd'
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432
VITE_SERVER_ENDPOINT=https://imfe-pilot.noc.ac.uk/
VITE_ORCID_CLIENT_ID=eeeeeeeeeeeeeeeeeeeeeeeeeeeeee
VITE_ORCID_CLIENT_SECRET=ffffffffffffffffffffffffffffffff
VITE_ORCID_CLIENT_REDIRECT_URI=https://imfe-pilot.noc.ac.uk/auth
```

## Generating SSL Keys for localhost (optional)

Depending on your development environment, you may require SSL on your localhost. Follow these steps:

1. Install mkcert:

   ```bash
   brew install mkcert
   mkcert -install
   ```

2. Generate the SSL certificates:

   ```bash
   mkcert localhost
   ```

   This will create two files: `./localhost.pem` and `./localhost-key.pem`. Copy these files to the root folder of your tileserver repository.

## Running the Server as a Docker Compose

First, build the Docker Compose:

```bash
docker-compose build
```

Now, start the containers:

```bash
docker-compose up
```

This will run the app in development mode. Open [http://localhost:8081](http://localhost:8081) in your browser to access it.

If you want to access localhost over HTTPS, you need to modify the Docker Compose file. Change the line:

```yaml
command: bash -c "uvicorn api.fast:app --host 0.0.0.0 --port 8081 --reload"
```

to:

```yaml
command: bash -c "uvicorn api.fast:app --host 0.0.0.0 --port 8081 --ssl-certfile ./localhost.pem --ssl-keyfile ./localhost-key.pem  --reload"
```