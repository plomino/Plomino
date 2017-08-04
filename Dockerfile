FROM robot_tests as robot_tests
ENV NVM_DIR /usr/local/nvm
ENV NODE_VERSION 6.1
ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH      $NVM_DIR/v$NODE_VERSION/bin:$PATH

COPY . /buildout/
USER root
RUN chown -fR seluser.seluser /buildout || exit 0

USER seluser
RUN cd /buildout && bin/buildout -c travis.cfg
RUN ["/bin/bash","-c", "source $NVM_DIR/nvm.sh && cd /buildout/ide  && npm run build"]

