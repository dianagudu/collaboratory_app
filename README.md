# S3 Credentials App

HBP Collaboratory app for retrieving the S3 credentials necessary to access the
S3 storage at KIT.

### Setup

```bash
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```

### Configuration

Copy .env-sample to .env and fill in the required values. Register an OIDC
client at the following url to get a "Client ID" and a "Client Secret":

https://collab.humanbrainproject.eu/#/collab/54/nav/1051
