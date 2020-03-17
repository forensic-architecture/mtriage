RUN pip install -e git+https://github.com/twintproject/twint.git@origin/master#egg=twint
RUN cd /mtriage/src/twint && python setup.py install
