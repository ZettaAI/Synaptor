FROM ranlu/pytorch_base:2.2

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && echo "[GoogleCompute]\nservice_account = default" > /etc/boto.cfg \
    && git clone -b v1dd https://github.com/ZettaAI/Synaptor.git /Synaptor \
    && printf "[build-system]\nrequires = [\"setuptools\", \"wheel\", \"pybind11\"]\nbuild-backend = \"setuptools.build_meta\"\n" > /Synaptor/pyproject.toml \
    &&  conda install -c conda-forge -c defaults \
        python-igraph h5py pandas \
        scipy sqlalchemy \
    && pip --no-cache-dir install --upgrade gsutil task-queue==2.12.0 cirrus-volume simplejpeg==1.7.6 \
    && pip install git+https://github.com/ZettaAI/kombu-worker \
    && pip install -e /Synaptor \
    && conda clean -t -p

WORKDIR /Synaptor/scripts
ENTRYPOINT ["./entrypoint.sh"]
