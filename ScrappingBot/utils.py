import re
import hashlib

def get_substring(instr, startstr, endstr=None):
    """
    Get sub string between the start and end string
    """
    if startstr == "":
        length = instr.find(endstr)
        if length >= 0:
            return instr[:length]

    start_idx = instr.find(startstr) + len(startstr)
    if start_idx >= 0:
        if endstr:
            length = instr[start_idx:].find(endstr)
            if length == -1:
                return instr[start_idx:]                            
            return instr[start_idx:start_idx+length]
        return instr[start_idx:]


def get_hash(unique_string):
    """
    Encode a dictionary into md5 hash
    The hash value becomes collection index for quick search
    """
    m = hashlib.md5()
    m.update(unique_string.encode('utf-8'))
    return m.hexdigest()

def refine_text(text):
    """
    Refine text to remove special characters
    """    
    if text == "" or text == None:
        return ""

    re_text = re.sub('(&amp;)+', "&", text)
    re_text = re.sub('(&quot;)+', '"', re_text)
    re_text = re.sub('(&apos;)+', "'", re_text)
    re_text = re.sub('(&gt;)+', '>', re_text)
    re_text = re.sub('(&lt;)+', '<', re_text)
    re_text = re.sub('\/|\\|\*', '', re_text)
    re_text = re.sub('\s\s+', ' ', re_text)

    return re_text.strip()

def replace_quote(text):
    """
    Replace quote code with the responding unicode
    """   
    return text.replace("â\x80\x98", "\u2018").replace("â\x80\x99", "\u2019").replace("â\x80\x9c", "\u201C").replace("â\x80\x9d", "\u201D")