# Beacon

Nginx слухає порт 8080 у контейнері, а локальний порт 8468 опубліковано лише на 127.0.0.1. Головна сторінка та health.json містять ідентифікатор `devops6-beacon-58`, а `/missing-page` повертає 404.

## Запуск власного образу

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export BASE_URL=http://127.0.0.1:8468
export EXPECTED_RELEASE=devops6-beacon-58
export CHECK_TIMEOUT=3
docker build -t beacon-web:lab .
docker run -d --name beacon-web -p 127.0.0.1:8468:8080 beacon-web:lab
curl -fsS --max-time 2 --retry 5 --retry-all-errors "$BASE_URL/"
```

## Перевірки

```bash
python -m pytest -v --hosts=docker://beacon-web tests
python check_beacon.py
```

Справний варіант проходить 16 тестів. Testinfra перевіряє синтаксис Nginx, файли, режим доступу до index.html та ідентифікатор. HTTP-тести перевіряють статуси маршрутів і дані відповідей. Команда check_beacon повертає 0 для успіху, 1 для невдалої перевірки та 2 для тайм-ауту.

## Відтворення несправностей

Перед кожним дослідом перевір справний контейнер. Після команди внесення зміни й після відновлення повтори pytest та check_beacon.

| Сценарій | Команда внесення зміни | Відновлення |
| --- | --- | --- |
| Обмеження читання index.html | `docker exec beacon-web chmod 000 /opt/beacon/public/index.html` | `docker exec beacon-web chmod 644 /opt/beacon/public/index.html` |
| Неправильний код для /missing-page | Заміни `return 404;` на `return 200 "not found";` у `/etc/nginx/conf.d/default.conf` контейнера, виконай `nginx -t` і `nginx -s reload` через docker exec | `docker cp nginx/beacon.conf beacon-web:/etc/nginx/conf.d/default.conf`, потім `docker exec beacon-web nginx -s reload` |
| Пауза контейнера | `docker pause beacon-web` | `docker unpause beacon-web` |

Команда для відтворення неправильного HTTP-коду.

```bash
docker exec beacon-web sh -c 'sed -i "s/return 404;/return 200 \"not found\";/" /etc/nginx/conf.d/default.conf && nginx -t && nginx -s reload'
sleep 1
curl -sS --max-time 5 -w '\nHTTP %{http_code}\n' "$BASE_URL/missing-page"
```

Після дослідів видали контейнер командою `docker rm -f beacon-web`. Збірка із незмінених файлів проєкту відтворює справний варіант.

## Запуски CI

У `.github/workflows/beacon.yml` окремі завдання виконують unit-тести й перевірки живого контейнера. Підсумковий крок запускається після успіху обох завдань. Для контрольованого збою створіть гілку `beacon-route-check`, змініть код відсутнього ресурсу на 200, запуште коміт і запустіть workflow з цієї гілки через **Actions → Run workflow**. Наступним комітом поверніть 404 та повторіть ручний запуск. Артефакти `beacon-command-report` і `beacon-live-report` містять XML-звіти й журнали.

## Демо зі стандартним образом

```bash
docker build -t devops6-demo ./sample
docker run -d --name devops6-web -p 127.0.0.1:8080:80 devops6-demo
curl --fail --max-time 5 http://127.0.0.1:8080/
python -m pytest -v --hosts=docker://devops6-web sample/tests/infra
docker rm -f devops6-web
```
