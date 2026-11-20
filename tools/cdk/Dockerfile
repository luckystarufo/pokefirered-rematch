# The AWS CDK command line, so nothing needs installing on the Mac (tools/cdk.sh runs it).
FROM node:22-slim
RUN npm install -g aws-cdk@2.1147.0 && npm cache clean --force
WORKDIR /work/infra
ENTRYPOINT ["cdk"]
