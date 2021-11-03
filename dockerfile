FROM debian:buster

RUN apt update \
    && apt install -y \
    autoconf \
    automake \
    build-essential \
    git \
    libtool \
    libgmp-dev \
    libmpfr-dev \
    libqd-dev \
    make \
    pkg-config \
    python3-dev \
    python3-pip \
    wget \
    && apt clean


# Download and build Valgrind
WORKDIR /root
RUN wget 'ftp://sourceware.org/pub/valgrind/valgrind-3.15.0.tar.bz2' \
    && tar xf valgrind-3.15.0.tar.bz2 \
    && rm -rf valgrind-3.15.0.tar.bz2

RUN git clone https://github.com/SideChannelMarvels/Tracer
RUN cp -r Tracer/TracerGrind/tracergrind valgrind-3.15.0 \
    && patch -p0 < Tracer/TracerGrind/valgrind-3.15.0.diff

WORKDIR /root/valgrind-3.15.0
RUN ./autogen.sh \
    && ./configure \
    && make -j4 \
    && make install

# copy the hwmemtrace tool
COPY ./hwmemtrace /root/Tracer/TracerGrind/hwmemtrace
WORKDIR /root/Tracer/TracerGrind/hwmemtrace
RUN make && make install


# fplll
WORKDIR /root
RUN git clone --branch master https://github.com/fplll/fplll && \
    cd fplll && \
    autoreconf -i && \
    ./configure --prefix=/usr && \
    make -j4 install

# fpylll
WORKDIR /root
RUN git clone --branch master https://github.com/fplll/fpylll && \
    cd fpylll && \
    pip3 install Cython && \
    pip3 install -r requirements.txt && \
    python3 setup.py build && \
    python3 setup.py -q install

# scikit-learn
RUN pip3 install -U scikit-learn


# OpenSSL
WORKDIR /root
RUN wget -O - -nv "https://www.openssl.org/source/openssl-1.1.1k.tar.gz" 2>/dev/null | tar xzv > /dev/null

WORKDIR /root/openssl-1.1.1k
RUN ./config 2>/dev/null && \
    make -j 2>/dev/null &&  \
    make -j install_sw 2>/dev/null && \
    echo "export LD_LIBRARY_PATH=/usr/local/lib" >> /root/.bash_profile


# copy the Python scripts for simulation and analysis and sample data
COPY ./scripts /root/ecdummyrpa
COPY ./sample.tar.gz /root/ecdummyrpa/
WORKDIR /root/ecdummyrpa


