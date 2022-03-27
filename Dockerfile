FROM ubuntu:20.04
ADD . /



RUN apt update
RUN apt install python3 -y
RUN apt-get update
RUN apt-get -y install python3-pip
RUN pip3 install argparse
RUN pip3 install urllib3

#Creating new folder in the ubuntu and cloaning our code into it to use it 
RUN mkdir /home/jfrog
RUN mv /final_test.py /home/jfrog/final_test.py
RUN mv /config.json /home/jfrog/config.json


#Set working directory
WORKDIR /home/jfrog

CMD ["python3", "./final_test.py" ,"-v", "--list", "pe16366karamj.jfrog.io", "karamj@jfrog.com", "Admin1234!"]