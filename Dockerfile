FROM ubuntu

# install ubuntu packages
RUN apt-get update
RUN apt-get install -y cmake python-bs4 python-pip python-dev
RUN pip install pyastyle

# prepare working directory
ADD . /usr/local/tpm
WORKDIR /usr/local/tpm

# change settings
RUN echo 'SET = True' >> scripts/settings.py

# prepare build
RUN mkdir -p build
WORKDIR /usr/local/tpm/build

# extract source
RUN cmake -G "Unix Makefiles" ../cmake -DCMAKE_BUILD_TYPE=Debug -DSPEC_VERSION=116

# build
RUN make

# expose ports
EXPOSE 2321
EXPOSE 2322

# cmd
ENTRYPOINT ["/usr/local/tpm/build/Simulator"]
