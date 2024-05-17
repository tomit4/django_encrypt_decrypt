# Proof Of Concept (File Uploader/Downloader Encryption/Decryption with Django)

## Introduction

This repository contains Proof Of Concept(POC) Code to later be integrated into
a larger group project. Utilizing Django and Basic HTML and JavaScript, this
repository demonstrates the basic uploading of image files (only jpg as of right
now) to a Django Server. Upon Upload the image is encrypted and the unencrypted
image is deleted. Upon Viewing of the images, all encrypted images are decrypted
and then displayed to the user. Again, the decrypted images are deleted after
the Django route is hit.

### Installation

Since this repository is mainly meant to be utilized by participants within the
group project, I'll not go into the details regarding what knowledge is
necessary to get started, and will rather move quickly on how to install and get
this project up and running.

**Clone This Repo:**

```sh
git clone https://github.com/tomit4/django_encrypt_decrypt && cd django_encrypt_decrypt/backend
```

**Activate Virtual Environment:**

Once inside the repository's backend, you'll need to first activate a python
virtual environment:

```sh
python3 -m virtualenv myproject_venv && source myproject_venv/bin/activate
```

**Dependencies and Env Vars:**

You'll then need to install the required dependencies and establish the needed
environment variables:

```sh
pip install -r requirements.txt && cp env-sample .env
```

**Starting up the PostgreSQL DB in Docker:**

This project's base uses PostgreSQL DB inside of Docker, you'll need to compose
the docker container with the PostgreSQL DB running inside of it, then use
Django's `manage.py` to migrate the DB's defaults:

```sh
docker-compose -f ./docker-compose.yml up -d
```

Then migrate the DB defaults:

```sh
python manage.py makemigrations && python manage.py migrate
```

**Start Up the Backend Server:**

Simply start the django backend:

```sh
python manage.py runserver
```

**Start Up The Frontend Server:**

In another terminal, navigate to the frontend directory and start up VSCode,
opening up the `index.html` file:

```sh
cd django_encrypt_decrypt/frontend && code index.html
```

Activate the [Live Server Extension](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) which will serve the index.html.

### Uploading Files

Following the <b>Upload</b> Link, you'll find yourself on a basic HTML page
which will allow you to <b>Browse</b> your File System and Choose an image file
(right now only `.jpg` extension is accepted). Once you have selected the image,
the browser should preview the image for you to view. You can then click on
the <b>Upload Image</b> button, which will upload the image to the Django
Server. You can upload many images in this fashion if you'd like.

### Viewing Your Gallery

Once you have uploaded the image(s), you can view them by returning via the
<b>Home</b> button and then clicking on the <b>Gallery</b> button. This page
will simply display the images you have uploaded.

**Where Images Are Stored:**

Currently, all encrypted images, and their respective IV files, are located in
the project's `backend/media/images` folder. Note that upon both upload and
viewing(download) of image files, the original `.jpg` files are removed, this is
to enforce the fact that in the group project, the original images are not
stored on disk.

**NOTE:**

In the final application, it would be <em>highly</em> preferable that the image
be encrypted and decrypted in such a way that the original file is never saved
to hard disk at all. This is a security/privacy feature, but requires a bit more
inspection into the encryption/decryption algorithms used and an integration of
said algorithms with the network calls themselves to get it right.

### Files Of Note:

Should you wish to inspect the logic of how this POC was accomplished, look at
the following files for the related code:

- backend/upload/views.py (backend routing and logic)
- frontend/upload.html (frontend upload logic)
- frontend/gallery.html (frontend download/viewing logic)
