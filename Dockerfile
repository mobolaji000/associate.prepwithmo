# set base image (host OS)
FROM tiangolo/uwsgi-nginx-flask:python3.8


# set the working directory in the container
WORKDIR /app

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip3 install -r requirements.txt
#RUN pip3 install -I --ignore-installed -r requirements.txt

COPY /overwrite_flask_user_mixin/user_mixin.py /usr/local/lib/python3.8/site-packages/flask_user/user_mixin.py

# copy the content of the local app directory to the working directory
COPY app/ /app
COPY data/ /app/data
#COPY vensti-df64afca06ca.json .

#Wtrigger

EXPOSE 5001
ENV LISTEN_PORT 5001
ENV PYTHONUNBUFFERED=1

ENV FLASK_ENV=development
ENV FLASK_APP=run
ENV FLASK_DEBUG=True
ENV FLASK_RUN_PORT=5001

ENV DEPLOY_REGION=prod

# -v $(pwd)/data:/app/data#
#CMD  flask db init && flask db stamp head && flask db migrate -m "Initial migration." && python3 -m flask db upgrade && python3 -m flask run --host=0.0.0.0
CMD python3 -m flask run --host=0.0.0.0
#docker kill associate.perfectscoremo && docker build -f Dockerfile.Local -t mobolaji00/associate.perfectscoremo . && docker run --rm --add-host=host:192.168.1.107 --name=associate.perfectscoremo -p 5001:5001 -v ${pwd}:/code --env-file DockerEnv mobolaji00/associate.perfectscoremo

