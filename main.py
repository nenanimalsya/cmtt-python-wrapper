import requests
import json
from enum import Enum, auto
from datetime import datetime

API_VERSION = '1.6'
USER_AGENT = 'cmtt-python-wrapper'
CALLS_LIMIT = 3


class ValueEnum(Enum):
	def __str__(self):
		return str(self._value_)


class NameEnum(Enum):
	def __str__(self):
		return self._name_


class Platform(ValueEnum):
	TJ = 'tjournal.ru'
	DTF = 'dtf.ru'
	VC = 'vc.ru'


class TimelineSorting(NameEnum):
	recent = auto()
	popular = auto()
	week = auto()
	month = auto()


class TimelineCategory(NameEnum):
	index = auto()
	gamedev = auto()
	mainpage = auto()


class CommentsSorting(NameEnum):
	recent = auto()
	popular = auto()


class CommentsSortingLevel(NameEnum):
	date = auto()
	popular = auto()


class SearchOrder(NameEnum):
	relevant = auto()
	date = auto()


class TweetsMode(NameEnum):
	fresh = auto()
	day = auto()
	week = auto()
	month = auto()


class SubsiteTimelineSorting(ValueEnum):
	topweek = '/top/week'
	topmonth = '/top/month'
	topyear = '/top/year'
	topall = '/top/all'
	new = 'new'
	default = ''


class SubsitesListType(NameEnum):
	sections = auto()
	companies = auto()


class LikeEntryType(NameEnum):
	content = auto()
	comment = auto()


class LikeSign(ValueEnum):
	like = 1
	unlike = 0
	dislike = -1


class FavoriteType(ValueEnum):
	ENTRY = 1
	COMMENT = 2


class MuteAction(NameEnum):
	mute = auto()
	unmute = auto()


class Committee:

	def __init__(self, platform: Platform, token: str, version=API_VERSION):
		self.platform = platform
		self.token = token
		self.version = version
		self.calls_timing = list()

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

	def _doGetRequest(self, endpoint: str, params: dict = None):
		payload = {}
		if params:
			for k,v in params.items():
				if params[k] is not None:
					payload[k]=v
		headers = {'User-agent': USER_AGENT, 'X-Device-Token': self.token}
		while self._hittingCallsLimit():
			pass
		response = requests.get('https://api.' + str(self.platform) + '/v' + self.version + endpoint, headers=headers, params=payload)
		response.raise_for_status()
		return response.json()

	def _doPostRequest(self, endpoint: str, params: dict = None, filepath=None):
		files = None
		if filepath:
			files = {'file': open(filepath, 'rb')}
		payload = {}
		if params:
			for k,v in params.items():
				if params[k] is not None:
					payload[k]=v
		if 'attachments' in payload:
			payload['attachments']=json.dumps(payload['attachments'])
		headers = {'User-agent': USER_AGENT, 'X-Device-Token': self.token}
		while self._hittingCallsLimit():
			pass
		response = requests.post('https://api.' + str(self.platform) + '/v' + self.version + endpoint, headers=headers, data=payload, files=files)
		response.raise_for_status()
		return response.json()

	def getTimeline(self, category: TimelineCategory, sorting: TimelineSorting, count: int = None, offset: int = None):
		return self._doGetRequest(f'/timeline/{category}/{sorting}', {'count': count, 'offset': offset})

	def getTimelineByHashtag(self, hashtag: str, count: int = None, offset: int = None):
		return self._doGetRequest(f'/timeline/mainpage', {'hashtag': hashtag, 'count': count, 'offset': offset})

	def getTimelineNews(self, count: int = None, offset: int = None):
		return self._doGetRequest(f'/news/default/recent', {'count': count, 'offset': offset})

	def getFlashholder(self):
		return self._doGetRequest(f'/getflashholdedentry')

	def getEntryById(self, id: int):
		return self._doGetRequest(f'/entry/{id}')

	def getPopularEntries(self, id: int):
		return self._doGetRequest(f'/entry/{id}/popular')

	def likeEntry(self, id: int, type: LikeEntryType, sign: LikeSign):
		return self._doPostRequest(f'/like', {'id': id, 'type': type, 'sign': sign})

	def entryCreate(self, title: str, text: str, subsite_id: int, attachments = None):
		return self._doPostRequest(f'/entry/create', {'title': title, 'text': text, 'subsite_id': subsite_id, 'attachments': attachments})

	def entryCreateWithBlocks(self, title: str, entry : str, subsite_id: int):
		#https://www.notion.so/73acb29bca4848d88ac6545e5775a987
		return self._doPostRequest(f'/entry/create', {'title': title, 'entry': entry, 'subsite_id': subsite_id})

	def entryLocate(self, url: str):
		return self._doGetRequest(f'/entry/locate', {'url': url})

	def getEntryComments(self, id: int, sorting: CommentsSorting):
		return self._doGetRequest(f'/entry/{id}/comments/{sorting}')

	def getEntryCommentsLevelsGet(self, id: int, sorting: CommentsSortingLevel):
		return self._doGetRequest(f'/entry/{id}/comments/levels/{sorting}')

	def getEntryCommentsThread(self, entryId: int, commentId: int):
		return self._doGetRequest(f'/entry/{entryId}/comments/thread/{commentId}')

	def getCommentLikes(self, id: int):
		return self._doGetRequest(f'/comment/likers/{id}')

	def commentEdit(self, commentId: int, entryId: int, text: str = None):
		return self._doPostRequest(f'/comment/edit/{commentId}/{entryId}', {'text': text})

	# в доках id и reply_to почему-то являются string типом
	def commentSend(self, id: int, text: str, reply_to: int = 0, attachments = None):
		# пример использования:
		# uploaded = client.uploaderUpload(r'C:\Users\blabla\Pictures\mars.jpg')
		# client.commentSend(86279,'api test',attachments=uploaded['result'])
		return self._doPostRequest(f'/comment/add', {'id': id, 'text': text, 'reply_to': reply_to, 'attachments': attachments})

	def commentSaveCommentsSeenCount(self, content_id: int, count: int):
		return self._doPostRequest(f'/comment/saveCommentsSeenCount', {'content_id': content_id, 'count': count})

	def uploaderUpload(self, filepath):
		return self._doPostRequest(f'/uploader/upload', filepath=filepath)

	def uploaderExtract(self, url: str):
		return self._doPostRequest(f'/uploader/extract', {'url': url})

	def locate(self, url: str):
		return self._doGetRequest(f'/locate', {'url': url})

	def search(self, query: str, order_by: SearchOrder = None, page: int = None):
		return self._doGetRequest(f'/search', {'query': query, 'order_by': order_by, 'page': page})

	def entryComplaint(self, content_id: int):
		return self._doPostRequest(f'/entry/complaint', {'content_id': content_id})

	def entryCommentComplaint(self, content_id: int):
		return self._doPostRequest(f'/entry/comment/complaint', {'content_id': content_id})

	def getUser(self, id: int):
		return self._doGetRequest(f'/user/{id}')

	def getUserMe(self):
		return self._doGetRequest(f'/user/me')

	def getUserMeUpdates(self, id: int, is_read: int = 1, last_id: int = None):
		return self._doGetRequest(f'/user/me/updates', {'id': id, 'is_read': is_read, 'last_id': last_id})

	def getUserMeUpdatesCount(self):
		return self._doGetRequest(f'/user/me/updates/count')

	def userMeUpdatesReadId(self, id: int):
		return self._doPostRequest(f'/user/me/updates/read/{id}')

	def userMeUpdatesRead(self, ids: [int]):
		return self._doPostRequest(f'/user/me/updates/read', {'ids': '|'.join(str(x) for x in ids)})

	def getUserComments(self, id: int, count: int = None, offset: int = None):
		return self._doGetRequest(f'/user/{id}/comments', {'count': count, 'offset': offset})

	def getUserMeComments(self, count: int = None, offset: int = None):
		return self._doGetRequest(f'/user/me/comments', {'count': count, 'offset': offset})

	def getUserEntries(self, id: int, count: int = None, offset: int = None):
		return self._doGetRequest(f'/user/{id}/entries', {'count': count, 'offset': offset})

	def getUserMeEntries(self, count: int = None, offset: int = None):
		return self._doGetRequest(f'/user/me/entries', {'count': count, 'offset': offset})

	def getUserFavoritesEntries(self, id: int, count: int = None, offset: int = None):
		return self._doGetRequest(f'/user/{id}/favorites/entries', {'count': count, 'offset': offset})

	def getUserFavoritesComments(self, id: int, count: int = None, offset: int = None):
		return self._doGetRequest(f'/user/{id}/favorites/comments', {'count': count, 'offset': offset})

	def getUserMeFavoritesEntries(self, count: int = None, offset: int = None):
		return self._doGetRequest(f'/user/me/favorites/entries', {'count': count, 'offset': offset})

	def getUserMeFavoritesComments(self, count: int = None, offset: int = None):
		return self._doGetRequest(f'/user/me/favorites/comments', {'count': count, 'offset': offset})

	def getUserMeFavoritesVacancies(self, count: int = None, offset: int = None):
		return self._doGetRequest(f'/user/me/favorites/vacancies', {'count': count, 'offset': offset})

	def getUserMeSubscriptionsRecommended(self):
		return self._doGetRequest(f'/user/me/subscriptions/recommended')

	def getUserMeSubscriptionsSubscribed(self):
		return self._doGetRequest(f'/user/me/subscriptions/subscribed')

	def favoriteAdd(self, id: int, type: FavoriteType):
		return self._doPostRequest(f'/user/me/favorites', {'id': id, 'type': type})

	def favoriteRemove(self, id: int, type: FavoriteType):
		return self._doPostRequest(f'/user/me/favorites/remove', {'id': id, 'type': type})

	def getUserMeTuneCatalog(self):
		return self._doGetRequest(f'/user/me/tunecatalog')

	def userMeTuneCatalog(self, settings: dict):
		return self._doPostRequest(f'/user/me/tunecatalog', {'settings': settings})

	def getLayout(self, version: int):
		return self._doGetRequest(f'/layout/{version}')

	def getLayoutHashtag(self, hashtag: str):
		return self._doGetRequest(f'/layout/hashtag/{hashtag}')

	def getUserPushTopic(self):
		return self._doGetRequest(f'/user/push/topic')

	def getUserPushSettings(self):
		return self._doGetRequest(f'/user/push/settings/get')

	def updateUserPushSettings(self, settings: int):
		return self._doPostRequest(f'/user/push/settings/update', {'settings': settings})

	def paymentsCheck(self):
		return self._doGetRequest(f'/payments/check')

	def getTweets(self, mode: TweetsMode, count: int = None, offset: int = None):
		return self._doGetRequest(f'/tweets/{mode}', {'count': count, 'offset': offset})

	def getRates(self):
		return self._doGetRequest(f'/rates')

	def getSubsiteTimeline(self, id: int, sorting: SubsiteTimelineSorting, count: int = None, offset: int = None):
		return self._doGetRequest(f'/subsite/{id}/timeline{sorting}', {'count': count, 'offset': offset})

	def getSubsitesList(self, type: SubsitesListType):
		return self._doGetRequest(f'/subsites_list/{type}')

	def getSubsiteVacancies(self, subsite_id: int):
		return self._doGetRequest(f'/subsite/{subsite_id}/vacancies')

	def getSubsiteVacanciesMore(self, subsite_id: int, last_id: int):
		return self._doGetRequest(f'/subsite/{subsite_id}/vacancies/more/{last_id}')

	def subsiteSubscribe(self, id: int):
		# по-хорошему это должен быть POST запрос
		return self._doGetRequest(f'/subsite/{id}/subscribe')

	def subsiteUnsubscribe(self, id: int):
		# по-хорошему это должен быть POST запрос тоже
		return self._doGetRequest(f'/subsite/{id}/unsubscribe')

	def getJob(self):
		return self._doGetRequest(f'/job')

	def getJobMore(self, last_id: int):
		return self._doGetRequest(f'/job/more/{last_id}')

	def getJobFilters(self):
		return self._doGetRequest(f'/job/filters')

	def getVacancies(self):
		return self._doGetRequest(f'/vacancies/widget')

	def apiWebhooksGet(self):
		return self._doGetRequest(f'/webhooks/get')

	def apiWebhookAdd(self, url: str, event: str = 'new_comment'):
		return self._doPostRequest(f'/webhooks/add', {'url': url, 'event': event})

	def apiWebhookDel(self, event: str = 'new_comment'):
		return self._doPostRequest(f'/webhooks/del', {'event': event})

	def contentMute(self, action: MuteAction, id: int):
		return self._doPostRequest(f'/content/mute', {'action': action, 'id': id})

	def hashtagMute(self, action: MuteAction, id: int):
		return self._doPostRequest(f'/hashtag/mute', {'action': action, 'id': id})

	def subsitegMute(self, action: MuteAction, id: int):
		return self._doPostRequest(f'/subsite/mute', {'action': action, 'id': id})

