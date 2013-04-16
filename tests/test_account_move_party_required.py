#!/usr/bin/env python
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

import sys, os
DIR = os.path.abspath(os.path.normpath(os.path.join(__file__,
    '..', '..', '..', '..', '..', 'trytond')))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))

import unittest
import datetime
import trytond.tests.test_tryton
from trytond.tests.test_tryton import test_view, test_depends
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.transaction import Transaction
from trytond.exceptions import UserError


class AccountMovePartyRequiredTestCase(unittest.TestCase):
    '''
    Test Account module.
    '''

    def setUp(self):
        trytond.tests.test_tryton.install_module('account_move_party_required')
        self.account_template = POOL.get('account.account.template')
        self.account = POOL.get('account.account')
        self.type = POOL.get('account.account.type')
        self.company = POOL.get('company.company')
        self.user = POOL.get('res.user')
        self.account_move = POOL.get('account.move')
        self.account_move_line = POOL.get('account.move.line')
        self.journal = POOL.get('account.journal')
        self.period = POOL.get('account.period')
        self.party = POOL.get('party.party')
        self.sequence = POOL.get('ir.sequence')
        self.fiscalyear = POOL.get('account.fiscalyear')

    def test0005views(self):
        '''
        Test views.
        '''
        test_view('account')

    def test0006depends(self):
        '''
        Test depends.
        '''
        test_depends()

    def test0010account_chart(self):
        'Test creation of minimal chart of accounts'
        with Transaction().start(DB_NAME, USER,
                context=CONTEXT):
            company, = self.company.search([('party.name', '=', 'B2CK')])
            self.user.write([self.user(USER)], {
                    'main_company': company.id,
                    'company': company.id,
                    })
            type_, = self.type.create([{
                        'name': 'Type',
                        'company': company.id,
                        }])
            first, second = self.account.create([{
                        'code': '1000000',
                        'name': 'One',
                        'kind': 'payable',
                        'company': company.id,
                        'type': type_.id,
                        'party_required': True,
                        }, {
                        'code': '1000001',
                        'name': 'Two',
                        'kind': 'payable',
                        'company': company.id,
                        'type': type_.id,
                        'party_required': False,
                        }])

            today = datetime.date.today()
            sequence, = self.sequence.create([{
                        'name': '%s' % today.year,
                        'code': 'account.move',
                        'company': company.id,
                        }])
            fiscalyear, = self.fiscalyear.create([{
                        'name': '%s' % today.year,
                        'start_date': today.replace(month=1, day=1),
                        'end_date': today.replace(month=12, day=31),
                        'company': company.id,
                        'post_move_sequence': sequence.id,
                        }])
            self.fiscalyear.create_period([fiscalyear])

            period_id = self.period.find(company.id, date=today)
            journal = self.journal.search([])[0]
            party = self.party.search([])[0]

            move, = self.account_move.create([{
                        'number': '1',
                        'period': period_id,
                        'journal': journal.id,
                        'date': today,
                        }])
            self.account_move_line.create([{
                        'move': move.id,
                        'account': first.id,
                        'party': party.id,
                        }, {
                        'move': move.id,
                        'account': second.id,
                        }, {
                        'move': move.id,
                        'account': first.id,
                        'party': second.id,
                        }])
            self.assertRaises(UserError,
                self.account_move_line.create, [{
                        'move': move.id,
                        'account': first.id,
                        }])

def suite():
    suite = trytond.tests.test_tryton.suite()
    from trytond.modules.company.tests import test_company
    for test in test_company.suite():
        if test not in suite:
            suite.addTest(test)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountMovePartyRequiredTestCase))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
