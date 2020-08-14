
import smartpy as sp
from time import sleep

LEADERSHIP_PAYMENT_AMOUNT = sp.mutez(200000) # two tenths of a tez
COUNTDOWN_DROP_FACTOR = sp.nat(3*60*60*1000)
MINIMAL_COUNT_DOWN_SECONDS = sp.int(5*60)
MINIMAL_COUNT_DOWN_MILLISECONDS = MINIMAL_COUNT_DOWN_SECONDS*sp.int(1000)

class TZButton(sp.Contract):
    def __init__(self):
        self.init(
            leader=sp.address("tz1YtuZ4vhzzn7ssCt93Put8U9UJDdvCXci4"),
            leadership_start_timestamp=sp.timestamp(999999999999999),
            countdown_seconds = sp.int(24*60*60)
        )

    @sp.entry_point
    def default(self, params):
        sp.verify(sp.amount == LEADERSHIP_PAYMENT_AMOUNT)
        sp.verify(self.data.leadership_start_timestamp.add_seconds(self.data.countdown_seconds) > sp.now)
        self.data.leader = sp.sender
        self.data.leadership_start_timestamp = sp.now
        
        balance_weight_tenthtez = sp.fst(sp.ediv(sp.balance,sp.mutez(1)).open_some())/sp.nat(100000) # mutez becomes tenth of a tez
        countdown_milliseconds = self.data.countdown_seconds*sp.int(1000)
        countdown_drop_milliseconds = sp.to_int((COUNTDOWN_DROP_FACTOR+balance_weight_tenthtez)/balance_weight_tenthtez)
        sp.if countdown_milliseconds - countdown_drop_milliseconds > MINIMAL_COUNT_DOWN_MILLISECONDS:
            self.data.countdown_seconds = sp.to_int(sp.as_nat(countdown_milliseconds - countdown_drop_milliseconds)/sp.nat(1000))
        sp.else:
            self.data.countdown_seconds = MINIMAL_COUNT_DOWN_SECONDS
        
    @sp.entry_point
    def withdraw(self, params):
        sp.verify(self.data.leader == sp.sender)
        sp.verify(self.data.leadership_start_timestamp.add_seconds(self.data.countdown_seconds) < sp.now)
        sp.send(sp.sender, sp.balance)

    @sp.entry_point
    def get_leader(self, params):
        destination = sp.set_type_expr(params.callback,
                                       sp.TContract(sp.TAddress))
        sp.transfer(self.data.leader, sp.mutez(0), destination)

    @sp.entry_point
    def get_leadership_start_timestamp(self, params):
        destination = sp.set_type_expr(params.callback,
                                       sp.TContract(sp.TTimestamp))
        sp.transfer(self.data.leadership_start_timestamp, sp.mutez(0), destination)
    
    @sp.entry_point
    def get_countdown_seconds(self, params):
        destination = sp.set_type_expr(params.callback,
                                       sp.TContract(sp.TInt))
        sp.transfer(self.data.countdown_seconds, sp.mutez(0), destination)


class ViewConsumer(sp.Contract):
    def __init__(self):
        self.init(
            leader=sp.address("tz1YtuZ4vhzzn7ssCt93Put8U9UJDdvCXci4"),
            leadership_start_timestamp=sp.timestamp(999999999999999),
            countdown_seconds = sp.int(24*60*60)
        )

    @sp.entry_point
    def receive_leader(self, params):
        sp.set_type(params, sp.TAddress)
        self.data.leader = params

    @sp.entry_point
    def receive_leadership_start_timestamp(self, params):
        sp.set_type(params, sp.TTimestamp)
        self.data.leadership_start_timestamp = params
        
    @sp.entry_point
    def receive_countdown_seconds(self, params):
        sp.set_type(params, sp.TInt)
        self.data.countdown_seconds = params

@sp.add_test(name="TZButton Test")
def test():
    scenario = sp.test_scenario()
    scenario.h1("TZButton - A social dApp experiment")
    scenario.table_of_contents()

    creator = sp.test_account("creator")
    alice = sp.test_account("Alice")
    bob = sp.test_account("Robert")
    dan = sp.test_account("Dan")

    scenario.h2("Accounts")
    scenario.show([creator, alice, bob, dan])
    tz_button_contract = TZButton()
    scenario += tz_button_contract
    
    viewer_contract = ViewConsumer()
    scenario += viewer_contract

    scenario.h2("Pay-In")
    scenario.p("Alice does not pay")
    scenario += tz_button_contract.default().run(sender=alice, valid=False)

    scenario.p("Alice pays too little")
    scenario += tz_button_contract.default().run(sender=alice, amount=sp.mutez(20000), valid=False)

    scenario.p("Alice pays too much")
    scenario += tz_button_contract.default().run(sender=alice, amount=sp.mutez(20001), valid=False)

    scenario.p("Alice pays correct amount")
    scenario += tz_button_contract.default().run(sender=alice, amount=sp.mutez(200000))

    scenario.p("Bob pays correct amount")
    scenario += tz_button_contract.default().run(sender=bob, amount=sp.mutez(200000), now=1)

    scenario.p("Alice pays correct amount after bob again")
    scenario += tz_button_contract.default().run(sender=alice, amount=sp.mutez(200000), now=2)

    scenario.h2("Withdraw")
    scenario.p("Leader tries to withdraw before countdown")
    scenario += tz_button_contract.withdraw().run(sender=alice, valid=False)

    scenario.p("Non-Leader tries to withdraw after countdown")
    scenario += tz_button_contract.withdraw().run(sender=bob, valid=False, now=60*60*24)

    scenario.p("Non-Leader tries to pays correct amount after countdown")
    scenario += tz_button_contract.default().run(sender=bob, amount=sp.mutez(200000), valid=False, now=60*60*24)

    scenario.p("Leader tries to pays correct amount after countdown")
    scenario += tz_button_contract.default().run(sender=alice, amount=sp.mutez(200000), valid=False, now=60*60*24)

    scenario.p("Leader tries to withdraw after countdown")
    scenario += tz_button_contract.withdraw().run(sender=alice, now=60*60*24)




