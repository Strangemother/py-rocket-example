from condition import Condition, ConditionProxy, ConditionProps


class ConditionSet(ConditionProps):
    def set_many(self, k, v):
        items = (self.c1, self.c2, self.c3, )
        for c in items:
            c.live_set(k, v)

    def condition_emit_match_all(self, condition=None):
        print(f'*  Success: {self.__class__.__name__} condition match', condition)

        if condition == self._condition:
            print('Hit Self!')
            return self.all_conditions_success(condition)

        bn = getattr(condition, '_bound_name', None)
        if bn is None:
            print('\nno bound name to condition:', condition)
            return

        print('\nSet', bn)
        # setattr(self, bn, True)
        self._condition.set(bn, True)

    def condition_emit_match_fail(self, condition=None):
        print(f'*  Fail: {self.__class__.__name__} condition match', condition)

        if condition == self._condition:
            print('Hit Self!')
            return self.all_conditions_failure(condition)

        bn = getattr(condition, '_bound_name', None)
        if bn is None:
            print('\nno bound name to condition:', condition)
            return

        print('\nSet', bn)
        # setattr(self, bn, True)
        self._condition.set(bn, False)

    def all_conditions_success(self, condition):
        """All conditions are met, with the given condition as the _instigator_
        of all conditions.
        """
        print('\n.All conditions met.\n')

    def all_conditions_failure(self, condition):
        print('\n.all conditions failure.\n')


class CondLiveT(ConditionSet):
    c1 = Condition({ 'egg': True, 'bacon': True, 'cheese': True})
    c2 = Condition({ 'egg': True, 'bacon': True, 'window': 1})
    c3 = Condition({ 'egg': False, 'cheese': True })

    condition_target = {
        'c1': True,
        'c2': True,
        'c3': True,
    }

    def all_conditions_success(self, condition):
        """All conditions are met, with the given condition as the _instigator_
        of all conditions.
        """
        print('\n.All conditions met.\n')

    def all_conditions_failure(self, condition):
        print('\n.all conditions failure.\n')


class CondLive(ConditionSet):
    c1 = Condition({ 'egg': True, 'bacon': True, 'cheese': True})
    c2 = Condition({ 'egg': True, 'bacon': True, 'window': 1})
    c3 = Condition({ 'egg': False, 'cheese': True })

    condition_target = {
        'c1': True,
        'c2': True,
        'c3': False,
    }

def main():
    p = ConditionProxy()
    c = Condition({ 'egg': True, 'bacon': True, 'cheese': True})
    c2 = Condition({ 'egg': True, 'bacon': True, 'window': 1})
    c3 = Condition({ 'egg': False, 'cheese': True })

    p.add(c, c2, c3)


    return p, c, c2, c3



if __name__ == '__main__':
    #p, c, c2, c3  = main()
    clt = CondLive()
    cl = CondLive()

    print('\nTurning on')
    cl.c1.egg=True
    cl.c1.bacon=True
    cl.c1.cheese=True


    cl.c2.egg=True
    cl.c2.bacon=True
    cl.c2.window=1

    cl.c3.egg=False
    cl.c3.cheese=True


    clt.c1.egg=True
    clt.c1.bacon=True
    clt.c1.cheese=True


    clt.c2.egg=True
    clt.c2.bacon=True
    clt.c2.window=1

    clt.c3.egg=False
    clt.c3.cheese=True

