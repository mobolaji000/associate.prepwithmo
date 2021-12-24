# set base image (host OS)
FROM tiangolo/uwsgi-nginx-flask:python3.8


# set the working directory in the container
WORKDIR /app

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip3 install -r requirements.txt
#RUN pip3 install -I --ignore-installed -r requirements.txt

# copy the content of the local app directory to the working directory
COPY app/ /app

#WORKDIR

EXPOSE 5001
ENV LISTEN_PORT 5001
ENV PYTHONUNBUFFERED=1

ENV FLASK_ENV=development
ENV FLASK_APP=run
ENV FLASK_RUN_PORT=5001

ENV DEPLOY_REGION=prod

CMD python3 -m flask run --host=0.0.0.0

#CMD python3 run
