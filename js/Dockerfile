# BYO proxy test actor (JS) — Scrapely Node SDK
# SDK is preinstalled in the prebuilt base image at /opt/scrapely
FROM scrapely/actor-node:22

WORKDIR /actor/package

# No dependencies — only manifests + source
COPY --chown=myuser:myuser package.json scrapely.json ./
COPY --chown=myuser:myuser main.js ./

# Restore scrapely SDK + shims into ./node_modules (NODE_PATH is ignored for ESM
# imports; mirrors buildWorker's prebuilt-base shim restoration)
RUN mkdir -p node_modules/@alexrosulek \
    && ln -sf /opt/scrapely/node_modules/@alexrosulek/scrapely node_modules/@alexrosulek/scrapely \
    && mkdir -p node_modules/@crawlee \
    && rm -rf node_modules/@crawlee/core \
    && ln -sf /opt/scrapely/node_modules/@crawlee/core node_modules/@crawlee/core \
    && rm -rf node_modules/scrapely \
    && mkdir -p node_modules/scrapely \
    && cp -r /opt/scrapely/shims/scrapely/. node_modules/scrapely/ \
    && node -e "const fs=require('fs'),path=require('path');const link=path.resolve('node_modules/crawlee');if(!fs.existsSync(path.join(link,'package.json'))){const r=path.dirname(require.resolve('crawlee/package.json'));fs.mkdirSync(path.dirname(link),{recursive:true});fs.symlinkSync(r,link,'dir');}"

WORKDIR /actor

ENTRYPOINT ["node", "/actor/package/main.js"]
