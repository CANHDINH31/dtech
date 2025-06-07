# Tạo môi trường ảo (khuyến khích)

```
python -m venv venv
source venv/bin/activate # trên Linux/macOS
venv\Scripts\activate # trên Windows
```

# Cài Django và Django REST Framework

```
pip install django djangorestframework
```

# Tạo project mới

```
django-admin startproject dtech
cd dtech
```

# Tạo app mới

```
python manage.py startapp core
```

# requirements

```
pip freeze > requirements.txt
pip install -r requirements.txt
```

# runserver

```
python manage.py migrate
python manage.py runserver
```

## Deploy

`gunicorn yourproject.wsgi:application --bind 0.0.0.0:8000`

`sudo nano /etc/systemd/system/gunicorn.service
sudo systemctl daemon-reexec
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
 sudo systemctl enable gunicorn
`

`sudo systemctl restart gunicorn
sudo systemctl status gunicorn`
