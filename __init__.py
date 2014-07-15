#This file is part account_move_party_required module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from trytond.pool import Pool
from .account import *
from .move import *


def register():
    Pool.register(
        AccountTemplate,
        Account,
        Line,
        Move,
        module='account_move_party_required', type_='model')
