# ansible-vault

При использовании Ansible для автоматизации серверов, скорее всего, вам потребуется
использовать пароли или другие конфиденциальные данные для некоторых задач,
будь то установка пароля администратора или запись секретного ключа в конфигурации и т.д.

Такие данные можно хранить в обычном файле переменных `vars/main.yml`. Но в таком случае
доступ к данным может получить любой, у кого есть доступ к плейбукам.
К паролям и конфиденциальным данным лучше относиться особо осторожно.

Используйте Ansible Vault, который встроен в Ansible и хранит зашифрованные пароли и
другие конфиденциальные данные вместе с остальной частью плейбука.

Ansible Vault работает следующим образом:

1. Берем переменные, которые хотим зашифровать и сохраняем в файл [переменных](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#variable-precedence-where-should-i-put-a-variable).
2. Ansible шифрует файл с переменными с помощью ключа (пароль).
3. Ключ (пароль) хранится отдельно от плейбука в том месте, к которому только вы имеете доступ.
4. Ключ используется, чтобы Ansible расшифровывал зашифрованный файл каждый раз, когда запускается плейбук.

Посмотрим, как это работает на практике. Вот плейбук в файле `main.yml`, который
использует ключ-токен к API. Такие ключи надо хранить в Vault, чтобы у других не было
к нему доступа.

```yaml
---
- hosts: all

  vars_files:
    - vars/api_key.yml # <----- читаем переменные из vars/api_key.yml

  tasks:
    - name: Выводим секретный ключ!
      shell: echo $API_KEY
      environment:
        API_KEY: "{{ secret_token }}" # <---- передаем наш токен в команду
```

Файл `vars/api_key.yml`, который хранится вместе с плейбуком в папке `vars`, выглядит так:

```yaml
---
secret_token: "EoechC2a5DqK"
```

Это удобно, но небезопасно хранить ключ от API в виде простого текста.
Даже при локальном запуске плейбука на своем компьютере секреты должны быть зашифрованы.

Чтобы зашифровать файл с помощью Vault, запустите:

```bash
ansible-vault encrypt vars/api_key.yml
```

Vault потребует ввести пароль для файла, и Ansible зашифрует его.
Если открыть зашифрованный файл, то вывод будет примерно таким:

```
$ANSIBLE_VAULT;1.1;AES256
31356363383765333065663934373432353462613736303265663533343763376338373731303933
6663363834393264306662383032633837386163316363630a313363626336636361373330343036
31636663376533643761613964616261323163643365343936386430333334376664323062303732
3863656233353966340a396238613538313539663839623535323831353632346431343735653837
62356234636538366364363466393839366630656537303930643830343137393635
```

В следующий раз, когда запустится плейбук, нужно будет ввести пароль, который был использован
для шифрования. Ansible тогда расшифрует файл на короткий период, в течение которого он будет
использоваться. Если не указать пароль, то выйдет сообщение об ошибке:

```bash
$ ansible-playbook main.yml
ERROR: A vault password must be specified to decrypt vars/api_key.yml
```

Чтобы ввести пароль, нужно запустить плейбук с ключом `--ask-vault-pass`.

```bash
$ ansible-playbook main.yml --ask-vault-pass
Vault password:
```

Можно редактировать зашифрованный файл с помощью `ansible-vault edit`.
Также можно изменить пароль файла, создать новый файл, просмотреть существующий файл
или расшифровать файл.

### Полезное

- [Документация Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html)

### Задание

1. В репозитории `jusan-ansible` создайте ветку `vault`, которая исходит от ветки `roles`.
   Вести работу будем в нем.
2. Создать `/vars/nginx_secret_token.yaml`, который содержит переменную `secret_token` со
   значением `Jusan Singularity`.
3. Зашифруйте этот файл через `ansible-vault` с паролем `kazakhstan2022`.
4. Создайте шаблон `Jinja2` в роли `nginx-configuration`, который принимает переменные и
   генерит конф. сервер блока:

   - `server_port` - порт сервер блока
   - `server_name` - домен сервер блока
   - `secret` - в сервер блоке есть `location /`, который возвращает строку из `secret_token`.

5. В `nginx-configuration` создайте новый `template` таск, который принимает переменные и
   записывает конфигурацию в нужный путь:

   - `server_port: 9090`
   - `server_name: jusan-secret.kz`
   - `secret: "{{ secret_token }}"`

6. В плейбуке `playbook.yaml` прочитать `vars/nginx_secret_token.yaml` и передать переменную в
   `nginx-configuration`.
7. Запустите и проверьте на работоспособность.
8. Запушить в гит.

Чтобы проверить правильно ли запущено все, запустите тестировщик [checker-vault.sh](https://stepik.org/media/attachments/lesson/698792/checker-vault.sh).

```bash
bash checker-vault.sh
```

---

### Ответ

#### nginx-secret-token.yaml

```yaml
mkdir vars
echo -e "---\nsecret_token: \"Jusan Singularity\"" > vars/nginx_secret_token.yaml
ansible-vault encrypt vars/nginx_secret_token.yaml --vault-password-file=<(echo "kazakhstan2022")
```

#### server_secret.conf.j2
```nginx
server {
    listen {{ server_port }};
    server_name {{ server_name }};

    location / {
        return 200 "{{ secret }}";
    }
}

```

#### main.yaml

```yaml
- name: Generate server block with secret
  ansible.builtin.template:
    src: server_secret.conf.j2
    dest: /etc/nginx/conf.d/{{ server_name }}.conf
  vars:
    server_port: 9090
    server_name: jusan-secret.kz
    secret: "{{ secret_token }}"
  notify: reload-nginx
```

#### playbook.yaml

```yaml

---
- hosts: lb
  become: true

  vars_files:
    - vars/nginx_secret_token.yaml

  roles:
    - nginx
    - nginx-configuration

- hosts: app
  become: true
  roles:
    - application

```

```bash
ansible-playbook playbook.yaml --vault-password-file=<(echo "kazakhstan2022")
```