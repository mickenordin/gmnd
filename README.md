# gMNd
gMNd is my gemini server, which is written in python. It has support for serving static files, or run cgi-scripts. Documentation will primarily be supplied via [gemini://mic.ke/gmnd/docs](gemini://mic.ke/gmnd/docs), but if you are not yet able to access content via gemini, here is a quick start guide for your viewing pleasure:

## Installation
Please use supplied debian and rpm repos. Packages are signed with gpg.

### DEB
```
curl https://repo.mic.ke/PUBLIC.KEY | sudo apt-key add -
curl https://repo.mic.ke/debian/debian-micke-unstable.list | sudo tee /etc/apt/sources.list.d/debian-micke-unstable.list
sudo apt update && sudo apt install gmnd
```



### RPM
```
wget https://repo.mic.ke/PUBLIC.KEY
sudo rpm --import PUBLIC.KEY
sudo dnf config-manager --add-repo https://repo.mic.ke/rpm/rpm-micke.repo
sudo dnf install gmnd
```

### Docker

You can build and run it from the supplied Dockerfile if you so whish:
```
docker build -t gmnd:latest .
```
By just running it, it will create self signed certs and serve example content from this repo:
```
docker run -p 1965:1965 gmnd
```
A slightly more interesting thing it can do is serve your own content, in this example from /tmp/content on your host machine and cgi-scripts from /tmp/cgi-bin:
```
docker run --mount type=bind,source="/tmp/content,target=/app/content" --mount type=bind,source="/tmp/cgi-bin,target=/app/cgi-bin" -p 1965:1965 gmnd
```
Or even supply your own certificates from the outside, in this example in /usr/local/certs with static content from /tmp/content:
```
docker run --mount type=bind,source="/tmp/content,target=/app/content" --mount type=bind,source="/usr/local/certs,target=/app/certs" -p 1965:1965 gmnd
```
