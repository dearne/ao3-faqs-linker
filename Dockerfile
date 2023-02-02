FROM python:3

ADD requirements.txt /
RUN pip3 install -r requirements.txt

ADD ao3-faq-linker.py /
ADD credentials-sheets.json /

WORKDIR /srv/otw