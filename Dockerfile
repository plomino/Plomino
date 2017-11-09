FROM robot_tests
ENV NVM_DIR /usr/local/nvm
ENV NODE_VERSION 6.1
ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH      $NVM_DIR/v$NODE_VERSION/bin:$PATH

COPY --chown=plone:plone . /plone/instance/
#USER root
#RUN chown -fR plone.plone /plone/instance || exit 0
USER plone

RUN mkdir -p /plone/.buildout && printf "[buildout]\neggs-directory=/plone/buildout-cache/eggs\ndownload-cache=/plone/buildout-cache/downloads\n" > ~/.buildout/default.cfg


RUN cd /plone/instance && bin/buildout -c buildout.cfg install test resources robot instance
RUN ["/bin/bash","-c", "source $NVM_DIR/nvm.sh && cd /plone/instance/ide  && npm install && npm run build"]

