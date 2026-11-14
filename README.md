# phpstorm

## Свой репозиторий плагинов

Плагины (`*.zip`, `*.jar`) лежат в корне репо. IDE ставит и обновляет их как из Marketplace.

В IDE: **Settings → Plugins → ⚙ → Manage Plugin Repositories → +** →

```
https://raw.githubusercontent.com/des1roer/phpstorm/main/updatePlugins.xml
```

После этого плагины ищутся на вкладке Marketplace.

Добавить или обновить плагин: положить архив в корень, старую версию удалить, пересобрать индекс и закоммитить:

```bash
python3 tools/gen_update_plugins.py
git add -A && git commit -m "update plugins" && git push
```

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
