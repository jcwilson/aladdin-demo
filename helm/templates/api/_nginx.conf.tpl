{{/* Config file for nginx */}}

# Note: This define name is global, if loading multiple templates with the same name, the last
# one loaded will be used.
{{ define "nginx-config" -}}

# Specify some event configs
events {
    worker_connections 4096;
}

http {
    # Create a server that listens on the nginx port
    server {
        listen {{ .Values.api.nginx.port }};

        # Match incoming request uri with these prefixes and route them to the api uvicorn app
        location ~ ^/(ping|app|_api) {
            proxy_set_header Host $http_host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
            proxy_buffering off;
            proxy_pass http://api;
        }

        # Otherwise, nginx tries to serve static content. The only file should exist is index.html,
        # which is written by the initContainer. Get requests with "/" or "/index.html" will return
        # a short message, everything else will return 404
        location / {
            root /usr/share/nginx/html;
            index index.html;
        }
    }

    # The univorn upstream definition
    upstream api {
{{ if .Values.api.uvicorn.autoreload }}
        # UVICORN_AUTORELOAD is true
        # It only works over http, though
        server 127.0.0.1:{{ .Values.api.uvicorn.port }} ;
{{ else }}
        # UVICORN_AUTORELOAD is false
        server unix:/run/socks/{{ .Values.api.uvicorn.domainSocket }};
{{ end }}
    }
}

{{ end }}
