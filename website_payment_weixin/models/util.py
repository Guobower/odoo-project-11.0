# -*- coding: utf-8 -*-

try:
    import hashlib

    md5_constructor = hashlib.md5
    md5_hmac = md5_constructor
    sha_constructor = hashlib.sha1
    sha_hmac = sha_constructor
except ImportError:
    import md5

    md5_constructor = md5.new
    md5_hmac = md5
    import sha

    sha_constructor = sha.new
    sha_hmac = sha

md5 = md5_constructor


def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Returns a bytestring version of 's', encoded as specified in 'encoding'.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    if not isinstance(s, str):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([smart_str(arg, encoding, strings_only,
                                           errors) for arg in s])
            return str(s).encode(encoding, errors)
    elif isinstance(s, str):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s


def params_filter(params):
    ks = sorted(params.keys())
    newparams = {}
    prestr = ''
    for k in ks:
        v = params[k]
        k = smart_str(k, 'utf-8')
        if k not in ('sign', 'sign_type') and v != '':
            newparams[k] = smart_str(v, 'utf-8')
            if isinstance(newparams[k], str):
                newparam = newparams[k]
            else:
                newparam = str(newparams[k], encoding='utf-8')
            prestr += '%s=%s&' % (str(k, encoding='utf-8'), newparam)
    prestr = prestr[:-1]
    return newparams, prestr


def build_mysign(prestr, key, sign_type='MD5'):
    if sign_type == 'MD5':
        data = (prestr + ("&key=" + key)).encode("utf-8")
        return hashlib.md5(data).hexdigest().upper()
    return ''
