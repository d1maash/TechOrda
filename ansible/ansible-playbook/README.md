# ansible-playbook

Задание данного модуля проверяются в конце ментором. Это первая часть проекта. Сделав это задание, переходите к следующему.

### Полезное

- [Модуль apt в Ansible](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/apt_module.html)
- [Модуль service в Ansible](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/service_module.html)

### Задание

1. Для сдачи данного модуля создайте репозиторий в ([ССЫЛКА GITHUB CLASSROOM]). Вести работу будем в нем.
2. Создайте скрипт `setup.sh`, который будет запускать контейнеры для Ansible:
   - запускает образ `atlekbai/local-vps` с именем контейнера `local-vps-22` и перенаправялет порты 22 и 80 внутрь контейнера;
   - устанавливает на сервер ssh-ключ.
3. Проверьте ssh подключение `ssh root@127.0.0.1`, авторизация должна происходить без пароля.
4. Создайте инвентори файл `hosts.ini`, в котором есть группе под названием `lb`. В группе записан наш сервер.
5. Создать плэйбук `playbook.yml`, который:
   - работает с хостами из группы `lb`;
   - содержит таск по установке `nginx` через `apt`;
   - содержит таск по запуску сервиса `nginx` - `started`, `enabled`;
6. Запустите плейбук с указанием инвентори файла.
7. Проверьте, что запрос на сервер работает `curl http://127.0.0.1`
8. Запушьте файлы `setup.sh`, `hosts.ini`, `playbook.yml` в гит.

---

### Ответ

#### Setup.sh
```bash
#!/bin/bash

docker run -d \
  --name local-vps-22 \
  -p 22:22 \
  -p 80:80 \
  atlekbai/local-vps
sleep 5

docker exec -i local-vps-22 bash -c "mkdir -p /root/.ssh && chmod 700 /root/.ssh"
docker cp ~/.ssh/id_rsa.pub local-vps-22:/root/.ssh/authorized_keys
docker exec -i local-vps-22 bash -c "chmod 600 /root/.ssh/authorized_keys"

ssh -o StrictHostKeyChecking=no root@127.0.0.1 exit

echo "Setup complete. You can now SSH into the container."
```

#### hosts.ini
```ini
[lb]
127.0.0.1 ansible_connection=ssh ansible_user=root ansible_ssh_private_key_file=~/.ssh/id_rsa
```

#### playbook.yml
```yaml
- name: Configure Load Balancer
  hosts: lb
  become: yes
  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: present
        update_cache: yes

    - name: Ensure nginx is started and enabled
      service:
        name: nginx
        state: started
        enabled: yes
```
#### Run playbook

```bash
ansible-playbook -i hosts.ini playbook.yml
```
