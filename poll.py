from pyteal import *

def approval_program():

    #numglobaluints: 32
    #numglobalbyteslices: 32

    #numlocaluints: 1
    
    on_optin = Seq(
        Approve() # approve opt in call
    )

    poll_title = Txn.application_args[0] # to store the poll title
    poll_start_time = Btoi(Txn.application_args[1]) # to store the start timestamp of the poll
    poll_end_time = Btoi(Txn.application_args[2]) # to store the end timestamp of the poll

    index = ScratchVar(TealType.uint64) # index for loop
    
    on_application_create = Seq(
        If (And(
            Txn.application_args.length() <= Int(34), # only 30 options can be added (+ integral incremental values to make 60) + 4 to give 64 max global states
            poll_start_time > Global.latest_timestamp(),
            poll_end_time > poll_start_time
        )).Then(
            Seq(
                App.globalPut(Bytes("creator"), Txn.sender()), # write state for the poll creator to global state
                App.globalPut(Bytes("poll_title"), poll_title), # write title for the poll to global state
                App.globalPut(Bytes("poll_start_time"), poll_start_time), # write poll start time to global state
                App.globalPut(Bytes("poll_end_time"), poll_end_time), # write poll end time to global state

                For (index.store(Int(3)), index.load() < Txn.application_args.length(), index.store(index.load() + Int(1))).Do(
                    App.globalPut(Concat(Bytes("option-"), Itob(index.load())), Txn.application_args[index.load()]) # store options in state
                ),

                Approve()
            )
        ).Else(
            Reject()
        )
    )

    choice = Txn.application_args[1] # get index of option

    number_of_votes_for_choice = ScratchVar(TealType.uint64)

    start_time = App.globalGet(Bytes("poll_start_time")) # get poll start time
    end_time = App.globalGet(Bytes("poll_end_time")) # get poll end time
    
    is_allowed_to_vote = And(
        Txn.sender() != Global.creator_address(), # must not be poll creator
        App.localGet(Txn.sender(), Bytes("voted")) == Int(0), # must not have casted a vote
        Global.latest_timestamp() >= start_time, # start date must be reached
        Global.latest_timestamp() <= end_time, # end date must not be exceeded
        App.globalGet(Concat(Bytes("option-"), choice)) != Int(0) # option must be a valid option
    )

    on_vote = Seq(
        If (is_allowed_to_vote).Then(
            Seq(
                number_of_votes_for_choice.store(App.globalGet(Concat(Bytes("option-"), choice, Bytes("-votes"))) + Int(1)), # get vote count + 1
                App.localPut(Txn.sender(), Bytes("choice"), choice), # write to state to ensure user doesn't double vote
                App.globalPut(Concat(Bytes("option-"), choice, Bytes("-votes")), number_of_votes_for_choice.load()), # increment vote count for vote option
                Approve()
            )
        ).Else(
            Reject()
        )
    )

    get_votes_count = ScratchVar(TealType.uint64)
    choice = App.localGet(Txn.sender(), Bytes("choice")) # get user choice

    on_retract = Seq(
        get_votes_count.store(App.globalGet(Concat(Bytes("option-"), choice, Bytes("-votes")))), # store value of votes for choice
        If (
            And(
                choice != Int(0), # make sure choice isn't empty
                get_votes_count.load() >= Int(1) # ensure there is at least one vote
            )
        ).Then(
            Seq(
                App.globalPut(App.globalGet(Concat(Bytes("option-"), choice, Bytes("-votes"))), get_votes_count.load() - Int(1)), # remove user vote
                App.localDel(Txn.sender(), Bytes("choice")) # remove state for choice
            )
        ),
        Approve()
    )
    
    on_call_method = Txn.application_args[0]
    
    on_call = Cond(
        [on_call_method == Bytes("optin"), on_optin],
        [on_call_method == Bytes("vote"), on_vote],
        [on_call_method == Bytes("retract"), on_retract],
    )
    
    program = Cond(
        [Txn.application_id() == Int(0), on_application_create],
        [
            Or(
                Txn.on_completion() == OnComplete.OptIn,
                Txn.on_completion() == OnComplete().NoOp
            ),
            on_call
        ],
        [
            Or(
                Txn.on_completion() == OnComplete.CloseOut,
                Txn.on_completion() == OnComplete.UpdateApplication,
                Txn.on_completion() == OnComplete.DeleteApplication
            ),
            Reject()
        ]
    )
    return program

def clear_program():
    get_votes_count = ScratchVar(TealType.uint64)
    choice = App.localGet(Txn.sender(), Bytes("choice")) # get user choice
    return Seq(
        get_votes_count.store(App.globalGet(Concat(Bytes("option-"), choice, Bytes("-votes")))), # store value of votes for choice
        If (
            And(
                choice != Int(0), # make sure choice isn't empty
                get_votes_count.load() >= Int(1) # ensure there is at least one vote
            )
        ).Then(
            Seq(
                App.globalPut(App.globalGet(Concat(Bytes("option-"), choice, Bytes("-votes"))), get_votes_count.load() - Int(1)), # remove user vote
                App.localDel(Txn.sender(), Bytes("choice")) # remove state for choice
            )
        ),
        Approve()
    )

#compile teal
if __name__ == "__main__":
    with open("poll_approval_program.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=5)
        f.write(compiled)

    with open("poll_clear_program.teal", "w") as f:
        compiled = compileTeal(clear_program(), mode=Mode.Application, version=5)
        f.write(compiled)