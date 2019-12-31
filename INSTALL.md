## Installation
### Requirements:
- [python>=3.5](https://www.python.org/downloads/)
- [mongodb](https://www.mongodb.com/download-center/community)
### Linux
```
git clone https://github.com/lyl472324464/AI-analyse-of-class-video.git
cd AI-analyse-of-class-video
wget -O test.zip 'https://data.xyzgate.com/e973eb8dc7e90aeb1de41870e3b6376f.zip'
unzip test.zip
mongorestore -d test test
pip install tornado numpy
```
