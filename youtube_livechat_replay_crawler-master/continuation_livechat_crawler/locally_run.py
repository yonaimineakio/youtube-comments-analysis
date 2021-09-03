import logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from continuation_livechat_crawler.main import get_ytInitialData, get_continuation, convert_chatreplay, get_chat_replay_from_continuation, RestrictedFromYoutube
from initial_livechat_check.main import get_initial_continuation, check_livechat_replay_disable, ContinuationURLNotFound, LiveChatReplayDisabled, RestrictedFromYoutube
from visualize_data import all_comments_graph
from visualize_data import per_comments_graph


import json

if __name__ == '__main__':

    video_id = sys.argv[1]
    if not os.path.exists(f"./chatlog_replay_{video_id}.json"):
        target_url = "https://www.youtube.com/watch?v=" + video_id

        continuation = get_initial_continuation(target_url)
        comment_data, continuation = get_chat_replay_from_continuation(video_id, continuation, 4000, True)

        dmplist = []
        for line in comment_data:
           dmplist.append(json.dumps(line, ensure_ascii=False))
        output_file = './chatlog_replay_' + video_id + '.json'
        with open(output_file, mode='w', encoding="UTF-8") as f:
            f.write('\n'.join(dmplist))

        print('DONE!')
    print(f'{video_id}のデータは取得済みです。')
    json_path=f"./chatlog_replay_{video_id}.json"
    all_comments_graph.preprocessing(json_path)
    per_comments_graph.preprocessing(json_path)

