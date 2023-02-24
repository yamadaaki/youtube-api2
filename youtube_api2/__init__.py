import json
import re
from typing import Any

import requests


def search(query: str) -> list[dict[str, Any]]:
    res = requests.get(f'https://www.youtube.com/results?search_query={query}').text
    data = json.loads(re.findall(r'ytInitialData = ({.+});</script>', res)[0])
    raw_results = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
    results = []

    for result in raw_results:
        if result.get('videoRenderer') is None:
            continue

        results.append({
            'id': result['videoRenderer']['videoId'],
            'title': result['videoRenderer']['title']['runs'][0]['text'],
            'view_count': result['videoRenderer']['viewCountText']['simpleText'],
            'length': result['videoRenderer']['lengthText']['simpleText'],
            'published_at': result['videoRenderer']['publishedTimeText']['simpleText'],
            'channel_thumbnails': result['videoRenderer']['channelThumbnailSupportedRenderers']['channelThumbnailWithLinkRenderer']['thumbnail']['thumbnails'],
        })
    return results


def search_channel(channel_id: str):
    res = requests.get(f'https://www.youtube.com/@{channel_id}/videos')
    info = json.loads(re.findall(r'ytInitialData = ({.+});</script>', res.text)[0])
    videos = info['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content']['richGridRenderer']['contents'][:-1]

    return [
        {
            'id': video['richItemRenderer']['content']['videoRenderer']['videoId'],
            'title': video['richItemRenderer']['content']['videoRenderer']['title']['runs'][0]['text'],
            'view_count': video['richItemRenderer']['content']['videoRenderer']['viewCountText']['simpleText'],
            'duration': video['richItemRenderer']['content']['videoRenderer']['lengthText']['simpleText'],
            'published_at': video['richItemRenderer']['content']['videoRenderer']['publishedTimeText']['simpleText']
        }
        for video in videos
    ]


def get_video_data(url: str) -> dict[str, Any]:
    res = requests.get(url).text
    video_data = json.loads(re.findall(r'ytInitialData = ({.+});</script>', res)[0])['contents']['twoColumnWatchNextResults']['results']['results']['contents']

    info1 = video_data[0]['videoPrimaryInfoRenderer']
    info2 = video_data[1]['videoSecondaryInfoRenderer']

    try:
        description = info2['attributedDescription']['content']
    except KeyError:
        description = ''.join(map(lambda x:x['text'], info2['description']['runs']))

    return {
        'channel': info2['owner']['videoOwnerRenderer']['title']['runs'][0]['text'],
        'title': info1['title']['runs'][0]['text'],
        'view_count': info1['viewCount']['videoViewCountRenderer']['viewCount']['simpleText'],
        'like_count': info1['videoActions']['menuRenderer']['topLevelButtons'][0]['segmentedLikeDislikeButtonRenderer']['likeButton']['toggleButtonRenderer']['defaultText']['accessibility']['accessibilityData']['label'],
        'subscribers': info2['owner']['videoOwnerRenderer']['subscriberCountText']['accessibility']['accessibilityData']['label'],
        'published_at': info1['dateText']['simpleText'],
        'description': description,
        'channel_thumbnails': info2['owner']['videoOwnerRenderer']['thumbnail']['thumbnails']
    }
