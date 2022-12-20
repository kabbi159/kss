# Copyright (C) 2021 Hyunwoong Ko <kevin.ko@tunib.ai> and Sang-Kil Park <skpark1224@hyundai.com>
# All rights reserved.

from typing import List, Tuple


def _get_linux_mecab():
    from mecab import MeCab

    analyzer = MeCab()
    analyzer.morphs("_")
    backend = "mecab"
    return analyzer, backend


def _get_linux_konlpy_mecab():
    from konlpy.tag import Mecab

    analyzer = Mecab()
    analyzer.morphs("_")
    backend = "konlpy"
    return analyzer, backend


def _get_windows_mecab():
    import MeCab

    analyzer = MeCab.Tagger()

    def pos(text: str) -> List[Tuple[str, str]]:
        """Mecab MSVC wrapper"""
        node = analyzer.parseToNode(text)
        outputs = []

        while node:
            surface = node.surface
            tag = node.feature.split(",")[0]
            if "BOS" not in tag and "EOS" not in tag:
                outputs.append((surface, tag))
            node = node.next

        return outputs

    setattr(analyzer, "pos", pos)
    analyzer.pos("_")
    backend = "mecab"
    return analyzer, backend


def _get_windows_konlpy_mecab():
    from konlpy.tag import Mecab

    analyzer = Mecab(dicpath=r"C:\mecab\mecab-ko-dic")
    analyzer.pos("_")
    backend = "konlpy"
    return analyzer, backend


def _get_mecab():
    """
    Try to import and get mecab morpheme analyzer

    Returns:
        Tuple[Optional[Union[mecab.MeCab, konlpy.tag.Mecab, Mecab.Tagger]], Optional[str]]:
            mecab morpheme analyzer and its backend
    """
    try:
        # python-mecab-kor (Linux/MacOS)
        return _get_linux_mecab()
    except Exception:
        try:
            # konlpy (Linux/MacOS)
            return _get_linux_konlpy_mecab()
        except Exception:
            try:
                # mecab-python-msvc (Windows)
                return _get_windows_mecab()
            except Exception:
                try:
                    # konlpy (Windows)
                    return _get_windows_konlpy_mecab()
                except Exception:
                    return None, None


def _get_pecab():
    """
    Try to import and get pecab morpheme analyzer

    Returns:
        Tuple[Optional[pecab.PeCab], Optional[str]]:
            pecab morpheme analyzer and its backend
    """
    try:
        from pecab import PeCab

        analyzer = PeCab()
        analyzer.morphs("_")
        backend = "pecab"
        return analyzer, backend
    except Exception:
        return None, None


def _preserve_space(text: str, tokens: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    Restore spaces from analyzed results

    Args:
        text (str): input text
        tokens (List[Tuple[str, str]]): analyzed results

    Returns:
        List[Tuple[str, str]]: analyzed results with space

    References:
        PororoMecabKoTokenizer from Pororo (kakaobrain)
        https://github.com/kakaobrain/pororo/blob/master/pororo/tasks/tokenization.py#L250
    """
    text = text.strip()
    text_ptr = 0
    results = list()

    for unit in tokens:
        token = unit[0]
        pos = unit[1]
        # \u200d is treated as EMOJI, not SP.
        while text[text_ptr] in " \t\n\r\f\v\u200b\u200c\u2060\ufeff":
            results.append((text[text_ptr], "SP"))
            text_ptr += 1
        results.append((token, pos))
        text_ptr += len(token)
    return results