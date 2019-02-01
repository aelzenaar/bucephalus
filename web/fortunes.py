from werkzeug import unescape

import random
from datetime import datetime
import requests
import sys

import config

def short_fortune():
  now = datetime.now()
  if(now.month == 3 and now.day == 14):
    return "<a href=\"https://www.youtube.com/watch?v=FtxmFlMLYRI\">happy $\pi$ day</a>."
  if(now.month == 4 and now.day == 26):
    return "<a href=\"https://www.youtube.com/watch?v=PWZYId1fWnM\">it's April 26</a>."
  did_you_know = ["this is bucephawiki, also known as bucephalus2."
                  #"you can view multiple tags at once by appending them to the URL. For example: <code>/v/tag/tag1/tag2</code>.",
                  #"the search functionality doesn't actually work.",
                  #"the search functionality allows regular expressions.",
                  "eventually, Bucephalus will integrate with git.",
                  #"Bucephalus now integrates with git.",
                  "eventually, Bucephalus will integrate with geogebra.",
                  #"Bucephalus' web interface now integrates with geogebra.",
                  "eventually, Bucephalus will have more features.",
                  "Bucephalus is running on Python " + str(sys.version_info[0]) + "." + str(sys.version_info[1]) + ".",
                  #"you can update files using the command line after adding them.",
                  "if your files are lost, you'll wish you had a backup.",
                  "'Βουκέφαλος' means ox-head.",
                  "Bucephalus was named after a mark on his body depicting the head of an ox.",
                  "the pigeonhole principle will probably solve your problem.",
                  "$3987^{12} + 4365^{12} = 4472^{12}$",
                  "oops.",
                  "in science one tries to tell people, in such a way as to be understood by everyone, something that no one ever knew before. But in poetry, it's the exact opposite. (PAM Dirac)",
                  "mathematics is the art of giving the same name to different things. (Henri Poincaré)",
                  "this is getting dangerously close to topology."
                  ]

  return "Did you know: " + random.choice(did_you_know)

def long_fortune():
  if not config.enable_long_fortunes():
    return None
  try:
    questionid = random.choice([{'qid':22299, 'site':"mathoverflow.net"}, {'qid':1083, 'site':"mathoverflow.net"},
                                {'qid':7155, 'site':"mathoverflow.net"}, {'qid':2144, 'site':"mathoverflow.net"},
                                {'qid':14574, 'site':"mathoverflow.net"}, {'qid':879, 'site':"mathoverflow.net"},
                                {'qid':16829, 'site':"mathoverflow.net"}, {'qid':47214, 'site':"mathoverflow.net"},
                                {'qid':44326, 'site':"mathoverflow.net"}, {'qid':29006, 'site':"mathoverflow.net"},
                                {'qid':38856, 'site':"mathoverflow.net"}, {'qid':7584, 'site':"mathoverflow.net"},
                                {'qid':117668, 'site':"mathoverflow.net"}, {'qid':8846, 'site':"mathoverflow.net"},
                                {'qid':178139, 'site':"mathoverflow.net"}, {'qid':42512, 'site':"mathoverflow.net"},
                                {'qid':4994, 'site':"mathoverflow.net"},
                                {'qid':733754, 'site':"math.stackexchange.com"}, {'qid':323334, 'site':"math.stackexchange.com"},
                                {'qid':178940, 'site':"math.stackexchange.com"}, {'qid':111440, 'site':"math.stackexchange.com"},
                                {'qid':250, 'site':"math.stackexchange.com"}, {'qid':820686, 'site':"math.stackexchange.com"},
                                {'qid':505367, 'site':"math.stackexchange.com"}, {'qid':362446, 'site':"math.stackexchange.com"},
                                {'qid':8814, 'site':"math.stackexchange.com"}, {'qid':260656, 'site':"math.stackexchange.com"},
                                {'qid':2949, 'site':"math.stackexchange.com"},
                                {'qid':4351, 'site':"matheducators.stackexchange.com"}, {'qid':1817, 'site':"matheducators.stackexchange.com"},
                              ])
    question = requests.get('https://api.stackexchange.com/questions/' + str(questionid['qid']) + '?site=' + str(questionid['site']) +
                            '&filter=!gB66oJbwvcXSH(Ni5Ti9FQ4PaxMw.WKlBWC', timeout=config.external_request_timeout())
    question.raise_for_status()
    question = question.json()['items'][0]
    ansid = random.choice(question['answers'])['answer_id']

    fullrequest = requests.get('https://api.stackexchange.com/answers/' + str(ansid) + '?site=' + str(questionid['site']) +
                              '&filter=!Fcb(61J.xH8s_mAfP-LmG*7fPe', timeout=config.external_request_timeout())
    fullrequest.raise_for_status()
    fullrequest = fullrequest.json()
    answer = fullrequest['items'][0]

    randomse = {'qtitle': unescape(question['title']), 'qbody': question['body'], 'qlink': question['link'],
                'abody': answer['body'], 'alink': answer['link'], 'ascore': answer['score'], 'quota': fullrequest['quota_remaining'] }
    return randomse
  except requests.Timeout as ex:
    print(ex)
    print('*** Note: get_randomse() timed out.')
    return None
  except Exception as ex:
    randomse = {'qtitle': 'Exception occurred', 'qbody': str(ex), 'qlink': 'https://xkcd.com/1084/',
                'abody': '<img src="https://imgs.xkcd.com/comics/error_code.png"/>', 'alink': 'https://xkcd.com/1024/', 'ascore': '', 'quota': '' }
    return randomse
