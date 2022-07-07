from pyteal import *

def approval_program():
    
    on_optin = Seq(
        Approve()
    )
    
    on_create = Seq(
        
    )
    
    on_call_method = Txn.application_args[0]
    
    on_call = Cond(
        [on_call_method == Bytes("optin"), on_optin],
    )
    
    program = Cond(
        [Txn.application_id() == Int(0), on_create],
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
    return Return(Int(1))

#compile teal
if __name__ == "__main__":
    with open("poll_approval_program.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=5)
        f.write(compiled)

    with open("poll_clear_program.teal", "w") as f:
        compiled = compileTeal(clear_program(), mode=Mode.Application, version=5)
        f.write(compiled)