def fit(src, dst):
    src_aspect = src[0]/src[1]
    dst_aspect = dst[0]/dst[1]
    if src_aspect < dst_aspect:
        return (dst[1] * src_aspect, dst[1])
    else:
        return (dst[0], dst[0] / src_aspect)