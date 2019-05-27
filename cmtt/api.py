from datetime import datetime
from .settings import *
from .enums import *

import aiohttp
import aiofiles
import logging
import json


def create_logger():
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    return logging.getLogger(__name__)


logger = create_logger()


class CMTT:
    __slots__ = ('platform', 'token', 'version', 'calls_timing', 'headers')

    def __init__(self, platform: Platform, token: str = None, version=API_VERSION):
        self.platform = platform
        self.token = token
        self.version = version
        self.calls_timing = []
        self.headers = {'User-agent': USER_AGENT}

        if self.token:
            self.headers['X-Device-Token'] = self.token

    def _hittingCallsLimit(self) -> bool:
        if len(self.calls_timing) == CALLS_LIMIT:
            if (datetime.now() - self.calls_timing[-1]).seconds >= 1:
                self.calls_timing.pop(-1)
                self.calls_timing.append(datetime.now())
                return False
            else:
                return True
        else:
            self.calls_timing.append(datetime.now())
            return False

    async def _get(self, endpoint: str, params: dict = None):
        if params is None:
            params = {}
        payload = {k: v for k, v in params.items() if v is not None}

        while self._hittingCallsLimit():
            pass

        async with aiohttp.ClientSession() as session:
            url = f'https://api.{self.platform}.ru/v{self.version}' + endpoint

            logger.info(f'[GET]: url={url} | data={payload}')
            async with session.get(url, headers=self.headers, params=payload) as response:
                response.raise_for_status()

                return await response.json()

    async def _post(self, endpoint: str, params: dict = None, path: str = None):
        files = None

        if path:
            async with aiofiles.open(path, 'rb') as content:
                files = await content.read()

            files = {'file': files}
        if params is None:
            params = {}
        payload = {k: v for k, v in params.items() if v is not None}

        if 'attachments' in payload:
            payload['attachments'] = json.dumps(payload['attachments'])

        while self._hittingCallsLimit():
            pass

        async with aiohttp.ClientSession() as session:
            url = f'https://api.{self.platform}.ru/v{self.version}' + endpoint

            logger.info(f'[POST]: url={url} | data={payload} | files={files}')
            data = payload if not path else files
            async with session.post(url, headers=self.headers, data=data) as response:
                response.raise_for_status()

                return await response.json()

    async def getTimeline(self, category: TimelineCategory, sorting: TimelineSorting, count: int = None,
                          offset: int = None):
        return await self._get(f'/timeline/{category}/{sorting}', {'count': count, 'offset': offset})

    async def getTimelineByHashtag(self, hashtag: str, count: int = None, offset: int = None):
        return await self._get(f'/timeline/mainpage', {'hashtag': hashtag, 'count': count, 'offset': offset})

    async def getTimelineNews(self, count: int = None, offset: int = None):
        return await self._get(f'/news/async default/recent', {'count': count, 'offset': offset})

    async def getFlashholder(self):
        return await self._get(f'/getflashholdedentry')

    async def getEntryById(self, id: int):
        return await self._get(f'/entry/{id}')

    async def getPopularEntries(self, id: int):
        return await self._get(f'/entry/{id}/popular')

    async def likeEntry(self, id: int, type: LikeEntryType, sign: LikeSign):
        return await self._post(f'/like', {'id': id, 'type': type, 'sign': sign})

    async def entryCreate(self, title: str, text: str, subsite_id: int, attachments=None):
        return await self._post(f'/entry/create',
                                   {'title': title, 'text': text, 'subsite_id': subsite_id, 'attachments': attachments})

    async def entryCreateWithBlocks(self, title: str, entry: str, subsite_id: int):
        # https://www.notion.so/73acb29bca4848d88ac6545e5775a987
        return await self._post(f'/entry/create', {'title': title, 'entry': entry, 'subsite_id': subsite_id})

    async def entryLocate(self, url: str):
        return await self._get(f'/entry/locate', {'url': url})

    async def getEntryComments(self, id: int, sorting: CommentsSorting):
        return await self._get(f'/entry/{id}/comments/{sorting}')

    async def getEntryCommentsLevelsGet(self, id: int, sorting: CommentsSortingLevel):
        return await self._get(f'/entry/{id}/comments/levels/{sorting}')

    async def getEntryCommentsThread(self, entryId: int, commentId: int):
        return await self._get(f'/entry/{entryId}/comments/thread/{commentId}')

    async def getCommentLikes(self, id: int):
        return await self._get(f'/comment/likers/{id}')

    async def commentEdit(self, commentId: int, entryId: int, text: str = None):
        return await self._post(f'/comment/edit/{commentId}/{entryId}', {'text': text})

    # в доках id и reply_to почему-то являются string типом
    async def commentSend(self, id: int, text: str, reply_to: int = 0, attachments=None):
        # пример использования:
        # uploaded = client.uploaderUpload(r'C:\Users\blabla\Pictures\mars.jpg')
        # client.commentSend(86279,'api test',attachments=uploaded['result'])
        return await self._post(f'/comment/add',
                                   {'id': id, 'text': text, 'reply_to': reply_to, 'attachments': attachments})

    async def commentSaveCommentsSeenCount(self, content_id: int, count: int):
        return await self._post(f'/comment/saveCommentsSeenCount', {'content_id': content_id, 'count': count})

    async def uploaderUpload(self, path):
        return await self._post(f'/uploader/upload', path=path)

    async def uploaderExtract(self, url: str):
        return await self._post(f'/uploader/extract', {'url': url})

    async def locate(self, url: str):
        return await self._get(f'/locate', {'url': url})

    async def search(self, query: str, order_by: SearchOrder = None, page: int = None):
        return await self._get(f'/search', {'query': query, 'order_by': order_by, 'page': page})

    async def entryComplaint(self, content_id: int):
        return await self._post(f'/entry/complaint', {'content_id': content_id})

    async def entryCommentComplaint(self, content_id: int):
        return await self._post(f'/entry/comment/complaint', {'content_id': content_id})

    async def getUser(self, id: int):
        return await self._get(f'/user/{id}')

    async def getUserMe(self):
        return await self._get(f'/user/me')

    async def getUserMeUpdates(self, id: int, is_read: int = 1, last_id: int = None):
        return await self._get(f'/user/me/updates', {'id': id, 'is_read': is_read, 'last_id': last_id})

    async def getUserMeUpdatesCount(self):
        return await self._get(f'/user/me/updates/count')

    async def userMeUpdatesReadId(self, id: int):
        return await self._post(f'/user/me/updates/read/{id}')

    async def userMeUpdatesRead(self, ids: [int]):
        return await self._post(f'/user/me/updates/read', {'ids': '|'.join(str(x) for x in ids)})

    async def getUserComments(self, id: int, count: int = None, offset: int = None):
        return await self._get(f'/user/{id}/comments', {'count': count, 'offset': offset})

    async def getUserMeComments(self, count: int = None, offset: int = None):
        return await self._get(f'/user/me/comments', {'count': count, 'offset': offset})

    async def getUserEntries(self, id: int, count: int = None, offset: int = None):
        return await self._get(f'/user/{id}/entries', {'count': count, 'offset': offset})

    async def getUserMeEntries(self, count: int = None, offset: int = None):
        return await self._get(f'/user/me/entries', {'count': count, 'offset': offset})

    async def getUserFavoritesEntries(self, id: int, count: int = None, offset: int = None):
        return await self._get(f'/user/{id}/favorites/entries', {'count': count, 'offset': offset})

    async def getUserFavoritesComments(self, id: int, count: int = None, offset: int = None):
        return await self._get(f'/user/{id}/favorites/comments', {'count': count, 'offset': offset})

    async def getUserMeFavoritesEntries(self, count: int = None, offset: int = None):
        return await self._get(f'/user/me/favorites/entries', {'count': count, 'offset': offset})

    async def getUserMeFavoritesComments(self, count: int = None, offset: int = None):
        return await self._get(f'/user/me/favorites/comments', {'count': count, 'offset': offset})

    async def getUserMeFavoritesVacancies(self, count: int = None, offset: int = None):
        return await self._get(f'/user/me/favorites/vacancies', {'count': count, 'offset': offset})

    async def getUserMeSubscriptionsRecommended(self):
        return await self._get(f'/user/me/subscriptions/recommended')

    async def getUserMeSubscriptionsSubscribed(self):
        return await self._get(f'/user/me/subscriptions/subscribed')

    async def favoriteAdd(self, id: int, type: FavoriteType):
        return await self._post(f'/user/me/favorites', {'id': id, 'type': type})

    async def favoriteRemove(self, id: int, type: FavoriteType):
        return await self._post(f'/user/me/favorites/remove', {'id': id, 'type': type})

    async def getUserMeTuneCatalog(self):
        return await self._get(f'/user/me/tunecatalog')

    async def userMeTuneCatalog(self, settings: dict):
        return await self._post(f'/user/me/tunecatalog', {'settings': settings})

    async def getLayout(self, version: int):
        return await self._get(f'/layout/{version}')

    async def getLayoutHashtag(self, hashtag: str):
        return await self._get(f'/layout/hashtag/{hashtag}')

    async def getUserPushTopic(self):
        return await self._get(f'/user/push/topic')

    async def getUserPushSettings(self):
        return await self._get(f'/user/push/settings/get')

    async def updateUserPushSettings(self, settings: int):
        return await self._post(f'/user/push/settings/update', {'settings': settings})

    async def paymentsCheck(self):
        return await self._get(f'/payments/check')

    async def getTweets(self, mode: TweetsMode, count: int = None, offset: int = None):
        return await self._get(f'/tweets/{mode}', {'count': count, 'offset': offset})

    async def getRates(self):
        return await self._get(f'/rates')

    async def getSubsiteTimeline(self, id: int, sorting: SubsiteTimelineSorting, count: int = None, offset: int = None):
        return await self._get(f'/subsite/{id}/timeline{sorting}', {'count': count, 'offset': offset})

    async def getSubsitesList(self, type: SubsitesListType):
        return await self._get(f'/subsites_list/{type}')

    async def getSubsiteVacancies(self, subsite_id: int):
        return await self._get(f'/subsite/{subsite_id}/vacancies')

    async def getSubsiteVacanciesMore(self, subsite_id: int, last_id: int):
        return await self._get(f'/subsite/{subsite_id}/vacancies/more/{last_id}')

    async def subsiteSubscribe(self, id: int):
        # по-хорошему это должен быть POST запрос
        return await self._get(f'/subsite/{id}/subscribe')

    async def subsiteUnsubscribe(self, id: int):
        # по-хорошему это должен быть POST запрос тоже
        return await self._get(f'/subsite/{id}/unsubscribe')

    async def getJob(self):
        return await self._get(f'/job')

    async def getJobMore(self, last_id: int):
        return await self._get(f'/job/more/{last_id}')

    async def getJobFilters(self):
        return await self._get(f'/job/filters')

    async def getVacancies(self):
        return await self._get(f'/vacancies/widget')

    async def apiWebhooksGet(self):
        return await self._get(f'/webhooks/get')

    async def apiWebhookAdd(self, url: str, event: str = 'new_comment'):
        return await self._post(f'/webhooks/add', {'url': url, 'event': event})

    async def apiWebhookDel(self, event: str = 'new_comment'):
        return await self._post(f'/webhooks/del', {'event': event})

    async def contentMute(self, action: MuteAction, id: int):
        return await self._post(f'/content/mute', {'action': action, 'id': id})

    async def hashtagMute(self, action: MuteAction, id: int):
        return await self._post(f'/hashtag/mute', {'action': action, 'id': id})

    async def subsitegMute(self, action: MuteAction, id: int):
        return await self._post(f'/subsite/mute', {'action': action, 'id': id})
