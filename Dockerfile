FROM elgalu/selenium:2
USER root
RUN apt-get update && apt-get install -y virtualenv git gcc python-dev build-essential autoconf libjpeg-turbo8-dev libxml2-dev libxslt1-dev

ENV NVM_DIR /usr/local/nvm
ENV NODE_VERSION 6.1

# Install nvm with node and npm
RUN ["/bin/bash","-c", "curl -sL https://raw.githubusercontent.com/creationix/nvm/v0.31.0/install.sh | bash \
    && ls /usr/local/nvm \
    && source $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default \
    && npm i -g npm@3 \
    && npm i -g typescript@2.1.4 \ 
    && npm cache clean \
    && npm set registry http://registry.npmjs.org \
    && npm update -g"]
ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH      $NVM_DIR/v$NODE_VERSION/bin:$PATH

COPY . /buildout/
RUN mkdir -p /buildout/buildout-cache/eggs /buildout/buildout-cache/downloads
RUN chown -R seluser.seluser /buildout
USER seluser

RUN cd /buildout && virtualenv . && bin/pip install zc.buildout==2.2.5 setuptools==8.3 && bin/buildout -c travis.cfg install download install
RUN cd /buildout && bin/buildout -c travis.cfg
RUN ["/bin/bash","-c", "source $NVM_DIR/nvm.sh && cd /buildout/ide && npm install && npm run build"]

