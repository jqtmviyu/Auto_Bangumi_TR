import threading

from .status import ProgramStatus

from module.rss import analyser, add_rules
from module.manager import Renamer, eps_complete
from module.notification import PostNotification
from module.database import BangumiDatabase
from module.conf import settings


class RSSThread(ProgramStatus):
    def __init__(self):
        super().__init__()
        self._rss_thread = threading.Thread(
            target=self.rss_loop,
        )

    def rss_loop(self):
        while not self.stop_event.is_set():
            with BangumiDatabase() as db:
                analyser.rss_to_data(rss_link=settings.rss_link, database=db)
            add_rules()
            if settings.bangumi_manage.eps_complete:
                eps_complete()
            self.stop_event.wait(settings.program.rss_time)

    def rss_start(self):
        self.rss_thread.start()

    def rss_stop(self):
        if self._rss_thread.is_alive():
            self._rss_thread.join()

    @property
    def rss_thread(self):
        if not self._rss_thread.is_alive():
            self._rss_thread = threading.Thread(
                target=self.rss_loop,
            )
        return self._rss_thread


class RenameThread(ProgramStatus):
    def __init__(self):
        super().__init__()
        self._rename_thread = threading.Thread(
            target=self.rename_loop,
        )

    def rename_loop(self):
        while not self.stop_event.is_set():
            with Renamer() as renamer:
                renamed_info = renamer.rename()
            with PostNotification() as notifier:
                for info in renamed_info:
                    notifier.send_msg(info)
            self.stop_event.wait(settings.program.rename_time)

    def rename_start(self):
        self.rename_thread.start()

    def rename_stop(self):
        if self._rename_thread.is_alive():
            self._rename_thread.join()

    @property
    def rename_thread(self):
        if not self._rename_thread.is_alive():
            self._rename_thread = threading.Thread(
                target=self.rename_loop,
            )
        return self._rename_thread
