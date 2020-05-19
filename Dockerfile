FROM python:3.7
# The ENV ensures that the python output to terminal without buffering
ENV PYTHONBUFFERED 1 

RUN echo Updating existing packages, installing and upgrading python and pip.
RUN apt-get update -y
RUN pip install --upgrade pip

ADD /flaskr/requirements.txt .

RUN echo Installing Python packages listed in requirements.txt
RUN pip install -r ./requirements.txt

RUN echo Copying tests directory
COPY ./tests /tests

RUN echo Copying flaskr directory
COPY ./flaskr /flaskr

WORKDIR /flaskr

RUN echo Starting python and starting the Flask service...
ENTRYPOINT ["python"]
CMD ["app.py"]