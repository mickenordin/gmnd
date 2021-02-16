# gMNd
gMNd is my gemini server, which is written in python.

Currently it only serves static files. You can build and run it from the supplied Dockerfile if you so whish:
```
docker build -t gmnd:latest .
```
By just running it, it will create self signed certs and serve example content from this repo:
```
docker run -p 1965:1965 gmnd
```
A slightly more interesting thing it can do is serve your own content, in this example from /tmp/content on your host machine:
```
docker run --mount type=bind,source="/tmp/content,target=/app/content" -p 1965:1965 gmnd
```
Or even supply your own certificates from the outside, in this example in /usr/local/certs:
```
docker run --mount type=bind,source="/tmp/content,target=/app/content" --mount type=bind,source="/usr/local/certs,target=/app/certs" -p 1965:1965 gmnd
```
