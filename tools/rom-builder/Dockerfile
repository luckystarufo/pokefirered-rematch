# ROM build toolchain for game/ (pret/pokefirered).
# Follows game/INSTALL.md "Debian/Ubuntu" + "Install agbcc" sections.
# Reused later as the CI build image (step 5.1).

# --- Stage 1: build Poryscript (a Go program) from a pinned tag -------------
# Poryscript compiles our .pory scripts into the decomp's .inc assembly macros.
# Built from source because its release zips don't state the CPU architecture.
FROM golang:1.23-bookworm AS poryscript
ARG PORYSCRIPT_TAG=3.6.1
RUN git clone --depth 1 --branch "$PORYSCRIPT_TAG" https://github.com/huderlem/poryscript /src \
 && cd /src && CGO_ENABLED=0 go build -o /out/poryscript .

# --- Stage 2: the actual build image ---------------------------------------
FROM ubuntu:24.04

# build-essential  -> gcc/g++/make for the host-side helper tools (gbagfx, scaninc, ...)
# binutils-arm-none-eabi -> the GBA assembler + linker (as, ld, objcopy)
# libpng-dev       -> needed by gbagfx to turn PNGs into GBA graphics
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      build-essential binutils-arm-none-eabi git libpng-dev ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# agbcc = the period-accurate C compiler that makes the build byte-identical.
# Pinned to a commit so every build (laptop or CI) uses the same compiler.
ARG AGBCC_COMMIT=da598c1d918402c42c0c0d7128ba14567f3175e9
RUN git clone https://github.com/pret/agbcc /opt/agbcc-src \
 && cd /opt/agbcc-src \
 && git checkout "$AGBCC_COMMIT" \
 && ./build.sh \
 && mkdir -p /opt/agbcc-dist \
 && ./install.sh /opt/agbcc-dist \
 && rm -rf /opt/agbcc-src
# install.sh puts the compiler in /opt/agbcc-dist/tools/agbcc/{bin,include,lib}

COPY --from=poryscript /out/poryscript /opt/poryscript/poryscript

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

WORKDIR /work
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["make"]
