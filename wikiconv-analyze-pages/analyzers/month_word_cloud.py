import argparse
import matplotlib.pyplot as plt
from typing import Any, Counter, Dict, Mapping, List, Union, cast
from wordcloud import WordCloud
from .analyzer import Analyzer
from ..utils import emotion_lexicon
from pathlib import Path
from datetime import datetime

class MonthWordCloud(Analyzer):
    lang = 'en'
    outputPath: Path = Path('.')

    @staticmethod
    def inizialize():
        MonthWordCloud.configureArgs()
        emotion_lexicon.initEmotionLexicon(MonthWordCloud.lang)

    @staticmethod
    def configureArgs():
        parser = argparse.ArgumentParser(
            prog='emotion_analyzer',
            description='',
        )
        parser.add_argument(
            '--output-dir-path',
            metavar='OUTPUT_DIR',
            type=Path,
            required=True,
            help='XML output directory.',
        )
        parser.add_argument(
            '--lang',
            type=str,
            required=False,
            default='en',
            help='Language.',
        )
        parsed_args, _ = parser.parse_known_args()
        MonthWordCloud.lang = parsed_args.lang
        MonthWordCloud.outputPath = parsed_args.output_dir_path


    def filterId(self, sectionId: int) -> bool:
        return True

    def filterObj(self, obj: Mapping[str, Any]) -> bool:
        if obj['type'] == 'ADDITION' or obj['type'] == 'CREATION':
            return True
        else:
            return False


    def finalizeSection(self, sectionCounter: int, currentSectionObjs: List[Mapping[str, Any]], currentSectionId: int) -> Union[None, bool]:
        month = str(currentSectionId)
        if sectionCounter < 10:
            print("Skipped " + month)
            return
        print("------" + month)

        wordsByEmotions: Union[Dict[emotion_lexicon.Emotions, List[str]], None] = None
        for obj in currentSectionObjs:
            wordsByEmotions = emotion_lexicon.separateWordsByEmotion(obj['cleanedContent'], wordsByEmotions)

        fig, axs = plt.subplots(nrows=6, ncols=2, figsize=(40,70))
        fig.suptitle(month)
        fig.tight_layout()

        for i, e in enumerate(emotion_lexicon.Emotions):
            x = i // 2
            y = i % 2
            wordcloud = WordCloud(collocations=False, max_font_size=40).generate(' '.join(wordsByEmotions[e]))
            axs[x][y].set_title(f"{emotion_lexicon.getEmotionName(e)} - {len(wordsByEmotions[e])}", fontsize=72)
            axs[x][y].axis("off")
            axs[x][y].imshow(wordcloud, interpolation='bilinear')

        fig.savefig(MonthWordCloud.outputPath /  f'{month}.png')
        print(f'{month} Done')