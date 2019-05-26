from enum import Enum, auto


class ValueEnum(Enum):
    def __str__(self):
        return str(self._value_)


class NameEnum(Enum):
    def __str__(self):
        return self._name_


class Platform(ValueEnum):
    TJ = 'tjournal'
    DTF = 'dtf'
    VC = 'vc'


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