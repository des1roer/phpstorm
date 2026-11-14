# phpstorm

Свой репозиторий плагинов JetBrains (Custom Plugin Repository) для случаев, когда Marketplace из IDE недоступен, но архивы плагинов скачать можно.
IDE читает `updatePlugins.xml` и ставит или обновляет плагины по ссылкам из него, как из Marketplace.

Репозиторий: https://github.com/des1roer/phpstorm (**публичный**), ветка `main`. Клон лежит в WSL: `~/proj/phpstorm`.

## Файлы

| Путь | Что это |
|---|---|
| `*.zip`, `*.jar` в корне | архивы плагинов, по одной версии каждого |
| `updatePlugins.xml` | индекс для IDE, генерируется, хранится в git |
| `tools/gen_update_plugins.py` | генератор индекса, только стандартная библиотека Python |
| `tools/serve.sh` | запасная локальная раздача на `http://localhost:8765` |
| `grazie/*.jar` | языковые пакеты Grazie, не плагины |

## Подключение в IDE

Settings → Plugins → ⚙ → Manage Plugin Repositories → `https://raw.githubusercontent.com/des1roer/phpstorm/main/updatePlugins.xml`

## Добавить или обновить плагин

1. Проверить метаданные и совместимость, не копируя архив в репо:
   ```bash
   mkdir -p /tmp/newplugins && cp /mnt/d/chrome/<file>.zip /tmp/newplugins/
   python3 -I tools/gen_update_plugins.py --dir /tmp/newplugins --out /tmp/newplugins/check.xml --build 263.7307.215
   ```
2. Скопировать архив в корень (`install -m 644`), старую версию того же плагина удалить через `git rm`. Две версии одного id в индексе не держать.
3. Имена файлов без пробелов и скобок: браузер сохраняет `name (2).zip`, такой суффикс убирать.
4. Пересобрать индекс: `python3 -I tools/gen_update_plugins.py --build 263.7307.215`.
5. Закоммитить архивы вместе с `updatePlugins.xml` и запушить.
6. Проверить без авторизации: `updatePlugins.xml` и архив по raw-ссылке отдают 200, размер совпадает с исходным файлом.

Билд IDE пользователя: PhpStorm 2026.3, `263.7307.215` (`C:\Program Files\JetBrains\PhpStorm 2026.3\product-info.json`).

## Устройство генератора

- `read_plugin_xml()` ищет `META-INF/plugin.xml` в самом архиве (jar) или в `<Plugin>/lib/*.jar` внутри zip.
- id берётся из `<id>`, при его отсутствии из `<name>`. У PlantUML id действительно `PlantUML integration`.
- `since-build` и `until-build` копируются из `<idea-version>`, по ним IDE отсекает несовместимые версии.
- `--base-url` по умолчанию `https://raw.githubusercontent.com/des1roer/phpstorm/main`; `serve.sh` пишет отдельный `updatePlugins.local.xml` (в `.gitignore`) с localhost-ссылками.
- `--build` печатает `ok` / `INCOMPATIBLE` для каждого плагина.

## Подводные камни

- Индекс не перегенерирован после добавления архива: IDE новую версию не увидит. Всегда коммитить архив и `updatePlugins.xml` вместе.
- Raw-ссылки работают только пока репозиторий публичный. В приватном raw отдаёт 404, а GitHub Pages на бесплатном плане недоступен.
- `grazie/ru-*.jar` содержит LanguageTool без `plugin.xml`, генератор его пропускает. Ставится копированием в `%APPDATA%\JetBrains\PhpStorm2026.3\grazie\` и перезапуском IDE.
- Mermaid 0.0.26 (до 261.\*) и One Dark theme (до 251.\*) несовместимы с билдом 263, нужны новые версии.
- InfinityFree и похожий бесплатный PHP-хостинг не подходят: JS-проверка от ботов ломает загрузку из IDE, лимит 10 МБ на файл.
- История схлопнута в один коммит перед публикацией. Старая история сохранена в `~/backups/phpstorm-history-7e0c0a3.bundle` (WSL). Старые коммиты пока доступны на GitHub по прямому хешу; полностью убрать можно через поддержку GitHub или пересоздание репо, только с согласия пользователя.

## Окружение и правила

- Клон в WSL; команды запускать через `wsl.exe -d Ubuntu -- bash -s <<'EOF' ... EOF`, git тоже внутри WSL.
- Windows-программы из WSL (`curl.exe` и т. п.) съедают stdin скрипта `bash -s`: вызывать их с `< /dev/null`.
- Фоновый процесс, запущенный в одном вызове `wsl.exe`, завершается вместе с ним; сервер и проверки держать в одном скрипте.
- Все файлы с LF. Комментарии в коде не добавлять.
- Сообщения коммитов на английском. Пушить в `main` по просьбе пользователя; force-push и смену видимости репо только с явного согласия.
