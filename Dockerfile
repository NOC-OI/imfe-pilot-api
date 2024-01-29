# FROM python:3.9

# COPY . . 

# COPY ./requirements.txt requirements.txt

# RUN pip install -e .

# RUN pip install --no-cache-dir --upgrade -r requirements.txt

# CMD ["uvicorn", "api.fast:app", "--host", "0.0.0.0", "--port", "8081"]

# Pull base image
FROM python:3.9

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /code/

# # Install dependencies
# RUN pip install pipenv
# COPY Pipfile Pipfile.lock /code/
# RUN pipenv install --system --dev

COPY ./requirements.txt requirements.txt
COPY . /code/

RUN apt-get update && apt-get install -y --no-install-recommends libgdal-dev
RUN pip install -e .

# CMD ["uvicorn", "api.fast:app", "--host", "0.0.0.0", "--port", "8081"]
EXPOSE 8081