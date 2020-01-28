#! /usr/bin/env python3
#
#   riskfactor_extractor.py
#
#   last update: Feb.5, 2019 Y.Noda
#
import re
from extractor_base import ExtractorBase


class ExtractorRiskfactor(ExtractorBase):

    BEGIN_REGEX = [
        r'(^\s*i\s*te\s*m\s*(No.\s*)?(I|1|2)?\.?\s*a?[\s\—\.\-\–:\227\222|]+ri\s*s\s*k(s)?\s*factors\.?\s*$)',
        r'(\.\s*i\s*te\s*m\s*1\.?a[\s\—\.\-:\227\222|]+?ri\s*s\s*k\s*factors\.?\s*[^\—\-(]$)',  # allowed not starting from a newline -  continued from prior text.
        r'(^\s*i\s*te\s*m\s*1\.?a[\s\—\.\-:\227\222|]+?ris\s*k\s*factors\.?\s+[^\—\-(]$)',  # can match "riskfactors"
        r'(^1?(A\.)?\s*risk\s*factors\.?\s*$)',  # can match "riskfactors"
        r'(^\s*Risk\s+Factors\n+\s*$)',
    ]
    BEGIN_REGEX2 = [
        r'(\s*item\s*1\.?a[\s\—\.\-:\227\222|]+risk\s*factors\.?)',  # allowed not starting from a newline -  continued from prior text.
        r'(\s*item\s*1\.?a[\s\—\.\-:\227\222|]+item\s*1\.?a[\s\—\.\-:\227\222|]+\s*$)',   # Item 1A. Item 1A.
        r'(^\s*([A-Z]\.)?\s*Risk\s+Factors\s+[^(\—\-])',
        r'(^\s*CERTAIN\s+BUSINESS\s+RISKS\.?\s*$)',
        r'(^\s*CERTAIN\s+RISK\s+FACTORS\.?\s*$)',
        r'(^\s*RISKS\s+RELATING\s+TO\s+OUR\s+BUSINESS\.?\s*$)',
        r'(^\s*FACTORS\s+THAT\s+MAY\s+AFFECT\s+FUTURE\s+RESULTS\.?\s*$)',
        r'(^\s*RISKS\s+RELATED\s+TO\s+OUR\s+BUSINESS\s*$)',
        r'(^\s*(item\s*1\.?a[\s\—\.\-:\227\222|]+)?RISKS\s+AND\s+UNCERTAINTIES\s*$)',
        r'(^\s*RISKS\s*$)',
        r'(\s*Forward(\s|-)Looking\s+Statements\s+and\s+Risk\s+Factors\s*$)',
    ]
    END_REGEX = [
        r'(^\s*(i\s*te\s*m\s*)?1\.?(B|\(B\))[\s\-\–\—\.:\227\222|]*UNRE[SEOLV]+ED\s*(SEC\s*)?(ST\s*AFF\s*)?(CO(M)+ENT|ISSUE|MATTER)(S)?\.?\s*$)',
        r'(\s*i\s*te\s*m\s*1\.?\s*B[\s\–\—\.\-:\227\222|]*UNRE[SEOLV]+ED\s*ST\s*AFF\s*CO(M)+ENT(S)?\.?\s*$)',  # allowed not starting from a newline -  continued from prior text.
        r'(\.\s*i\s*te\s*m\s*1\.?\s*B[\s\—\.\-:\227\222|]*UNRE[SEOLV]+ED\s*STAFF\s*CO(M)+ENT(S)?\.?\s*$)',  # allowed not starting from a newline -  continued from prior text.
        r'(\s*ITEM\s*1\.?\s*B[\s\—\.\-:\227\222|]*UNRE[SEOLV]+ED\s*COMMENT\s*LETTER(S)?\.?\s*$)',  # new Nov 18,2016

        r'(^\s*ITEM\s*(2|3)(\.|:)?[\s\.\–\—\-:\227\222|]*(DESCRIPTION\s*OF)?\s*PROPERT(IES|Y)\.? *)',
        r'(^\s*ITEM\s*(2|3)\.?\s*LEGAL\s*PROCEEDINGS\s*$)',   # Nov 18

        r'(^\s*i\s*tem\s*7\.?\s*A[\s\–\—\.\-:\227\222|]*QUA[LITAN]+TIVE\s*AND\s*QUA[LINTA]+TIVE\s*DISCLOSURE(S)?\s*(ABOUT|REGARDING)\s*MARKET\s*RISK(S)?\.?\s*)',
        # r'(^\s*i\s*tem\s*7\.?\s*A[\s\—\.\-:\227\222|]*QUANTITATIVE\s*AND\s*QUALITATIVE\s*DISCLOSURE(S)?\s*(about|regarding)\s*market\s*risk(s)?\.?\s*)',
        r'(^\s*I\s*TEM\s*8\.?[\s\–\—\.\-:\227\222|]*FI[NAIC]+AL\s*STATEMENTS(\s*AND\s*SUPPLEMENTARY\s*DATA)?\.?\s*$)',

        r'(^\s*ITEM\s*9\.?\s*CHANGES\sIN\s*AND\s*DISAGREEMENTS\s*WITH\s*[ACCOUNTANTS]+\s*ON\s*[ACCOUNTING]+\s*AND\s*[FINANCIAL]+\s*DISCLOSURE\.?\s*$)',   # new Nov 18

        r'(^\s*MANAGEMENT\'S REPORT ON INTERNAL\s*CONTROL OVER FINANCIAL REPORTING\s*\n)',
        r'(^\s*FORWARD-LOOKING\s*STATEMENTS\s*\n)',   # added July 26
        r'(^\s*Management.s\s*DISCUSSION\s*AND\s*ANALYSIS\s*OF\s*FINANCIAL\s*CONDITION\s*AND\s*RESULTS\s*OF\s*OPERATIONS\.?\s*$)',   # added July 26
        r'(^CONTROLS\s*AND\s*PROCEDURES\s*$)'  # added Oct 25, 2016
    ]

    # TODO: Prepare Item 1B alternatives - there are times when
    # Item 1B does not exist even though Item 1A exist.

    def __init__(self, input, output, **opts):
        """
        We expect 'resultdir' specified in arg opt.

        """
        super(ExtractorRiskfactor, self).__init__(
            input=input,
            output=output,
            regexs_tuple=(ExtractorRiskfactor.BEGIN_REGEX,
                          ExtractorRiskfactor.BEGIN_REGEX2,
                          ExtractorRiskfactor.END_REGEX),
            **opts
        )

        self.opts = opts
        self.MINIMUM_SECTION_SIZE = 80  # same as default
        self.load_keyword_list('./rf_list.txt')
        self.section_name = self.output

    def find_ending(self, spa, item1b_spans):
        """
        Pick a next section titie from the arg item1b_spans
        The comparison order defines which title is higer priority.
        Item 1B always appears before Item 2 and so forth.
        """
        if spa is None:
            return None
        spb = None
        for spb in item1b_spans:
            # Check if this is within a paragraph
            s = self.text[spb[0]-10:spb[0]].strip()
            if not s.endswith('.') and re.search(r'\b(see|in|and|with)\b',
                                                 s, re.I):
                continue
            if bool(re.match('^item1b', spb[2], re.I)):
                if spa[0] < spb[0]:
                    break
            elif bool(re.match('^item1\(b\)', spb[2], re.I)):
                if spa[0] < spb[0]:
                    break
            elif bool(re.match('^item2', spb[2], re.I)):
                if spa[0] < spb[0]:
                    break
            elif bool(re.match('^item3', spb[2], re.I)):
                if spa[0] < spb[0]:
                    break
            elif bool(re.match('^item7a', spb[2], re.I)):
                if spa[0] < spb[0]:
                    break
            elif bool(re.match('^item8', spb[2], re.I)):
                if spa[0] < spb[0]:
                    break
            elif bool(re.match('^manage', spb[2], re.I)):
                if spa[0] < spb[0]:
                    break
        return spb

    def pick_start_title(self, item1a_spans):
        """
        Picks up start point from the arg item1a_spans list.
        """
        spA = None
        if 0 < len(item1a_spans):
            last_item1a = None
            last_riskfactor = None
            last_other = None
            for spA in item1a_spans:
                s = self.text[spA[1]:spA[1]+20]
                if re.search(r'\bcontinued\b', s, re.I):
                    continue   # has conitunued
                s = self.text[spA[0]-10:spA[0]]
                if re.search(r'\b(see|in|and|with)\b', s, re.I):
                    continue   # in paragraph

                if bool(re.match('^item1a', spA[2], re.I)):
                    last_item1a = spA
                if bool(re.match('.*riskfactor', spA[2], re.I)):
                    last_riskfactor = spA
                if bool(re.match('certain', spA[2], re.I)):
                    last_other = spA
                if bool(re.match('risks', spA[2], re.I)):
                    last_other = spA
                if bool(re.match('factors', spA[2], re.I)):
                    last_other = spA
            spA = None
            if last_item1a:
                spA = last_item1a
            elif last_riskfactor:
                spA = last_riskfactor
            else:
                spA = last_other
            # when it is small, it has to be the table contents
            if spA and spA[0] < ExtractorRiskfactor.TABLE_CONTENTS_AREA_MAX:
                spA = last_riskfactor
        return spA

    def pick_start_title_level2(self, item1a_spans):
        """
        Picks up start point from the arg item1a_spans list.
        On level 2, we don't check the existence of 'item1a' string.
        """
        spA = None
        if 0 < len(item1a_spans):
            last_item1a = None
            last_riskfactor = None
            last_other = None
            for spA in item1a_spans:

                if bool(re.match('.*riskfactor', spA[2], re.I)):
                    last_riskfactor = spA
                if bool(re.match('certain', spA[2], re.I)):
                    last_other = spA
                if bool(re.match('risks', spA[2], re.I)):
                    last_other = spA
                if bool(re.match('factors', spA[2], re.I)):
                    last_other = spA
            spA = None
            if last_riskfactor:
                spA = last_riskfactor
            else:
                spA = last_other
            # when it is small, it has to be the table contents
            if spA and spA[0] < ExtractorRiskfactor.TABLE_CONTENTS_AREA_MAX:
                spA = last_riskfactor
        return spA

    def fit(self, X, y=None):
        """
        Used from Pipeline
        X is an n x 1 matrix. y is not used.
        X is a list of filepathes to process.
        """
        return self

    def fit_transform(self, X, y=None, **kwargs):
        """
        Used from Pipeline
        X is an n x 1 matrix. y is not used.
        X is a list of filepathes to process.
        """
        return self.transform(X)

    def transform(self, X):
        text = X[self.input]
        r = self.search_target_section(text, 0)  # text, path, level
        features_dict = self._organize_output(r, X)
        return features_dict
