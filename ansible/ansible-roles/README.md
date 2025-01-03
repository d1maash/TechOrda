# ansible-roles

В задании `ansible-apps` наш плейбук стал очень большим. Такое сложно поддерживать,
т.е. дописывать новые таски либо изменять что-то.

Чтобы четко разделить наши таски по тем задачам, которые они выполняют, нужно использовать
**Роли**.

Роли в Ansible используют для разбиения монолитного плейбука на раздельные шаги. Можно даже
представить, что роль - это как функция в программировании. Можно отдельно вынести определенные
операции и потом переиспользовать их.

Каждая роль представляет из себя маленький плейбук - также состоит из тасков, хендлеров, есть
свои файлы и шаблоны. Роль написана хорошо, если она служит для выполнения одной конкретной задачи.

## Структура ролей

```tree
└── nginx
    ├── meta
    ├── files
    │   └── nginx.conf
    ├── handlers
    │   └── main.yml
    └── tasks
        └── main.yml
```

В примере выше описана структура для роли nginx. В ней есть 4 директории:

- `meta` - _обязательная директория_, в ней хранится описание роли и какие переменные для нее требуются.
- `tasks` - _обязательная директория_, хранит основные таски роли.
- `files` - хранит файлы, которые можно, например, копировать с помощью `copy`.
- `handlers` - хранит хендлеры, которые могут вызываться из тасков.

Роли должны храниться в директории `roles`. Для примера выше, роль `nginx` будет
храниться так - `roles/nginx`.

```
roles/
    nginx/
playbook.yaml
```

Если вы создадите такую структуру папок, как показано выше, с файлом `main.yml` в
каждой директории - Ansible будет запускать все таски, определенные в `tasks/main.yml`.
Роль следует вызывать из плейбука, используя следующий синтаксис:

```yaml
---
- hosts: all
  become: yes

  roles:
    - nginx
```

### Полезное

- [Роли в Ansible](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html)

### Задание

1. В репозитории `jusan-ansible` создайте ветку `roles`, которая исходит от ветки `apps`.
   Вести работу будем в ней.
2. Создайте 3 роли:
   - `nginx` для установки nginx;
   - `nginx-configuration` для настройки nginx - nginx.conf и добавление сервер блоков;
   - `application` для установки `api` сервиса.
3. В каждой роли создайте требуемую структуру директорий: `tasks`, `meta` и т.д.
4. Перенесите таски и хендлеры из `playbook.yaml` в подходящие роли.
5. Для каждой роли в папке `meta` добавьте описание роли в `short_description`.
6. В итоге `playbook.yaml` должен выглядеть следующим образом:

```yaml
---
- hosts: lb
  become: true
  roles:
    - nginx
    - nginx-configuration

- hosts: app
  become: true
  roles:
    - application
```

7. Запустите и проверьте на работоспособность.
8. Запушить в гит.

P.S. Для того чтобы отдельно не создавать одни и те же папки для каждой роли - можно
использовать хитрости bash, чтобы разом создать одни и те же папки для каждой роли.

```bash
mkdir -p roles/{nginx,nginx-servers,application}/{tasks,handlers,files,templates,meta}
```

Чтобы проверить правильно ли запущено все, запустите тестировщик [checker-apps.sh](https://stepik.org/media/attachments/lesson/698792/checker-apps.sh).

```bash
bash checker-apps.sh
```

---

### Ответ


#### main.yaml

```yaml
# roles/nginx/tasks/main.yml
---
- name: Install Nginx
  ansible.builtin.apt:
    name: nginx
    state: present

# roles/nginx/handlers/main.yml
---
- name: reload-nginx
  ansible.builtin.service:
    name: nginx
    state: reloaded

# roles/nginx/meta/main.yml
---
galaxy_info:
  role_name: nginx
  description: "Role to install and manage Nginx"

```

```yaml
# roles/nginx-configuration/tasks/main.yml
---
- name: Copy nginx.conf
  ansible.builtin.copy:
    src: nginx.conf
    dest: /etc/nginx/nginx.conf
  notify: reload-nginx

- name: Remove default.conf
  ansible.builtin.file:
    path: /etc/nginx/conf.d/default.conf
    state: absent

- name: Create server blocks from templates
  ansible.builtin.template:
    src: server.conf.j2
    dest: /etc/nginx/conf.d/{{ item.server_name }}.conf
  loop:
    - server_port: 80
      server_name: jusan-apps.kz
      apps:
        - local-vps-23:9090
        - local-vps-24:9090
  notify: reload-nginx

# roles/nginx-configuration/meta/main.yml
---
galaxy_info:
  role_name: nginx-configuration
  description: "Role to configure Nginx with custom server blocks"

```


```yaml
# roles/application/tasks/main.yml
---
- name: Download API binary
  ansible.builtin.get_url:
    url: https://github.com/jusan-singularity/track-devops-systemd-api/releases/download/v0.1/api
    dest: /tmp/api
    mode: '0755'

- name: Deploy API service
  ansible.builtin.copy:
    src: api.service
    dest: /etc/systemd/system/api.service

- name: Enable and start API service
  ansible.builtin.systemd:
    name: api
    enabled: true
    state: started

# roles/application/meta/main.yml
---
galaxy_info:
  role_name: application
  description: "Role to manage the application service"

```


```yaml
---
- hosts: lb
  become: true
  roles:
    - nginx
    - nginx-configuration

- hosts: app
  become: true
  roles:
    - application
```