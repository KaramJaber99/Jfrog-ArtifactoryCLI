FROM ubuntu:latest


#installing git 
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

#Creating new folder in the ubuntu and cloaning our code into it to use it 
RUN mkdir /home/jfrog       
WORKDIR  /home/jfrog         
RUN git clone https://github.com/KaramJaber99/Jfrog-ArtifactoryCLI.git

RUN apt-get update && apt-get install -y --no-install-recommends \
    python\
    python3-pip

RUN pip install argparse

RUN python3 -m pip install urllib3


#Set working directory
WORKDIR /home/jfrog/Jfrog-ArtifactoryCLI

CMD ["python3", "./final_test.py" ,"-p", "--list", "pe16366karamj.jfrog.io", "karamj@jfrog.com", "Admin1234!"]