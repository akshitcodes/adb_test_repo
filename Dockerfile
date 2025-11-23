# set base image (host OS)
FROM python:3.8

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

RUN apt-get -y update
RUN apt-get install -y curl nano wget nginx git

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list


# Mongo - Install MongoDB directly without relying on Debian packages
# Download and install MongoDB community server
RUN ln -s /bin/echo /bin/systemctl
RUN cd /tmp && wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-debian10-5.0.0.tgz && \
    tar -zxvf mongodb-linux-x86_64-debian10-5.0.0.tgz && \
    cp -r /tmp/mongodb-linux-x86_64-debian10-5.0.0/bin/* /usr/local/bin/ && \
    mkdir -p /data/db && \
    useradd -m mongodb || true && \
    chown -R mongodb:mongodb /data/db

# Install Node.js and Yarn (use NodeSource for up-to-date Node, then install yarn via npm)
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g yarn

# Install PIP (pip is already included with Python 3.8)


ENV ENV_TYPE staging
ENV MONGO_HOST mongo
ENV MONGO_PORT 27017
##########

ENV PYTHONPATH=$PYTHONPATH:/src/

# copy the dependencies file to the working directory
COPY src/requirements.txt .

# install dependencies
RUN pip install -r requirements.txt
