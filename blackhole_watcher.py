import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from shared.shared import sonarr, radarr, whisparr
from blackhole import on_created, getPath

class BlackholeHandler(FileSystemEventHandler):
    def __init__(self, arr_type):
        super().__init__()
        self.arr_type = arr_type
        self.path_name = getPath(arr_type, create=True)

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith((".torrent", ".magnet")):
            asyncio.run(on_created(self.arr_type))

    async def on_run(self):
        await on_created(self.arr_type)

async def main():
    radarr_handler = None
    sonarr_handler = None
    whisparr_handler = None
    radarr_observer = None
    sonarr_observer = None
    whisparr_observer = None
    print("Watching blackhole")

    if radarr['enabled']:
        radarr_handler = BlackholeHandler('radarr')
        radarr_observer = Observer()
        radarr_observer.schedule(radarr_handler, radarr_handler.path_name)

    if sonarr['enabled']:
        sonarr_handler = BlackholeHandler('sonarr')
        sonarr_observer = Observer()
        sonarr_observer.schedule(sonarr_handler, sonarr_handler.path_name)

    if whisparr['enabled']:
        whisparr_handler = BlackholeHandler('whisparr')
        whisparr_observer = Observer()
        whisparr_observer.schedule(whisparr_handler, whisparr_handler.path_name)

    try:
        tasks = []
        if radarr_observer:
            radarr_observer.start()
            tasks.append(radarr_handler.on_run())
        if sonarr_observer:
            sonarr_observer.start()
            tasks.append(sonarr_handler.on_run())
        if whisparr_observer:
            whisparr_observer.start()
            tasks.append(whisparr_handler.on_run())

        await asyncio.gather(*tasks)

    except KeyboardInterrupt:
        if radarr_observer:
            radarr_observer.stop()
        if sonarr_observer:
            sonarr_observer.stop()
        if whisparr_observer:
            whisparr_observer.stop()

    if radarr_observer:
        radarr_observer.join()
    if sonarr_observer:
        sonarr_observer.join()
    if whisparr_observer:
        whisparr_observer.join()

if __name__ == "__main__":
    asyncio.run(main())