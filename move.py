#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction


__all__ = ['Move']
__metaclass__ = PoolMeta


class Move:
    __name__ = 'account.move'

    @classmethod
    def create(cls, vlist):
        pool = Pool()
        Account = pool.get('account.account')
        MoveLine = pool.get('account.move.line')
        context = Transaction().context
        if context.get('active_model') == 'account.move.line':
            party = None
            for active_id in context.get('active_ids', []):
                move_line = MoveLine(active_id)
                if getattr(move_line, 'party'):
                    party = move_line.party
                    break
            if party:
                for value in vlist:
                    for line in value['lines']:
                        for line_values in line[1]:
                            account = Account(line_values['account'])
                            if (account.party_required
                                    and 'party' not in line_values):
                                line_values['party'] = party
        return super(Move, cls).create(vlist)
