import argparse
import matplotlib.pyplot as plt
from typing import Any, Counter, Dict, Mapping, List, Union, cast
from wordcloud import WordCloud
from .analyzer import Analyzer
from ..utils import emotion_lexicon
from pathlib import Path
from datetime import datetime

class ItemWordCloud(Analyzer):
    lang = 'en'

    @staticmethod
    def inizialize():
        ItemWordCloud.configureArgs()
        emotion_lexicon.initEmotionLexicon(ItemWordCloud.lang)

    @staticmethod
    def configureArgs():
        parser = argparse.ArgumentParser(
            prog='emotion_analyzer',
            description='',
        )
        parser.add_argument(
            '--lang',
            type=str,
            required=False,
            default='en',
            help='Language.',
        )
        parsed_args, _ = parser.parse_known_args()
        ItemWordCloud.lang = parsed_args.lang

    def filterId(self, sectionId: int) -> bool:
        return True

    def filterObj(self, obj: Mapping[str, Any]) -> bool:
        if obj['type'] == 'ADDITION' or obj['type'] == 'CREATION':
            return True
        else:
            return False


    def finalizeSection(self, sectionCounter: int, currentSectionObjs: List[Mapping[str, Any]], currentSectionId: int) -> Union[None, bool]:
        if sectionCounter < 4000:
            return
        print(datetime.now().strftime("%H:%M:%S"))

        pageTitle: str = currentSectionObjs[0]['pageTitle']

        wordsByEmotions: Union[Dict[emotion_lexicon.Emotions, List[str]], None] = None
        for obj in currentSectionObjs:
            wordsByEmotions = emotion_lexicon.separateWordsByEmotion(obj['cleanedContent'], wordsByEmotions)


        fig, axs = plt.subplots(11, figsize=(20,100))
        fig.suptitle(pageTitle)
        fig.tight_layout()

        for i, e in enumerate(emotion_lexicon.Emotions):
            wordcloud = WordCloud(collocations=False, max_font_size=40).generate(' '.join(wordsByEmotions[e]))
            axs[i].set_title(f"{emotion_lexicon.getEmotionName(e)} - {len(wordsByEmotions[e])}", fontsize=20)
            axs[i].axis("off")
            axs[i].imshow(cast(Any, wordcloud), interpolation='bilinear')

        fig.show()
        fig.savefig(Path('temp') /  f'{pageTitle.replace("/", "-")}.png')
        print(datetime.now().strftime("%H:%M:%S"))
        print(f'{pageTitle} Done')

        return