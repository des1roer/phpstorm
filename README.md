# phpstorm

## Свой репозиторий плагинов

Плагины (`*.zip`, `*.jar`) лежат в корне репо. IDE ставит и обновляет их как из Marketplace.

В IDE: **Settings → Plugins → ⚙ → Manage Plugin Repositories → +** →

```
https://raw.githubusercontent.com/des1roer/phpstorm/main/updatePlugins.xml
```

После этого плагины ищутся на вкладке Marketplace.

Подтянуть новые версии всех плагинов из Marketplace (старые остаются), пересобрать индекс и закоммитить:

```bash
python3 tools/fetch_updates.py
python3 tools/gen_update_plugins.py
git add -A && git commit -m "update plugins" && git push
```

`fetch_updates.py` берёт последнюю версию каждого плагина и последнюю совместимую с каждой установленной IDE
(`/mnt/c/Program Files/JetBrains/*/product-info.json`, или явно `--build PS-263.7307.215`), скачивает через
`downloads.marketplace.jetbrains.com`. `--dry-run` только показывает, что нового.

Конкретная версия по ссылке со страницы Marketplace (в том числе bundled-плагины, которых ещё нет в репо):

```bash
python3 tools/fetch_updates.py https://plugins.jetbrains.com/plugin/33314-air/versions/stable/1220002
```

Новый плагин: положить архив в корень и так же пересобрать индекс.

Раздача без GitHub (из WSL или Linux): `tools/serve.sh`, в IDE указать `http://localhost:8765/updatePlugins.local.xml`.

Проверить совместимость с билдом IDE (Help → About):

```bash
python3 tools/gen_update_plugins.py --build 263.7307.215
```

## Языковые пакеты Grazie

`grazie/*.jar` — не плагины, а языковые модели для проверки текста (Settings → Editor → Natural Languages).
Если IDE не может скачать язык сама, скопировать jar в папку конфигурации IDE и перезапустить её:

- Windows: `%APPDATA%\JetBrains\PhpStorm2026.3\grazie\`
- Linux: `~/.config/JetBrains/PhpStorm2026.3/grazie/`
