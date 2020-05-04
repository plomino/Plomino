FROM robot_tests as robot_tests
#COPY --from=robot_tests --chown=plone:plone /plone/instance /plone/instance
ENV NVM_DIR /usr/local/nvm
ENV NODE_VERSION 6.1
ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH      $NVM_DIR/v$NODE_VERSION/bin:$PATH

COPY --chown=plone:plone . /plone/instance/
#USER plone


SHELL ["/bin/bash", "-c"]
USER plone
RUN cd /plone/instance && bin/buildout -c buildout.cfg install test resources robot instance && source $NVM_DIR/nvm.sh && cd /plone/instance/ide  && npm install && npm run build || true
USER root
RUN chown -R --from=root:root plone:plone .
USER plone
#RUN ["/bin/bash","-c", "source $NVM_DIR/nvm.sh && cd /plone/instance/ide  && npm install && npm run build"]

