### About

A webapp to convert BibTeX (from the ORCID) into a HTML.

### Install using Docker

> Prerequisite: [taskfile](https://taskfile.dev/) should be installed. Otherwise just take commands from the `yaml` files.

* Clone repo
	```bash 
	git clone https://github.com/vdmitriyev/orcidtohtml.git
	```
* Go to folder
	```
	cd orcidtohtml
	```	
* Build Docker image
	```
	task build
	```
* Run container
	```
	task up	
	```
* The service should be available on:
	```
	http://localhost:5252
	```

### Production Deployment

Use the following nginx config to deploy the Docker Container in production

```
location /orcidtohtml/ {
    access_log /var/log/nginx/orcidtohtml-access.log;
    error_log /var/log/nginx/orcidtohtml-error.log;

    proxy_pass http://localhost:5252/;
    proxy_set_header Host "localhost";
}
```

### JabRef for BibTeX to HTML Export

* Manual on exporting BibTeX database to the HTML file with help of JabRef can be found in [jabref](jabref).

### License

MIT
