STOPWORDS = {
    "el","la","de","y","en","que","un","una","los","las","por","para","con","del","al"
}
BLACKLIST = {
    # añade insultos/obscenidades/spam según tu política
    "http","https","www"
}

def is_allowed(lemma: str) -> bool:
    if lemma in STOPWORDS: 
        return False
    for bad in BLACKLIST:
        if bad in lemma:
            return False
    return True
