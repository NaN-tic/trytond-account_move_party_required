#This file is part account_move_party_required module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool
from trytond.pyson import Eval, Bool

__all__ = ['AccountTemplate', 'Account', 'Line']


class AccountTemplate(ModelSQL, ModelView):
    __name__ = 'account.account.template'
    party_required = fields.Boolean('Party Required', help='If set, it will '
        'ensure all move lines have a party.')

    def _get_account_value(self, account=None):
        res = super(AccountTemplate, self)._get_account_value(account)
        if not account or account.party_required != self.party_required:
            res['party_required'] = self.party_required
        return res


class Account(ModelSQL, ModelView):
    __name__ = 'account.account'
    party_required = fields.Boolean('Party Required', help='If set, it will '
        'ensure all move lines have a party.')

    @classmethod
    def __setup__(cls):
        super(Account, cls).__setup__()
        cls._error_messages.update({
                'party_required': ('Party Required cannot be set on account '
                    '"%s" because some of its moves have no party set.'),
                })

    @classmethod
    def write(cls, *args):
        Line = Pool().get('account.move.line')
        actions = iter(args)
        for accounts, values in zip(actions, actions):
            if values.get('party_required'):
                moves = Line.search([
                        ('account', 'in', [x.id for x in accounts]),
                        ('party', '=', None),
                        ], limit=1)
                if moves:
                    cls.raise_user_error('party_required', (
                            moves[0].account.rec_name,))
        return super(Account, cls).write(*args)


class Line(ModelSQL, ModelView):
    __name__ = 'account.move.line'
    party_required = fields.Function(fields.Boolean('Party Required'),
        'on_change_with_party_required')

    @fields.depends('account')
    def on_change_with_party_required(self, name=None):
        if self.account:
            return self.account.party_required
        return False

    @classmethod
    def __setup__(cls):
        super(Line, cls).__setup__()
        required = Bool(Eval('party_required'))
        if not cls.party.states.get('required'):
            cls.party.states['required'] = required
        else:
            cls.party.states['required'] |= required
        if 'party_required' not in cls.party.depends:
            cls.party.depends.append('party_required')
