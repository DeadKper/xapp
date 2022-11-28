class FrozenDict(dict):
    def __hash__(self):
        return id(self)

    def __immutable__(self, *args, **kws):
        raise TypeError('object is immutable')

    __setitem__ = __immutable__
    __delitem__ = __immutable__
    clear = __immutable__
    update = __immutable__
    setdefault = __immutable__  # type: ignore
    pop = __immutable__
    popitem = __immutable__
