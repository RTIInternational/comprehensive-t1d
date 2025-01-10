# Comprehensive Diabetes Simulation Model - Backend

This repository contains the python code for the comprehensive diabetes simulation model. This repository is maintained by RTI staff including Rainer Hilscher, Alex Harding, Andy Kawabata and Manuel Alvarado.

## Running
This repository is intended to be run as part of a larger system - whether that be the internal orchestration using `docker-compose` for local development at RTI, or the ECPAAS infrastructure at CDC. See `Dockerfile.dev` for the intended containerization of this repository, which depends on a few other containers (notably redis and postgresql).

This repository builds as a single image, but has dual purpose:

* To run this image as a webserver using tornado to operationalize the model run the following command:
```bash
. ./runner.sh
```

* To run this image as a worker container intended to run tasks off of the redis queue, run the following command:
```bash
celery -A src.orchestration.asynchronous_orchestrator worker -l info -n default@%h
```

Note that in a fully deployed application, both of these services are expected to run.

## Elevating user privileges
To access the admin panel, users need to be elevated to superuser status. If no user has access to the admin panel, you can elevate a user to superuser status by doing the following:

0) Obtain the username of the user you want to elevate to superuser status
1) Open a shell in the backend container called `comprehensive_model_tornado`
2) Navigate to app root with `cd src/webserver/`
3) Run the following command to open the Django shell:

   ```bash
   python manage.py shell
   ```
4) In the Django shell, use the following Python commands to update the user's superuser status. Be sure to replace `'username'` with actual username:

   ```python
   from django.contrib.auth.models import User
   user = User.objects.get(username='username')
   user.is_superuser = True
   user.is_staff = True
   user.save()
   ```  
5) Exit the Django shell with `exit()`