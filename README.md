# Проект Yatube

## Описание:
Создание тематических групп, публикации в них постов  с возможностью подписаться на авторов,
оставлять комментарии под записями.


## Запуск проекта:

1. Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/il-mo/hw05_final
```

```
cd yatube
```

2. Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source env/bin/activate
```

3. Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

4. Выполнить миграции:

```
python manage.py migrate
```

5. Запустить проект:

```
python manage.py runserver
```
## Cтек технологий

<img src="https://camo.githubusercontent.com/1d60a65352c961dc0bc3bfcddb926a34787b47ffced9bcadeaea32962297ef5a/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d507974686f6e2d3035313232413f7374796c653d666c6174266c6f676f3d707974686f6e"> <img src="https://camo.githubusercontent.com/e3b0a2acde2315cf6389d5f30fc1ad13d74a087554a28d5193a2131d4e79d180/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d446a616e676f2d3035313232413f7374796c653d666c6174266c6f676f3d646a616e676f266c6f676f436f6c6f723d303932453230"> <img src="https://camo.githubusercontent.com/d738d76484d50c8345c2d01e39364b707285bc7936140858e7909dfe6424efb2/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d4353532d3035313232413f7374796c653d666c6174266c6f676f3d43535333266c6f676f436f6c6f723d313537324236"> <img src="https://camo.githubusercontent.com/c8d13e1c596a6726b1da8475a9299fac133f95ef009083b48be01f975a44987e/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d48544d4c2d3035313232413f7374796c653d666c6174266c6f676f3d48544d4c35"> <img src="https://camo.githubusercontent.com/1a3d592707d940e585ac708278cf93823ccf24115714e2b90d27165c2abac401/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d426f6f7473747261702d3035313232413f7374796c653d666c6174266c6f676f3d626f6f747374726170266c6f676f436f6c6f723d353633443743"> 


## Тесты:
Чтобы запустить тесты, перейдите в каталог `cd`, в котором находится файл `manage.py`:
```sh
(env)$ python manage.py test 
```
