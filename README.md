### About

Webapp to convert BibTeX (ORCID based) into HTML

### Install using Docker

* Install Docker
* ```bash git clone https://github.com/vdmitriyev/orcidtohtml.git```
* ```cd orcidtohtml```
* Build Docker image
	+ ```docker build -t orcidtohtml:latest .```
* Run created image
	+  ```docker run -d -p "127.0.0.1:5252:5252" --name orcidtohtml --restart unless-stopped orcidtohtml```
* Should run on ```localhost:5252```

### Nging Config (production deployment)

```
location /orcidtohtml/ {
    access_log /var/log/nginx/orcidtohtml-access.log;
    error_log /var/log/nginx/orcidtohtml-error.log;

    proxy_pass http://localhost:5252/;
    proxy_set_header Host "localhost";
}
```

### JabRef for BibTeX to HTML Export

* Manual on exporting BibTeX database to the HTML file with help of JabRef can be found in [jabref][jabref].

### Author

* Viktor Dmitriyev
